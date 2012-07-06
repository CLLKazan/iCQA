GetUserProfiles <- function(db.channel, db.name) {
  # Retrieves user profiles (related questions/answers per user)
  # from the given database connection
  #
  # Args:
  #   db.channel: db connection object
  #
  # Returns:
  #   Frame, containing user profile data
  require(RMySQL)
  results <- 
    dbSendQuery(db.channel,
                paste("SELECT author_id as user_id,
                      GROUP_CONCAT(body SEPARATOR '') FROM ", 
                      db.name, ".forum_node GROUP BY author_id"))
  data <- fetch(results, n=-1)
  names(data)[2] <- "profile"
  # Strips the HTML and LaTeX markups
  data$profile <- gsub("<(.|\n)*?>","", data$profile)
  data$profile <- gsub("\\$.[^$]*\\$","", data$profile)
  data
}