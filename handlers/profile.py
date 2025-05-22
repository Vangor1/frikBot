from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import db


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Личный кабинет пользователя
    Выводит информацию о пользователе и его напоминаниях
    """
    query = update.callback_query
    if query:
        await query.answer()
        chat_id = query.message.chat.id
        total, next_reminders = db.get_user_stats(chat_id)
        text = [f"📝 У вас всего напоминаний: {total}"]
        if next_reminders:
            rem_id, remind_dt, message = next_reminders
            text.append(
                f"""⏰ Следующее напоминание:
                {remind_dt.strftime('%Y-%m-%d %H:%M')} - {message}
                """
            )
        else:
            text.append("⏰ У вас нет активных напоминаний")
        markup = profile_buttons()
        await query.edit_message_text("\n".join(text), reply_markup=markup)
    else:
        chat_id = update.effective_chat.id
        total, next_reminders = db.get_user_stats(chat_id)
        text = [f"📝 У вас всего напоминаний: {total}"]
        if next_reminders:
            rem_id, remind_dt, message = next_reminders
            text.append(
                f"""⏰ Следующее напоминание:
                {remind_dt.strftime('%Y-%m-%d %H:%M')} - {message}
                """
            )
        else:
            text.append("⏰ У вас нет активных напоминаний")
        markup = profile_buttons()
        await update.message.reply_text("\n".join(text), reply_markup=markup)


def profile_buttons():
    """
    Создает кнопки для личного кабинета
    """
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Создать напоминание",
                    callback_data="create_reminder",
                ),
                InlineKeyboardButton(
                    "Список напоминаний",
                    callback_data="show_list",
                ),
            ],
        ]
    )
