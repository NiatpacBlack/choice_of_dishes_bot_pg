import os

from db import PostgresClient
from dotenv import load_dotenv


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


def create_table_dishes():
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


if __name__ == "__main__":
    create_table_menu_categories()
    create_table_dishes()
