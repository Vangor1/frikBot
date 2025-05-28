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
        [InlineKeyboardButton(subject[1], callback_data=f"subject_{subject[0]}")]
        for subject in subjects
    ]
    keyboard.append(
        [InlineKeyboardButton("🔙 В личный кабинет", callback_data="profile")]
    )
    await query.edit_message_text(
        "Выберите предмет для изучения:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def choose_stage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Окно выбора раздела для изучения.
    """
    query = update.callback_query
    await query.answer()
    subject_id = int(query.data.split("_")[1])
    context.user_data["subject_id"] = subject_id
    stages = database.get_stages_by_subject(subject_id)
    print("DEBUG stages:", stages)
    if not stages:
        await query.edit_message_text(
            "Нет доступных этапов для изучения.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 В личный кабинет", callback_data="profile")]]
            ),
        )
        return
    keyboard = [
        [InlineKeyboardButton(stage[1], callback_data=f"stage_{stage[0]}")]
        for stage in stages
    ]
    keyboard.append(
        [InlineKeyboardButton("🔙 В выбор предмета", callback_data="choose_subject")]
    )
    await query.edit_message_text(
        "Выберите этап для изучения:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


def can_open_next_stage(user_id: int, stage_id: int, threshold: int = 80) -> bool:
    """
    Проверяет, может ли пользователь открыть следующий этап:
    средняя оценка по темам этапа >= threshold.
    """
    avg = database.get_average_grade(user_id, stage_id)
    return avg is not None and avg >= threshold


async def choose_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Окно выбора раздела для изучения.
    """
    query = update.callback_query
    await query.answer()
    stage_id = int(query.data.split("_")[1])
    context.user_data["stage_id"] = stage_id
    if stage_id == 1:
        # Этап 1 всегда доступен
        accessible = True
    else:
        accessible = can_open_next_stage(query.from_user.id, stage_id, threshold=80)
    if accessible:
        sections = database.get_sections_by_stage(stage_id)
        keyboard = [
            [InlineKeyboardButton(section[1], callback_data=f"section_{section[0]}")]
            for section in sections
        ]
        keyboard.append(
            [
                InlineKeyboardButton(
                    "🔙 В выбор этапа",
                    callback_data=f"subject_{context.user_data['subject_id']}",
                )
            ]
        )
        await query.edit_message_text(
            "Выберите раздел для изучения:", reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await query.edit_message_text(
            """Вы не можете открыть этот этап, так как ваша средняя оценка
            по темам предыдущего этапа ниже 80%.""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔙 В выбор этапа",
                            callback_data=f"subject_{context.user_data['subject_id']}",
                        )
                    ]
                ]
            ),
        )
