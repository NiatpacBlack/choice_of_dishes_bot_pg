from unittest import TestCase, main
from db import PostgresClient
import os
from dotenv import load_dotenv
from exceptions import CantTableError
from psycopg2 import errors

load_dotenv()


class PostgresClientTest(TestCase):
    """
    Тесты методов класса PostgresClient.

    Для работы тестов в базе данных должна быть таблица test_table хотя-бы с 1 строкой с данными.
    Создать таблицу можно следующим запросом:
        CREATE TABLE test_table
    (
        Id SERIAL PRIMARY KEY,
        FirstName CHARACTER VARYING(30),
        LastName CHARACTER VARYING(30),
        Email CHARACTER VARYING(30),
        Age INTEGER
    );
    """

    def setUp(self):
        self.postgres_client = PostgresClient(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
        )

    def test_type_select_all_tables_from_db(self):
        """Тест возвращаемого типа данных функции select_all_tables_from_db."""

        self.assertEqual(
            type(self.postgres_client.select_all_tables_name_from_db()), list
        )

    def test_type_select_all_from_table(self):
        """Тест возвращаемого типа данных функции select_all_from_table."""

        # Тестируем тип данных при их наличии.
        self.assertEqual(
            type(self.postgres_client.select_all_from_table(table_name="test_table")),
            list,
        )

    def test_error_select_all_from_table(self):
        """Тест функции select_all_from_table при неверном вводе аргументов."""

        # Если в функцию передано неверное название таблицы или тип данных, должна появится кастомная ошибка.
        with self.assertRaises(CantTableError) as e:
            self.postgres_client.select_all_from_table("1234556732523626")
            self.assertEqual(
                "Вы ввели несуществующее название таблицы.",
                e.exception.args[0],
            )

        with self.assertRaises(CantTableError) as e:
            self.postgres_client.select_all_from_table(252)
            self.assertEqual(
                "Вы ввели несуществующее название таблицы.",
                e.exception.args[0],
            )

    def test_type_select_columns_from_table(self):
        """Тест возвращаемого типа данных функции select_columns_from_table."""

        # Тестируем тип данных при их наличии.
        self.assertEqual(
            type(
                self.postgres_client.select_columns_from_table(
                    "test_table", "id", "firstname"
                )
            ),
            list,
        )

    def test_error1_select_columns_from_table(self):
        """Тест 1 функции select_columns_from_table при неверном вводе аргументов."""

        # Если в функцию передано неверное название таблицы, должна появится специальная ошибка модуля psycopg2.
        with self.assertRaises(errors.UndefinedTable) as e:
            self.postgres_client.select_columns_from_table("123214", "id", "age")
            self.assertEqual(
                'отношение "123214" не существует',
                e.exception.args[0],
            )

    def test_error2_select_columns_from_table(self):
        """Тест 2 функции select_columns_from_table при неверном вводе аргументов."""

        # Если в функцию передано неверное название столбца, должна появится специальная ошибка модуля psycopg2.
        with self.assertRaises(errors.UndefinedColumn) as e:
            self.postgres_client.select_columns_from_table("test_table", "id23", "age")
            self.assertEqual(
                'столбец "id23" не существует',
                e.exception.args[0],
            )

    def test_error3_select_columns_from_table(self):
        """Тест 3 функции select_columns_from_table при неверном вводе аргументов."""

        # Если в функцию передано неверный тип данных столбца или таблицы, должна появиться TypeError.
        with self.assertRaises(TypeError) as e:
            self.postgres_client.select_columns_from_table("test_table", 1234, "age")
            self.postgres_client.select_columns_from_table(1234, "id", "age")
            self.assertEqual(
                "SQL identifier parts must be strings",
                e.exception.args[0],
            )

    def test_create_and_delete_table(self):
        """Тест функции создающей таблицу в базе данных и тест функции удаляющей таблицу."""

        # Получаем количество всех таблиц до добавления
        tables_count = len(self.postgres_client.select_all_tables_name_from_db())

        # Создаем тестовую таблицу
        self.postgres_client.create_table(
            table_name="new_test_table",
            values_pattern="test TEXT, test1 VARCHAR(20), test2 INTEGER",
        )

        # Проверяем, что таблиц стало на 1 больше после добавления
        self.assertEqual(
            len(self.postgres_client.select_all_tables_name_from_db()), tables_count + 1
        )

        # Удаляем добавленную тестовую таблицу
        self.postgres_client.delete_table("new_test_table")

        # Проверяем, что количество таблиц уменьшилось
        self.assertEqual(
            len(self.postgres_client.select_all_tables_name_from_db()), tables_count
        )

    def test_insert_and_delete_in_table(self):
        """Тест функции, добавляющей данные в определенную таблицу и функции удаляющей данные из таблицы."""

        # Проверяем количество элементов в таблице до добавления
        values_count = len(self.postgres_client.select_all_from_table("test_table"))

        # Добавляем тестовые данные в таблицу
        self.postgres_client.insert_in_table(
            table_name="test_table",
            firstname="testtest",
            lastname="testtest",
            email="testtest@testmail.ru",
            age="1224",
        )

        # Сравниваем количество элементов в таблице после добавления
        self.assertEqual(
            len(self.postgres_client.select_all_from_table("test_table")),
            values_count + 1,
        )

        # Удаляем тестовую строку из таблицы
        self.postgres_client.delete_value_in_table(
            "test_table", "email='testtest@testmail.ru'"
        )

        # Сравниваем, что количество элементов в таблице равно первоначальному
        self.assertEqual(
            len(self.postgres_client.select_all_from_table("test_table")), values_count
        )


if __name__ == "__main__":
    main()
