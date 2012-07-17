#!/usr/bin/env Rscript

# Script for computing satisfaction prediction for all unanswered questions

library("RMySQL")
library("R.utils")

# Loading auxiliary functions
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/common",
                      sep=""), pattern="*.R")
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/satisfaction",
                      sep=""), pattern="*.R", recursive=FALSE)

# Creating connection to database
db.configuration <- ReadDBConfiguration()
mychannel <- 
  dbConnect(MySQL(), user=db.configuration$user,
            host="localhost", password=db.configuration$password,
            dbname=db.configuration$name)
# Retrieving training data
data <- GetTrainingData(mychannel)

# Trained model
model <- TrainModel(data)

# Predict scores only for new questions
results <- dbSendQuery(mychannel, "SELECT id AS q_id FROM forum_node WHERE 
                       node_type='question' AND id NOT IN (SELECT question_id FROM
                       analytics_satisfaction)")
new.data <- fetch(results, n=-1)
data <- subset(data, satisfied==0, select=-satisfied)
data$row.names <- NULL
new.data <- merge(data, new.data)

# If such questions exist
if (length(new.data$q_id) > 0) {
  scores <- predict(model, newdata=new.data, type="probability")[,2]
  dbWriteTable(mychannel, "analytics_satisfaction", 
               data.frame(question_id=new.data$q_id, score=scores),
               append=TRUE, row.names=FALSE)
}

dbDisconnect(mychannel)