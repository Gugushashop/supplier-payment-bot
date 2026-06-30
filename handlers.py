from aiogram import Dispatcher, types
from aiogram.filters import Command
from config import ADMIN_ID
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
            "Я бот для подсчёта оплат поставщикам 💰\n\n"
            "<b>Доступные команды:</b>\n"
            "  /summary - сводка за сегодня\n"
            "  /recalculate - пересчитать вручную\n"
            "  /balance - текущий баланс\n"
            "  /status - статус бота\n"
            "  /help - справка",
            parse_mode="HTML"
        )
        logger.info(f"👤 Пользователь {message.from_user.id} вызвал /start")
    
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        """Команда /help"""
        await message.reply(
            "📖 <b>Справка по боту</b>\n\n"
            "<b>Как работает:</b>\n"
            "1️⃣ Я слушаю все сообщения в чатах поставщиков\n"
            "2️⃣ Автоматически парсю:\n"
            "   • Заказы (ТТН + сумма)\n"
            "   • Минусы (списания)\n"
            "   • Реквизиты (новые счета)\n"
            "3️⃣ До 17:00 накапливаю данные\n"
            "4️⃣ В 17:00 отправляю сводку\n\n"
            "<b>Команды:</b>\n"
            "  /summary - получить сводку сейчас\n"
            "  /recalculate - пересчитать вручную\n"
            "  /balance - баланс по поставщикам\n"
            "  /status - статус бота\n"
            "  /help - эта справка",
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
            logger.info("📊 Администратор запросил сводку через /summary")
        except Exception as e:
            logger.error(f"❌ Ошибка при генерации сводки: {e}")
            await message.reply(f"❌ <b>Ошибка:</b> {e}", parse_mode="HTML")
    
    @dp.message(Command("recalculate"))
    async def cmd_recalculate(message: types.Message):
        """Команда /recalculate - пересчитать итоги вручную"""
        
        if message.from_user.id != ADMIN_ID:
            await message.reply("❌ У тебя нет доступа к этой команде")
            return
        
        try:
            summary = calculate_daily_totals()
            await message.reply(
                "🔄 <b>ПЕРЕСЧЁТ ИТОГОВ (вручную)</b>\n\n" + summary,
                parse_mode="HTML"
            )
            logger.info("🔄 Администратор вручную пересчитал итоги")
        except Exception as e:
            logger.error(f"❌ Ошибка при пересчете: {e}")
            await message.reply(f"❌ <b>Ошибка:</b> {e}", parse_mode="HTML")
    
    @dp.message(Command("balance"))
    async def cmd_balance(message: types.Message):
        """Команда /balance - текущий баланс"""
        
        if message.from_user.id != ADMIN_ID:
            await message.reply("❌ У тебя нет доступа к этой команде")
            return
        
        await message.reply(
            "💰 <b>Функция баланса</b>\n\n"
            "Находится в разработке 🔨\n\n"
            "Пока используй /summary для получения сводки за день",
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
            f"🕐 Время: {now.strftime('%H:%M:%S')}\n"
            f"📅 Дата: {now.strftime('%d.%m.%Y')}\n\n"
            f"⏰ Сводка будет отправлена в 17:00\n"
            f"📊 Используй /summary для сводки сейчас\n"
            f"🔄 Используй /recalculate для пересчета",
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
            "Функция находится в разработке 🔨\n\n"
            "Пока реквизиты добавляются вручную в config.py",
            parse_mode="HTML"
        )

    logger.info("✅ Обработчики команд зарегистрированы")
