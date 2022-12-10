CREATE TABLE menu_categories (
    category_id SERIAL PRIMARY KEY,
    name_category VARCHAR(60)
);

CREATE TABLE dishes (
    dish_id SERIAL PRIMARY KEY,
    name_dish VARCHAR(100),
    category_id INTEGER,
    price NUMERIC(4, 2),
    description_of_dish VARCHAR(255),
    in_stock INTEGER DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES menu_categories (category_id)
);