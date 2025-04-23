import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes

in_memory_reminders = {}

logger = logging.getLogger(__name__)

async def schedule (update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        time_str = context.args[0]
        message_text = " ".join(context.args[1:])
        remind_time = datetime.strptime(time_str, "%H:%M").time()
    except(IndexError, ValueError):
        await update.message.reply_text(
            "Неверный формат"
        )
        return
    chat_id = update.effective_chat.id
    now = datetime.now()
    today_run = datetime.combine(now.date(), remind_time)
    if today_run<=now:
        next_run = today_run+timedelta(days=1)
    else:
        next_run = today_run
    in_memory_reminders.setdefault(chat_id, []).append((next_run, message_text))
    context.job_queue.run_once(
        send_reminder,
        when = (next_run - now).total_seconds(),
        chat_id=chat_id,
        name=str(chat_id),
        data={'message':message_text}
    )
        
    await update.message.reply_text(
        f"Напомининание установлено"
    )

async def send_reminder(context:ContextTypes.DEFAULT_TYPE):
    job= context.job
    chat_id = job.chat_id
    message_text = job.data.get('message')
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Напоминание:{message_text}"
        )
    except Exception as e:
        logger.error(f"Ошибка")