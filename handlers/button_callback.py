from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from handlers.choose_subject import choose_subject, handle_choose_subject
from handlers.lesson import end_lesson

from handlers.list import list_reminders
from handlers.profile import profile
from handlers.schedule.selection_date import (
    can_open_next_stage,
    choose_section,
    choose_stage,
    choose_subject_for_reminder,
    choose_topic,
    not_can_open_next_stage,
    WAIT_DATE
)
from handlers.schedule.sсhedule_start import build_calendar, schedule_start


def parse_callback_data(raw: str) -> dict:
    """
    Парсит строки
    """
    params = {}
    for part in raw.split(";"):
        if "=" in part:
            key, val = part.split("=", 1)
            params[key] = val
    return params

async def _go_to_month(update:Update, context: ContextTypes.DEFAULT_TYPE, year: int, month:int):
    """
    Отрисовка месяца календаря
    """
    context.user_data["calendar_month"] = month
    context.user_data["calendar_year"] = year
    markup = build_calendar(year, month)
    await update.callback_query.edit_message_reply_markup(reply_markup=markup)
    return WAIT_DATE

async def _prev_month(update:Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Переход на предыдущий месяц
    """
    year = context.user_data["calendar_year"]
    month = context.user_data["calendar_month"]
    if month == 1:
        month = 12
        year -= 1        
    else:
        month -= 1
    return await _go_to_month(update, context, year, month)

async def _next_month(update:Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Переход на следующий месяц
    """
    year = context.user_data["calendar_year"]
    month = context.user_data["calendar_month"]
    if month == 12:
        month = 1
        year += 1
    else:
        month += 1
    return await _go_to_month(update, context, year, month)

async def _current_month(update:Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Вернуться к текущему месяцу
    """
    now = datetime.now()
    return _go_to_month(update, context, now.year, now.month)

async def _subject_for_reminder(update:Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выбор предмета при создании занятия
    """
    subject_id = update.callback_query.data.split("_")[1]
    context.user_data["subject_id"] = subject_id
    await choose_stage(update, context)


async def _stage(update:Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выбор этапа
    """
    stage_id = int(update.callback_query.data.split("_")[1])
    context.user_data["stage_id"] = stage_id
    if can_open_next_stage(update.callback_query.from_user.id, context):
        await choose_section(update, context)
    else:
        await not_can_open_next_stage(update, context)

async def _section(update:Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выбор раздела
    """
    section_id = int(update.callback_query.data.split("_")[1])
    context.user_data["section_id"] = section_id
    await choose_topic(update, context)

DATA_HANDLERS ={
    "show_list": list_reminders,
    "create_reminder": schedule_start,
    "profile": profile,
    "PREV_MONTH": _prev_month,
    "NEXT_MONTH": _next_month,
    "GO_TO_CURRENT_MONTH": _go_to_month,
    "end_lesson": end_lesson,
    "select_subject": choose_subject,
}
async def button_callback(update, context):
    """
    Обработка нажатий на кнопки
    """
    query = update.callback_query
    await query.answer()
    data = query.data
    print("DEBUG callback_data in button callback:", data)
    if data == "IGNORE":
        return
    handler = DATA_HANDLERS.get(data)
    if handler:
        return await handler(update, context)
    if data.startswith("day_"):
        await choose_subject_for_reminder(update, context)
    elif data.startswith("subjectforchoose_"):
        await handle_choose_subject(update, context)
    elif data.startswith("subjectforreminder_"):
        await _subject_for_reminder(update, context)
    elif data.startswith("stage_"):
        await _stage(update, context)
    elif data.startswith("section_"):
        await _section(update, context)

