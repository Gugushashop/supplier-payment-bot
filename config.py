import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "8738672362:AAGXJbRXNnEXPjiBFoS0k8GrgPVKq1LUzKc")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1362248715"))

# БД
DATABASE_PATH = "supplier_bot.db"

# Поставщики (добавляй сюда новых)
SUPPLIERS = {
    "gugusha_poliit": {
        "name": "Gugusha-Poliit",
        "chat_id": None,  # Заполним позже
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

# Google Sheets (опционально)
GOOGLE_SHEETS_KEY = os.getenv("GOOGLE_SHEETS_KEY")

# Время отправки сводки (часов, минут)
SUMMARY_TIME = (17, 0)  # 17:00
