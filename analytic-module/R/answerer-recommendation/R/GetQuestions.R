GetOpenQuestions <- function(db.channel) {
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
                "SELECT f.id, f.title, f.body, f.author_id, min(tag_id) as tag_id
                FROM forum_node f LEFT JOIN forum_node_tags t ON f.id=t.node_id
                WHERE f.node_type='question' AND 
                      NOT EXISTS (SELECT * FROM forum_node f2
                      WHERE f2.parent_id=f.id AND f2.marked=1) 
                      GROUP BY f.id")
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
GetCandidateQuestions <- function(db.channel) {
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
          "SELECT f.id, f.title, f.body, f.author_id, min(tag_id) as tag_id
                FROM forum_node f LEFT JOIN forum_node_tags t ON f.id=t.node_id
                WHERE f.node_type='question' AND 
                EXISTS (SELECT * FROM forum_node f2
                WHERE f2.parent_id=f.id AND f2.node_type='answer') 
                GROUP BY f.id")
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
GetQuestionAnswerers <- function(db.channel) {
  # Retrieves question-answerer pairs
  # from the given database connection
  #
  # Args:
  #   db.channel: database connection object
  #
  # Returns:
  #   Frame, containing question-pair data
  require(RMySQL)
  results <- 
    dbSendQuery(db.channel,
                "SELECT DISTINCT t1.id as question_id, t2.author_id as answerer_id
                        FROM forum_node t1
                        LEFT JOIN forum_node t2 ON t1.id=t2.parent_id
                        WHERE t1.node_type='question' and t2.node_type='answer'")
  data <- fetch(results, n=-1) 
  row.names(data) <- 1:length(data$question_id)
  data
}