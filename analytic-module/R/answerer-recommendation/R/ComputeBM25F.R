ComputeBM25F <- function(dtm,
                         candidate.dtm,
                         question,
                         candidate.question,
                         question.offset,
                         candidate.title.offset,
                         candidate.body.offset,
                         candidate.tag.offset) {
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
  candidate.question.ids <- candidate.title.offset:dtm$nrow
  candidate.question.number <- candidate.dtm$nrow
  question.terms <- 
    tm::findFreqTerms(dtm[question.offset+question.id,],1)
  question.term.ids <- 
    laply(question.terms, function(term) {which(tm::Terms(dtm)[]==term)})
  # Computes IDFs
  question.term.ids.in.candidate.dtm <- 
    laply(question.terms, function(term) {which(tm::Terms(candidate.dtm)[]==term)})
  idfs <- laply(question.term.ids.in.candidate.dtm, function(id) {
    document.frequency <- length(candidate.dtm[,id]$i)
    log( (candidate.dtm$nrow - document.frequency + 0.5) / (document.frequency + 0.5) ) 
  })
}