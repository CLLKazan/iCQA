GetOpenQuestions <- function(db.channel, db.name) {
  # Retrieves open (not answered) questions from the given database connection
  #
  # Args:
  #   db.channel: db connection object
  #
  # Returns:
  #   Frame, containing question data
  require(RMySQL)
  results <- 
    dbSendQuery(db.channel,
                paste("SELECT f.id, f.title, f.body, f.author_id, min(tag_id) as tag_id
                FROM ", db.name, ".forum_node f LEFT JOIN ", db.name,
                      ".forum_node_tags t ON f.id=t.node_id
                WHERE f.node_type='question' AND 
                      EXISTS (SELECT * FROM ", db.name, ".forum_node f2
                      WHERE f2.parent_id=f.id AND f2.marked=1) 
                      GROUP BY f.id"))
  data <- fetch(results, n=-1)
  # Strips the HTML and LaTeX markups
  data$title <- gsub("<(.|\n)*?>","", data$title)
  data$title <- gsub("\\$.[^$]*\\$","", data$title)
  data$title <- gsub("[^[:alpha:] ,.!?-]", "", data$title)
  data$body <- gsub("<(.|\n)*?>","", data$body)
  data$body <- gsub("\\$.[^$]*\\$","", data$body)
  data$body <- gsub("[^[:alpha:] ,.!?-]", "", data$body)
  row.names(data) <- 1:length(data$id)
  data
}
GetCandidateQuestions <- function(db.channel, db.name) {
  # Retrieves candidate questions (with at least 1 answerer)
  # from the given database connection
  #
  # Args:
  #   db.channel: db connection object
  #
  # Returns:
  #   Frame, containing question data
  require(RMySQL)
  results <- 
    dbSendQuery(db.channel,
          paste("SELECT f.id, f.title, f.body, f.author_id, min(tag_id) as tag_id
                FROM ", db.name, ".forum_node f LEFT JOIN ", db.name,
                ".forum_node_tags t ON f.id=t.node_id
                WHERE f.node_type='question' AND 
                EXISTS (SELECT * FROM ", db.name, ".forum_node f2
                WHERE f2.parent_id=f.id AND f2.node_type='answer') 
                GROUP BY f.id"))
  data <- fetch(results, n=-1)
  # Strips the HTML and LaTeX markups
  data$title <- gsub("<(.|\n)*?>","", data$title)
  data$title <- gsub("\\$.[^$]*\\$","", data$title)
  data$title <- gsub("[^[:alpha:] ,.!?-]", "", data$title)
  data$body <- gsub("<(.|\n)*?>","", data$body)
  data$body <- gsub("\\$.[^$]*\\$","", data$body)
  data$body <- gsub("[^[:alpha:] ,.!?-]", "", data$body)
  row.names(data) <- 1:length(data$id)
  data
}