
library("RMySQL")
library("R.utils")
library("igraph")
library("authority")

# Loading auxiliary functions
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/common",
                      sep=""), pattern="*.R")

sink("/dev/null")                      
db.configuration <- ReadDBConfiguration()
mychannel <- 
  dbConnect(MySQL(), user=db.configuration$user,
            host="localhost", password=db.configuration$password)

# Retrieving all tags (categories)
tags <- GetTagsFromDB(mychannel, db.configuration$name)

lapply(tags[1:2], ComputeUsersAuthoritiesForTag, db.channel=mychannel, 
       db.name=db.configuration$name)

# Closing the connection
dbDisconnect(mychannel)

sink()
2+2
