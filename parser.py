import re
from typing import Dict, Optional

def parse_message(text: str, chat_id: int, message_id: int) -> Dict:
    """
    Парсит сообщение и определяет тип контента
    
    Возвращает словарь с типом и данными
    """
    
    if not text:
        return {'type': 'unknown'}
    
    text = text.strip()
    
    # Определяем поставщика по chat_id (позже добавим маппинг)
    supplier_id = get_supplier_by_chat(chat_id)
    
    # Проверяем тип контента
    
    # 1. ТТН (накладная) - обычно 10-14 цифр
    ttn_match = re.search(r'ттн\s*(\d{10,14})', text, re.IGNORECASE)
    if ttn_match:
        ttn = ttn_match.group(1)
        
        # Ищем сумму после ТТН
        amount, currency = extract_amount_and_currency(text)
        
        if amount:
            return {
                'type': 'order',
                'supplier_id': supplier_id,
                'ttn': ttn,
                'amount': amount,
                'currency': currency,
                'chat_id': chat_id,
                'message_id': message_id
            }
    
    # 2. Минус - "сделать минус X" или просто число с минусом
    minus_match = re.search(r'сделать\s+минус\s+([\d\s\.,]+(?:дол|грн|\$|uah|usd)?)', text, re.IGNORECASE)
    if minus_match:
        minus_text = minus_match.group(1)
        amount, currency = extract_amount_and_currency(minus_text)
        
        if amount:
            return {
                'type': 'minus',
                'supplier_id': supplier_id,
                'amount': amount,
                'currency': currency,
                'chat_id': chat_id,
                'message_id': message_id
            }
    
    # 3. Баланс - "баланс" или "на баланс"
    if re.search(r'\b(баланс|на баланс)\b', text, re.IGNORECASE):
        return {
            'type': 'balance',
            'supplier_id': supplier_id,
            'chat_id': chat_id,
            'message_id': message_id
        }
    
    # 4. Новый реквизит - номер карты/счёта
    requisite = extract_requisite(text)
    if requisite:
        return {
            'type': 'new_requisite',
            'supplier_id': supplier_id,
            'requisite': requisite,
            'chat_id': chat_id,
            'message_id': message_id
        }
    
    return {'type': 'unknown'}

def extract_amount_and_currency(text: str) -> tuple:
    """
    Извлекает сумму и валюту из текста
    
    Примеры:
    - "1480" -> (1480, "UAH")
    - "34дол" -> (34, "USD")
    - "34$" -> (34, "USD")
    - "19$+40" -> (19, "USD")  # сложнее
    - "19$+40грн" -> (19, "USD")  # мікс валют
    """
    
    # Паттерны для разных форматов
    
    # Формат: число + валюта (34дол, 34$, 34грн)
    pattern_with_currency = r'([\d\s.,]+)\s*([дол$usd]|грн|uah)'
    matches = re.findall(pattern_with_currency, text, re.IGNORECASE)
    
    if matches:
        amount_str, currency_str = matches[0]
        
        # Очищаем число
        amount = float(amount_str.replace(',', '.').replace(' ', ''))
        
        # Определяем валюту
        if 'дол' in currency_str.lower() or '$' in currency_str or 'usd' in currency_str.lower():
            currency = 'USD'
        else:
            currency = 'UAH'
        
        return amount, currency
    
    # Формат: просто число (предполагаем грн)
    simple_number = re.search(r'(\d+)', text)
    if simple_number:
        amount = float(simple_number.group(1))
        return amount, 'UAH'
    
    return None, None

def extract_requisite(text: str) -> Optional[str]:
    """
    Ищет номер карты или счёта
    """
    
    # Карты (16 цифр)
    card = re.search(r'\b(\d{4}\s*\d{4}\s*\d{4}\s*\d{4})\b', text)
    if card:
        return card.group(1).replace(' ', '')
    
    # Номер счёта (много цифр подряд)
    account = re.search(r'\b(\d{20,})\b', text)
    if account:
        return account.group(1)
    
    # IBAN
    iban = re.search(r'\b(UA\d{25})\b', text)
    if iban:
        return iban.group(1)
    
    return None

def get_supplier_by_chat(chat_id: int) -> str:
    """
    Возвращает supplier_id по chat_id
    TODO: Добавить маппинг из конфига или БД
    """
    
    # Временный маппинг - обновим когда добавим ботов в чаты
    chat_to_supplier = {
        # -1001234567890: "gugusha_poliit",
        # -1009876543210: "mauri",
        # -1005555555555: "bisou",
    }
    
    return chat_to_supplier.get(chat_id, f"unknown_{chat_id}")
