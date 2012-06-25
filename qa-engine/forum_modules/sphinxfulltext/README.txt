Full text search (using sphinx search)

Currently full text search works only with sphinx search engine
And builtin PostgreSQL (postgres only >= 8.3???)

5.1 Instructions for Sphinx search setup
Sphinx at this time supports only MySQL and PostgreSQL databases
to enable this, install sphinx search engine and djangosphinx

configure sphinx, sample configuration can be found in
sphinx/sphinx.conf file usually goes somewhere in /etc tree

build osqa index first time manually

% indexer --config /path/to/sphinx.conf --index osqa

setup cron job to rebuild index periodically with command
your crontab entry may be something like

0 9,15,21 * * * /usr/local/bin/indexer --config /etc/sphinx/sphinx.conf --all --rotate >/dev/null 2>&1
adjust it as necessary this one will reindex three times a day at 9am 3pm and 9pm

if your forum grows very big ( good luck with that :) you'll
need to two search indices one diff index and one main
please refer to online sphinx search documentation for the information
on the subject http://sphinxsearch.com/docs/

in settings.py look for INSTALLED_APPS
and uncomment #'djangosphinx',