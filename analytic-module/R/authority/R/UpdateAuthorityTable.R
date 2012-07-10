UpdateAuthorityTable <- function(db.channel, user.id, tag.id, score, update=T) {
  # Updates the analytics_authority table with the given data
  #
  # Args:
  #   db.channel: db connection object
  #   user.id:    user id
  #   tag.id:     tag id
  #   score:      authority score
  #   update:     update duplicate keys
  sql.statement <- sprintf("INSERT INTO analytics_authority 
                           (`user_id`, `tag_id`, `score`) VALUES (%d, %d, %f)",
                           user.id, tag.id, score)
  if (update){
    sql.statement <- paste(sql.statement, 
                           sprintf("ON DUPLICATE KEY UPDATE 
                                    user_id=%d, tag_id=%d, score=%f",
                                    user.id, tag.id, score))
  }
                             
  res <- dbSendQuery(db.channel, sql.statement)
  dbGetRowsAffected(res)
}
