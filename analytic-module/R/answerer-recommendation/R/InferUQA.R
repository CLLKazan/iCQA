GetQuestionTopicDistribution <- function(dtm,
                                         question.title.offset,
                                         question.body.offset,
                                         uqa.model,
                                         question,
                                         topics) {
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
  #   topics:                 topics
  #
  # Returns:
  #   a list that contains question id and a vector of probabilities
  # arranged according to the given topic list
  require(tm)
  thetas <- uqa.model$theta
  phis <- uqa.model$phi
  psis <- uqa.model$psi
  id <- as.integer(rownames(question))
  
  title.terms <- tm::findFreqTerms(dtm[question.title.offset+id,],1)
  title.word.ids <- llply(title.terms, function(term) {which(tm::Terms(dtm)[]==term)})
  body.terms <- tm::findFreqTerms(dtm[question.body.offset+id,],1)
  body.word.ids <- llply(body.terms, function(term) {which(tm::Terms(dtm)[]==term)})
  
  question.topic.probabilities <- 
    llply(topics,
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
            prob
        })
  question.topic.probabilities <- unlist(question.topic.probabilities)
  # Workaround for dealing with vectors of zeros
  if (length(question.topic.probabilities) < length(topics)) {
    question.topic.probabilities <- rep(0, length(topics))
  }
  return (list(id=question$id, prob=question.topic.probabilities))
}

GetUserProfileTopicDistribution <- function(dtm,
                                            uqa.model,
                                            user.id,
                                            topics) {
  # Retrieves topic distribution for the given user profile 
  # represented via given document-term matrix
  # using the trained UQA model
  #
  # Args:
  #   dtm:                    document-term matrix
  #   uqa.model:              trained UQA model
  #   user.id:                user id
  #   topics:                 topics
  #
  # Returns:
  #   a list that contains user id and a vector of probabilities
  # arranged according to the given topic list
  require(tm)
  require(foreach)
  thetas <- uqa.model$theta
  phis <- uqa.model$phi
  psis <- uqa.model$psi
  user.post.indexes <- 
    as.integer(rownames(user.profiles[which(user.profiles$user_id==user.id),]))
  terms <- foreach(post.id=iter(user.post.indexes), .combine=union) %do% {
    tm::findFreqTerms(dtm[post.id,],1)
  }
  terms <- unique(terms)
  word.ids <- llply(terms, function(term) {which(tm::Terms(dtm)[]==term)})
  
  user.profile.topic.probabilities <- 
    llply(topics,
          function(topic) {
            word.probabilities <-
              unlist(llply(word.ids, function(word) {
                p <- with(phis, phis[which(word_id==word &
                  topic_id==topic),]$phi)
                p
              }))
            prob <-
              sum(word.probabilities)/
              (1 + length(terms))
            prob
          })
  user.profile.topic.probabilities <- unlist(user.profile.topic.probabilities)
  # Workaround for dealing with vectors of zeros
  if (length(user.profile.topic.probabilities) < length(topics)) {
    user.profile.topic.probabilities <- rep(0, length(topics))
  }
  return (list(id=user.id, prob=user.profile.topic.probabilities))
}