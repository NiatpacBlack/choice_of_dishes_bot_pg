from db import create_table


def create_table_menu_categories():
    create_table(
        "menu_categories", "category_id SERIAL PRIMARY KEY, name_category VARHCAR(60)"
    )


def create_table_dishes():
    create_table(
        "dishes",
        """dish_id SERIAL PRIMARY KEY,
         name_dish VARCHAR(60),
       category_id INTEGER,
             price NUMERIC(5, 2),
       description VARCHAR(255),
          in_stock INTEGER DEFAULT 1,
       FOREIGN KEY (category_id) REFERENCES menu_categories (category_id)""",
    )
