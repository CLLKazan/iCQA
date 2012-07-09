UpdateAuthorityTable <- function(db.channel, db.name, user.id, tag.id, score) {
  # Updates the analytics_authority table with the given data
  #
  # Args:
  #   db.channel: db connection object
  #   db.name:    name of the database
  #   user.id:    user id
  #   tag.id:     tag id
  #   score:      authority score
  sql.statement <- sprintf("INSERT INTO %s.analytics_authority 
                               (user_id, tag_id, score) VALUES (%d, %d, %f) 
                               ON DUPLICATE KEY UPDATE user_id=%2$d, 
                               tag_id=%3$d, score=%4$f", db.name,
                           user.id, tag.id, score)
  dbSendQuery(db.channel, sql.statement)
}