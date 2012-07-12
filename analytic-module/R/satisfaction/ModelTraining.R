GetTrainingData <- function(db.channel) {
  require("RMySQL")
  
  folder <- paste(Sys.getenv("CQA_HOME"),
                  "/analytic-module/R/satisfaction/features/", sep="")
  
  sql <- paste(readLines(paste(folder, "Satisfied.sql", sep="")), 
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  data <- fetch(results, n=-1)
  
  sql <- paste(readLines(paste(folder, "AvgAnsNumForTag.sql", sep="")), 
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  data <- merge(data, fetch(results, n=-1), all=TRUE)
  
  sql <- paste(readLines(paste(folder, "AvgAnsNumForUser.sql", sep="")), 
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  data <- merge(data, fetch(results, n=-1), all=TRUE)
  
  sql <- paste(readLines(paste(folder, "AvgAnsNumPerHourForTag.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  data <- merge(data, fetch(results, n=-1), all=TRUE)
  
  sql <- paste(readLines(paste(folder, "AvgAnsScoreForTag.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  data <- merge(data, fetch(results, n=-1), all=TRUE)
  
  sql <- paste(readLines(paste(folder, "MemberDuration.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  data <- merge(data, fetch(results, n=-1), all=TRUE)
  
  sql <- paste(readLines(paste(folder, "NumAnsAccepted.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  data <- merge(data, fetch(results, n=-1), all=TRUE)
  
  sql <- paste(readLines(paste(folder, "NumAnsReceived.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  data <- merge(data, fetch(results, n=-1), all=TRUE)
  
  sql <- paste(readLines(paste(folder, "PostingTime.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  data <- merge(data, fetch(results, n=-1), all=TRUE)
  
  sql <- paste(readLines(paste(folder, "UserRating.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  data <- merge(data, fetch(results, n=-1), all=TRUE)
  
  data$satisfied <- as.factor(data$satisfied)
  data[is.na(data)] <- 0
  data
}

TrainModel <- function(training.data) {
  require("RWeka")
  
  J48(satisfied ~ ., data=training.data)
}

library("RMySQL")
library("rJava")

sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/common",
                      sep=""), pattern="*.R")
db.configuration <- ReadDBConfiguration()
mychannel <- 
  dbConnect(MySQL(), user=db.configuration$user,
            host="localhost", password=db.configuration$password,
            dbname=db.configuration$name)
data <- GetTrainingData(mychannel)

model <- TrainModel(data)
.jcache(model$classifier)
save(model,file=paste(Sys.getenv("CQA_HOME"), 
                           "/analytic-module/R/satisfaction/model.dat",
                           sep=""))

dbDisconnect(mychannel)