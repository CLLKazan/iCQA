GetQuestionAuthor <- function(db.channel, db.name, question.id) {
  # Retrieves author id for the given question
  #
  # Args:
  #   db.channel: db connection object
  #   db.name:    name of the database
  #   question.id:     question id
  #
  # Returns:
  #   Author id
  results <- 
    dbSendQuery(db.channel,
                paste("SELECT author_id FROM ", 
                      db.name, ".forum_node", " WHERE id=", 
                      question.id, sep=""))
  data <- fetch(results, n=-1)
  data$author_id
}