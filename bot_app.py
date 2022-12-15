import os

from dotenv import load_dotenv
from telebot import TeleBot

from bot_answers import (
    cb_admin_answer, cb_create_menu_answer, cb_add_category_answer, cb_add_dish_answer, cb_back_to_start_answer,
    cb_menu_answer,
)
from db_services import (
    create_table_menu_categories,
    create_table_dishes,
    get_all_categories_data,
)
from services import (
    get_start_keyboard,
    get_menu_keyboard,
    get_admin_keyboard,
    add_category_in_menu,
    add_dish_in_category, get_nice_categories_format,
)
from validators import (
    admin_chat_id_validator, get_menu_validator, )

load_dotenv()
bot = TeleBot(os.getenv("BOT_TOKEN"))


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Здравствуйте, {message.from_user.full_name}, выберите действие:",
        reply_markup=get_start_keyboard(),
    )


@bot.message_handler(commands=["add_category"])
def add_category(message):
    """Добавляет полученное по шаблону название категории в меню."""

    result = add_category_in_menu(message)
    bot.send_message(
        chat_id=message.chat.id,
        text=result,
    )


@bot.message_handler(commands=["add_dish"])
def add_category(message):
    """Добавляет полученное по шаблону блюдо в соответствующую категорию меню."""

    result = add_dish_in_category(message=message)
    bot.send_message(
        chat_id=message.chat.id,
        text=result,
    )


@bot.callback_query_handler(func=lambda callback: callback.data == "menu")
def callback_menu(callback):
    """Выводит категории меню или сообщение об его отсутствии."""

    validation_result = get_menu_validator()
    bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_menu_answer.answer if validation_result else cb_menu_answer.false_answer,
        reply_markup=get_menu_keyboard() if validation_result else None,
    )


@bot.callback_query_handler(func=lambda callback: callback.data == "admin")
def callback_admin(callback):
    """Выводит функционал администратора если id чата соответствует зарегистрированному админскому id."""

    validation_result = admin_chat_id_validator(callback.message.chat.id)

    bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_admin_answer.answer if validation_result else cb_admin_answer.false_answer,
        reply_markup=get_admin_keyboard() if validation_result else None,
    )


@bot.callback_query_handler(func=lambda callback: callback.data == "create_menu")
def callback_create_menu(callback):
    """При нажатии кнопки 'Создать меню' создает пустые таблицы для меню в бд и уведомит об этом пользователя."""

    create_table_menu_categories()
    create_table_dishes()
    bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_create_menu_answer.answer,
    )


@bot.callback_query_handler(func=lambda callback: callback.data == "add_category")
def callback_add_category(callback):
    """Сообщает пользователю в ответном сообщении действия, которые нужно сделать, чтобы добавить новую категорию."""

    bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_add_category_answer.answer,
        parse_mode="html",
    )


@bot.callback_query_handler(func=lambda callback: callback.data == "add_dish")
def callback_add_dish(callback):
    """
    Сообщает пользователю в ответном сообщении действия, которые нужно сделать, чтобы добавить новое блюдо.

    В ответном сообщении присутствуют текущие доступные категории из меню, чтобы пользователь понимал с чем работать.
    """
    categories_data = get_all_categories_data()
    categories_text = get_nice_categories_format(categories_data) if categories_data else 'Доступных категорий нет'

    bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_add_dish_answer.answer + f"<i>{categories_text}</i>",
        parse_mode="html",
    )


@bot.callback_query_handler(func=lambda callback: callback.data == "back_to_start")
def callback_back_to_start(callback):
    """Возвращает пользователя на начальное меню."""

    bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_back_to_start_answer.answer,
        reply_markup=get_start_keyboard(),
    )


if __name__ == "__main__":
    bot.polling(non_stop=True, interval=0)
