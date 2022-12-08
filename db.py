import os
from typing import List, Tuple

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv()


class PostgresConnect:
    """Класс для работы с базой данных PostgresSQL."""

    def __init__(self, dbname, user, password, host):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.db_connect = psycopg2.connect(dbname=self.dbname, user=self.user,
                                           password=self.password, host=self.host)
        self.cursor = self.db_connect.cursor()

    def select_columns_from_table(self, table_name: str, *args: str) -> List[Tuple[str, ...]]:
        """Возвращает список с кортежами, содержащими данные переданных полей из *args из таблицы table_name."""

        query = sql.SQL('SELECT {} FROM {}').format(
            sql.SQL(',').join(map(sql.Identifier, args)),
            sql.Identifier(table_name)
        )
        self.cursor.execute(query)

        return self.cursor.fetchall()

    def select_all_from_table(self, table_name: str) -> List[Tuple[str, ...]]:
        """Возвращает все значения из переданной таблицы table_name.""" 

        self.cursor.execute('SELECT * FROM {}'.format(table_name))

        return self.cursor.fetchall()



    def create_table(self, table_name: str, values_pattern: str) -> None:
        """
        Создаёт новую таблицу table_name с переданными полями и параметрами полей из values_pattern.
           
        Поля и параметры values_pattern передаются по шаблону: "test TEXT, test1 VARCHAR(20), test2 INTEGER". 
        """

        query = sql.SQL("CREATE TABLE IF NOT EXISTS {}({})".format(table_name, values_pattern))
        self.cursor.execute(query)
        self.db_connect.commit()

        

    def insert_in_table(self, table_name: str, **kwargs: str) -> None:
        """
        Добавляет данные переданные в **kwargs в таблицу table_name.

        Важно, что данные должны быть строками, иначе функция не сработает!
        """

        insert = sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier, kwargs.keys())),
            sql.SQL(', ').join(map(sql.Literal, kwargs.values())),
        )
        self.cursor.execute(insert)
        self.db_connect.commit()



if __name__ == '__main__':
    my_postgres_db = PostgresConnect(dbname=os.getenv('DB_NAME'), user=os.getenv('DB_USER'),
                                     password=os.getenv('DB_PASSWORD'), host=os.getenv('DB_HOST'))    

    # # Тесты функции select_all_from_table
    # print(my_postgres_db.select_all_from_table('test_table'))


    # # Тесты функции select_columns_from_table
    # print(my_postgres_db.select_columns_from_table('test_table', 'id', 'firstname'))
    # print(my_postgres_db.select_columns_from_table('test_table', 'id', 'age'))

    # Тесты функции insert_in_table
    # my_postgres_db.insert_in_table('test_table', firstname='Sasha3', lastname='Ivanov3', email='sasha3@mail.ru',
    #                                age='45')
    # my_postgres_db.insert_in_table('test_table', firstname='Sasha2', lastname='Ivanov2', email='sasha2@mail.ru')
    # my_postgres_db.insert_in_table('test_table', firstname='Sasha4', email='sasha4@mail.ru')
    # my_postgres_db.insert_in_table('test_table', email='sasha5@mail.ru')
    # my_postgres_db.insert_in_table('test_table')
    # print(my_postgres_db.insert_in_table('test_table', firstname='Sasha', lastname='Ivanov', email='sasha@mail.ru',
    #                                      age='45'))

