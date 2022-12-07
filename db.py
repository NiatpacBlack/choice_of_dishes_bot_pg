import os
from typing import List, Tuple

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv()


class PostgresConnect:
    """Класс для работы с базой данных PostgresSQL"""

    def __init__(self, dbname, user, password, host):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.db_connect = psycopg2.connect(dbname=self.dbname, user=self.user,
                                           password=self.password, host=self.host)
        self.cursor = self.db_connect.cursor()

    def select_columns_from_table(self, table_name: str, *args: str) -> List[Tuple[str, ...], ...]:
        """Возвращает список с кортежами, содержащими данные переданных полей из *args из таблицы table_name."""

        query = sql.SQL('SELECT {} FROM {}').format(
            sql.SQL(',').join(map(sql.Identifier, args)),
            sql.Identifier(table_name)
        )
        self.cursor.execute(query)

        return [el for el in self.cursor]


if __name__ == '__main__':
    my_postgres_db = PostgresConnect(dbname=os.getenv('DB_NAME'), user=os.getenv('DB_USER'),
                                     password=os.getenv('DB_PASSWORD'), host=os.getenv('DB_HOST'))

    print(my_postgres_db.select_columns_from_table('test_table', 'id', 'firstname'))
    print(my_postgres_db.select_columns_from_table('test_table', 'id', 'age'))
