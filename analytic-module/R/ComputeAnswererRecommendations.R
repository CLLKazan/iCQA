#!/usr/bin/env Rscript

# Script for computing answerer recommendations per each question

library(RMySQL)
library(R.utils)
library(tm)
library(foreach)
library(iterators)
library(doMC)
library(Snowball)
library(plyr)
# Registers the multicore environment
registerDoMC(cores=3)
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
                         candidate.questions$body,
                         candidate.questions$tagnames)
corpus <- tm::Corpus(VectorSource(indexing.vector))
dtm <- 
  tm::DocumentTermMatrix(corpus, control=list(tolower=T,
                                              removePunctuation=T,
                                              removeNumbers=T,
                                              stopwords=T,
                                              stemming=T))
# Building the document term matrix for candidate questions
candidate.index.vector <- 
  foreach(candidate=iter(candidate.questions, by='row'), .combine=c) %dopar%{
  paste(candidate$title, candidate$body, candidate$tagnames)
}
candidate.corpus <- tm::Corpus(VectorSource(candidate.index.vector))
candidate.dtm <- 
  tm::DocumentTermMatrix(candidate.corpus, control=list(tolower=T,
                                              removePunctuation=T,
                                              removeNumbers=T,
                                              stopwords=T,
                                              stemming=T))
# Trains the UQA model
uqa.model <- TrainUQA(dtm, user.profiles)
topics <- unique(uqa.model$theta$topic_id)
# Gets the topic distributions for each open question
question.distributions <- 
  foreach(question=iter(open.questions, by='row')) %dopar% {
      GetQuestionTopicDistribution(dtm,
                                   length(user.profiles$post),
                                   length(user.profiles$post)+
                                   length(open.questions$title),
                                   uqa.model,
                                   question,
                                   topics)
    }
# Gets the topic distributions for each candidate question
candidate.distributions <-
  foreach(candidate=iter(candidate.questions, by='row')) %dopar% {
    cand.title.offset <- length(user.profiles$post)+ length(open.questions$title)+
      length(open.questions$body)
    cand.body.offset <- 
      length(user.profiles$post) + length(open.questions$title)+
      length(open.questions$body)+ length(candidate.questions$title)
      GetQuestionTopicDistribution(dtm,
                                  cand.title.offset,
                                  cand.body.offset,
                                  uqa.model,
                                  candidate,
                                  topics)
}
# Computes QST-TOPIC scores (see the original paper)
topic.number <- length(topics)
candidate.number <- length(candidate.questions$id)
qst.topic.scores <- 
  foreach(question=iter(question.distributions, by='row'), .combine=rbind) %dopar% {
    foreach(candidate=iter(candidate.distributions, by='row'), .combine=rbind) %dopar% {
        if (question$id==candidate$id) {(NULL)}
          else {
            candidate.probability <- topic.number*
                                    (candidate$prob %*% 
                                    question$prob)/candidate.number    
            candidate.answerers <- 
                with(question.answerer.pairs, question.answerer.pairs[which(
                question_id==candidate$id),])
      foreach(answerer=iter(candidate.answerers, by='row'), .combine=rbind) %do% {
        c(question$id, answerer$answerer_id, candidate.probability)
      }
              }
  }
}

qst.topic.scores <- as.data.frame(qst.topic.scores)
names(qst.topic.scores) <- c("question_id", "user_id", "score")
rownames(qst.topic.scores) <- 1:length(qst.topic.scores$question_id)
# Merging the duplicates
qst.topic.scores <- ddply(qst.topic.scores,
                            .(qst.topic.scores$question_id,
                              qst.topic.scores$user_id),
                            function(row) {max(row$score)})
names(qst.topic.scores) <- c("question_id", "user_id", "score")
# Gets the topic distributions for each user profile
users <- unique(user.profiles$user_id)
user.profile.distributions <- 
  llply(users, function(user.id) {
    GetUserProfileTopicDistribution(dtm,
                                    uqa.model,
                                    user.id,
                                    topics)
  }, .parallel=T)
# Computes USER-TOPIC scores (see the original paper)
user.number <- length(users)
user.topic.scores <- ldply(question.distributions, function(question) {
    ldply(user.profile.distributions, function(candidate) {
        candidate.probability <- topic.number*
          (candidate$prob %*% 
          question$prob)/user.number
          if (question$id==1 & candidate$id==1) {
            print(candidate)
          }
          frame <- as.data.frame(t(c(question$id, candidate$id, candidate.probability)))
          names(frame) <- c("question_id", "user_id", "score")
          frame
      })
    }, .parallel=T)
# Computes QST-USER-TOPIC scores (see the original paper)
qst.user.topic.scores <- 
  merge(user.topic.scores, qst.topic.scores, by=c("question_id", "user_id"), all=T)
names(qst.user.topic.scores) <- c("question_id", "user_id",
                                  "qst_topic_score", "user_topic_score")
qst.user.topic.scores$qst_topic_score[which(
                          is.na(qst.user.topic.scores$qst_topic_score))] <- 0
qst.user.topic.scores$user_topic_score[which(
  is.na(qst.user.topic.scores$user_topic_score))] <- 0
lambda1 <- 0.8
qst.user.topic.values <- (lambda1*qst.user.topic.scores$qst_topic_score) +
                          ((1-lambda1)*qst.user.topic.scores$user_topic_score)
qst.user.topic.scores$qst_user_topic_score <- qst.user.topic.values
question.answerers <- 
  subset(qst.user.topic.scores, select=c("question_id", "user_id", "qst_user_topic_score"))
names(question.answerers) <- c("question_id", "user_id", "score")
# Update the question answerer index
dbWriteTable(channel, "analytics_answerer_recommendation",
             question.answerers, overwrite=T, row.names=F)
# Closing the connection
dbDisconnect(channel)
