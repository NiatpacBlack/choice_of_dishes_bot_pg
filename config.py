import os
from dotenv import load_dotenv


load_dotenv()

# токен телеграмм бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# строка с id чата администратора в телеграмме
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# данные для подключения к базе данных PostgresSQL
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
