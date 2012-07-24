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

GetAnswerScores <- function(db.connection){
  # returns answer scores for questions
  # score for question with marked answer is 1
  # score for question without answers is 0
  # otherwise - maximum score of answers divided by question's views count
  #
  # Args:
  #   db.connection: db connection object
  #   questions:     dataframe
  
  marked <- fetch(
    dbSendQuery(db.connection,
                "SELECT 1 as score, parent_id AS id FROM forum_node\
                          WHERE marked=1 AND parent_id IS NOT NULL"),
    n=-1)

  not.marked <- fetch(
    dbSendQuery(db.connection,
                "SELECT MAX(score) AS score, parent_id AS id
                FROM forum_node
                LEFT JOIN
                (SELECT DISTINCT(parent_id), 1 as mkd
                FROM forum_node WHERE marked = 1) t USING (parent_id)
                WHERE mkd IS NULL
                AND node_type = 'answer'
                AND parent_id IS NOT NULL
                GROUP BY parent_id"),
    n=-1)
  
  hits <- fetch(
    dbSendQuery(db.connection,
                "SELECT id, extra_count FROM forum_node
                          WHERE node_type='question'"),
    n=-1)
    
  not.marked <- merge(not.marked, hits)
  not.marked$score <- not.marked$score/not.marked$extra_count
  not.marked$score[is.na(not.marked$score)] <- 0
  
  return(rbind(marked, not.marked[,c("id","score")]))
}
