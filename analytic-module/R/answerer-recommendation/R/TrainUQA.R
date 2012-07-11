TrainUQA <- function(db.channel, db.name, user.profiles) {
  # Trains a UQA model proposed in the paper J. Guo et al. "Tapping on the Potential
  # of Q&A community by recommending answer providers" (2008)
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
  users <- unique(user.profiles$user_id)[10]
  topic.word.assignments <- ldply(users, 
                                  function(u) 
                                {BuildTopicWordAssignments(u,
                                                           dtm,
                                                           user.profiles,
                                                           topic.number)},
                                  .progress="text")
  topics <- unique(topic.word.assignments$topic_id)
  # Computes overall frequencies
  word.topic.frequencies <- ddply(topic.word.assignments,
                                .(topic.word.assignments$word_id,
                                  topic.word.assignments$topic_id),
                                  nrow)
  names(word.topic.frequencies) <- c("word_id", "topic_id", "Freq")
  category.topic.frequencies <- ddply(topic.word.assignments,
                                      .(topic.word.assignments$category_id,
                                        topic.word.assignments$topic_id),
                                      nrow)
  names(category.topic.frequencies) <- c("category_id", "topic_id", "Freq")
  user.topic.frequencies <- ddply(topic.word.assignments,
                                  .(topic.word.assignments$user_id,
                                    topic.word.assignments$topic_id),
                                  nrow)
  names(user.topic.frequencies) <- c("user_id", "topic_id", "Freq")
  category.number <- length(unique(category.topic.frequencies$category_id))
  # Processes assignments
  by(topic.word.assignments,  1:nrow(topic.word.assignments),
        function(row) {ProcessAssignment(row,
                                      word.topic.frequencies,
                                      category.topic.frequencies,
                                      user.topic.frequencies,
                                      topic.word.assignments,
                                      topics,
                                      category.number)}, simplify=T)  

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
                                     which(Terms(dtm)[]==term),
                                     category.id,
                                     sample(1:topic.number,1,T))})   
    df <- as.data.frame(topic.word.assignments)
    
    names(df) <- c("user_id", "word_id", "category_id", "topic_id")  
    result <- df
    }
    return (result)
}
ProcessAssignment <- function(assignment,
                              word.topic.frequencies,
                              category.topic.frequencies,
                              user.topic.frequencies,
                              topic.word.assignments,
                              topics,
                              category.number) {
  # Decreases the related frequencies
  word.topic.freq <- with(word.topic.frequencies,
                  word.topic.frequencies[which(word_id==assignment$word_id & 
         topic_id==assignment$topic_id),])
  if (nrow(word.topic.freq) > 0 & word.topic.freq$Freq > 0) {
        word.topic.freq$Freq <- word.topic.freq$Freq - 1
  }
  category.topic.freq <- with(category.topic.frequencies,
                              category.topic.frequencies[
                              which(category_id==assignment$category_id & 
                              topic_id==assignment$topic_id),])
  if (nrow(category.topic.freq) & category.topic.freq$Freq > 0) {
    category.topic.freq$Freq <- category.topic.freq$Freq - 1
  }
  user.topic.freq <- with(user.topic.frequencies,
                          user.topic.frequencies[
                            which(user_id==assignment$user_id & 
                              topic_id==assignment$topic_id),])
  if (nrow(user.topic.freq) & user.topic.freq$Freq > 0) {
    user.topic.freq$Freq <- user.topic.freq$Freq - 1
  }
  # Computes topic probabilities
  topic.number <- length(topics)
  topic.probabilities <- llply(topics,
                               function(topic) {
                                 ComputeTopicProbability(topic.word.assignments,
                                                         word.topic.frequencies,
                                                         category.topic.frequencies,
                                                         assignment,
                                                         topic,
                                                         category.number,
                                                         topic.number)})
#   print(topic.number)
  topic.probabilities <- unlist(topic.probabilities)
#   print(topic.probabilities)
  sampled.topic.id <- sample(topics, 1, prob=topic.probabilities)
#   print(sample.topic.id)
#   topic.probabilities <- unlist(topic.probabilities)
#   print(topic.probabilities)
#   sampled.topic <- sample(topics, 1, prob=topic.probabilities)
#   print(sampled.topic)
#   stop("error")
}

ComputeTopicProbability <- function(topic.word.assignments,
                                      word.topic.frequencies,
                                      category.topic.frequencies,
                                      assignment,
                                      topic.id,
                                      category.number,
                                      topic.number) {
  
  t <- with(topic.word.assignments, topic.word.assignments[
    which(user_id==assignment$user_id & topic_id==topic.id),])
  l.uz.ui <- nrow(t)
  
  word.freqs <- 
    with(word.topic.frequencies, 
         word.topic.frequencies[which(topic_id==topic.id),]$Freq)
  n.z.ui.w.ui <- 
    with(word.topic.frequencies, 
         word.topic.frequencies[which(word_id==assignment$word_id &
           topic_id==topic.id),]$Freq)
  if (length(n.z.ui.w.ui)==0) {
    n.z.ui.w.ui <- 0
  }
  beta.params <- rep(.05, length(word.freqs))
  n.z.ui.v <- word.freqs + beta.params
  
  m.z.ui.c.ui <- with(category.topic.frequencies,
                      category.topic.frequencies[which(category_id==assignment$category_id & 
                        topic_id==topic.id),]$Freq)
  if (length(m.z.ui.c.ui)==0) {
    m.z.ui.c.ui <- 0
  }
  category.freqs <- 
    with(category.topic.frequencies, 
         category.topic.frequencies[which(topic_id==topic.id),]$Freq)
  gamma.params <- rep(50/category.number, length(category.freqs))
  m.z.ui.c <- category.freqs + gamma.params
  topic.probability <- 
    (l.uz.ui + 50/topic.number - 1)*(n.z.ui.w.ui + .05 - 1)*
    (m.z.ui.c.ui + 50/category.number - 1)/((sum(n.z.ui.v) - 1)*(sum(m.z.ui.c) - 1))
  return (topic.probability)
}