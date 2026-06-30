import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from config import BOT_TOKEN, ADMIN_ID
from database import init_db, add_order, add_minus
from parser import parse_message
from calculator import calculate_daily_totals
from handlers import register_handlers

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Регистрация обработчиков
register_handlers(dp, bot)

async def send_daily_summary():
    """Отправляет сводку в 17:00"""
    while True:
        try:
            now = datetime.now()
            
            # Проверяем, 17:00
            if now.hour == 17 and now.minute == 0:
                try:
                    summary = calculate_daily_totals()
                    
                    # Отправляем в личку админу
                    await bot.send_message(
                        ADMIN_ID,
                        summary,
                        parse_mode="HTML"
                    )
                    
                    logger.info("✅ Сводка отправлена в 17:00")
                    await asyncio.sleep(60)  # Не отправлять ещё 60 сек
                except Exception as e:
                    logger.error(f"❌ Ошибка при отправке сводки: {e}")
            
            await asyncio.sleep(30)  # Проверяем каждые 30 сек
        except Exception as e:
            logger.error(f"❌ Ошибка в send_daily_summary: {e}")
            await asyncio.sleep(60)

@dp.message()
async def handle_message(message: Message):
    """Обработчик всех сообщений в чатах поставщиков"""
    try:
        if message.photo or message.text:
            # Парсим сообщение
            parsed = parse_message(
                text=message.text or message.caption,
                chat_id=message.chat.id,
                message_id=message.message_id
            )
            
            if parsed.get('type') == 'order':
                add_order(
                    supplier_id=parsed['supplier_id'],
                    ttn=parsed['ttn'],
                    amount=parsed['amount'],
                    currency=parsed['currency']
                )
                logger.info(f"📦 Заказ: {parsed['amount']} {parsed['currency']} | TTN: {parsed['ttn']}")
            
            elif parsed.get('type') == 'minus':
                add_minus(
                    supplier_id=parsed['supplier_id'],
                    amount=parsed['amount'],
                    currency=parsed['currency']
                )
                logger.info(f"➖ Минус: {parsed['amount']} {parsed['currency']}")
            
            elif parsed.get('type') == 'balance':
                logger.info(f"💰 Баланс упомянут для {parsed['supplier_id']}")
            
            elif parsed.get('type') == 'new_requisite':
                await bot.send_message(
                    ADMIN_ID,
                    f"⚠️ <b>НОВЫЙ РЕКВИЗИТ НАЙДЕН!</b>\n\n"
                    f"Поставщик: <code>{parsed['supplier_id']}</code>\n"
                    f"Реквизит: <code>{parsed['requisite']}</code>\n"
                    f"Чат ID: <code>{message.chat.id}</code>",
                    parse_mode="HTML"
                )
                logger.info(f"🆕 Новый реквизит: {parsed['requisite']}")
    
    except Exception as e:
        logger.error(f"❌ Ошибка обработки: {e}")

async def main():
    """Главная функция"""
    # Инициализируем БД
    init_db()
    logger.info("✅ БД инициализирована")
    
    # Запускаем отправку сводки в 17:00
    asyncio.create_task(send_daily_summary())
    logger.info("✅ Задача отправки сводки запущена")
    
    logger.info("🤖 Бот запущен и слушает сообщения...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
