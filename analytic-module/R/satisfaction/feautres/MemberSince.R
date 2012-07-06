MemberSince <- function(db.channel, db.name, user.id) {
  # Retrieves user's date joined
  #
  # Args:
  #   db.channel: db connection object
  #   db.name:    name of the database
  #   user.id:    user id
  #
  # Returns:
  #   User's joined date if user exists, 
  #   NULL otherwise
  results <- 
    dbSendQuery(db.channel,
                paste("SELECT date_joined FROM ", 
                      db.name, ".auth_user", " WHERE id=", 
                      user.id, sep=""))
  data <- fetch(results, n=-1)
  data$date_joined
}