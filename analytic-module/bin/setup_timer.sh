#!/bin/sh
tmpfile=/tmp/crontab.tmp

crontab -l | grep -vi "analytic-module" > $tmpfile

# add custom entries to crontab
for file in $CQA_HOME/analytic-module/R/*.R; do
echo "0 0 * * * $file" >> $tmpfile
done
#load crontab from file
crontab $tmpfile

# remove temporary file
rm $tmpfile

# restart crontab
/etc/init.d/cron restart
