import asyncio
import logging
from datetime import datetime, time
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from config import BOT_TOKEN, ADMIN_ID
from database import init_db, add_order, add_minus, get_daily_summary
from parser import parse_message
from calculator import calculate_daily_totals
from handlers import register_handlers

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Регистрация обработчиков
register_handlers(dp, bot)

async def send_daily_summary():
    """Отправляет сводку в 17:00"""
    while True:
        now = datetime.now().time()
        
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
            
            if parsed['type'] == 'order':
                add_order(
                    supplier_id=parsed['supplier_id'],
                    ttn=parsed['ttn'],
                    amount=parsed['amount'],
                    currency=parsed['currency']
                )
                logger.info(f"📦 Заказ добавлен: {parsed['amount']} {parsed['currency']}")
            
            elif parsed['type'] == 'minus':
                add_minus(
                    supplier_id=parsed['supplier_id'],
                    amount=parsed['amount'],
                    currency=parsed['currency']
                )
                logger.info(f"➖ Минус добавлен: {parsed['amount']} {parsed['currency']}")
            
            elif parsed['type'] == 'balance':
                logger.info(f"💰 Баланс упомянут: {parsed['supplier_id']}")
            
            elif parsed['type'] == 'new_requisite':
                # Алертим админа о новом реквизите
                await bot.send_message(
                    ADMIN_ID,
                    f"⚠️ <b>Новый реквизит!</b>\n"
                    f"Поставщик: {parsed['supplier_id']}\n"
                    f"Реквизит: <code>{parsed['requisite']}</code>\n"
                    f"Чат: <code>{message.chat.id}</code>",
                    parse_mode="HTML"
                )
                logger.info(f"🆕 Найден новый реквизит: {parsed['requisite']}")
    
    except Exception as e:
        logger.error(f"❌ Ошибка обработки сообщения: {e}")

async def main():
    """Главная функция"""
    # Инициализируем БД
    init_db()
    
    # Запускаем отправку сводки в 17:00
    asyncio.create_task(send_daily_summary())
    
    logger.info("🤖 Бот запущен...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
