from aiogram import Dispatcher, types
from aiogram.filters import Command
from config import ADMIN_ID
from database import get_daily_summary
from calculator import calculate_daily_totals
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def register_handlers(dp: Dispatcher, bot):
    """Регистрирует все обработчики команд"""
    
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        """Команда /start"""
        await message.reply(
            "👋 <b>Привет!</b>\n\n"
            "Я бот для подсчёта оплат поставщикам.\n\n"
            "Доступные команды:\n"
            "  /balance - текущий баланс\n"
            "  /summary - сводка за сегодня\n"
            "  /help - справка",
            parse_mode="HTML"
        )
    
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        """Команда /help"""
        await message.reply(
            "📖 <b>Справка</b>\n\n"
            "<b>Как работает бот:</b>\n\n"
            "1️⃣ Я слушаю все сообщения в чатах поставщиков\n"
            "2️⃣ Автоматически парсю:\n"
            "   • Заказы (ТТН + сумма)\n"
            "   • Минусы (списания)\n"
            "   • Новые реквизиты\n"
            "3️⃣ До 17:00 накапливаю данные\n"
            "4️⃣ В 17:00 отправляю сводку\n\n"
            "<b>Твои команды:</b>\n"
            "  /summary - получить сводку сейчас\n"
            "  /balance - баланс по поставщикам\n"
            "  /addrequisite - добавить реквизит\n"
            "  /status - статус бота",
            parse_mode="HTML"
        )
    
    @dp.message(Command("summary"))
    async def cmd_summary(message: types.Message):
        """Команда /summary - сводка за сегодня"""
        
        # Только админ может вызвать
        if message.from_user.id != ADMIN_ID:
            await message.reply("❌ У тебя нет доступа к этой команде")
            return
        
        try:
            summary = calculate_daily_totals()
            await message.reply(summary, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Ошибка при генерации сводки: {e}")
            await message.reply(f"❌ Ошибка: {e}")
    
    @dp.message(Command("balance"))
    async def cmd_balance(message: types.Message):
        """Команда /balance - текущий баланс"""
        
        if message.from_user.id != ADMIN_ID:
            await message.reply("❌ У тебя нет доступа к этой команде")
            return
        
        await message.reply(
            "💰 <b>Функция баланса будет добавлена позже</b>\n\n"
            "Сейчас ты можешь использовать /summary для сводки за день",
            parse_mode="HTML"
        )
    
    @dp.message(Command("status"))
    async def cmd_status(message: types.Message):
        """Команда /status - статус бота"""
        
        if message.from_user.id != ADMIN_ID:
            await message.reply("❌ У тебя нет доступа к этой команде")
            return
        
        now = datetime.now()
        
        await message.reply(
            f"✅ <b>Бот работает нормально!</b>\n\n"
            f"🕐 Время сейчас: {now.strftime('%H:%M:%S')}\n"
            f"📅 Дата: {now.strftime('%d.%m.%Y')}\n\n"
            f"⏰ Сводка будет отправлена в 17:00\n"
            f"📊 Используй /summary для сводки сейчас",
            parse_mode="HTML"
        )
    
    @dp.message(Command("addrequisite"))
    async def cmd_add_requisite(message: types.Message):
        """Команда /addrequisite - добавить новый реквизит"""
        
        if message.from_user.id != ADMIN_ID:
            await message.reply("❌ У тебя нет доступа к этой команде")
            return
        
        await message.reply(
            "📝 <b>Добавление реквизита</b>\n\n"
            "Используй формат:\n"
            "/addrequisite supplier_name requisite_number\n\n"
            "Пример:\n"
            "/addrequisite gugusha_poliit 4149123456789999\n\n"
            "<i>Функция будет реализована позже</i>",
            parse_mode="HTML"
        )
