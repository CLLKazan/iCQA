ALPHA1 <- 0.7
ALPHA2 <- 0.2
ALPHA3 <- 0.1
SPARCE <- 0.995
is.parallel <- require(doMC)

ComputeSimilarityScores <- function(question, candidates, lda){
  # returns dataframe each row of which contains ID of questions 
  # and thier similarity score
  # 
  # Args:
  #  quesition:  single row cotaining given question
  #  candidates: dataframe with other questions
  #  lda:        LDA_VEM object
  
  count <- nrow(candidates)
  all.docs <- rbind(candidates, question)
  dtm <- GetDTM(cbind(all.docs$title,all.docs$body), sparseTerms=SPARCE)
                        
  mtr.idf <- as.matrix(weightTfIdf(dtm))
                        
  topics.distr <- posterior(lda,dtm)$topics
  question.td   <- topics.distr[count+1, ]
  question.tfidf <- mtr.idf[count+1,]
  
  similarity <- laply(1:count,function(i){
    topics.sim <- CosSim(topics.distr[i, ], question.td)
    tfidf.sim  <- CosSim(mtr.idf[i,], question.tfidf)
    topics.sim*ALPHA1 * tfidf.sim*ALPHA2 * candidates$score[i]*ALPHA3
  }, .parallel=is.parallel)
  
  result <-  data.frame(
        rep(question$id, count),
        candidates$id,
        similarity)
  names(result) <- c("question_id","related_question_id","similarity")
  
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
  
  dtm.tf <- GetDTM(cbind(questions$title,questions$body), sparseTerms=SPARCE)

  ldas <- llply(K[K < nrow(dtm.tf)], function(k){
    LDA(dtm.tf, k, method="Gibbs")
  }, .parallel=is.parallel)
  
  perps <- llply(ldas, function(l){
    perplexity(l, dtm.tf)
  }, .parallel=is.parallel)
  
  #return model with minimum perplexity
  ldas[ order(unlist(perps))[1] ][[1]]
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
  #   textColumns:       Either character vector or a cbind() of columns
  #   removeSparseTerms: a numeric for the maximal allowed sparsity
  
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
