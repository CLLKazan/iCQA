TrainUQA <- function(dtm, user.profiles, max.iteration=50) {
  # Trains a UQA model proposed in the paper J. Guo et al. "Tapping on the Potential
  # of Q&A community by recommending answer providers" (2008)
  #
  # Args:
  #   dtm:     document-term matrix
  #   user.profiles:  user profiles 
  #   max.iteration:  maximum number of iterations
  #
  # Returns:
  #   Trained UQA model
  require(RMySQL)
  require(tm)
  require(plyr)
  require(foreach)
  require(iterators)  
  
  users <- unique(user.profiles$user_id)
  # TODO(nzhiltsov): calculate the topic number optimally
  topic.number <- 20

  topic.word.assignments <- ldply(users, 
                                  function(u) 
                                {BuildTopicWordAssignments(u,
                                                           dtm,
                                                           user.profiles,
                                                           topic.number)},
                                  .progress="text")
  
  
  prev.perplexity <- Inf
  iteration.number <- 0
  topics <- unique(topic.word.assignments$topic_id)
  words <- unique(topic.word.assignments$word_id)
  categories <- unique(topic.word.assignments$category_id)
  
  category.number <- length(unique(topic.word.assignments$category_id))
  
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
  # Estimates the parameters
  theta.parameters <- ComputeThetaParameters(topic.word.assignments,
                                             users, 
                                             topics)
  
  phi.parameters <- ComputePhiParameters(word.topic.frequencies,
                                         words,
                                         topics)
  psi.parameters <- ComputePsiParameters(category.topic.frequencies,
                                         categories,
                                         topics)
  # Computes perplexity
  perplexity <- ComputePerplexity(topic.word.assignments, topics,
                                  theta.parameters, phi.parameters, psi.parameters)
  print(paste("The initial perplexity =", perplexity))
  for (i in 1:max.iteration)  {
  # Processes assignments
    foreach (assignment=iter(topic.word.assignments, by='row')) %do% {
          # Processes the row
            new.row <- ProcessAssignment(assignment,
                                      word.topic.frequencies,
                                      category.topic.frequencies,
                                      user.topic.frequencies,
                                      topic.word.assignments,
                                      topics,
                                      category.number)
      # Decreases the related frequencies
          t <-  word.topic.frequencies[which(word.topic.frequencies$word_id==assignment$word_id &
              word.topic.frequencies$topic_id==assignment$topic_id),]$Freq    
          if (t > 0)   {
      word.topic.frequencies[which(word.topic.frequencies$word_id==assignment$word_id &
        word.topic.frequencies$topic_id==assignment$topic_id),]$Freq <- t - 1
          }
      t <- category.topic.frequencies[which(category.topic.frequencies$category_id==assignment$category_id &
        category.topic.frequencies$topic_id==assignment$topic_id),]$Freq
            if (t > 0) {
      category.topic.frequencies[which(category.topic.frequencies$category_id==assignment$category_id &
        category.topic.frequencies$topic_id==assignment$topic_id),]$Freq <- t - 1
            }
      t <- user.topic.frequencies[which(user.topic.frequencies$user_id==assignment$user_id &
        user.topic.frequencies$topic_id==assignment$topic_id),]$Freq
            if (t > 0) {
      user.topic.frequencies[which(user.topic.frequencies$user_id==assignment$user_id &
        user.topic.frequencies$topic_id==assignment$topic_id),]$Freq <- t - 1
            }
            
            # Replaces the topic
            topic.word.assignments[as.integer(rownames(assignment)),]$topic_id <-
              new.row$topic_id
            
          # Increases the related frequencies
          if (nrow(word.topic.frequencies[which(word.topic.frequencies$word_id==new.row$word_id &
            word.topic.frequencies$topic_id==new.row$topic_id),]) > 0)  {
          word.topic.frequencies[which(word.topic.frequencies$word_id==new.row$word_id &
            word.topic.frequencies$topic_id==new.row$topic_id),]$Freq <-
            word.topic.frequencies[which(word.topic.frequencies$word_id==new.row$word_id &
            word.topic.frequencies$topic_id==new.row$topic_id),]$Freq + 1
          } else {
            word.topic.frequencies <- rbind(word.topic.frequencies,
                                            c(new.row$word_id, new.row$topic_id, 1))
          }
          if (nrow(category.topic.frequencies[which(category.topic.frequencies$category_id==new.row$category_id &
            category.topic.frequencies$topic_id==new.row$topic_id),]) > 0) {
          category.topic.frequencies[which(category.topic.frequencies$category_id==new.row$category_id &
            category.topic.frequencies$topic_id==new.row$topic_id),]$Freq <-
            category.topic.frequencies[which(category.topic.frequencies$category_id==new.row$category_id &
            category.topic.frequencies$topic_id==new.row$topic_id),]$Freq + 1
          } else {
            category.topic.frequencies <- rbind(category.topic.frequencies,
                                                c(new.row$category_id, new.row$topic_id, 1))
          }
          if (nrow(user.topic.frequencies[which(user.topic.frequencies$user_id==new.row$user_id &
            user.topic.frequencies$topic_id==new.row$topic_id),]) > 0)       {
         user.topic.frequencies[which(user.topic.frequencies$user_id==new.row$user_id &
            user.topic.frequencies$topic_id==new.row$topic_id),]$Freq <-
            user.topic.frequencies[which(user.topic.frequencies$user_id==new.row$user_id &
            user.topic.frequencies$topic_id==new.row$topic_id),]$Freq + 1
          } else {
            user.topic.frequencies <- rbind(user.topic.frequencies,
                                            c(new.row$user_id, new.row$topic_id, 1))
          }
        }
  # Estimates the parameters
  theta.parameters <- ComputeThetaParameters(topic.word.assignments,
                         users, 
                         topics)

  phi.parameters <- ComputePhiParameters(word.topic.frequencies,
                                         words,
                                         topics)
  psi.parameters <- ComputePsiParameters(category.topic.frequencies,
                                         categories,
                                         topics)
  # Computes perplexity
  perplexity <- ComputePerplexity(topic.word.assignments, topics,
                    theta.parameters, phi.parameters, psi.parameters)
  iteration.number <- iteration.number + 1
    print(paste("Training UQA model:", iteration.number,
                "iteration(s) completed; the perplexity value =", perplexity))
  if (prev.perplexity - perplexity < 1)  {
    break
  }
  prev.perplexity <- perplexity
  }
  
  print(paste("Accomplished training the UQA model within", i, "iteration(s)."))
  return (list(theta=theta.parameters, phi=phi.parameters, psi=psi.parameters))
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
    names(topic.word.assignments) <-
      c("user_id", "word_id", "category_id", "topic_id")  
    result <- topic.word.assignments
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
                                                         topic.number)}, .parallel=T)
  topic.probabilities <- unlist(topic.probabilities)
  sampled.topic.id <- sample(topics, 1, prob=topic.probabilities)
  # Update the assignment's topic value
  assignment$topic_id <- sampled.topic.id

  return (assignment)
}

ComputeTopicProbability <- function(topic.word.assignments,
                                      word.topic.frequencies,
                                      category.topic.frequencies,
                                      assignment,
                                      topic.id,
                                      category.number,
                                      topic.number) {
  
    l.uz.ui <- ComputeNumberOfWordsAssignedToTopic(topic.word.assignments,
                                                   assignment$user_id,
                                                   topic.id)
  
  word.freqs <- 
    with(word.topic.frequencies, 
         word.topic.frequencies[which(topic_id==topic.id),]$Freq)
  n.z.ui.w.ui <- ComputeTotalNumberOfWordsAssignedToTopic(word.topic.frequencies,
                                                          assignment$word_id,
                                                          topic.id)
    
  beta.params <- rep(.05, length(word.freqs))
  n.z.ui.v <- word.freqs + beta.params
  
  m.z.ui.c.ui <- ComputeNumberOfCategoriesAssignedToTopic(category.topic.frequencies,
                                                          assignment$category_id,
                                                          topic.id)
  category.freqs <- 
    with(category.topic.frequencies, 
         category.topic.frequencies[which(topic_id==topic.id),]$Freq)
  gamma.params <- rep(50/category.number, length(category.freqs))
  m.z.ui.c <- category.freqs + gamma.params

    topic.probability <- 
    (l.uz.ui + 50/topic.number)*(n.z.ui.w.ui + .05)*
    (m.z.ui.c.ui + 50/category.number)/(sum(n.z.ui.v)*sum(m.z.ui.c))
 
  return (topic.probability)
}
ComputeNumberOfWordsAssignedToTopic <- function(topic.word.assignments,
                                                user.id,
                                                topic.id) {
  t <- with(topic.word.assignments, topic.word.assignments[
    which(user_id==user.id & topic_id==topic.id),])
  l.uz.ui <- nrow(t)
  return (l.uz.ui)
}
ComputeTotalNumberOfWordsAssignedToTopic <- function(word.topic.frequencies,
                                                     word.id,
                                                     topic.id) {
  n.z.ui.w.ui <- 
    with(word.topic.frequencies, 
         word.topic.frequencies[which(word_id==word.id &
           topic_id==topic.id),]$Freq)
  if (length(n.z.ui.w.ui)==0) {
    n.z.ui.w.ui <- 0
  }
  return (n.z.ui.w.ui)
}

ComputeNumberOfCategoriesAssignedToTopic <- function(category.topic.frequencies,
                                                     category.id,
                                                     topic.id) {
  m.z.ui.c.ui <- with(category.topic.frequencies,
                      category.topic.frequencies[which(category_id==category.id & 
                        topic_id==topic.id),]$Freq)
  if (length(m.z.ui.c.ui)==0) {
    m.z.ui.c.ui <- 0
  }
  return (m.z.ui.c.ui)
}

ComputeThetaParameters <- function(topic.word.assignments,
                                  users, 
                                  topics) {
  
  topic.number <- length(topics)
  alpha.params <- rep(50/topic.number, topic.number) 
  theta.parameters <- ldply(users,
            function(user.id) {
    l.uz.z <- unlist(llply(topics,
          function(topic) {
            ComputeNumberOfWordsAssignedToTopic(topic.word.assignments,
                                                              user.id,
                                                              topic)}))
    theta.per.user <- ldply(topics, function(topic) {
    l.uz.ui <- ComputeNumberOfWordsAssignedToTopic(topic.word.assignments,
                                                    user.id,
                                                    topic)
    theta <- (l.uz.ui + 50/topic.number)/(sum(l.uz.z + alpha.params))
    c(user.id, topic, theta)
    })
    theta.per.user <- as.data.frame(theta.per.user)
    names(theta.per.user) <- c("user_id", "topic_id", "theta")
    theta.per.user
  }, .parallel=T)
    return (theta.parameters)
}

ComputePhiParameters <- function(word.topic.frequencies,
                                 words,
                                topics) {
  beta.params <- rep(.05, length(words)) 
  phi.parameters <- 
    ldply(topics,
          function(topic) {
              n.z.ui.w.v <- 
                unlist(llply(words,
                             function(word) {
                ComputeTotalNumberOfWordsAssignedToTopic(word.topic.frequencies,
                                                          word,
                                                          topic)
                            }))
              phi.per.user <- ldply(words, function(word) {
                n.z.ui.w.ui <- 
                  ComputeTotalNumberOfWordsAssignedToTopic(word.topic.frequencies,
                                                               word,
                                                               topic)
                phi <- (n.z.ui.w.ui + .05)/(sum(n.z.ui.w.v+beta.params))
                c(topic, word, phi)
              })
              phi <- as.data.frame(phi.per.user)
              names(phi.per.user) <- c("topic_id", "word_id", "phi")
              phi.per.user
          }, .parallel=T)
  return (phi.parameters)
}

ComputePsiParameters <- function(category.topic.frequencies,
                                 categories,
                                 topics) {
  category.number <- length(categories)
  gamma.params <- rep(50/category.number, category.number) 
  psi.parameters <- 
    ldply(topics,
          function(topic) {
            m.z.ui.c <- 
              unlist(llply(categories,
                           function(category) {
                ComputeNumberOfCategoriesAssignedToTopic(category.topic.frequencies,
                                                         category,
                                                         topic)
                           }))
            psi.per.user <- ldply(categories, function(category) {
              m.z.ui.c.ui <- 
                ComputeNumberOfCategoriesAssignedToTopic(category.topic.frequencies,
                                                         category,
                                                         topic)
              psi <- (m.z.ui.c.ui + 50/category.number)/
                (sum(m.z.ui.c+gamma.params))
              c(topic, category, psi)
            })
            psi <- as.data.frame(psi.per.user)
            names(psi.per.user) <- c("topic_id", "category_id", "psi")
            psi.per.user
          }, .parallel=T)
  return (psi.parameters)
}

ComputePerplexity <- function(topic.word.assignments, topics,
                  theta.parameters, phi.parameters, psi.parameters) {
  require(foreach)
  require(iterators)
  test.set.size <- nrow(topic.word.assignments)
  probabilities <- foreach(assignment=iter(topic.word.assignments, by='row'),
                           .combine=c) %dopar% {
                        word.category.probabilities <-
                          unlist(llply(topics, function(topic) {
                          word.topic.probability <- with(phi.parameters,
                               phi.parameters[which(word_id==assignment$word_id & 
                                 topic_id==topic),]$phi)
                          category.topic.probability <- with(psi.parameters,
                               psi.parameters[which(category_id==assignment$category_id & 
                                 topic_id==topic),]$psi)
                          user.topic.probability <- with(theta.parameters,
                          theta.parameters[which(user_id==assignment$user_id & 
                            topic_id==topic),]$theta)
                          word.topic.probability*category.topic.probability*
                            user.topic.probability
                        }))
                        sum(word.category.probabilities)
                  }
  perplexity <- exp(-sum(log(probabilities))/test.set.size)
  return (perplexity)
}