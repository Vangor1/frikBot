from telegram import Update
from telegram.ext import ContextTypes

import db


async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /list показывает все активные напоминания
    """
    chat_id = update.effective_chat.id
    reminders = db.get_reminders_by_chat(chat_id)
    if not reminders:
        # Сообщение об отсутсвии напоминаний
        await update.message.reply_text("Нечего напоминать")
        return
    # Создание списка
    lines = ["Ваши напоминания:"]
    for rem_id, _, remind_dt, message in reminders:
        when = remind_dt.strftime("%Y-%m-%d %H:%M")
        lines.append(f"ID {rem_id}: {when} - {message}")
    # Отправка сообщения
    await update.message.reply_text("\n".join(lines))
