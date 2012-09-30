require("related.questions") || stop("unable to load related.questions")
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/common",
                      sep=""), pattern="TestPackage.R")
testPackage("related.questions")
