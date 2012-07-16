GetUserProfiles <- function(db.channel) {
  # Retrieves user profiles (related questions/answers per user)
  # from the given database connection
  #
  # Args:
  #   db.channel: database connection object
  #
  # Returns:
  #   Frame, containing user profile data
  require(RMySQL)
  questions <- 
    dbSendQuery(db.channel,
                "SELECT t1.author_id as user_id, min(t2.tag_id) as tag_id,
                t1.body as post FROM forum_node t1 LEFT JOIN 
                      forum_node_tags t2 ON t1.id=t2.node_id
                      WHERE t1.node_type = 'question' GROUP BY user_id")
  data <- fetch(questions, n=-1)
  answers <- 
    dbSendQuery(db.channel,
                "SELECT t1.author_id as user_id, min(t2.tag_id) as tag_id,
                t1.body as post FROM forum_node t1 LEFT JOIN 
                      forum_node_tags t2 ON t1.parent_id=t2.node_id
                      WHERE t1.node_type = 'answer' GROUP BY user_id")
  answer.data <- fetch(answers, n=-1)
  data <- rbind(data, answer.data)
  # Strips the HTML and LaTeX markups
  data$post <- gsub("<(.|\n)*?>","", data$post)
  data$post <- gsub("\\$.[^$]*\\$","", data$post)
  data$post <- gsub("[^[:alpha:] ,.!?-]", "", data$post)
  row.names(data) <- 1:length(data$user_id)
  data
}