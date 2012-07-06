NumberOfAnswersAcceptedByUser <- function(db.channel, db.name, user.id) {
  # Retrieves number of answers that were accepted by user
  #
  # Args:
  #   db.channel: db connection object
  #   db.name:    name of the database
  #   user.id:    user id
  #
  # Returns:
  #   Number of answers that were accepted by user if user exists, 
  #   0 otherwise
  sql.statement <- sprintf("SELECT COUNT(*) AS count FROM %s.forum_node as t1, 
                           %s.forum_node as t2 WHERE t1.id=t2.parent_id and 
                           t1.author_id=%d AND t2.state_string='(accepted)'", 
                           db.name, db.name, user.id)
  results <- dbSendQuery(db.channel, sql.statement)
  data <- fetch(results, n=-1)
  data$count
}