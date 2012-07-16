GetQuestionTopicDistribution <- function(dtm,
                                         question.title.offset,
                                         question.body.offset,
                                         uqa.model,
                                         question) {
  # Retrieves topic distribution for the given question 
  # represented via given document-term matrix
  # using the trained UQA model
  #
  # Args:
  #   dtm:                    document-term matrix
  #   question.title.offset:  offset for getting vector representation
  #                           of the question title by id
  #   question.body.offset:   offset for getting vector representation
  #                           of the question body by id
  #   uqa.model:              trained UQA model
  #   question:               question data
  #
  # Returns:
  #   vector of probabilities
  require(tm)
  thetas <- uqa.model$theta
  phis <- uqa.model$phi
  psis <- uqa.model$psi
  topics <- unique(thetas$topic_id)
  id <- as.integer(rownames(question))
  
  title.terms <- tm::findFreqTerms(dtm[question.title.offset+id,],1)
  title.word.ids <- llply(title.terms, function(term) {which(tm::Terms(dtm)[]==term)})
  body.terms <- tm::findFreqTerms(dtm[question.body.offset+id,],1)
  body.word.ids <- llply(body.terms, function(term) {which(tm::Terms(dtm)[]==term)})
  
  question.topic.probabilities <- 
    laply(topics,
        function(topic) {
            category.probability <- 
              with(psis, psis[which(category_id==question$tag_id &
              topic_id==topic),]$psi)
            title.word.probabilities <-
               unlist(llply(title.word.ids, function(word) {
                 p <- with(phis, phis[which(word_id==word &
                   topic_id==topic),]$phi)
                 p
               }))
            body.word.probabilities <-
              unlist(llply(body.word.ids, function(word) {
                p <- with(phis, phis[which(word_id==word &
                  topic_id==topic),]$phi)
                p
              }))
            prob <-
              (category.probability + 
                  sum(title.word.probabilities + 
                    sum(body.word.probabilities)))/
                (1 + length(title.terms) + length(body.terms))
            print(prob)
            prob
        })
  return (list(topics=topics, prob=question.topic.probabilities))
}