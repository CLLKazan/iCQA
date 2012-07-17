require("satisfaction") || stop("unable to load satisfaction")
sourceDirectory(paste(Sys.getenv("CQA_HOME"),
                      "/analytic-module/R/common",
                      sep=""), pattern="TestPackage.R")
testPackage("satisfaction")
