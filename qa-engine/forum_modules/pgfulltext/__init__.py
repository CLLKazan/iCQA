NAME = 'Postgresql Full Text Search'
DESCRIPTION = "Enables PostgreSql full text search functionality."

try:
    import psycopg2
    from django.conf import settings
    CAN_USE = settings.DATABASE_ENGINE in ('postgresql_psycopg2', 'postgresql', )
except:
    CAN_USE = False
    