import os
from forum.models import KeyValue
from django.db import connection, transaction
import settings

VERSION = 11

if int(settings.PG_FTSTRIGGERS_VERSION) < VERSION:
    f = open(os.path.join(os.path.dirname(__file__), 'pg_fts_install.sql'), 'r')

    try:
        cursor = connection.cursor()
        cursor.execute(f.read())
        transaction.commit_unless_managed()

        settings.PG_FTSTRIGGERS_VERSION.set_value(VERSION)
        
    except Exception, e:
        #import sys, traceback
        #traceback.print_exc(file=sys.stdout)
        pass
    finally:
        cursor.close()

    f.close()

import handlers
