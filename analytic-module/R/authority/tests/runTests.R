require("authority") || stop("unable to load authority")
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/common",
                      sep=""), pattern="TestPackage.R")
testPackage("authority")
