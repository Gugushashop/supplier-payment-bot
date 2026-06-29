import sqlite3
from datetime import datetime
from config import DATABASE_PATH
import logging

logger = logging.getLogger(__name__)

def init_db():
    """Инициализирует БД и создаёт таблицы"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Таблица поставщиков
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id TEXT PRIMARY KEY,
            name TEXT,
            chat_id INTEGER,
            balance_uah REAL DEFAULT 0,
            balance_usd REAL DEFAULT 0
        )
        ''')
        
        # Таблица заказов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id TEXT,
            ttn TEXT,
            amount REAL,
            currency TEXT,
            date DATE,
            time TIME,
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
        )
        ''')
        
        # Таблица минусов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS minuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id TEXT,
            amount REAL,
            currency TEXT,
            reason TEXT,
            date DATE,
            time TIME,
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
        )
        ''')
        
        # Таблица реквизитов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS requisites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id TEXT,
            requisite TEXT,
            currency TEXT,
            date_added DATE,
            status TEXT DEFAULT 'active',
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
        )
        ''')
        
        # Таблица дневных сводок
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id TEXT,
            date DATE,
            orders_uah REAL,
            orders_usd REAL,
            minuses_uah REAL,
            minuses_usd REAL,
            total_uah REAL,
            total_usd REAL,
            balance_mentioned BOOLEAN,
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ БД инициализирована успешно")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise

def add_order(supplier_id, ttn, amount, currency):
    """Добавляет заказ в БД"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        now = datetime.now()
        
        cursor.execute('''
        INSERT INTO orders (supplier_id, ttn, amount, currency, date, time)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (supplier_id, ttn, amount, currency, now.date(), now.time()))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Заказ добавлен: {supplier_id} | {amount} {currency}")
    except Exception as e:
        logger.error(f"❌ Ошибка добавления заказа: {e}")

def add_minus(supplier_id, amount, currency):
    """Добавляет минус в БД"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        now = datetime.now()
        
        cursor.execute('''
        INSERT INTO minuses (supplier_id, amount, currency, date, time)
        VALUES (?, ?, ?, ?, ?)
        ''', (supplier_id, amount, currency, now.date(), now.time()))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Минус добавлен: {supplier_id} | {amount} {currency}")
    except Exception as e:
        logger.error(f"❌ Ошибка добавления минуса: {e}")

def add_requisite(supplier_id, requisite, currency="USD"):
    """Добавляет новый реквизит в БД"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO requisites (supplier_id, requisite, currency, date_added)
        VALUES (?, ?, ?, ?)
        ''', (supplier_id, requisite, currency, datetime.now().date()))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Реквизит добавлен: {supplier_id} | {requisite}")
    except Exception as e:
        logger.error(f"❌ Ошибка добавления реквизита: {e}")

def get_daily_summary(supplier_id, date):
    """Получает сводку за день (до 17:00)"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Заказы до 17:00
        cursor.execute('''
        SELECT 
            SUM(CASE WHEN currency='UAH' THEN amount ELSE 0 END) as orders_uah,
            SUM(CASE WHEN currency='USD' THEN amount ELSE 0 END) as orders_usd
        FROM orders
        WHERE supplier_id = ? AND date = ? AND time < '17:00:00'
        ''', (supplier_id, date))
        
        orders_result = cursor.fetchone()
        orders_uah = orders_result[0] or 0 if orders_result else 0
        orders_usd = orders_result[1] or 0 if orders_result else 0
        
        # Минусы до 17:00
        cursor.execute('''
        SELECT 
            SUM(CASE WHEN currency='UAH' THEN amount ELSE 0 END) as minuses_uah,
            SUM(CASE WHEN currency='USD' THEN amount ELSE 0 END) as minuses_usd
        FROM minuses
        WHERE supplier_id = ? AND date = ? AND time < '17:00:00'
        ''', (supplier_id, date))
        
        minuses_result = cursor.fetchone()
        minuses_uah = minuses_result[0] or 0 if minuses_result else 0
        minuses_usd = minuses_result[1] or 0 if minuses_result else 0
        
        conn.close()
        
        return {
            'orders_uah': float(orders_uah),
            'orders_usd': float(orders_usd),
            'minuses_uah': float(minuses_uah),
            'minuses_usd': float(minuses_usd)
        }
    except Exception as e:
        logger.error(f"❌ Ошибка получения сводки: {e}")
        return {
            'orders_uah': 0,
            'orders_usd': 0,
            'minuses_uah': 0,
            'minuses_usd': 0
        }

def get_all_suppliers():
    """Получает список всех поставщиков из БД"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, chat_id FROM suppliers')
        suppliers = cursor.fetchall()
        conn.close()
        
        return suppliers
    except Exception as e:
        logger.error(f"❌ Ошибка получения поставщиков: {e}")
        return []

def clear_daily_data(date):
    """Очищает данные за день (для отладки)"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM orders WHERE date = ?', (date,))
        cursor.execute('DELETE FROM minuses WHERE date = ?', (date,))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Данные за {date} очищены")
    except Exception as e:
        logger.error(f"❌ Ошибка очистки данных: {e}")
