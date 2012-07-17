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
  
  sql <- paste(readLines(paste(folder, "AvgAnsUpsForTag.sql", sep="")),
               collapse=" ")
  results <- dbSendQuery(db.channel, sql)
  data <- merge(data, fetch(results, n=-1), all=TRUE)
  
  sql <- paste(readLines(paste(folder, "AvgAnsDownsForTag.sql", sep="")),
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
  data$avg_ans_score_tag <- data$avg_ans_ups_tag - data$avg_ans_downs_tag
  data$avg_ans_ups_tag <- NULL
  data$avg_ans_downs_tag <- NULL
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