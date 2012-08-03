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
                      "/analytic-module/R/authority/R",
                      sep=""), pattern="*.R")

# Creating connection to database
db.configuration <- ReadDBConfiguration()
mychannel <- 
  dbConnect(MySQL(), user=db.configuration$user, dbname=db.configuration$name,
            host="localhost", password=db.configuration$password)

# Retrieving all tags (categories)
tags <- GetTagsFromDB(mychannel)

lapply(tags, ComputeUsersAuthoritiesForTag, db.channel=mychannel)

# Closing the connection
dbDisconnect(mychannel)
