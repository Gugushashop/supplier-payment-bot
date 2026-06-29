from datetime import datetime
from database import get_daily_summary, get_all_suppliers
import logging

logger = logging.getLogger(__name__)

def calculate_daily_totals() -> str:
    """
    Подсчитывает итоги за день и возвращает сформатированную сводку
    """
    
    today = datetime.now().date()
    suppliers = get_all_suppliers()
    
    if not suppliers:
        return "❌ <b>Нет добавленных поставщиков</b>\n\nДобавьте поставщиков в config.py и БД"
    
    # Общие суммы
    total_uah = 0
    total_usd = 0
    
    # Сводка по каждому поставщику
    summary_lines = [
        "✅ <b>СВОДКА НА {date} (до 17:00)</b>".format(date=today.strftime("%d.%m.%Y")),
        "",
        "<b>За сегодня платим:</b>",
    ]
    
    supplier_details = []
    
    for supplier_id, supplier_name, chat_id in suppliers:
        # Получаем данные за день
        data = get_daily_summary(supplier_id, today)
        
        orders_uah = data['orders_uah']
        orders_usd = data['orders_usd']
        minuses_uah = data['minuses_uah']
        minuses_usd = data['minuses_usd']
        
        # Считаем итого
        total_pay_uah = orders_uah - minuses_uah
        total_pay_usd = orders_usd - minuses_usd
        
        total_uah += total_pay_uah
        total_usd += total_pay_usd
        
        # Добавляем в общий список если есть что платить
        if total_pay_uah > 0 or total_pay_usd > 0:
            if total_pay_uah > 0 and total_pay_usd > 0:
                summary_lines.append(f"  🏪 {supplier_name}: {total_pay_usd:.0f} дол + {total_pay_uah:.0f} грн")
            elif total_pay_usd > 0:
                summary_lines.append(f"  🏪 {supplier_name}: {total_pay_usd:.0f} дол")
            else:
                summary_lines.append(f"  🏪 {supplier_name}: {total_pay_uah:.0f} грн")
        
        # Детали по поставщику
        details = format_supplier_summary(
            supplier_name, supplier_id,
            orders_uah, orders_usd,
            minuses_uah, minuses_usd,
            total_pay_uah, total_pay_usd
        )
        
        supplier_details.append(details)
    
    # Общая сводка
    summary_lines.append("")
    summary_lines.append("━" * 50)
    summary_lines.append("")
    
    # Добавляем детали по каждому поставщику
    for detail in supplier_details:
        summary_lines.append(detail)
        summary_lines.append("━" * 50)
        summary_lines.append("")
    
    # Итоговая сумма
    summary_lines.append("<b>💰 ИТОГО К ОПЛАТЕ:</b>")
    if total_usd > 0 and total_uah > 0:
        summary_lines.append(f"  {total_usd:.0f} дол + {total_uah:.0f} грн")
    elif total_usd > 0:
        summary_lines.append(f"  {total_usd:.0f} дол")
    elif total_uah > 0:
        summary_lines.append(f"  {total_uah:.0f} грн")
    else:
        summary_lines.append("  Нет заказов")
    
    summary_lines.append("")
    summary_lines.append("📊 <i>Сводка сформирована автоматически</i>")
    
    return "\n".join(summary_lines)

def format_supplier_summary(
    supplier_name: str,
    supplier_id: str,
    orders_uah: float,
    orders_usd: float,
    minuses_uah: float,
    minuses_usd: float,
    total_uah: float,
    total_usd: float
) -> str:
    """
    Форматирует сводку по одному поставщику
    """
    
    lines = [f"<b>🏪 {supplier_name}</b>"]
    
    # Заказы
    if orders_uah > 0 or orders_usd > 0:
        if orders_usd > 0 and orders_uah > 0:
            lines.append(f"Заказы: {orders_usd:.0f} дол + {orders_uah:.0f} грн")
        elif orders_usd > 0:
            lines.append(f"Заказы: {orders_usd:.0f} дол")
        else:
            lines.append(f"Заказы: {orders_uah:.0f} грн")
    
    # Минусы
    if minuses_uah > 0 or minuses_usd > 0:
        if minuses_usd > 0 and minuses_uah > 0:
            lines.append(f"Минусы: -{minuses_usd:.0f} дол - {minuses_uah:.0f} грн")
        elif minuses_usd > 0:
            lines.append(f"Минусы: -{minuses_usd:.0f} дол")
        else:
            lines.append(f"Минусы: -{minuses_uah:.0f} грн")
    
    # Итого
    if total_usd > 0 and total_uah > 0:
        lines.append(f"<b>Итого: {total_usd:.0f} дол + {total_uah:.0f} грн</b>")
    elif total_usd > 0:
        lines.append(f"<b>Итого: {total_usd:.0f} дол</b>")
    else:
        lines.append(f"<b>Итого: {total_uah:.0f} грн</b>")
    
    # TODO: Добавить информацию о счётах для оплаты
    lines.append("")
    lines.append("💳 <b>Счёты для оплаты:</b>")
    lines.append("  (реквизиты будут добавлены позже)")
    
    # TODO: Добавить информацию о балансе
    lines.append("")
    lines.append("💰 <b>Баланс:</b> (будет добавлен позже)")
    
    return "\n".join(lines)
