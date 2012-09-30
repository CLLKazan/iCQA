#!/usr/bin/env Rscript

# Script for finding related questions
# NOTE: Retraining of the LDA model is preformed automatically. 
# Retraining occurs when the number of questions has been increased 
# twice since the previuos training.
# If you want retrain model then you should manually 
# remove 'data/lda.RData' file

library("RMySQL")
library("R.utils")
library("topicmodels")
library("plyr")

is.parallel <- require(doMC)
if(is.parallel){
  registerDoMC()
}

package.home <- paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/related-questions",
                      sep="")
stored.lda <- paste(package.home,"/data/lda.RData",sep="")
info.file <- paste(package.home,"/data/info.RData",sep="")

# Loading auxiliary functions
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/common",
                      sep=""), pattern="*.R")
sourceDirectory(paste(package.home,"/R",sep=""), pattern="*.R")

# Creating connection to database
db.configuration <- ReadDBConfiguration()
mychannel <- 
  dbConnect(MySQL(), user=db.configuration$user, dbname=db.configuration$name,
            host="localhost", password=db.configuration$password)

# retrieving all questions from db
questions <- GetQuestions(mychannel)

# removing HTML tags
questions$body <- laply(questions$body, function(q){
  gsub("<[^>]+>","",q)
}, .parallel=is.parallel)

# loading a saved configuration, which contains information 
# about the size of the database on which model has been trained,
# and the ID numbers of questions
# for which the calculation was performed in the previous runs
if(file.exists(info.file)){
  load(info.file)
  processed <- prev.info[[1]]
  db.size   <- prev.info[[2]]
  retrain <- db.size * 2 < nrow(questions)
}else{
  # ID numbers of already processed quesitons
  processed <- c()
  retrain <- T
}

# training or loading LDA model
if(!retrain & file.exists(stored.lda)){
  load(stored.lda)
}else{
  lda <- GetLDAModel(questions,c(32,64,128,256))
  save(lda, file=stored.lda)
  db.size <- nrow(questions)
  processed <- c()
}

# making the regular expression containing trigger words
tw <- paste(
        scan(paste(package.home,"inst/trigger.words",sep="/"), character()),
        collapse="|")

# computing freshness scores
questions$freshness <- daply(questions, c("id"), ComputeFreshness, 
                             time.words.re=tw, .parallel=is.parallel)

# add answer scores
questions <- merge(questions, GetAnswerScores(mychannel), all.x=T)
questions$score[is.na(questions$score)] <- 0

tags <- GetTagQuestionAssociations(mychannel)

# perform the computation for questions that have been added since the previous run
result <- ddply(questions[! questions$id %in% processed,], c("id"), function(q){
  cnd <- GetQuestionsSimilarByTags(q, questions, tags)
  if( nrow(cnd) > 0 ){
    res <- ComputeSimilarityScores(q, cnd, lda)
    return(head(res[res$similarity > 0,], n=10))
  }else{
    return(NULL)
  }
}, .progress="text",.parallel=F)

names(result) <- c("question_id","related_question_id","similarity")

if(nrow(result) > 0){

  if(!retrain){
    # the relation of similarity is transitive
    upd <- result[result$related_question_id %in% processed,]
    names(upd) <- names(result)[c(2,1,3)]
    result <- rbind(result, upd)
  }

  dbWriteTable(mychannel, "forum_questionrelation", 
             result, append=!retrain,
             overwrite=retrain, row.names=F)
}

# saving the info
prev.info <- list(questions$id, db.size)
save(prev.info, file=info.file)
# Closing the connection
dbDisconnect(mychannel)
