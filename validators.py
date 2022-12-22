from typing import Optional

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


def allowable_length_validator(message: str, max_lenght: int) -> bool:
    """
    Проверяет, не превышает ли значение добавляемое в меню, максимальное количество
    символов установленное для полей таблиц в базе данных.
    """

    return len(message) <= max_lenght
