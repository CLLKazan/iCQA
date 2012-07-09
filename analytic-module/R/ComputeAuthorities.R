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
ComputeUsersAuthoritiesForTag <- function(tag.id) {
  # Retrieving questions with the given tag
  questions <- GetQuestionsFromDB(mychannel, db.configuration$name, tag.id)
  
  UpdateMatrixForQuestion <- function(question.id) {
    answer.author <- GetQuestionAcceptedAnswerAuthor(mychannel, 
                                                     db.configuration$name, 
                                                     question.id)
    question.author <- GetQuestionAuthor(mychannel, 
                                         db.configuration$name, 
                                         question.id)
    # If accepted answer exists
    if (!is.null(answer.author)) {
      result <- c(question.author, answer.author)
    } else {
      result <- c(NA, NA)
    }
    result
  }
  #matrix of edges
  list <- lapply(questions, UpdateMatrixForQuestion)
  data <- unlist(list)
  if(!is.null(data)) {
    user.matrix <- na.omit(matrix(data, ncol=2, byrow=TRUE))
    
    # Creating graph and computing authority scores
    user.graph <- graph.edgelist(user.matrix)
    score <- authority.score(user.graph)$vector
    
    users <- seq(length=length(score))
    score.frame <- data.frame(score, users)
    ordered.score.frame <- score.frame[-order(score.frame$score),]
    
    UpdateAuthorityForUser <- function(user.id) {
      if (!is.na(score[user.id])) {
        # Update the table
        UpdateAuthorityTable(mychannel, db.configuration$name, user.id, 
                             tag.id, score[user.id])
      }
    }
    # Write score only of 12 top users
    lapply(ordered.score.frame[1:12,]$users, UpdateAuthorityForUser)
  }
}
lapply(tags, ComputeUsersAuthoritiesForTag)

# Closing the connection
dbDisconnect(mychannel)