GetQuestions <- function(db.connection) {
  # returns questions from DB
  #
  # Args:
  #   db.connection: db connection object
  
  results <- 
    dbSendQuery(db.connection,
                "SELECT id, title, body FROM forum_node 
                 WHERE node_type='question' AND state_string!='(deleted)'")
                      
  fetch(results, n=-1)
}

GetTagQuestionAssociations <- function(db.connection){
  # returns the 'forum_node_tags' table 
  # except for rows with questions without answer
  #
  # Args:
  #   db.connection: db connection object
  
  fetch(
    dbSendQuery(db.connection,
                "SELECT node_id, tag_id FROM forum_node_tags\
                WHERE node_id IN\
                  (SELECT DISTINCT(parent_id) FROM forum_node\
                          WHERE node_type='answer')"), 
    n=-1)
}

PopulateWithAnswerScores <- function(db.connection, questions){
  # returns answer scores for questions
  # score for question with marked answer is 1
  # score for question without answers is 0
  # 
  # Args:
  #   db.connection: db connection object
  #   questions:     dataframe
  
  marked <- fetch(
    dbSendQuery(db.connection,
                "SELECT 1 as score, parent_id AS id FROM forum_node\
                          WHERE marked=1"),
    n=-1)

  not.marked <- fetch(
    dbSendQuery(db.connection,
                "SELECT MAX(score) AS score, parent_id AS id\
                FROM forum_node\
                WHERE node_type='answer' AND parent_id IS NOT NULL\
                AND parent_id NOT IN\
                  (SELECT parent_id FROM forum_node\
                          WHERE marked=1)\
                GROUP BY parent_id"),
    n=-1)
    
  #normalize scores
  not.marked$score <- not.marked$score/(max(not.marked$score)+1)
  
  questions <- merge(questions, rbind(marked, not.marked), all.x=T)
  questions$score[is.na(questions$score)] <- 0
  questions
}
