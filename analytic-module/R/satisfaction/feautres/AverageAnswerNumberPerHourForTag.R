AverageAnswerNumberForTag <- function(db.channel, db.name, tag.id) {
  # Retrieves average number of answers per hour in this category
  #
  # Args:
  #   db.channel: db connection object
  #   db.name:    name of the database
  #   tag.id:    tag id
  #
  # Returns:
  #   Average number of answers per hour for this tag, if tag exists, 
  #   NA otherwise
  sql.statement <- sprintf("SELECT COUNT(*) AS count FROM %s.forum_node AS t1,
                           %s.forum_node_tags AS t2 WHERE 
                           t1.parent_id=t2.node_id AND t2.tag_id=%d AND 
                           t1.node_type='answer' GROUP BY 
                           DATE_FORMAT(t1.added_at, '%Y %m %d %H');", 
                           db.name, db.name, tag.id)
  results <- dbSendQuery(db.channel, sql.statement)
  data <- fetch(results, n=-1)
  
  mean(data$count)
}
