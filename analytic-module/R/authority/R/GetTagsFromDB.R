GetTagsFromDB <- function(db.channel) {
  # Retrieves tags from the given db
  #
  # Args:
  #   db.channel: db connection object
  #
  # Returns:
  #   Vector, containing tag id's
  results <- 
    dbSendQuery(db.channel,"SELECT id FROM forum_tag")
  data <- fetch(results, n=-1)
  data$id
}
