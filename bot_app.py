import re
from typing import Tuple, Optional

from telebot import TeleBot, apihelper

from bot_answers import (
    cb_admin_answer,
    cb_create_menu_answer,
    cb_add_category_answer,
    cb_add_dish_answer,
    cb_back_to_start_answer,
    cb_menu_answer,
    add_dish_answer,
    cb_dishes_in_category_answer,
    cb_back_to_menu_answer,
    add_category_answer,
)
from bot_keyboards import (
    get_start_keyboard,
    get_admin_keyboard,
    get_menu_keyboard,
    get_dishes_keyboard,
    back_to_dishes_button,
)
from config import BOT_TOKEN, ADMIN_CHAT_ID
from db_services import (
    create_table_menu_categories,
    create_table_dishes,
    get_all_categories_data,
    get_dish_parameters,
    create_table_selection_dishes,
    add_dish_selection_in_selection_dishes_table,
    create_table_last_messages,
    add_message_in_last_messages_table,
)
from services import (
    add_category_in_menu,
    add_dish_in_category,
    get_nice_categories_format,
    get_most_popular_dishes_report,
    get_most_popular_users_report,
    get_last_messages_report,
)
from validators import get_menu_validator


bot = TeleBot(BOT_TOKEN)
last_message_data = []


def rewrite_last_message(func):
    """Декоратор, созданный для перезаписи последнего сообщения."""

    def wrapper(*args, **kwargs):
        global last_message_data

        try:
            if last_message_data:
                bot.delete_message(*last_message_data)
        except apihelper.ApiTelegramException:
            pass

        last_message_data = func(*args, **kwargs)

    return wrapper


def admin_chat_id_validator(func):
    """
    Декоратор, который проверяет полученный chat_id на соответствие аккаунту администратора.

    Выполняет переданную функцию в случае, если она запущена из чата администратора, в противном случае отправляет
    сообщение об отсутствии прав у пользователя.
    Список id админов берётся из переменной окружения. По умолчанию используется заглушка.
    """

    def wrapper(message) -> Optional[Tuple[int, int]]:
        admin_chat_id = ADMIN_CHAT_ID or "0000000000"
        list_admin_chat_id = admin_chat_id.split()
        try:
            message_chat_id = message.message.chat.id
        except AttributeError:
            message_chat_id = message.chat.id

        if str(message_chat_id) in list_admin_chat_id:
            func(message)
            return None
        last_message = bot.send_message(
            chat_id=message_chat_id,
            text="У вашего аккаунта нет прав администратора. Обратитесь к менеджеру заведения.",
            reply_markup=get_start_keyboard(),
        )
        return message_chat_id, last_message.id

    return wrapper


@bot.message_handler(commands=["start"])
@rewrite_last_message
def start(message) -> Tuple[int, int]:
    """Отображает пользователю приветственное сообщение и начальное меню."""

    last_message = bot.send_message(
        chat_id=message.chat.id,
        text=f"Здравствуйте, {message.from_user.full_name}, выберите действие:",
        reply_markup=get_start_keyboard(),
    )
    return message.chat.id, last_message.id


@bot.message_handler(commands=["add_category"])
@rewrite_last_message
@admin_chat_id_validator
def add_category(message) -> Tuple[int, int]:
    """Отправляет пользователю ответ о результате добавления категории в меню."""

    result = add_category_in_menu(message)
    last_message = bot.send_message(
        chat_id=message.chat.id,
        text=add_category_answer.answer if result else add_category_answer.false_answer,
        reply_markup=get_admin_keyboard(),
    )
    return message.chat.id, last_message.id


@bot.message_handler(commands=["add_dish"])
@rewrite_last_message
@admin_chat_id_validator
def add_dish(message) -> Tuple[int, int]:
    """Отправляет пользователю ответ о результате добавления блюда в меню."""

    result = add_dish_in_category(message=message)
    last_message = bot.send_message(
        chat_id=message.chat.id,
        text=add_dish_answer.answer if result else add_dish_answer.false_answer,
        reply_markup=get_admin_keyboard(),
    )
    return message.chat.id, last_message.id


@bot.message_handler(content_types=["text"])
def handle_text_message(message) -> None:
    """Отлавливает все текстовые сообщения переданные боту и записывает их в таблицу базы данных."""

    add_message_in_last_messages_table(message.text)


@bot.callback_query_handler(func=lambda callback: callback.data == "menu")
@rewrite_last_message
def callback_menu(callback) -> Tuple[int, int]:
    """Выводит кнопки категорий меню или сообщение об его отсутствии."""

    validation_result = get_menu_validator()
    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_menu_answer.answer
        if validation_result
        else cb_menu_answer.false_answer,
        reply_markup=get_menu_keyboard() if validation_result else None,
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "admin")
@rewrite_last_message
@admin_chat_id_validator
def callback_admin(callback) -> Tuple[int, int]:
    """Выводит кнопки с функционалом администратора если id чата соответствует зарегистрированному админскому id."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_admin_answer.answer,
        reply_markup=get_admin_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "create_menu")
@rewrite_last_message
def callback_create_menu(callback) -> Tuple[int, int]:
    """При нажатии кнопки 'Создать меню' создает пустые таблицы для меню в бд и уведомит об этом пользователя."""

    create_table_menu_categories()
    create_table_dishes()
    create_table_selection_dishes()
    create_table_last_messages()

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_create_menu_answer.answer,
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "add_category")
@rewrite_last_message
def callback_add_category(callback) -> Tuple[int, int]:
    """Сообщает пользователю в ответном сообщении действия, которые нужно сделать, чтобы добавить новую категорию."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_add_category_answer.answer,
        parse_mode="html",
        reply_markup=get_admin_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "add_dish")
@rewrite_last_message
def callback_add_dish(callback) -> Tuple[int, int]:
    """
    Сообщает пользователю в ответном сообщении действия, которые нужно сделать, чтобы добавить новое блюдо.

    В ответном сообщении присутствуют текущие доступные категории из меню, чтобы пользователь понимал с чем работать.
    """

    categories_data = get_all_categories_data()
    categories_text = get_nice_categories_format(categories_data)

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_add_dish_answer.answer + f"<i>{categories_text}</i>",
        parse_mode="html",
        reply_markup=get_admin_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "back_to_start")
@rewrite_last_message
def callback_back_to_start(callback) -> Tuple[int, int]:
    """Отправляет пользователю кнопки стартового меню."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_back_to_start_answer.answer,
        reply_markup=get_start_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "back_to_menu")
@rewrite_last_message
def callback_back_to_menu(callback) -> Tuple[int, int]:
    """Отправляет пользователю кнопки с категориями меню."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_back_to_menu_answer.answer,
        reply_markup=get_menu_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: re.match(r"category_", callback.data))
@rewrite_last_message
def callback_dishes_in_category(callback) -> Tuple[int, int]:
    """Получает id категории из коллбека, и отображает все блюда этой категории."""

    category_id = callback.data.replace("category_", "")

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_dishes_in_category_answer.answer,
        reply_markup=get_dishes_keyboard(category_id),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: re.match(r"dish_", callback.data))
@rewrite_last_message
def callback_parameters_from_dish(callback) -> Tuple[int, int]:
    """
    Отображает пользователю полные данные о блюде, получая его id из коллбека.

    Записывает данные о нажатии в таблицу для статистики.
    """

    dish_id = callback.data.replace("dish_", "")

    add_dish_selection_in_selection_dishes_table(
        user_name=f"{callback.from_user.full_name}", dish_id=dish_id
    )

    dish_parameters = get_dish_parameters(dish_id)

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=f"Подробности о товаре <b>{dish_parameters['dish_name']}</b>:\n\n"
        f"<b>Цена:</b> {dish_parameters['price']}р.\n\n"
        f"<b>Описание:</b> {dish_parameters['description']}\n\n"
        f"{'Активен' if dish_parameters['is_active'] else 'Нет в продаже'}",
        parse_mode="html",
        reply_markup=back_to_dishes_button(dish_parameters["category_id"]),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "top_dishes_report")
@rewrite_last_message
def callback_top_dishes(callback) -> Tuple[int, int]:
    """Отправляет пользователю информацию о топе самых популярных блюд."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=get_most_popular_dishes_report(count=3),
        parse_mode="html",
        reply_markup=get_admin_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "top_users_report")
@rewrite_last_message
def callback_top_users(callback) -> Tuple[int, int]:
    """Отправляет пользователю информацию о топе самых популярных блюд."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=get_most_popular_users_report(count=3),
        parse_mode="html",
        reply_markup=get_admin_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(
    func=lambda callback: callback.data == "last_messages_report"
)
@rewrite_last_message
def callback_last_messages(callback) -> Tuple[int, int]:
    """Отправляет пользователю информацию о 100 последних сообщениях полученных ботом от пользователей."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=get_last_messages_report(count=100),
        parse_mode="html",
        reply_markup=get_admin_keyboard(),
    )
    return callback.message.chat.id, last_message.id


if __name__ == "__main__":
    bot.polling(non_stop=True, interval=0)
