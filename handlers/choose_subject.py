from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import database


async def choose_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Окно выбора предмета для изучения.
    """
    query = update.callback_query
    await query.answer()
    subjects = database.get_subjects()
    if not subjects:
        await query.edit_message_text(
            "Нет доступных предметов для изучения.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 В личный кабинет", callback_data="profile")]]
            ),
        )
        return
    keyboard = [
        [
            InlineKeyboardButton(
                subject[1], callback_data=f"subjectforchoose_{subject[0]}"
            )
        ]
        for subject in subjects
    ]
    keyboard.append(
        [InlineKeyboardButton("🔙 В личный кабинет", callback_data="profile")]
    )
    await query.edit_message_text(
        "Выберите предмет для изучения:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_choose_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Записывает выбранный предмет в БД.
    """
    query = update.callback_query
    await query.answer()
    chat_id = int(query.message.chat.id)
    subject_id = query.data.split("_")[1]
    database.add_user_subject(chat_id, subject_id)
    keyboard = [
        [
            InlineKeyboardButton(
                "🔙 В ЛК",
                callback_data="profile",
            ),
            InlineKeyboardButton(
                "➕ Запланировать занятие",
                callback_data="create_reminder",
            ),
        ]
    ]
    await query.edit_message_text(
        "Предмет выбран, можете сразу создать напоминание или вернуться в ЛК.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
