AverageAnswerScoreForTag <- function(db.channel, db.name, tag.id) {
  # Retrieves average score for answer with the given tag
  #
  # Args:
  #   db.channel: db connection object
  #   db.name:    name of the database
  #   user.id:    tag id
  #
  # Returns:
  #   Average score for answer with the given tag if tag exists, 
  #   NA otherwise
  sql.statement <- sprintf("SELECT avg(score) AS average FROM (SELECT node_id 
                           FROM %s.forum_node JOIN %s.forum_node_tags 
                           ON forum_node.id=forum_node_tags.node_id WHERE 
                           forum_node_tags.tag_id=%d) AS t1, %s.forum_node 
                           AS t2 WHERE t1.node_id=t2.parent_id;", db.name, 
                           db.name, tag.id, db.name)
  results <- dbSendQuery(db.channel, sql.statement)
  data <- fetch(results, n=-1)
  data$average
}