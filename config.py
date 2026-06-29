import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Проверка что токены заданы
if not BOT_TOKEN or BOT_TOKEN == "":
    raise ValueError("❌ BOT_TOKEN не задан в .env файле!")
if ADMIN_ID == 0:
    raise ValueError("❌ ADMIN_ID не задан в .env файле!")

# БД
DATABASE_PATH = "supplier_bot.db"

# Поставщики (добавляй новых по мере надобности)
SUPPLIERS = {
    "gugusha_poliit": {
        "name": "Gugusha-Poliit",
        "chat_id": None,  # Заполним когда добавим бота в чат
        "requisites": []
    },
    "mauri": {
        "name": "Аня Маури та Gugusha_shop",
        "chat_id": None,
        "requisites": []
    },
    "bisou": {
        "name": "Gugusha Bisou",
        "chat_id": None,
        "requisites": []
    }
}

# Время отправки сводки (часов, минут)
SUMMARY_TIME = (17, 0)  # 17:00

# Логирование
LOG_LEVEL = "INFO"
