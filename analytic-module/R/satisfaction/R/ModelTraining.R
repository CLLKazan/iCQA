MergeFrameList <- function(x, L) {
  # Merges list of data frames
  #
  # Args:
  #   x: initial frame
  #   L: list of data frames
  #
  # Returns:
  #   Resulting data frame
  for(e in L) {
    x <- merge(x,e,all=TRUE)
  }
  x
}

MergeFrames <- function(data, frame.list) {
  # Does necessary transformations into the training data
  #
  # Args:
  #   data: initial frame
  #   frame.list: list of data frames
  #
  # Returns:
  #   Resulting data frame
  data <- MergeFrameList(data,frame.list)
  data$satisfied <- as.factor(data$satisfied)
  data[is.na(data)] <- 0
  data$avg_ans_score_tag <- data$avg_ans_ups_tag - data$avg_ans_downs_tag
  data$avg_ans_ups_tag <- NULL
  data$avg_ans_downs_tag <- NULL
  data
}

GetTrainingData <- function(db.channel) {
  # Retrieves training data from the db
  #
  # Args:
  #   db.channel: db connection object
  #
  # Returns:
  #   Data frame of training data
  require("RMySQL")
  
  folder <- paste(Sys.getenv("CQA_HOME"),
                  "/analytic-module/R/satisfaction/inst/sql/", sep="")
  
  sql <- paste(readLines(paste(folder, "Satisfied.sql", sep="")), 
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  data <- fetch(results, n=-1)
  
  sql <- paste(readLines(paste(folder, "AvgAnsNumForTag.sql", sep="")), 
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  d1 <- fetch(results, n=-1)
  
  sql <- paste(readLines(paste(folder, "AvgAnsNumForUser.sql", sep="")), 
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  d2 <- fetch(results, n=-1)
  
  sql <- paste(readLines(paste(folder, "AvgAnsNumPerHourForTag.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  d3 <- fetch(results, n=-1)
  
  sql <- paste(readLines(paste(folder, "AvgAnsUpsForTag.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  d4 <- fetch(results, n=-1)
  
  sql <- paste(readLines(paste(folder, "AvgAnsDownsForTag.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  d5 <- fetch(results, n=-1)
  
  sql <- paste(readLines(paste(folder, "MemberDuration.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  d6 <- fetch(results, n=-1)
  
  sql <- paste(readLines(paste(folder, "NumAnsAccepted.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  d7 <- fetch(results, n=-1)
  
  sql <- paste(readLines(paste(folder, "NumAnsReceived.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  d8 <- fetch(results, n=-1)
  
  sql <- paste(readLines(paste(folder, "PostingTime.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  d9 <- fetch(results, n=-1)
  
  sql <- paste(readLines(paste(folder, "UserRating.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  d10 <- fetch(results, n=-1)
  
  data <- MergeFrames(data, list(d1,d2,d3,d4,d5,d6,d7,d8,d9,d10))
  data
}

TrainModel <- function(training.data) {
  # Trains C4.5 decision tree
  #
  # Args:
  #   training.data: data frame of training data
  #
  # Returns:
  #   Trained model
  require("RWeka")
  
  J48(satisfied ~ ., data=training.data)
}
