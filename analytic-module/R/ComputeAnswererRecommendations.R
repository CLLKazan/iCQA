#!/usr/bin/env Rscript

# Script for computing answerer recommendations per each question

library(RMySQL)
library(R.utils)
library(tm)
library(foreach)
library(iterators)
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
  dbConnect(MySQL(), user=db.configuration$user,
            host="localhost", password=db.configuration$password)
# Retrieving open questions
# open.questions <- GetOpenQuestions(channel,db.configuration$name)
# # Retrieving candidate questions
# candidate.questions <- GetCandidateQuestions(channel,db.configuration$name)
# # Retrieving all answers
# answers <- GetAnswers(channel,db.configuration$name)
# # Retrieving user profiles
# user.profiles <- GetUserProfiles(channel,db.configuration$name)
# # Building the document-term matrix across user profiles and questions
# # ATTENTION!!! The order of concatenating shouldn't be changed, otherwise,
# # TrainUQA and other functions would be broken
# indexing.vector <- c(user.profiles$post,
#                          open.questions$title,
#                          open.questions$body,
#                          candidate.questions$title,
#                          candidate.questions$body)
# corpus <- tm::Corpus(VectorSource(indexing.vector))
# dtm <- 
#   tm::DocumentTermMatrix(corpus, control=list(removePunctuation=T, stopwords=T))
# 
# # Trains the UQA model
# uqa.model <- TrainUQA(dtm, user.profiles)
question.answerers <- 
  foreach(question=iter(open.questions[1:2,], by='row'), .combine=rbind) %do% {
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
      foreach(candidate=iter(candidate.questions[1:2,], by='row'), .combine=rbind) %do% {
              candidate.topic.probabilities <- GetQuestionTopicDistribution(dtm,
                                                              cand.title.offset,
                                                              cand.body.offset,
                                                              uqa.model,
                                                              candidate)
              candidate.probability <- 
                topic.number*
                (candidate.topic.probabilities$prob %*% 
                question.topic.probabilities$prob)/candidate.number
              c(question$id, candidate$author_id, .1)
            }
    }

# Closing the connection
dbDisconnect(channel)
