from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import database


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Личный кабинет пользователя
    Выводит информацию занятиях, напоминаниях, выбранных предметах
    """
    query = update.callback_query
    if query:
        await query.answer()
        chat_id = query.message.chat.id
        send = query.edit_message_text
    else:
        chat_id = update.effective_chat.id
        send = update.message.reply_text
    text = [f"*👤 Личный кабинет {update.effective_user.first_name}*"]
    # Предметы пользователя
    user_subjects = database.get_user_subjects(chat_id)
    if user_subjects:
        subjects_list = "\n".join(f"- {name}" for _, name in user_subjects)
        text.append("")
        text.append("📚 Ваши предметы:")
        text.append(f"Выбранные предметы:\n{subjects_list}\n")
    else:
        text.append("❗️Ты еще не начал изучать ни один предмет.")
    # Последнее занятие и оценка
    # last_lesson = get_last_lesson_for_user(chat_id)
    # if last_lesson:
    #    updated_at, subj_name, topic_name, section_name, grade = last_lesson
    #    text.append("")
    #    text.append(
    #        f"""📅 Последнее занятие:
    #        {updated_at.strftime('%Y-%m-%d %H:%M')} - {subj_name}
    #        {topic_name} / {section_name}
    #        Оценка: {grade if grade is not None else 'Нет оценки'}
    #        """
    #    )
    # else:
    #    text.append("")
    #    text.append("❗️ Ты еще не проходил занятия.")
    # Напоминания
    total, next_reminders = database.get_user_stats(chat_id)
    # text.append("")
    if next_reminders:
        rem_id, remind_dt, message = next_reminders
        text.append("🔔 *Ближайшее занятие:*")
        text.append(f"{remind_dt.strftime('%Y-%m-%d %H:%M')} — {message}")
    else:
        text.append("🔔 *Нет запланированных занятий*")

    markup = profile_buttons()
    await send("\n".join(text), parse_mode="Markdown", reply_markup=markup)


def profile_buttons():
    """
    Создает кнопки для личного кабинета
    """
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "➕ Запланировать занятие",
                    callback_data="create_reminder",
                ),
                InlineKeyboardButton(
                    "📅 Список занятий",
                    callback_data="show_list",
                ),
            ],
            [
                InlineKeyboardButton(
                    "Выбрать предмет для изучения",
                    callback_data="select_subject",
                ),
            ],
        ]
    )
