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
        await query.message.reply_text(
            "Нет доступных предметов для изучения.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 В личный кабинет", callback_data="profile")]]
            ),
        )
        return
    keyboard = [
        [InlineKeyboardButton(subject[1], callback_data=f"subject_{subject[0]}")]
        for subject in subjects
    ]
    keyboard.append(
        [InlineKeyboardButton("🔙 В личный кабинет", callback_data="profile")]
    )
    await query.edit_message_text(
        "Выберите предмет для изучения:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


def can_open_next_section(user_id: int, section_id: int, threshold: int = 80) -> bool:
    """
    Проверяет, может ли пользователь открыть следующий раздел:
    средняя оценка по темам раздела >= threshold.
    """
    avg = database.get_average_grade(user_id, section_id)
    return avg is not None and avg >= threshold
