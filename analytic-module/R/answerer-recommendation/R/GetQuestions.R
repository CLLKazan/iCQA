GetQuestions <- function(db.channel, db.name) {
  # Retrieves questions from the given database connection
  #
  # Args:
  #   db.channel: db connection object
  #
  # Returns:
  #   Frame, containing question data
  require(RMySQL)
  results <- 
    dbSendQuery(db.channel,
                paste("SELECT id, title, body, author_id FROM ", 
                      db.name, ".forum_node WHERE node_type='question'"))
  data <- fetch(results, n=-1)
  data$body <- gsub("<(.|\n)*?>","", data$body)
  data
}