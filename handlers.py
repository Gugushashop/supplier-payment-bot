from aiogram import Dispatcher, types
from aiogram.filters import Command
from config import ADMIN_ID, SUPPLIERS
from calculator import calculate_daily_totals
from database import add_requisite
from parser import extract_requisite
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
            "  /req - добавить реквизит (reply на сообщение)\n"
            "  /chatid - ID этого чата\n"
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
            "  /summary - сводка сейчас\n"
            "  /recalculate - пересчитать\n"
            "  /req - добавить реквизит (reply)\n"
            "  /chatid - ID чата\n"
            "  /balance - баланс\n"
            "  /status - статус\n"
            "  /help - справка",
            parse_mode="HTML"
        )
    
    @dp.message(Command("summary"))
    async def cmd_summary(message: types.Message):
        """Команда /summary - сводка за сегодня"""
        
        if message.from_user.id != ADMIN_ID:
            await message.reply("❌ У тебя нет доступа к этой команде")
            return
        
        try:
            summary = calculate_daily_totals()
            await message.reply(summary, parse_mode="HTML")
            logger.info("📊 Сводка запрошена")
        except Exception as e:
            logger.error(f"❌ Ошибка при генерации сводки: {e}")
            await message.reply(f"❌ <b>Ошибка:</b> {e}", parse_mode="HTML")
    
    @dp.message(Command("recalculate"))
    async def cmd_recalculate(message: types.Message):
        """Команда /recalculate - пересчитать итоги вручную"""
        
        if message.from_user.id != ADMIN_ID:
            await message.reply("❌ У тебя нет доступа")
            return
        
        try:
            summary = calculate_daily_totals()
            await message.reply(
                "🔄 <b>ПЕРЕСЧЁТ ИТОГОВ</b>\n\n" + summary,
                parse_mode="HTML"
            )
            logger.info("🔄 Пересчет выполнен")
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            await message.reply(f"❌ <b>Ошибка:</b> {e}", parse_mode="HTML")
    
    @dp.message(Command("req"))
    async def cmd_add_req(message: types.Message):
        """Команда /req - добавить реквизит (reply на сообщение)"""
        
        # Проверяем что это reply
        if not message.reply_to_message:
            await message.reply(
                "❌ <b>Ошибка!</b>\n\n"
                "Используй эту команду как reply на сообщение с реквизитом:\n\n"
                "1. Нажми на сообщение поставщика\n"
                "2. Выбери 'Reply'\n"
                "3. Напиши <code>/req</code>",
                parse_mode="HTML"
            )
            return
        
        # Берем текст из сообщения которому ответили
        original_message = message.reply_to_message
        text = original_message.text or original_message.caption or ""
        
        # Парсим реквизит
        requisite = extract_requisite(text)
        
        if not requisite:
            await message.reply(
                "❌ <b>Реквизит не найден!</b>\n\n"
                "Не смог парсить номер карты/счета из сообщения.\n"
                "Проверь что там есть номер карты (16 цифр) или счета (20+ цифр)",
                parse_mode="HTML"
            )
            logger.warning(f"Не удалось парсить реквизит из: {text}")
            return
        
        # Получаем chat_id и определяем поставщика
        chat_id = message.chat.id
        chat_name = message.chat.title or message.chat.username or "Unknown"
        
        # Определяем валюту (простой парсинг)
        currency = "USD" if ("$" in text or "доллар" in text.lower()) else "UAH"
        
        try:
            # Сохраняем в БД
            add_requisite(supplier_id=f"supplier_{abs(chat_id)}", requisite=requisite, currency=currency)
            
            await message.reply(
                f"✅ <b>Реквизит добавлен!</b>\n\n"
                f"💳 Реквизит: <code>{requisite}</code>\n"
                f"💱 Валюта: {currency}\n"
                f"💬 Чат: {chat_name}\n"
                f"📌 ID чата: <code>{chat_id}</code>",
                parse_mode="HTML"
            )
            logger.info(f"✅ Реквизит добавлен: {requisite} ({currency}) для чата {chat_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка добавления реквизита: {e}")
            await message.reply(f"❌ Ошибка при сохранении: {e}", parse_mode="HTML")
    
    @dp.message(Command("chatid"))
    async def cmd_chatid(message: types.Message):
        """Команда /chatid - получить ID этого чата"""
        
        chat_id = message.chat.id
        chat_name = message.chat.title or message.chat.username or "Личный чат"
        
        await message.reply(
            f"📌 <b>Chat ID:</b>\n\n"
            f"<code>{chat_id}</code>\n\n"
            f"💬 Чат: <code>{chat_name}</code>\n\n"
            f"Скопируй число и добавь в config.py",
            parse_mode="HTML"
        )
        logger.info(f"Chat ID: {chat_id}")
    
    @dp.message(Command("balance"))
    async def cmd_balance(message: types.Message):
        """Команда /balance - текущий баланс"""
        
        if message.from_user.id != ADMIN_ID:
            await message.reply("❌ Нет доступа")
            return
        
        await message.reply(
            "💰 <b>Функция баланса</b>\n\n"
            "В разработке 🔨\n\n"
            "Используй /summary для сводки",
            parse_mode="HTML"
        )
    
    @dp.message(Command("status"))
    async def cmd_status(message: types.Message):
        """Команда /status - статус бота"""
        
        if message.from_user.id != ADMIN_ID:
            await message.reply("❌ Нет доступа")
            return
        
        now = datetime.now()
        
        await message.reply(
            f"✅ <b>Бот в сети!</b>\n\n"
            f"🕐 Время: {now.strftime('%H:%M:%S')}\n"
            f"📅 Дата: {now.strftime('%d.%m.%Y')}\n\n"
            f"📊 Сводка в 17:00\n"
            f"💾 БД: SQLite (supplier_bot.db)",
            parse_mode="HTML"
        )

    logger.info("✅ Обработчики команд готовы")
