from typing import Tuple, List, Optional, Dict

from db_services import (
    insert_category_in_table_menu_categories,
    get_category_id_where_category_name,
    insert_dish_in_dishes_table,
    get_top_dishes_from_selection_dishes_table,
    get_top_users_from_selection_dishes_table,
    get_last_messages,
)
from validators import add_category_message_validator, price_validator


def add_category_in_menu(message) -> Optional[bool]:
    """
    Достает из полученного сообщения название категории и добавляет его в таблицу с категориями меню.

    В случае успеха добавления категории - вернет True, иначе - вернет None.
    """

    category_name = _get_category_name_from_message(message)
    if category_name:
        insert_category_in_table_menu_categories(category_name)
        return True


def add_dish_in_category(message) -> Optional[bool]:
    """Добавляет блюдо переданное в сообщении message в соответсвующую категорию меню."""

    parameters = _dish_in_category_message_converter(message)

    if parameters:
        insert_dish_in_dishes_table(
            dish_name=parameters["dish"],
            category_id=parameters["category"],
            price=parameters["price"],
            description=parameters["description"],
        )
        return True


def get_nice_categories_format(categories_data: Optional[List[Tuple[str, ...]]]) -> str:
    """Преобразует список с данными категорий меню в удобочитаемый строчный формат."""

    if categories_data:
        return "\n".join(map(lambda category_data: category_data[1], categories_data))
    return "Категории в меню отсутствуют"


def get_most_popular_dishes_report(count: int) -> str:
    """Возвращает пользователю текстовый отчет с информацией о самых популярных позициях в меню."""

    list_top_dishes_data = get_top_dishes_from_selection_dishes_table(limit=count)
    text_report = f"<b>Топ {count} самых популярных блюд меню:</b>\n\n"
    place = 1

    for dish, count in list_top_dishes_data:
        text_report += f"<i>{place}. {dish} - выбрано {count} раз</i>\n"
        place += 1

    return text_report


def get_most_popular_users_report(count: int) -> str:
    """Возвращает пользователю текстовый отчет с информацией о самых активных пользователях."""

    list_top_users_data = get_top_users_from_selection_dishes_table(limit=count)
    text_report = f"<b>Топ {count} самых активных пользователей:</b>\n\n"
    place = 1

    for username, count in list_top_users_data:
        text_report += f"<i>{place}. {username} - выбрал блюдо {count} раз</i>\n"
        place += 1

    return text_report


def get_last_messages_report(count: int) -> str:
    """Возвращает пользователю текстовый отчет с информацией о последних сообщениях от пользователя."""

    list_last_messages = get_last_messages(limit=count)
    text_report = f"<b> Последние {count} сообщений от пользователей:</b>\n\n"

    for place, message in enumerate(list_last_messages, 1):
        text_report += f"<i>{place}. {message[0]}</i>\n"

    return text_report


def _dish_in_category_message_converter(message) -> Optional[Dict[str, str]]:
    """
    Обрабатывает полученное сообщение с данными о блюде, которое нужно добавить в меню.

    В случае, если блюдо соответствует шаблону корректного ввода, возвращает словарь с данными, подготовленными для
    добавления в таблицу dish базы данных. В остальных случаях вернет None.
    """

    list_message_words = message.text.split()[1:]
    inner_parameters = {"category": "", "dish": "", "price": "", "description": ""}
    list_parameters_keys = list(inner_parameters.keys())

    if 5 > len(list_message_words) >= 3:

        for index, word in enumerate(list_message_words):
            inner_parameters[list_parameters_keys[index]] = " ".join(word.split("_"))

        category_id = get_category_id_where_category_name(
            category_name=inner_parameters["category"]
        )

        if price_validator(inner_parameters["price"]) and category_id:
            inner_parameters["category"] = str(category_id)
            return inner_parameters


def _get_category_name_from_message(message) -> Optional[str]:
    """
    В случае успеха проверки сообщения - находит в переданном сообщении название категории, форматирует и возвращает ее.

    В случае несоответствия сообщения шаблону добавления категории в меню - вернет None.
    """

    if add_category_message_validator(message):
        category_name = " ".join(message.text.split()[1:])
        category_name = category_name.replace("_", " ")
        return category_name
