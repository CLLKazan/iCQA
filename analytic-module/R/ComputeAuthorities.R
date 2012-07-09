#!/usr/bin/env Rscript

# Script for computing authority score for all the users in
# each category (tag)

library("RMySQL")
library("R.utils")
library("igraph")

# Loading auxiliary functions
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/common",
                      sep=""), pattern="*.R")
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/authority",
                      sep=""), pattern="*.R")

# Creating connection to database
db.configuration <- ReadDBConfiguration()
mychannel <- 
  dbConnect(MySQL(), user=db.configuration$user,
            host="localhost", password=db.configuration$password)

# Retrieving all tags (categories)
tags <- GetTagsFromDB(mychannel, db.configuration$name)

UpdateAuthorityForUser <- function(user.id, db.channel, db.name, 
                                   tag.id, score) {
  if (!is.na(score[user.id])) {
    # Update the table
    UpdateAuthorityTable(db.channel, db.name, user.id, 
                         tag.id, score[user.id])
  }
}

UpdateMatrixForQuestion <- function(question.id, db.channel, db.name) {
  answer.author <- GetQuestionAcceptedAnswerAuthor(db.channel, 
                                                   db.name, 
                                                   question.id)
  question.author <- GetQuestionAuthor(db.channel, 
                                       db.name, 
                                       question.id)
  # If accepted answer exists
  if (!is.null(answer.author)) {
    result <- c(question.author, answer.author)
  } else {
    result <- c(NA, NA)
  }
  result
}

ComputeUsersAuthoritiesForTag <- function(tag.id, db.channel, db.name) {
  # Retrieving questions with the given tag
  questions <- GetQuestionsFromDB(db.channel, db.name, tag.id)
  
  list <- lapply(questions, UpdateMatrixForQuestion, db.channel=db.channel, 
                 db.name=db.name)
  data <- unlist(list)
  if(!is.null(data)) {
    # Matrix of edges
    user.matrix <- na.omit(matrix(data, ncol=2, byrow=TRUE))
    
    # Creating graph and computing authority scores
    user.graph <- graph.edgelist(user.matrix)
    score <- authority.score(user.graph)$vector
    
    users <- seq(length=length(score))
    score.frame <- data.frame(score, users)
    ordered.score.frame <- score.frame[-order(score.frame$score),]
        
    # Write score only of 12 top users
    lapply(ordered.score.frame[1:12,]$users, UpdateAuthorityForUser, 
           db.channel=db.channel, db.name=db.name, 
           tag.id=tag.id, score=score)
  }
}
lapply(tags, ComputeUsersAuthoritiesForTag, db.channel=mychannel, 
       db.name=db.configuration$name)

# Closing the connection
dbDisconnect(mychannel)