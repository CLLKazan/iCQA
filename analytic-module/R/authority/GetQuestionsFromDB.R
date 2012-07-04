GetQuestionsFromDB <- function(db.channel, db.name, tag.id) {
  # Retrieves questions with given tag from the given db
  #
  # Args:
  #   db.channel: db connection object
  #   db.name:    name of the database
  #   tag.id:     tag id
  #
  # Returns:
  #   Vector, containing question id's
  results <- 
    dbSendQuery(db.channel,
                paste("SELECT node_id FROM ", 
                      db.name, ".forum_node_tags ", "WHERE tag_id=", tag.id, sep=""))
  data <- fetch(results, n=-1)
  data$node_id
}