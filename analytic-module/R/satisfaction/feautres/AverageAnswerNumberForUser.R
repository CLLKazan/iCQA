AverageAnswerNumberForUser <- function(db.channel, db.name, user.id) {
  # Retrieves average number of answers to user's questions
  #
  # Args:
  #   db.channel: db connection object
  #   db.name:    name of the database
  #   user.id:    user id
  #
  # Returns:
  #   Average number of answers to user's questions if user exists, 
  #   NA otherwise
  results <- 
    dbSendQuery(db.channel,
                paste("SELECT id FROM ", 
                      db.name, ".forum_node", " WHERE author_id=", 
                      user.id, " AND node_type='question'", sep=""))
  questions <- fetch(results, n=-1)
  
  NumberOfAnswers <- function(question.id) {
    result <- 
      dbSendQuery(db.channel,
                  paste("SELECT COUNT(*) AS count FROM ", 
                        db.name, ".forum_node", " WHERE node_type='answer'",
                        " AND parent_id=", question.id, sep=""))
    answers <- fetch(result, n=-1)
    answers$count
  }
  mean(sapply(questions$id, NumberOfAnswers))
}