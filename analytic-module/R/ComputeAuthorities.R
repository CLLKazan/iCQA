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
tags <- RetrieveTableFromDB(mychannel, db.configuration$name, 
                            ".forum_tag", "id")

for (tag.id in tags) {
  # Matrix of edges
  user.matrix <- matrix(nrow=0, ncol=2)
  
  # Retrieving questions with the given tag
  questions <- GetQuestionsFromDB(mychannel, db.configuration$name, tag.id)
  
  for (question.id in questions) {
    answer.author <- GetQuestionAcceptedAnswerAuthor(mychannel, 
                                                     db.configuration$name, 
                                                     question.id)
    question.author <- GetQuestionAuthor(mychannel, 
                                         db.configuration$name, 
                                         question.id)
    # If accepted answer exists
    if (!is.null(answer.author)) {
      # Add edge to the matrix
      user.matrix <- rbind(user.matrix, c(question.author, answer.author))
    }
  }
  
  # Creating graph and computing authority scores
  user.graph <- graph.edgelist(user.matrix)
  score <- authority.score(user.graph)$vector
  
  # Retrieve all the users
  users <- GetUsersFromDB(mychannel, db.configuration$name)
  for (user.id in users) {
    if (!is.na(score[user.id])) {
      # Update the table
      UpdateAuthorityTable(mychannel, db.configuration$name, user.id, 
                           tag.id, score[user.id])
    }
  }
}

# Closing the connection
dbDisconnect(mychannel)