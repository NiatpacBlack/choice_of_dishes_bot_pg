from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

import pytz

from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST
from db import PostgresClient, errors
from exceptions import InvalidSQLType


postgres_client = PostgresClient(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
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


def create_table_last_messages() -> None:
    """Создает таблицу last_messages, в которой будут храниться данные о сообщениях отправленных пользователями боту."""

    postgres_client.create_table(
        "last_messages",
        """
        last_message_id SERIAL PRIMARY KEY,
           text_message text NOT NULL
        """,
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

    query = f"SELECT dish_id, name_dish FROM dishes WHERE category_id={category_id}"
    postgres_client.cursor.execute(query)
    result = postgres_client.cursor.fetchall()
    return result if result else None


def get_dish_parameters(dish_id: str) -> Dict[str, Any]:
    """Возвращает словарь с информацией о конкретном товаре, id которого совпадает с переданным dish_id."""

    query = f"SELECT * FROM dishes WHERE dish_id={dish_id}"
    postgres_client.cursor.execute(query)
    cursor_data = postgres_client.cursor.fetchone()

    return {
        "id": cursor_data[0],
        "dish_name": cursor_data[1],
        "category_id": cursor_data[2],
        "price": cursor_data[3],
        "description": cursor_data[4],
        "is_active": cursor_data[5],
    }


def add_dish_selection_in_selection_dishes_table(user_name: str, dish_id: str):
    """Добавляет данные о пользователе и блюде, которое выбрал пользователь в таблицу selection_dishes."""

    postgres_client.insert_in_table(
        table_name="selection_dishes",
        username=user_name,
        dish_id=dish_id,
        datetime=str(datetime.now(pytz.timezone("Europe/Minsk"))),
    )


def add_message_in_last_messages_table(message: str) -> None:
    """Добавляет строку message в таблицу last_messages."""

    postgres_client.insert_in_table(
        table_name="last_messages",
        text_message=message,
    )


def get_last_messages(limit: int = 10) -> List[Tuple[str]]:
    """Получает n-ное количество последних сообщений из таблицы last_messages."""

    query = f"SELECT text_message FROM last_messages ORDER BY last_message_id DESC LIMIT ({limit})"
    postgres_client.cursor.execute(query)
    return postgres_client.cursor.fetchall()


def get_top_dishes_from_selection_dishes_table(limit: int) -> List[Tuple[str, int]]:
    """
    Получает n-ное количество названий блюд и количество раз, когда это блюдо было выбрано.

    Данные берутся из выборки количества всех выбранных пользователями блюд.
    """

    query = f"""
        SELECT name_dish, count(name_dish) 
          FROM selection_dishes JOIN dishes USING(dish_id)
      GROUP BY name_dish
      ORDER BY count DESC
         LIMIT {limit}
        """
    postgres_client.cursor.execute(query)
    return postgres_client.cursor.fetchall()


def get_top_users_from_selection_dishes_table(limit: int) -> List[Tuple[str, int]]:
    """
    Получает n-ное количество ников пользователей и количество блюд, которые они выбирали.

    Данные берутся из выборки количества всех выбранных пользователями блюд.
    """

    query = f"""
        SELECT username, count(username) 
          FROM selection_dishes JOIN dishes USING(dish_id)
      GROUP BY username
      ORDER BY count DESC
         LIMIT {limit}
        """
    postgres_client.cursor.execute(query)
    return postgres_client.cursor.fetchall()


if __name__ == "__main__":
    print(get_top_dishes_from_selection_dishes_table(3))
