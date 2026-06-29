import sqlite3
from datetime import datetime
from config import DATABASE_PATH
import logging

logger = logging.getLogger(__name__)

def init_db():
    """Инициализирует БД"""
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
    logger.info("✅ БД инициализирована")

def add_order(supplier_id, ttn, amount, currency):
    """Добавляет заказ"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    now = datetime.now()
    
    cursor.execute('''
    INSERT INTO orders (supplier_id, ttn, amount, currency, date, time)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (supplier_id, ttn, amount, currency, now.date(), now.time()))
    
    conn.commit()
    conn.close()

def add_minus(supplier_id, amount, currency):
    """Добавляет минус"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    now = datetime.now()
    
    cursor.execute('''
    INSERT INTO minuses (supplier_id, amount, currency, date, time)
    VALUES (?, ?, ?, ?, ?)
    ''', (supplier_id, amount, currency, now.date(), now.time()))
    
    conn.commit()
    conn.close()

def add_requisite(supplier_id, requisite, currency):
    """Добавляет новый реквизит"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO requisites (supplier_id, requisite, currency, date_added)
    VALUES (?, ?, ?, ?)
    ''', (supplier_id, requisite, currency, datetime.now().date()))
    
    conn.commit()
    conn.close()

def get_daily_summary(supplier_id, date):
    """Получает сводку за день"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT 
        SUM(CASE WHEN currency='UAH' THEN amount ELSE 0 END) as orders_uah,
        SUM(CASE WHEN currency='USD' THEN amount ELSE 0 END) as orders_usd
    FROM orders
    WHERE supplier_id = ? AND date = ? AND time < '17:00:00'
    ''', (supplier_id, date))
    
    orders = cursor.fetchone()
    
    cursor.execute('''
    SELECT 
        SUM(CASE WHEN currency='UAH' THEN amount ELSE 0 END) as minuses_uah,
        SUM(CASE WHEN currency='USD' THEN amount ELSE 0 END) as minuses_usd
    FROM minuses
    WHERE supplier_id = ? AND date = ? AND time < '17:00:00'
    ''', (supplier_id, date))
    
    minuses = cursor.fetchone()
    
    conn.close()
    
    return {
        'orders_uah': orders[0] or 0,
        'orders_usd': orders[1] or 0,
        'minuses_uah': minuses[0] or 0,
        'minuses_usd': minuses[1] or 0
    }

def get_all_suppliers():
    """Получает список всех поставщиков"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, chat_id FROM suppliers')
    suppliers = cursor.fetchall()
    conn.close()
    
    return suppliers
