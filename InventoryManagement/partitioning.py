from django.db import connection
from django.db.backends.signals import connection_created

def create_partitions(sender, connection, **kwargs):
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS localizeaccommodation (
                id SERIAL PRIMARY KEY,
                property_id INTEGER NOT NULL REFERENCES accommodation(id) ON DELETE CASCADE,
                language CHAR(2) NOT NULL,
                description TEXT,
                policy JSONB
            ) PARTITION BY LIST (language);
            
            CREATE TABLE IF NOT EXISTS localizeaccommodation_en PARTITION OF localizeaccommodation
            FOR VALUES IN ('en');

            CREATE TABLE IF NOT EXISTS localizeaccommodation_es PARTITION OF localizeaccommodation
            FOR VALUES IN ('es');

            CREATE TABLE IF NOT EXISTS localizeaccommodation_fr PARTITION OF localizeaccommodation
            FOR VALUES IN ('fr');
            """)
            
connection_created.connect(create_partitions)
