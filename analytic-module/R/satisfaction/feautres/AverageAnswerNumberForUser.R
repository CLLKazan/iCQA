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
  sql.statement <- sprintf("SELECT COUNT(*) as count FROM %s.forum_node AS 
                           t1, %s.forum_node AS t2 WHERE 
                           t1.node_type='answer' AND t1.parent_id=t2.id AND 
                           t2.author_id=%d GROUP BY t2.id;", db.name, 
                           db.name, user.id)
  results <- dbSendQuery(db.channel, sql.statement)
  data <- fetch(results, n=-1)
  mean(data$count)
}