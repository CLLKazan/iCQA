#!/usr/bin/env Rscript

# Script for computing answerer recommendations per each question

library(RMySQL)
library(R.utils)
library(tm)
library(foreach)
library(iterators)
library(doMC)
library(Snowball)
# Registers the multicore environment
registerDoMC(cores=2)
# Loading auxiliary functions
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/common",
                      sep=""), pattern="*.R")
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/answerer-recommendation/R",
                      sep=""), pattern="*.R")

# Creating connection to database
db.configuration <- ReadDBConfiguration()
channel <- 
  dbConnect(MySQL(), dbname=db.configuration$name, user=db.configuration$user,
            host="localhost", password=db.configuration$password)
# Retrieving open questions
open.questions <- GetOpenQuestions(channel)
# Retrieving candidate questions
candidate.questions <- GetCandidateQuestions(channel)
# Retrieving all answers
answers <- GetAnswers(channel)
# Retrieving user profiles
user.profiles <- GetUserProfiles(channel)
# Retrieving question-answerer pairs
question.answerer.pairs <- GetQuestionAnswerers(channel)
# Building the document-term matrix across user profiles and questions
# ATTENTION!!! The order of concatenating shouldn't be changed, otherwise,
# TrainUQA and other functions would be broken
indexing.vector <- c(user.profiles$post,
                         open.questions$title,
                         open.questions$body,
                         candidate.questions$title,
                         candidate.questions$body)
corpus <- tm::Corpus(VectorSource(indexing.vector))
dtm <- 
  tm::DocumentTermMatrix(corpus, control=list(tolower=T,
                                              removePunctuation=T,
                                              removeNumbers=T,
                                              stopwords=T,
                                              stemming=T))

# Trains the UQA model
uqa.model <- TrainUQA(dtm, user.profiles)

question.answerers <- 
  foreach(question=iter(open.questions[1:10,], by='row'), .combine=rbind) %dopar% {
    question.topic.probabilities <- 
      GetQuestionTopicDistribution(dtm,
                                   length(user.profiles$post),
                                   length(user.profiles$post)+
                                   length(open.questions$title),
                                   uqa.model,
                                   question)
    
      topic.number <- length(question.topic.probabilities$topics)
      candidate.number <- length(candidate.questions$id)
      cand.title.offset <- length(user.profiles$post)+ length(open.questions$title)+
                        length(open.questions$body)
      cand.body.offset <- 
            length(user.profiles$post) + length(open.questions$title)+
            length(open.questions$body)+ length(candidate.questions$title)
      foreach(candidate=iter(candidate.questions[1:10,], by='row'), .combine=rbind) %dopar% {
              candidate.topic.probabilities <- GetQuestionTopicDistribution(dtm,
                                                              cand.title.offset,
                                                              cand.body.offset,
                                                              uqa.model,
                                                              candidate)
              candidate.probability <- 
                topic.number*
                (candidate.topic.probabilities$prob %*% 
                question.topic.probabilities$prob)/candidate.number
              candidate.answerers <- 
                with(question.answerer.pairs, question.answerer.pairs[which(
                question_id==candidate$id),])
              foreach(answerer=iter(candidate.answerers, by='row'), .combine=rbind) %do% {
                c(question$id, answerer$answerer_id, candidate.probability)
              }
            }
    }
question.answerers <- as.data.frame(question.answerers)
names(question.answerers) <- c("question_id", "user_id", "score")
rownames(question.answerers) <- 1:length(question.answerers$question_id)
# Merging the duplicates
question.answerers <- ddply(question.answerers,
                            .(question.answerers$question_id,
                              question.answerers$user_id),
                            function(row) {sum(row$score)})
# Update the question answerer index
dbWriteTable(channel, "analytics_answerer_recommendation",
             question.answerers, overwrite=T)
# Closing the connection
dbDisconnect(channel)
