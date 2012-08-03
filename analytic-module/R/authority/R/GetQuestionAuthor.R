GetQuestionAuthor <- function(db.channel, question.id) {
  # Retrieves author id for the given question
  #
  # Args:
  #   db.channel: db connection object
  #   question.id:     question id
  #
  # Returns:
  #   Author id
  results <- 
    dbSendQuery(db.channel,
                paste("SELECT author_id FROM forum_node ",
                      "WHERE id=", question.id, sep=""))
  data <- fetch(results, n=-1)
  data$author_id
}
