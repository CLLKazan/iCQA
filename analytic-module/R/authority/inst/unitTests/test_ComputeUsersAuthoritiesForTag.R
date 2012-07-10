
test_ComputeUsersAuthoritiesForTag <- function(){
  require("RSQLite")
  db.name <- system.file("testData/sqlite.db", package="authority")
  mychannel <- dbConnect("SQLite", dbname = db.name)
  
  res <- dbSendQuery(mychannel, "DELETE FROM analytics_authority")
  tags <- GetTagsFromDB(mychannel)
  lapply(tags, ComputeUsersAuthoritiesForTag, db.channel=mychannel, update=F)
  
  results <- dbSendQuery(mychannel,
      "SELECT user_id, tag_id, score FROM analytics_authority")
  data <- fetch(results, n=-1)
  results <- dbSendQuery(mychannel,
      "SELECT user_id, tag_id, score FROM analytics_authority_test")
  data_original <- fetch(results, n=-1)
  
  dbDisconnect(mychannel)
  
  checkEquals(data,data_original)
}
