ComputeBM25F <- function(dtm,
                         candidate.dtm,
                         question,
                         candidate.question,
                         question.offset,
                         candidate.title.offset,
                         candidate.body.offset,
                         candidate.tag.offset,
                         average.title.length,
                         average.body.length,
                         average.tag.length) {
  # Computes a BM25F score between two given questions (in IR sense, 
  # the first question plays the role of a 'query' and 
  # the second one does the same for a 'document') represented as vectors
  # in a given document-term matrix
  #
  # Args:
  #   dtm:                      document term matrix
  #   question:                 question ('query')
  #   candidate.question:       candidate question ('document')
  #   question.offset:          offset for getting vector representation
  #                             of the question title by id
  #
  # Returns:
  #   Frame, containing the question pairs with scores
  require(tm)
  question.id <- as.integer(rownames(question))
  candidate.question.id <- as.integer(rownames(candidate.question))
  # Finds the question's terms
  question.terms <- 
    tm::findFreqTerms(dtm[question.offset+question.id,],1)
  if (length(question.terms) == 0) return (NA)
  question.term.ids <- 
    laply(question.terms, function(term) {which(tm::Terms(dtm)[]==term)})
  # Finds the candidate's fields' lengths
  candidate.title.length <- sum(dtm[candidate.title.offset+candidate.question.id, ]$v)
  candidate.body.length <- sum(dtm[candidate.body.offset+candidate.question.id, ]$v)
  candidate.tag.length <- sum(dtm[candidate.tag.offset+candidate.question.id, ]$v)
  # Setting up the field weights and free parameters
  tag.weight <- 1
  body.weight <- 2
  title.weight <- 3
  b <- 0.75
  k1 <- 2
  # Computes IDFs
  question.term.ids.in.candidate.dtm <- 
    laply(question.terms, function(term) {which(tm::Terms(candidate.dtm)[]==term)})
  
  idfs <- laply(question.term.ids.in.candidate.dtm, function(id) {
    document.frequency <- length(candidate.dtm[,id]$i)
    log( (candidate.dtm$nrow - document.frequency + 0.5) / (document.frequency + 0.5) ) 
  })
  term.frequency.weights <- 
    foreach(term=iter(question.term.ids), .combine=c) %do% {
      title.term.freq <- dtm[candidate.title.offset + candidate.question.id, term]$v
      body.term.freq <- dtm[candidate.body.offset + candidate.question.id, term]$v
      tag.term.freq <- dtm[candidate.tag.offset + candidate.question.id, term]$v
      title.score <- 
        title.weight*title.term.freq/(1 - b + b*candidate.title.length/average.title.length)
      if (equals(title.score, numeric(0))) {
        title.score <- 0
      }
      body.score <- 
        body.weight*body.term.freq/(1 - b + b*candidate.body.length/average.body.length)
      if (equals(body.score, numeric(0))) {
        body.score <- 0
      }
      tag.score <- 
        tag.weight*tag.term.freq/(1 - b + b*candidate.tag.length/average.tag.length)
      if (equals(tag.score, numeric(0))) {
        tag.score <- 0
      }
      term.frequency.weight <- 
         title.score + body.score + tag.score
      term.frequency.weight
  }
  # Workaround for dealing with vectors of zeros
  if (length(term.frequency.weights) < length(question.term.ids)) {
    term.frequency.weights <- rep(0, length(question.term.ids))
  }
  bm25.score <- 
    (idfs) %*% (term.frequency.weights/(k1 + term.frequency.weights))

  return (bm25.score[[1]])
}