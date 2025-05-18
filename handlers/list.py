from telegram import Update
from telegram.ext import ContextTypes

import db


async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает команду /list — выводит все активные напоминания пользователя.
    """
    chat_id = update.effective_chat.id
    reminders = db.get_reminders_by_chat(chat_id)
    if not reminders:
        # Сообщение об отсутсвии напоминаний
        text = "Нечего напоминать"
    else:
        # Создание списка
        lines = ["Ваши напоминания:"]
        for rem_id, _, remind_dt, message in reminders:
            when = remind_dt.strftime("%Y-%m-%d %H:%M")
            lines.append(f"ID {rem_id}: {when} - {message}")
        text = "\n".join(lines)
    # Отправка сообщения
    message = update.message or (
        update.callback_query and update.callback_query.message
    )
    if message:
        await message.reply_text(text)
