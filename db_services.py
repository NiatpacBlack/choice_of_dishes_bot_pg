from datetime import datetime
import os
from pprint import pprint
from typing import List, Tuple, Optional, Union

from dotenv import load_dotenv

from db import PostgresClient, errors
from exceptions import InvalidSQLType

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


def create_table_selection_dishes() -> None:
    """Создает таблицу selection_dishes, в которой будут храниться данные о нажатии на определенное блюдо из меню."""

    postgres_client.create_table(
        "selection_dishes",
        """selection_dishes_id SERIAL PRIMARY KEY,
                      username VARCHAR(255) NOT NULL,
                       dish_id INTEGER NOT NULL,
                       datetime timestamp with time zone NOT NULL,
                   FOREIGN KEY (dish_id) REFERENCES dishes (dish_id) ON DELETE CASCADE""",
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


def get_category_id_where_category_name(category_name: str) -> Optional[int]:
    """Возвращает id категории, название которой совпадает с названием переданным в category_name."""

    query = (
        f"SELECT category_id FROM menu_categories WHERE name_category='{category_name}'"
    )

    postgres_client.cursor.execute(query)

    result = postgres_client.cursor.fetchall()

    return result[0][0] if result else None


def insert_dish_in_dishes_table(
        dish_name: str, category_id: str, price: str, description: str = None
):
    """Добавляет блюдо в таблицу dishes."""
    try:
        postgres_client.insert_in_table(
            table_name="dishes",
            name_dish=dish_name,
            category_id=category_id,
            price=price,
            description=description,
        )
    except errors.InvalidTextRepresentation:
        raise InvalidSQLType(
            "Передан неверный тип данных. Вероятно в цену передано не число."
        )


def get_dishes_from_category_where(category_id: str) -> Optional[Tuple[int, str]]:
    """Возвращает кортеж с данными из таблицы dishes, где поле category_id соответствует переданному id."""

    query = (
        f"SELECT dish_id, name_dish FROM dishes WHERE category_id={category_id}"
    )
    postgres_client.cursor.execute(query)
    result = postgres_client.cursor.fetchall()
    return result if result else None


def get_dish_parameters(dish_id: str) -> Tuple[int, str, int, Union[int, float], str, bool]:
    """Возвращает информацию о конкретном товаре, id которого совпадает с переданным dish_id."""

    query = (
        f"SELECT * FROM dishes WHERE dish_id={dish_id}"
    )
    postgres_client.cursor.execute(query)
    return postgres_client.cursor.fetchone()


def add_dish_selection_in_selection_dishes_table(user_name: str, dish_id: str, date: datetime):
    """Добавляет данные о пользователе и блюде, которое выбрал пользователь в таблицу selection_dishes."""

    postgres_client.insert_in_table(
        table_name="selection_dishes", username=user_name, dish_id=dish_id, datetime=date,
    )


if __name__ == "__main__":
    pprint(get_all_categories_data())
