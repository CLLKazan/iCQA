ReadDBConfiguration <- function() {
# Reads the database connection configuration parameters 
#  from the OSQA settings' file
#  
# Returns: 
# The database connection configuration parameters
require(plyr)
require(stringr)

l <- readLines(paste(Sys.getenv("CQA_HOME"),
                     "/qa-engine/settings_local.py", sep=""))

found.line <- ldply(l, function(s) str_match(s, "DATABASE_NAME = '(.*)'"))
database.name <- found.line[which(!is.na(found.line$V1)),]$V2

found.line <- ldply(l, function(s) str_match(s, "DATABASE_USER = '(.*)'"))
database.user <- found.line[which(!is.na(found.line$V1)),]$V2

found.line <- ldply(l, function(s) str_match(s, "DATABASE_PASSWORD = '(.*)'"))
database.password <- found.line[which(!is.na(found.line$V1)),]$V2

db.configuration <- list(name = database.name,
                         user = database.user,
                         password = database.password)

db.configuration
}