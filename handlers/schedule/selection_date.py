import re
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import database
from database import add_reminder, get_average_grade_for_stage
from handlers.schedule.shedule_send import send_reminder

REQUEST_TEXT = 1
WAIT_DATE = 2


async def choose_subject_for_reminder(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Окно выбора предмета для изучения.
    """
    print("DEBUG choose_subject_for_reminder")
    query = update.callback_query
    await query.answer()
    context.user_data["day"] = query.data
    print("DEBUG ", context.user_data["day"])
    chat_id = int(query.message.chat.id)
    user_subjects = database.get_user_subjects(chat_id)
    keyboard = [
        [
            InlineKeyboardButton(
                subject[1], callback_data=f"subjectforreminder_{subject[0]}"
            )
        ]
        for subject in user_subjects
    ]
    keyboard.append(
        [InlineKeyboardButton("🔙 В личный кабинет", callback_data="profile")]
    )
    await query.edit_message_text(
        "Выберите предмет для планирования занятия:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def choose_stage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Окно выбора раздела для изучения.
    """
    query = update.callback_query
    await query.answer()
    subject_id = context.user_data.get("subject_id")
    stages = database.get_stages_by_subject(subject_id)
    print("DEBUG stages:", stages)
    keyboard = [
        [InlineKeyboardButton(stage[1], callback_data=f"stage_{stage[0]}")]
        for stage in stages
    ]
    keyboard.append(
        [
            InlineKeyboardButton(
                "🔙 В ЛК",
                callback_data="profile",
            ),
            InlineKeyboardButton(
                "🔙 В выбор предмета", callback_data=context.user_data["day"]
            ),
        ]
    )
    await query.edit_message_text(
        "Выберите этап для изучения:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


def can_open_next_stage(user_id: int, stage_id: int, threshold: int = 80) -> bool:
    """
    Проверяет, может ли пользователь открыть следующий этап:
    Для этого оценивается средняя оценка пользователя по темам предыдущего этапа.
    Если средняя оценка предыдущего этапа равна или превышает >= threshold.
    """
    prev_stage_id = stage_id - 1
    if prev_stage_id < 1:
        return True
    avg = get_average_grade_for_stage(user_id, prev_stage_id)
    return avg is not None and avg >= threshold


async def choose_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Окно выбора раздела для изучения.
    """
    query = update.callback_query
    await query.answer()
    stage_id = context.user_data.get("stage_id")
    subject_id = context.user_data["subject_id"]
    if stage_id == 1:
        # Этап 1 всегда доступен
        accessible = True
    else:
        accessible = can_open_next_stage(query.from_user.id, stage_id, threshold=80)
    if accessible:
        sections = database.get_sections_by_stage(stage_id)
        print(sections)
        keyboard = [
            [InlineKeyboardButton(section[1], callback_data=f"section_{section[0]}")]
            for section in sections
        ]
        keyboard.append(
            [
                InlineKeyboardButton(
                    "🔙 В ЛК",
                    callback_data="profile",
                ),
                InlineKeyboardButton(
                    "🔙 Назад",
                    callback_data=f"subjectforreminder_{subject_id}",
                ),
            ],
        )
        await query.edit_message_text(
            "Выберите раздел для изучения",
            reply_markup=InlineKeyboardMarkup(keyboard),
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
                            callback_data=f"stage_{stage_id}",
                        )
                    ]
                ]
            ),
        )


async def choose_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Окно выбора темы для изучения.
    """
    query = update.callback_query
    await query.answer()
    section_id = context.user_data.get("section_id")
    stage_id = context.user_data.get("stage_id")
    topics = database.get_topics_by_section(section_id)
    print(topics)
    keyboard = [
        [InlineKeyboardButton(topic[1], callback_data=f"topic_{topic[0]}")]
        for topic in topics
    ]
    keyboard.append(
        [
            InlineKeyboardButton(
                "🔙 В ЛК",
                callback_data="profile",
            ),
            InlineKeyboardButton(
                "🔙 В выбор раздела",
                callback_data=f"stage_{stage_id}",
            ),
        ]
    )
    await query.edit_message_text(
        "Выберите тему для изучения",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def selection_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Точка входа для установки напоминания — выводит календарь
    """
    print("DEBUG selection_date")
    query = update.callback_query
    await query.answer()
    topic_id = int(query.data.split("_")[1])
    print("topic----id: ", topic_id)
    context.user_data["topic_id"] = topic_id
    print("DEBUG callback_data:", context.user_data["day"])
    # Пытаемся найти соответствие между строкой в переменной data и шаблоном
    m = re.match(r"^day_(\d+)$", context.user_data["day"], flags=re.IGNORECASE)
    if not m:
        await query.answer()
        return
    day = int(m.group(1))
    month = context.user_data["calendar_month"]
    year = context.user_data["calendar_year"]
    selected_date = datetime(year, month, day)
    # Сохраняем выбранную дату и просим пользователя ввести время и текст напоминания
    context.user_data["selected_date"] = selected_date
    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Отмена", callback_data="profile"),
            ]
        ]
    )
    print("DEBUG selected_date:", context.user_data["selected_date"])
    await query.edit_message_text(
        f"Дата выбрана: {context.user_data['selected_date'].date()}\n"
        "Теперь введите время и текст напоминания в форме: \n"
        "ЧЧ:ММ Текст\n",
        reply_markup=markup,
    )
    return REQUEST_TEXT


async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Получает текст напоминания от пользователя
    Проверяет формат
    """
    print("DEBUG receive_text")
    user_text = update.message.text
    user_text = update.message.text.strip()
    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Отмена", callback_data="profile"),
            ]
        ]
    )
    if " " not in user_text:
        await update.message.reply_text(
            "Неправильный формат, попробуйте ещё раз.\n" "Формат: ЧЧ:ММ Текст\n",
            reply_markup=markup,
        )
        return REQUEST_TEXT
    time_str, message_text = user_text.split(" ", 1)
    try:
        remind_time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        await update.message.reply_text(
            "Неправильный формат времени, попробуйте ещё раз.\n"
            "Формат: ЧЧ:ММ Текст\n",
            reply_markup=markup,
        )
        return REQUEST_TEXT
    date = context.user_data.get("selected_date")
    if not date:
        await update.message.reply_text(
            "Выберите дату перед установкой времени.\n",
            reply_markup=markup,
        )
        return REQUEST_TEXT
    remind_date_time = datetime.combine(date.date(), remind_time)
    now = datetime.now()
    if remind_date_time <= now:  # Если время прошло переносится на следующий день
        remind_date_time += timedelta(days=1)
    chat_id = update.effective_chat.id
    subject_id = context.user_data.get("subject_id")
    stage_id = context.user_data.get("stage_id")
    section_id = context.user_data.get("section_id")
    topic_id = context.user_data.get("topic_id")
    # Сохранение напоминания в БД
    remind_id = add_reminder(
        chat_id,
        remind_date_time,
        message_text,
        subject_id,
        stage_id,
        section_id,
        topic_id,
    )
    # Вычисление задержки и планирование задачи
    delay = (remind_date_time - now).total_seconds()
    context.job_queue.run_once(
        send_reminder,
        when=delay,
        chat_id=chat_id,
        data={"message": message_text, "reminder_id": remind_id},
        name=str(remind_id),
    )
    await update.message.reply_text(
        f"Напоминание установлено на {remind_date_time.strftime('%Y-%m-%d %H:%M')}"
    )
    await update.message.reply_text(
        "🔙 Возвращаю в личный кабинет...",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🏠 Личный кабинет", callback_data="profile")]]
        ),
    )
    return ConversationHandler.END
