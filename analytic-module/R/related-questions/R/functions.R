# weights for combining factors of question recommendation
# the smallest weight for the most important factor
ALPHA1 <- 0.1    # weight for topics similarity
ALPHA2 <- 0.8    # weight for TF-IDF similarity
ALPHA3 <- 0.9    # importance of answer quality

is.parallel <- require(doMC)

ComputeSimilarityScores <- function(question, candidates, lda){
  # returns a dataframe each row of which contains ID of question 
  # and similarity score
  # 
  # Args:
  #  quesition:  single row cotaining given question
  #  candidates: dataframe with other questions
  #  lda:        LDA model object
  
  count <- nrow(candidates)
  all.docs <- rbind(candidates, question)
  dtm <- GetDTM(cbind(all.docs$title,all.docs$body))
                        
  mtr.idf <- as.matrix(weightTfIdf(dtm))
                        
  topics.distr <- posterior(lda,dtm)$topics
  question.td   <- topics.distr[count+1, ]
  question.tfidf <- mtr.idf[count+1,]
  
  similarity <- laply(1:count,function(i){
    topics.sim <- CosSim(topics.distr[i, ], question.td)
    tfidf.sim  <- CosSim(mtr.idf[i,], question.tfidf)
    topics.sim^ALPHA1 * tfidf.sim^ALPHA2 * candidates$score[i]^ALPHA3
  }, .parallel=is.parallel)
  
  result <-  data.frame(
        candidates$id,
        similarity)
  
  result[rev(order(result$similarity)), ]
}

CosSim <- function(a, b){
  # computes cosine similarity value for given vectors
  
  sum(a*b)/sqrt(sum(a*a)*sum(b*b))
}

GetLDAModel <- function(questions, K=c(32,64,128)){
  # returns LDA model for given number of topics
  #
  # Args:
  #  questions: set of questions for training
  #  K:         counts of topics
  
  dtm.tf <- GetDTM(cbind(questions$title,questions$body))

  ldas <- llply(K[K < nrow(dtm.tf)], function(k){
    LDA(dtm.tf, k, method="Gibbs")
  }, .parallel=is.parallel)
  
  perps <- laply(ldas, perplexity, newdata=dtm.tf, .parallel=is.parallel)
  
  #return model with minimum perplexity
  ldas[ order(perps)[1] ][[1]]
}

GetQuestionsSimilarByTags <- function(q, questions, tags){
  # filters questions with same tags as in given
  #
  # Args:
  #  q:         question
  #  questions: dataframe with questions
  #  tags:      dataframe containing node_id and tag_id
  
  q.tags <- tags[tags$node_id == q$id,]$tag_id
  cnd.id <- tags[tags$tag_id %in% q.tags, ]$node_id
  questions[questions$id %in% cnd.id[cnd.id != q$id], ]
}

GetDTM <- function(textColumns, sparseTerms = 0){
  # shortcut for making DocumentTermMatrix from given textColumns 
  # with term-frequency weighting
  #
  # Args:
  #   textColumns: either character vector or a cbind() of columns
  #   sparseTerms: a numeric for the maximal allowed sparsity
  
  control <- list(
      bounds = list(local = c(1, Inf)), 
      tolower = TRUE, 
      removeNumbers = TRUE, 
      removePunctuation = TRUE, 
      stopwords = TRUE, 
      stemming = TRUE,
      stripWhitespace = TRUE, 
      tokenize = scan_tokenizer,
      wordLengths = c(3, Inf), 
      weighting = weightTf)
      

  trainingColumn <- apply(as.matrix(textColumns), 1, paste, collapse = " ")
  trainingColumn <- sapply(as.vector(trainingColumn, mode = "character"), 
      iconv, to = "UTF8", sub = "byte")

  corpus <- Corpus(VectorSource(trainingColumn))
  matrix <- DocumentTermMatrix(corpus, control = control)
  
  if(sparseTerms > 0) 
    matrix <- removeSparseTerms(matrix, sparseTerms)
      
  matrix <- matrix[, sort(colnames(matrix))]
  gc()
  return(matrix)
}
