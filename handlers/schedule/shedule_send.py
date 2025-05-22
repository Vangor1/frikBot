import logging

from telegram.ext import ContextTypes

import db

logger = logging.getLogger(__name__)


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
