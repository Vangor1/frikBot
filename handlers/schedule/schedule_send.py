import logging
from telegram.ext import ContextTypes
from telegram import InlineKeyboardMarkup,InlineKeyboardButton


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
        lesson_hint = (
            f"Напоминание: {message_text}\n"
            f"Чтобы пройти занятие, отправьте команду /lesson_{remind_id}"
        )
        await context.bot.send_message(chat_id=chat_id, text=lesson_hint, reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🏠 Личный кабинет", callback_data="profile")]]
        ),)
                
    except Exception as e:
        logger.error(f"Ошибка {e} при отправке напоминания {message_text}")
