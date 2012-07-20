test_ComputePerplexity <- function() {
# Reads the test data  
topic.word.assignments <- readAssignments()
topics <- unique(topic.word.assignments$topic_id)
phi.parameters <- readPhiParams()
theta.parameters <- readThetaParams()
psi.parameters <- readPsiParams()

# Calls the function to be tested
perplexity <- ComputePerplexity(topic.word.assignments,
				                        topics,
	                              theta.parameters,
				                        phi.parameters,
				                        psi.parameters)
expected.perplexity <- 6.484451
checkEquals(expected.perplexity, perplexity,
            paste("\nThe perplexity values are not the same:\n
                  the expected value =", expected.perplexity,
                  ", but the actual value =", perplexity))
}
#
# Auxiliary functions
#
readAssignments <- function() {
  table <- read.table(file=paste(Sys.getenv("CQA_HOME"), 
"/analytic-module/R/answerer-recommendation/inst/testData/topicWordAssignments.csv",
                        sep=""),
             sep=" ",
             header=T)
  return (table)
}
readThetaParams <- function() {
  table <- read.table(file=paste(Sys.getenv("CQA_HOME"), 
"/analytic-module/R/answerer-recommendation/inst/testData/thetaParams.csv",
                        sep=""),
             sep=" ",
             header=T)
  return (table)
}
readPsiParams <- function() {
  table <- read.table(file=paste(Sys.getenv("CQA_HOME"), 
"/analytic-module/R/answerer-recommendation/inst/testData/psiParams.csv",
                        sep=""),
             sep=" ",
             header=T)
  return (table)
}
readPhiParams <- function() {
  table <- read.table(file=paste(Sys.getenv("CQA_HOME"), 
"/analytic-module/R/answerer-recommendation/inst/testData/phiParams.csv",
                                 sep=""),
                      sep=" ",
                      header=T)
  return (table)
}