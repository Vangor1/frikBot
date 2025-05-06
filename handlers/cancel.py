from telegram import Update
from telegram.ext import (ContextTypes, ConversationHandler)
import db

async def cancel(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    /cancel <id> - удаляет напоминание
    Проверяет ID на существование и принадлежность пользователю
    затем удаляет из бд и из jobQueue
    """
    #Проверка наличия аргумента
    if not context.args:
        await update.message.reply_text('Укажите ID: /cancel <id>')
        return
    #Парсинг ID и обработка ошибки
    try:
        rem_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text('ID должен быть числом.')
        return
    chat_id = update.effective_chat.id
    record = db.get_reminder_by_id(rem_id)
    #Проверка на существование напоминания и его принадлежности
    if not record or record[1] != chat_id:
        await update.message.reply_text('Напоминание с таким ID не найдено')
        return
    #Снятие задачи из очереди по имени и из БД
    jobs = context.job_queue.get_jobs_by_name(str(rem_id))
    for job in jobs:
        job.schedule_removal()
    db.delete_reminder(rem_id)
    await update.message.reply_text(f'Напоминание {rem_id} отменено')

async def dialogue_cancel (update: Update, context: ContextTypes.DEFAULT_TYPE)->int:
    """
    /cancel - внутри диалога прерывает диалог
    """
    await update.message.reply_text(
        f"Установка напоминания отменена"
    )
    return ConversationHandler.END
    