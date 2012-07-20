require("qar") || stop("unable to load the required answerer-recommendation package")
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/common",
                      sep=""), pattern="TestPackage.R")
testPackage("qar")
