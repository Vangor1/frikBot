import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
import db

logger = logging.getLogger(__name__)

async def schedule (update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает команду /schedule
    Сохраняет напоминание в БД и ставит в очередь
    """
    try:
        #парсинг времени и текста
        time_str = context.args[0]
        message_text = " ".join(context.args[1:])
        remind_time = datetime.strptime(time_str, "%H:%M").time()
    except(IndexError, ValueError):
        await update.message.reply_text(
            "Неверный формат"
        )
        return
    
    now = datetime.now()
    remind_datetime = datetime.combine(now.date(), remind_time)
    if remind_datetime<=now:#Если время прошло переносится на следующий день
        remind_datetime+=timedelta(days=1)
    chat_id = update.effective_chat.id
    #Сохранение напоминания в БД
    remind_id = db.add_reminder(chat_id, remind_datetime, message_text)
    #Вычисление задержки и планирование задачи
    delay = (remind_datetime-now).total_seconds()
    context.job_queue.run_once(
        send_reminder,
        when = delay,
        chat_id=chat_id,
        data={'message':message_text, 'reminder_id':remind_id}
    )
        
    await update.message.reply_text(
        f"Напомининание установлено"
    )

async def send_reminder(context:ContextTypes.DEFAULT_TYPE):
    """
    Функция коллбэк, вызываемая планировщиком
    Отправляет напоминание и удаляет запись из БД
    """
    job= context.job
    chat_id = job.chat_id
    message_text = job.data.get('message')
    remind_id = job.data.get('reminder_id')
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Напоминание:{message_text}"
        )
        if remind_id is not None:
            db.delete_reminder(remind_id)
    except Exception as e:
        logger.error(f"Ошибка")