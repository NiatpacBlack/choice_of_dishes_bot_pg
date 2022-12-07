import os
from contextlib import closing

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv()

with closing(psycopg2.connect(dbname=os.getenv('DB_NAME'), user=os.getenv('DB_USER'),
                              password=os.getenv('DB_PASSWORD'), host=os.getenv('DB_HOST'))) as conn:
    with conn.cursor() as cursor:
        columns = ('id', 'firstname', 'lastname', 'email', 'age')

        stmt = sql.SQL('SELECT {} FROM {}').format(
            sql.SQL(',').join(map(sql.Identifier, columns)),
            sql.Identifier('test_table')
        )
        cursor.execute(stmt)

        for row in cursor:
            print(row)
