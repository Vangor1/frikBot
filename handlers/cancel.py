import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database import delete_reminder, get_reminder_by_id


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /cancel_<id> - удаляет напоминание по id
    Проверяет ID на существование и принадлежность пользователю,
    затем удаляет из БД и из jobQueue
    """
    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Отмена", callback_data="profile"),
            ]
        ]
    )
    m = re.match(r"/cancel_(\d+)", update.message.text)
    if not m:
        await update.message.reply_text(
            "Некорректная команда. Используйте /cancel_<id>"
        )
        return
    rem_id = int(m.group(1))
    chat_id = update.effective_chat.id
    record = get_reminder_by_id(rem_id)
    # Проверка на существование напоминания и его принадлежности
    if not record or record[1] != chat_id:
        await update.message.reply_text("Напоминание с таким ID не найдено")
        return
    # Снятие задачи из очереди по имени и из БД
    jobs = context.job_queue.get_jobs_by_name(str(rem_id))
    for job in jobs:
        job.schedule_removal()
    delete_reminder(rem_id)
    await update.message.reply_text(
        f"Напоминание {rem_id} отменено", reply_markup=markup
    )
