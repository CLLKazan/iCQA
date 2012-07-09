TrainUQA <- function(db.channel, db.name, user.profiles) {
  # Trains a UQA model proposed in the paper J. Guo et al. "Tapping on the Potential
  # of Q&A community by recommending answer providers (2008)
  #
  # Args:
  #   db.channel:     database connection object
  #   db.name:        database name
  #   user.profiles:  user profiles 
  #
  # Returns:
  #   Trained UQA model
  require(RMySQL)
  require(tm)
  require(plyr)
  require(foreach)
  topic.number <- 5*length(unique(user.profiles$tag_id))
  # Building the document-term matrix
  corpus <- tm::Corpus(VectorSource(user.profiles$post))
  dtm <- 
    tm::DocumentTermMatrix(corpus, control=list(removePunctuation=T, stopwords=T))
  users <- unique(user.profiles$user_id)
  topic.word.assignments <- ldply(users, 
                                  function(u) 
                                {BuildTopicWordAssignments(u,
                                                           dtm,
                                                           user.profiles,
                                                           topic.number)},
                                  .progress="text")
  
  return (topic.word.assignments)
}

BuildTopicWordAssignments <- function(user, dtm, user.profiles, topic.number) {
  user.post.indexes <- 
    as.integer(rownames(user.profiles[which(user.profiles$user_id==user),]))
  
  topic.word.assignments <- 
    ldply(user.post.indexes,
          function(id) {BuildTuples(id, dtm, user.profiles, user,topic.number)})
  return (topic.word.assignments)
}

BuildTuples <- function(id, dtm, user.profiles, user,topic.number) {
    category.id <- user.profiles$tag_id[id]  
    terms <- tm::findFreqTerms(dtm[id,],1)
    result <- NULL
    if (length(terms) > 0) {
    topic.word.assignments <-
      ldply(terms, function(term) {c(user,
                                     term,
                                     category.id,
                                     sample(1:topic.number,1,T))})   
    df <- as.data.frame(topic.word.assignments)
    
    names(df) <- c("user_id", "word", "category_id", "topic_id")  
    result <- df
    }
    return (result)
}