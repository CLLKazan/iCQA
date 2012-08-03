#!/usr/bin/env Rscript

library("RMySQL")
library("R.utils")
# Loading auxiliary functions
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                "/analytic-module/R/common",
                sep=""), pattern="*.R")
db.configuration <- ReadDBConfiguration()
mychannel <- 
  dbConnect(MySQL(), user=db.configuration$user,
            host="localhost", password= db.configuration$password)
results <- 
  dbSendQuery(mychannel,
              paste("SELECT 1 FROM ", db.configuration$name, ".forum_node", sep=""))
data <- fetch(results, n=-1)
dbDisconnect(mychannel)
