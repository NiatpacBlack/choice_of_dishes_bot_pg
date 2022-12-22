from typing import Optional, List

from config import ADMIN_CHAT_ID
from db_services import get_all_tables_name_from_db


def admin_chat_id_validator(chat_id: int) -> Optional[bool]:
    """
    Возвращает результат проверки полученного chat_id на соответствие аккаунту администратора.

    Список id админов берётся из переменной окружения. По умолчанию используется заглушка.
    """

    admin_chat_id = ADMIN_CHAT_ID or "0000000000"
    list_admin_chat_id = admin_chat_id.split()

    if str(chat_id) in list_admin_chat_id:
        return True


def get_menu_validator() -> Optional[bool]:
    """Проверяет, есть ли в базе данных таблица с названиями категорий меню."""

    all_tables_in_db = get_all_tables_name_from_db()
    if ("menu_categories",) in all_tables_in_db:
        return True


def price_validator(price: str) -> bool:
    """Проверяет, является ли строка с информацией о цене товара числом и больше 0."""

    price.replace(",", ".")
    try:
        float(price)
        return True
    except ValueError:
        return False


def add_category_message_validator(message) -> bool:
    """Совершает череду проверок сообщения, полученного от пользователя, для добавления категории в меню."""

    list_message_words = message.text.split()
    return _allowable_message_word_count_validator(list_message_words) and _allowable_message_length_validator(
        list_message_words, 60)


def _allowable_message_word_count_validator(list_message_words: List[str]) -> bool:
    """Проверяет, передано ли в сообщении пользователя больше одного слова, т.к первое слово это команда."""

    return len(list_message_words) > 1


def _allowable_message_length_validator(list_message_words: List[str], max_length: int) -> bool:
    """
    Проверяет, не превышает ли значение добавляемое в меню, максимальное количество
    символов установленное для полей таблиц в базе данных.
    """

    return len(' '.join(list_message_words[1:])) <= max_length
