#!/usr/bin/env Rscript

# Script for finding related questions

library("RMySQL")
library("R.utils")
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

# removing HTML tags
questions$body <- laply(questions$body, function(q){
  gsub("<[^>]+>","",q)
}, .parallel=is.parallel)

# make regex containig trigger words for computing freshness
tw <- paste(
        scan(paste(package.home,"inst/trigger.words",sep="/"), character()),
        collapse="|")

questions$freshness <- daply(questions, c("id"), ComputeFreshness, 
                             time.words.re=tw, .parallel=is.parallel)

stored.lda <- paste(package.home,"/data/lda.RData",sep="")
if(file.exists(stored.lda)){
  load(stored.lda)
}else{
  lda <- GetLDAModel(questions,c(32,64,128,256))
  save(lda, file=stored.lda)
}

# add answer scores
questions <- merge(questions, GetAnswerScores(mychannel), all.x=T)
questions$score[is.na(questions$score)] <- 0

tags <- GetTagQuestionAssociations(mychannel)

result <- ddply(questions, c("id"), function(q){
  cnd <- GetQuestionsSimilarByTags(q, questions, tags)
  if( nrow(cnd) > 0 ){
    res <- ComputeSimilarityScores(q, cnd, lda)
    return(head(res[res$similarity > 0,], n=10))
  }else{
    return(NULL)
  }
}, .parallel=is.parallel)

names(result) <- c("question_id","related_question_id","similarity")

dbWriteTable(mychannel, "forum_questionrelation", 
             result, 
             overwrite=T, row.names=F)

# Closing the connection
dbDisconnect(mychannel)
