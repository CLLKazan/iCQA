
test_GetQuestionsSimilarByTags <- function(){
  questions <- read.table(system.file("testData/test", package="related.questions"))
  tags <- data.frame(
    c(1,1,1,2,2,3,3,3,4,4,5,5,5,6),
    c(1,2,3,2,3,4,5,6,2,7,1,7,2,4)
  )
  names(tags) <- c("node_id","tag_id")
  cnd <- GetQuestionsSimilarByTags(questions[1,], questions[2:nrow(questions),], tags)
  checkEquals(cnd$id, c(2,4,5))
}

test_ComputeFreshness <- function(){
  tw <- "today|recent|(last|past)\\s+(year|month)"
  questions <- read.table(system.file("testData/test", package="related.questions"),as.is=T)
  freshness <- daply(questions, c("id"), ComputeFreshness, 
                             time.words.re=tw)
  names(freshness)<- c()
  checkEquals(freshness, c(1, 1, 0.001312335958, 1, 1, 1, 1, 1, 1, 1, 1, 
              0.0008873114463, 1, 1, 1, 0.0008920606601))
}
