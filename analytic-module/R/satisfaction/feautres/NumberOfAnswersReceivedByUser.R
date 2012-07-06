NumberOfAnswersReceivedByUser <- function(db.channel, db.name, user.id) {
  # Retrieves number of answers that were received by user's questions
  #
  # Args:
  #   db.channel: db connection object
  #   db.name:    name of the database
  #   user.id:    user id
  #
  # Returns:
  #   Number of answers that were received by user's questions if user exists, 
  #   0 otherwise
  sql.statement <- sprintf("SELECT COUNT(*) AS count FROM %s.forum_node as t1, 
                           %s.forum_node as t2 WHERE t1.id=t2.parent_id and 
                           t1.author_id=%d", db.name, db.name, user.id)
  results <- dbSendQuery(db.channel, sql.statement)
  data <- fetch(results, n=-1)
  data$count
}