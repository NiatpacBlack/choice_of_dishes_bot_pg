import os
from pprint import pprint
from typing import List, Tuple

from dotenv import load_dotenv

from db import PostgresClient, errors

load_dotenv()
postgres_client = PostgresClient(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
)


def create_table_menu_categories() -> None:
    """Создаёт таблицу menu_categories, в которой будут находиться названия категорий меню."""

    postgres_client.create_table(
        "menu_categories",
        "category_id SERIAL PRIMARY KEY, name_category VARCHAR(60) NOT NULL",
    )


def create_table_dishes() -> None:
    """
    Создаёт таблицу dishes, в которой будут находиться данные о блюдах.

    Блюда связанны с конкретной категорией из menu_categories.
    """

    postgres_client.create_table(
        "dishes",
        """dish_id SERIAL PRIMARY KEY,
         name_dish VARCHAR(60) NOT NULL,
       category_id INTEGER NOT NULL,
             price NUMERIC(5, 2) NOT NULL,
       description VARCHAR(255),
          in_stock BOOLEAN NOT NULL DEFAULT TRUE,
       FOREIGN KEY (category_id) REFERENCES menu_categories (category_id) ON DELETE CASCADE""",
    )


def get_all_tables_name_from_db() -> List[Tuple[str]]:
    """Возвращает список всех таблиц из базы данных в виде картежей с названиями."""

    return postgres_client.select_all_tables_name_from_db()


def get_all_categories_data() -> List[Tuple[str, ...]]:
    """
    Возвращает кортежи с id и названием категории из таблицы menu_categories.

    Вернет пустой список, если не найдет таблицу или категории.
    """
    try:
        return postgres_client.select_all_from_table("menu_categories")
    except errors.UndefinedTable:
        return []


def insert_category_in_table_menu_categories(category_name: str) -> None:
    """Добавляет переданную строку с названием категории в таблицу category_name."""

    postgres_client.insert_in_table(
        table_name="menu_categories", name_category=category_name
    )


if __name__ == "__main__":
    pprint(get_all_categories_data())
