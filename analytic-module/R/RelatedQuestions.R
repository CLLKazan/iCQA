#!/usr/bin/env Rscript

# Script for finding related questions

library("RMySQL")
library("R.utils")
#library("RTextTools")
library("topicmodels")

is.parallel <- require(doMC)
if(is.parallel){
  registerDoMC()
}

# Loading auxiliary functions
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/common",
                      sep=""), pattern="*.R")
package.home <- paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/related-questions",
                      sep="")
sourceDirectory(paste(package.home,"/R",sep=""), pattern="*.R")

# Creating connection to database
db.configuration <- ReadDBConfiguration()
mychannel <- 
  dbConnect(MySQL(), user=db.configuration$user, dbname=db.configuration$name,
            host="localhost", password=db.configuration$password)

questions <- GetQuestions(mychannel)
tags <- GetTagQuestionAssociations(mychannel)

#removing HTML tags
questions$body <- unlist(llply(questions$body, function(q){
  gsub("<[^>]+>","",q)
}, .parallel=is.parallel))

stored.lda <- paste(package.home,"/data/lda.RData",sep="")
if(file.exists(stored.lda)){
  load(stored.lda)
}else{
  lda <- GetLDAModel(questions,c(16,32,48,64,128))
  save(lda, file=stored.lda)
}

questions <- PopulateWithAnswerScores(mychannel, questions)

result <- ddply(questions, c(), function(q){
  cnd <- GetQuestionsSimilarByTags(q, questions, tags)
  if( nrow(cnd) > 0 ){
    res <- ComputeSimilarityScores(q, cnd, lda)
    return(head(res, n=10))
  }else{
    return(NULL)
  }
}, .parallel=is.parallel)
save(result, file=paste(package.home,"/data/res.RData",sep=""))
dbWriteTable(mychannel, "forum_questionrelation", 
             result[,c("question_id","related_question_id","similarity")], 
             overwrite=T, row.names=F)

# Closing the connection
dbDisconnect(mychannel)
