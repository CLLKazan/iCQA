#!/usr/bin/env Rscript

# Script for computing answerer recommendations per each question

library(RMySQL)
library(R.utils)
library(tm)

# Loading auxiliary functions
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/common",
                      sep=""), pattern="*.R")
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/answerer-recommendation",
                      sep=""), pattern="*.R")

# Creating connection to database
db.configuration <- ReadDBConfiguration()
channel <- 
  dbConnect(MySQL(), user=db.configuration$user,
            host="localhost", password=db.configuration$password)
# Retrieving all questions
questions <- GetQuestions(channel,db.configuration$name)
# Retrieving all answers
answers <- GetAnswers(channel,db.configuration$name)
# Retrieving user profiles
user.profiles <- GetUserProfiles(channel,db.configuration$name)

uqa.model <- TrainUQA(channel,db.configuration$name, user.profiles)

# Closing the connection
dbDisconnect(channel)
