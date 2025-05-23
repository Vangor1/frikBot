from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import db


async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выводит список напоминаний пользователя
    """
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    reminders = db.get_reminders_by_chat(chat_id)
    if not reminders:
        # Сообщение об отсутсвии напоминаний
        text = "Нечего напоминать"
    else:
        # Создание списка
        lines = ["Ваши напоминания:"]
        for rem_id, _, remind_dt, message in reminders:
            when = remind_dt.strftime("%Y-%m-%d %H:%M")
            lines.append(
                f"""ID {rem_id}: {when} - {message}
                /cancel_{rem_id} - удалить напоминание"""
            )
        text = "\n".join(lines)
    markup = list_buttons()
    await query.edit_message_text(text, reply_markup=markup)


def list_buttons():
    """
    Создает кнопки для списка напоминаний
    """
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Создать напоминание",
                    callback_data="create_reminder",
                ),
                InlineKeyboardButton(
                    "Удалить напоминание",
                    callback_data="cancel_reminder",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🔙 В личный кабинет",
                    callback_data="profile",
                ),
            ],
        ]
    )
