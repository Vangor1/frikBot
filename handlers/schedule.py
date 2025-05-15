import calendar
import logging
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import db

logger = logging.getLogger(__name__)
# Переменная состояния разговора

WAIT_DATE, WAIT_DATETIME_MESSAGE = range(2)


async def schedule_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Показывает календарь для выбора даты
    """
    now = datetime.now()
    year = now.year
    month = now.month
    context.user_data["calendar_month"] = month
    context.user_data["calendar_year"] = year
    # Создание кнопок для дней месяца
    keyboard = []
    for week in calendar.monthcalendar(year, month):
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data="IGNORE"))
            else:
                row.append(InlineKeyboardButton(str(day), callback_data=f"day_{day}"))
        keyboard.append(row)
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"{calendar.month_name[month]} {year}", reply_markup=markup
    )
    return WAIT_DATE


async def handle_date_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обработка нажатия на календарь
    """
    query = update.callback_query
    await query.answer()
    print("DEBUG: попали в handle_date_selection:", query.data)
    if query.data == "IGNORE":
        return WAIT_DATE
    day = int(query.data.split("_")[1])
    month = context.user_data["calendar_month"]
    year = context.user_data["calendar_year"]
    try:
        selected_date = datetime(year, month, day)
    except ValueError:
        await query.edit_message_text("Неправильная дата, попробуйте ещё раз.")
        return WAIT_DATE
    context.user_data["selected_date"] = selected_date
    await query.edit_message_text(
        f"Дата выбрана: {selected_date.date()}\n"
        "Теперь введите время и текст напоминания в форме: \n"
        "ЧЧ:ММ Текст\n"
        "Или /cancel для отмены"
    )
    return WAIT_DATETIME_MESSAGE


async def handle_time_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Получаем время и текст после выбора даты
    """
    text = update.message.text.strip()
    if " " not in text:
        await update.message.reply_text(
            "Неправильный формат, попробуйте ещё раз.\n"
            "Формат: ЧЧ:ММ Текст\n"
            "Или /cancel для отмены"
        )
        return WAIT_DATETIME_MESSAGE
    time_str, message_text = text.split(" ", 1)
    try:
        remind_time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        await update.message.reply_text(
            "Неправильный формат времени, попробуйте ещё раз.\n"
            "Формат: ЧЧ:ММ Текст\n"
            "Или /cancel для отмены"
        )
        return WAIT_DATETIME_MESSAGE
    date = context.user_data.get("selected_date")
    if not date:
        await update.message.reply_text(
            "Выберите дату перед установкой времени.\n" "Или /cancel для отмены"
        )
        return WAIT_DATETIME_MESSAGE
    remind_date_time = datetime.combine(
        date.date(), remind_time
    )  # Объединение даты и времени в datetime
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
    return ConversationHandler.END


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """
    Функция коллбэк, вызываемая планировщиком
    Отправляет напоминание и удаляет запись из БД
    """
    job = context.job
    chat_id = job.chat_id
    message_text = job.data.get("message")
    remind_id = job.data.get("reminder_id")
    try:  # Отправка пользователю текст напоминания
        await context.bot.send_message(
            chat_id=chat_id, text=f"Напоминание: {message_text}"
        )
        # Удаление записи из бд чтоб повторно не сработало
        if remind_id is not None:
            db.delete_reminder(remind_id)
    except Exception as e:
        logger.error(f"Ошибка {e} при отправке напоминания {message_text}")
