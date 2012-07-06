QuestionPostingTime <- function(db.channel, db.name, question.id) {
  results <- 
    dbSendQuery(db.channel,
                paste("SELECT added_at FROM ", 
                      db.name, ".forum_node", " WHERE id=", 
                      question.id, sep=""))
  data <- fetch(results, n=-1)
  as.integer(strsplit(strsplit(data$added_at, " ")[[1]][2], ":")[[1]][1])
}