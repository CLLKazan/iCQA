GetAnswers <- function(db.channel) {
  # Retrieves answers from the given database connection
  #
  # Args:
  #   db.channel: db connection object
  #
  # Returns:
  #   Frame, containing answer data
  #
  require(RMySQL)
  results <- 
    dbSendQuery(db.channel,
                "SELECT id, body, author_id FROM forum_node
                WHERE node_type='answer'")
  data <- fetch(results, n=-1)
  data$body <- gsub("<(.|\n)*?>","", data$body)
  data
}
