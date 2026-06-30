import re
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

def parse_message(text: str, chat_id: int, message_id: int) -> Dict:
    """
    Парсит сообщение и определяет тип контента
    
    Типы:
    - order: заказ (ТТН + сумма)
    - minus: минус (списание)
    - balance: баланс упомянут
    - new_requisite: новый реквизит найден
    - unknown: не распознано
    """
    
    if not text:
        return {'type': 'unknown'}
    
    text = text.strip()
    
    # Определяем поставщика по chat_id
    supplier_id = get_supplier_by_chat(chat_id)
    
    # 1. ТТН (накладная) - обычно 10-14 цифр
    ttn_match = re.search(r'ттн\s*(\d{10,14})', text, re.IGNORECASE)
    if ttn_match:
        ttn = ttn_match.group(1)
        
        # Ищем сумму после ТТН или в конце
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
    
    # 2. Минус - "сделать минус X" или просто число
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

def extract_amount_and_currency(text: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Извлекает сумму и валюту из текста
    
    Примеры:
    - "1480" → (1480, "UAH")
    - "34дол" → (34, "USD")
    - "34$" → (34, "USD")
    - "19$+40" → (19, "USD")
    - "19$+40грн" → (19, "USD")
    """
    
    if not text:
        return None, None
    
    # Формат: число + валюта (34дол, 34$, 34грн, 34usd, 34uah)
    pattern_with_currency = r'([\d\s.,]+)\s*([дол$usd]|грн|uah)'
    matches = re.findall(pattern_with_currency, text, re.IGNORECASE)
    
    if matches:
        amount_str, currency_str = matches[0]
        
        try:
            # Очищаем число
            amount = float(amount_str.replace(',', '.').replace(' ', ''))
            
            # Определяем валюту
            if 'дол' in currency_str.lower() or '$' in currency_str or 'usd' in currency_str.lower():
                currency = 'USD'
            else:
                currency = 'UAH'
            
            return amount, currency
        except ValueError:
            return None, None
    
    # Формат: просто число (предполагаем грн)
    simple_number = re.search(r'(\d+)', text)
    if simple_number:
        try:
            amount = float(simple_number.group(1))
            return amount, 'UAH'
        except ValueError:
            return None, None
    
    return None, None

def extract_requisite(text: str) -> Optional[str]:
    """
    Ищет номер карты или счёта в тексте
    """
    
    if not text:
        return None
    
    # Карты Visa/Mastercard (16 цифр)
    card = re.search(r'\b(\d{4}\s*\d{4}\s*\d{4}\s*\d{4})\b', text)
    if card:
        return card.group(1).replace(' ', '')
    
    # Номер счёта (много цифр подряд 20+)
    account = re.search(r'\b(\d{20,})\b', text)
    if account:
        return account.group(1)
    
    # IBAN Украины
    iban = re.search(r'\b(UA\d{25,})\b', text)
    if iban:
        return iban.group(1)
    
    return None

def get_supplier_by_chat(chat_id: int) -> str:
    """
    Возвращает supplier_id по chat_id
    
    TODO: Добавить маппинг из конфига или БД
    Сейчас возвращает временный ID на основе chat_id
    """
    
    # Временный маппинг - обновим когда добавим ботов в чаты
    chat_to_supplier = {
        # Добавь сюда реальные chat_id когда добавишь бота в чаты
        # -1001234567890: "gugusha_poliit",
        # -1009876543210: "mauri",
        # -1005555555555: "bisou",
    }
    
    supplier = chat_to_supplier.get(chat_id)
    if supplier:
        return supplier
    
    # Если чат не найден - возвращаем temporary ID
    return f"supplier_{abs(chat_id)}"
