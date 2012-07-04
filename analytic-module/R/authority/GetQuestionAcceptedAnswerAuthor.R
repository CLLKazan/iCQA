GetQuestionAcceptedAnswerAuthor <- function(db.channel, db.name, question.id) {
  # Retrieves accepted answer's author id for the given question
  #
  # Args:
  #   db.channel: db connection object
  #   db.name:    name of the database
  #   question.id:     question id
  #
  # Returns:
  #   Accepted answer's author id if accepted answer exists, 
  #   NULL otherwise
  results <- 
    dbSendQuery(db.channel,
                paste("SELECT author_id FROM ", 
                      db.name, ".forum_node", " WHERE node_type='answer' 
                      AND state_string='(accepted)' AND parent_id=", 
                      question.id, sep=""))
  data <- fetch(results, n=-1)
  data$author_id
}