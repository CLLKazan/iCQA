UpdateMatrixForQuestion <- function(question.id, db.channel) {
  answer.author <- GetQuestionAcceptedAnswerAuthor(db.channel,
                                                   question.id)
  question.author <- GetQuestionAuthor(db.channel, 
                                       question.id)
  # If accepted answer exists
  if (!is.null(answer.author)) {
    result <- c(question.author, answer.author)
  } else {
    result <- c(NA, NA)
  }
  result
}

ComputeUsersAuthoritiesForTag <- function(tag.id, db.channel, update=T) {
  # Retrieving questions with the given tag
  questions <- GetQuestionsFromDB(db.channel, tag.id)
  
  list <- lapply(questions, UpdateMatrixForQuestion, db.channel=db.channel)
  data <- unlist(list)
  
  if(!is.null(data)) {
    # Matrix of edges
    user.matrix <- na.omit(matrix(data, ncol=2, byrow=TRUE))
    
    # Creating graph and computing authority scores
    user.graph <- graph.edgelist(user.matrix)
    score <- authority.score(user.graph)$vector
    
    users <- seq(length=length(score))
    score.frame <- data.frame(score, users)
    ordered.score.frame <- score.frame[order(-score.frame$score),]
    
    UpdateAuthorityForUser <- function(user.id, tag.id) {
      if (!is.na(score[user.id]) & score[user.id] > 0.000001) {
        # Update the table
        UpdateAuthorityTable(db.channel, user.id, 
                             tag.id, score[user.id], update)
      }
    }
    # Write score only of 12 top users
    lapply(ordered.score.frame[1:12,]$users, UpdateAuthorityForUser,
           tag.id=tag.id)
  }
}
