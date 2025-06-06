from datetime import datetime

from handlers.choose_subject import choose_subject, handle_choose_subject

# from handlers.cancel import dialogue_cancel
from handlers.list import list_reminders
from handlers.profile import profile
from handlers.schedule.selection_date import WAIT_DATE  # selection_date,
from handlers.schedule.selection_date import (
    choose_section,
    choose_stage,
    choose_subject_for_reminder,
    choose_topic,
)
from handlers.schedule.shedule_start import build_calendar, schedule_start


async def button_callback(update, context):
    """
    Обработка нажатий на кнопки
    """
    query = update.callback_query
    await query.answer()
    data = query.data
    print("DEBUG callback_data in button callback:", data)
    # Обработка нажатий основных кнопок в меню (лист, создание напоминания, профиль)
    if data == "show_list":
        await list_reminders(update, context)
    elif data == "create_reminder":
        await schedule_start(update, context)
    elif data == "profile":
        await profile(update, context)
    # Обработка нажатий в календаре (выбор даты, переходы между месяцами)
    elif data == "PREV_MONTH":
        year = context.user_data["calendar_year"]
        month = context.user_data["calendar_month"]
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
        context.user_data["calendar_month"] = month
        context.user_data["calendar_year"] = year
        markup = build_calendar(year, month)
        await query.edit_message_reply_markup(reply_markup=markup)
        return WAIT_DATE
    elif data == "NEXT_MONTH":
        year = context.user_data["calendar_year"]
        month = context.user_data["calendar_month"]
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        context.user_data["calendar_month"] = month
        context.user_data["calendar_year"] = year
        markup = build_calendar(year, month)
        await query.edit_message_reply_markup(reply_markup=markup)
        return WAIT_DATE
    elif data == "GO_TO_CURRENT_MONTH":
        now = datetime.now()
        year = now.year
        month = now.month
        context.user_data["calendar_month"] = month
        context.user_data["calendar_year"] = year
        markup = build_calendar(year, month)
        await query.edit_message_reply_markup(reply_markup=markup)
        return WAIT_DATE
    elif data.startswith("day_"):
        await choose_subject_for_reminder(update, context)
    # Обработка нажатий в меню выбора предмета
    elif data == "select_subject":
        await choose_subject(update, context)
    elif data.startswith("subjectforchoose_"):
        await handle_choose_subject(update, context)
    elif data.startswith("subjectforreminder_"):
        subject_id = query.data.split("_")[1]
        print("subject----id: ", subject_id)
        context.user_data["subject_id"] = subject_id
        await choose_stage(update, context)
    elif data.startswith("stage_"):
        stage_id = int(query.data.split("_")[1])
        print("stage----id: ", stage_id)
        context.user_data["stage_id"] = stage_id
        await choose_section(update, context)
    elif data.startswith("section_"):
        section_id = int(query.data.split("_")[1])
        print("section----id: ", section_id)
        context.user_data["section_id"] = section_id
        print(context.user_data["section_id"])
        await choose_topic(update, context)
