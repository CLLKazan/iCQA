from forum.modules import get_modules_script

get_modules_script('management')

from django.db.models.signals import post_syncdb
import forum.models

def post_syncdb_callback(sender, **kwargs):
    # Import the needed libraries to use the database and detect the
    # DB engine/sever type being currently employed.
    from django.db import connection, connections

    verbosity = int(kwargs["verbosity"])

    # Get the DB engine being used for persistence for this app.
    current_db_engine = connections.databases[connection.alias]['ENGINE']

    # Make sure the updates are only executed for a MySQL DB.
    if current_db_engine.find("mysql") > 0:
        # Ok, mysql was found in the engine description.  Go ahead
        # and attempt to execute the alter table statements.
        cursor = connection.cursor()

        # Pair the table names with the columns that need to be updated.
        updatable_table_columns = {
            "forum_tag": "name",
            "auth_user": "username"
        }

        # Update each column in turn.
        for table_name, column_name in updatable_table_columns.iteritems():
            alter_table_statement = "ALTER TABLE %(table_name)s MODIFY %(column_name)s varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL;" % {
                "table_name": table_name, "column_name": column_name}
            log_status(verbosity,"Updating MySQL column with this statement: " + alter_table_statement)
            cursor.execute(alter_table_statement)

def log_status(verbosity, message):
    if verbosity == 2:
        print "[DEBUG] " + str(message)

# Link the callback to the post_syncdb signal.
post_syncdb.connect(post_syncdb_callback, sender=forum.models)
