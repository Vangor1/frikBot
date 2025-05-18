from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import db


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Личный кабинет пользователя
    Выводит информацию о пользователе и его напоминаниях
    """
    chat_id = update.effective_chat.id
    total, next_reminders = db.get_user_stats(chat_id)
    text = [f"📝 У вас всего напоминаний: {total}"]
    buttons = []
    if next_reminders:
        rem_id, remind_dt, message = next_reminders
        text.append(
            f"""⏰ Следующее напоминание:
            {remind_dt.strftime('%Y-%m-%d %H:%M')} - {message}
            """
        )
    else:
        text.append("⏰ У вас нет активных напоминаний")
    buttons.append(
        [
            InlineKeyboardButton(
                "Создать напоминание",
                callback_data="create_reminder",
            ),
            InlineKeyboardButton(
                "Заглушка",
                callback_data="cancel_reminder",
            ),
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                "Список напоминаний",
                callback_data="show_list",
            ),
        ]
    )

    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("\n".join(text), reply_markup=markup)


async def profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка коллбэков из личного кабинета
    """
    query = update.callback_query
    data = query.data

    if data == "cancel_reminder":
        # Заглушка, просто отправляем текст
        await query.answer("Заглушка")
        await query.edit_message_text("Заглушка")

    elif data == "show_list":
        # Просто вызываем существующий list_reminders
        from handlers.list import list_reminders

        await list_reminders(update, context)
    elif data == "create_reminder":
        # Просто вызываем существующий schedule
        from handlers.schedule import schedule_start

        await schedule_start(update, context)
