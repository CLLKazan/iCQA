GetTagsFromDB <- function(db.channel, db.name) {
  # Retrieves tags from the given db
  #
  # Args:
  #   db.channel: db connection object
  #   db.name:    name of the database
  #
  # Returns:
  #   Vector, containing tag id's
  results <- 
    dbSendQuery(db.channel,
                paste("SELECT id FROM ", db.name, ".forum_tag", sep=""))
  data <- fetch(results, n=-1)
  data$id
}