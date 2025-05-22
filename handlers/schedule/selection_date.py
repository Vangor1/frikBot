import re
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import db
from handlers.schedule.shedule_send import send_reminder

REQUEST_TEXT = 1
WAIT_DATE = 2


async def selection_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Точка входа для установки напоминания — выводит календарь
    """
    print("DEBUG selection_date")
    query = update.callback_query
    await query.answer()
    data = query.data
    print("DEBUG callback_data:", data)
    # Пытаемся найти соответствие между строкой в переменной data и шаблоном
    m = re.match(r"^day_(\d+)$", data, flags=re.IGNORECASE)
    if not m:
        await query.answer()
        return
    day = int(m.group(1))
    month = context.user_data["calendar_month"]
    year = context.user_data["calendar_year"]
    selected_date = datetime(year, month, day)
    # Сохраняем выбранную дату и просим пользователя ввести время и текст напоминания
    context.user_data["selected_date"] = selected_date
    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Отмена", callback_data="CANCEL"),
            ]
        ]
    )
    await query.edit_message_text(
        f"Дата выбрана: {selected_date.date()}\n"
        "Теперь введите время и текст напоминания в форме: \n"
        "ЧЧ:ММ Текст\n",
        reply_markup=markup,
    )
    return REQUEST_TEXT


async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Получает текст напоминания от пользователя
    Проверяет формат
    """
    user_text = update.message.text
    user_text = update.message.text.strip()
    if " " not in user_text:
        await update.message.reply_text(
            "Неправильный формат, попробуйте ещё раз.\n"
            "Формат: ЧЧ:ММ Текст\n"
            "Или /cancel для отмены"
        )
        return REQUEST_TEXT
    time_str, message_text = user_text.split(" ", 1)
    try:
        remind_time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        await update.message.reply_text(
            "Неправильный формат времени, попробуйте ещё раз.\n"
            "Формат: ЧЧ:ММ Текст\n"
            "Или /cancel для отмены"
        )
        return REQUEST_TEXT
    date = context.user_data.get("selected_date")
    if not date:
        await update.message.reply_text(
            "Выберите дату перед установкой времени.\n" "Или /cancel для отмены"
        )
        return REQUEST_TEXT
    remind_date_time = datetime.combine(date.date(), remind_time)
    now = datetime.now()
    if remind_date_time <= now:  # Если время прошло переносится на следующий день
        remind_date_time += timedelta(days=1)
    chat_id = update.effective_chat.id
    # Сохранение напоминания в БД
    remind_id = db.add_reminder(chat_id, remind_date_time, message_text)
    # Вычисление задержки и планирование задачи
    delay = (remind_date_time - now).total_seconds()
    context.job_queue.run_once(
        send_reminder,
        when=delay,
        chat_id=chat_id,
        data={"message": message_text, "reminder_id": remind_id},
    )
    await update.message.reply_text(
        f"Напоминание установлено на {remind_date_time.strftime('%Y-%m-%d %H:%M')}"
    )
    await update.message.reply_text(
        "🔙 Возвращаю в личный кабинет...",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🏠 Личный кабинет", callback_data="profile")]]
        ),
    )
    return ConversationHandler.END
