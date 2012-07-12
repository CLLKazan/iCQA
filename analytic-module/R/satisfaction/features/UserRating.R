UserRating <- function(db.channel, db.name, user.id) {
  # Retrieves user rating
  #
  # Args:
  #   db.channel: db connection object
  #   db.name:    name of the database
  #   user.id:    user id
  #
  # Returns:
  #   User reputation score if user exists, 
  #   NULL otherwise
  results <- 
    dbSendQuery(db.channel,
                paste("SELECT reputation FROM ", 
                      db.name, ".forum_user", " WHERE user_ptr_id=", 
                      user.id, sep=""))
  data <- fetch(results, n=-1)
  data$reputation
}