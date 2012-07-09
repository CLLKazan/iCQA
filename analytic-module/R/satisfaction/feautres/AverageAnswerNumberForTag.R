AverageAnswerNumberForTag <- function(db.channel, db.name, tag.id, date=NULL) {
  # Retrieves average number of answers in this category
  #
  # Args:
  #   db.channel: db connection object
  #   db.name:    name of the database
  #   tag.id:     tag id
  #   date:       the average will be computed for this point in time
  #
  # Returns:
  #   Average number of answers for this tag, if tag exists, 
  #   NA otherwise
  if (is.null(date)) {
    sql.statement <- sprintf("SELECT COUNT(*) AS count FROM %s.forum_node AS t1,
                             %s.forum_node_tags AS t2 WHERE 
                             t1.parent_id=t2.node_id AND t2.tag_id=%d AND 
                             t1.node_type='answer' GROUP BY t1.parent_id;", 
                             db.name, db.name, tag.id)
  } else {
    sql.statement <- sprintf("SELECT COUNT(*) AS count FROM %s.forum_node AS t1,
                             %s.forum_node_tags AS t2 WHERE 
                             t1.parent_id=t2.node_id AND t2.tag_id=%d AND 
                             t1.node_type='answer' AND t1.added_at < '%s'
                             GROUP BY t1.parent_id;", 
                             db.name, db.name, tag.id, 
                             format(date, "%Y-%m-%d %H:%M:%S"))
  }
  results <- dbSendQuery(db.channel, sql.statement)
  data <- fetch(results, n=-1)
  
  mean(data$count)
}
