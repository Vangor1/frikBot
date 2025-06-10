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
from handlers.schedule.schedule_start import build_calendar, schedule_start
import utils

async def _go_to_month(update: Update, context: ContextTypes.DEFAULT_TYPE, year: int, month:int):
    """
    Отрисовка месяца календаря
    """
    context.user_data["calendar_month"] = month
    context.user_data["calendar_year"] = year
    markup = build_calendar(year, month)
    await update.callback_query.edit_message_reply_markup(reply_markup=markup)
    return WAIT_DATE

async def _prev_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def _next_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def _current_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Вернуться к текущему месяцу
    """
    now = datetime.now()
    return await _go_to_month(update, context, now.year, now.month)

async def _subject_for_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выбор предмета при создании занятия
    """
    params = utils.parse_callback_data(update.callback_query.data)
    subject_id = int(params.get("id", 0))
    context.user_data["subject_id"] = subject_id
    await choose_stage(update, context)


async def _stage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выбор этапа
    """
    params = utils.parse_callback_data(update.callback_query.data)
    stage_id = int(params.get("id", 0))
    #stage_id = int(update.callback_query.data.split("_")[1])
    context.user_data["stage_id"] = stage_id
    if can_open_next_stage(update.callback_query.from_user.id, context):
        await choose_section(update, context)
    else:
        await not_can_open_next_stage(update, context)

async def _section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выбор раздела
    """
    params = utils.parse_callback_data(update.callback_query.data)
    section_id = int(params.get("id", 0))
    #section_id = int(update.callback_query.data.split("_")[1])
    context.user_data["section_id"] = section_id
    await choose_topic(update, context)

DATA_HANDLERS ={
    "show_list": list_reminders,
    "create_reminder": schedule_start,
    "profile": profile,
    "PREV_MONTH": _prev_month,
    "NEXT_MONTH": _next_month,
    "GO_TO_CURRENT_MONTH": _current_month,
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
    params = utils.parse_callback_data(update.callback_query.data)
    cmd = params.get("cmd")
    if cmd =="day":
        await choose_subject_for_reminder(update, context)
    elif cmd=="subjectforchoose":
        await handle_choose_subject(update, context)
    elif cmd=="subjectforreminder":
        await _subject_for_reminder(update, context)
    elif cmd=="stage":
        await _stage(update, context)
    elif cmd == "section":
        await _section(update, context)