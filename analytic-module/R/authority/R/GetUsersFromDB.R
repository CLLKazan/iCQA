GetUsersFromDB <- function(db.channel) {
  # Retrieves users from the given db
  #
  # Args:
  #   db.channel: db connection object
  #
  # Returns:
  #   Vector, containing user id's
  results <- 
    dbSendQuery(db.channel,"SELECT user_ptr_id FROM forum_user")
  data <- fetch(results, n=-1)
  data$user_ptr_id
}
