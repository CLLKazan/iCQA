GetUsersFromDB <- function(db.channel, db.name) {
  # Retrieves users from the given db
  #
  # Args:
  #   db.channel: db connection object
  #   db.name:    name of the database
  #
  # Returns:
  #   Vector, containing user id's
  results <- 
    dbSendQuery(db.channel,
                paste("SELECT user_ptr_id FROM ", db.name, ".forum_user", sep=""))
  data <- fetch(results, n=-1)
  data$user_ptr_id
}