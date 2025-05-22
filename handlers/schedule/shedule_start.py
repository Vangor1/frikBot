import calendar
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


async def schedule_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Точка входа для установки напоминания — выводит календарь
    """
    query = update.callback_query
    await query.answer()
    now = datetime.now()
    year = now.year
    month = now.month
    context.user_data["calendar_month"] = month
    context.user_data["calendar_year"] = year
    markup = build_calendar(year, month)
    await query.edit_message_text("Выберите дату", reply_markup=markup)


def build_calendar(year: int, month: int) -> InlineKeyboardMarkup:
    """
    Генерирует inline-календарь для выбора даты с навигацией по месяцам
    Прошедшие даты отмечаются неактивными точками
    """
    cal = calendar.monthcalendar(year, month)
    now = datetime.now()
    today = now.date()
    keyboard = []
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(
                    InlineKeyboardButton(" ", callback_data="IGNORE")
                )  # пустая ячейка
            else:
                date = datetime(year, month, day).date()
                if date < today:
                    row.append(
                        InlineKeyboardButton("·", callback_data="IGNORE")
                    )  # неактивная дата
                else:
                    row.append(
                        InlineKeyboardButton(str(day), callback_data=f"day_{day}")
                    )
        keyboard.append(row)
    # Добавляем кнопки для навигации по месяцам
    nav_row = [
        InlineKeyboardButton("<<", callback_data="PREV_MONTH"),
        InlineKeyboardButton("Текущий месяц", callback_data="GO_TO_CURRENT_MONTH"),
        InlineKeyboardButton(">>", callback_data="NEXT_MONTH"),
    ]
    # Информация о месяце и кнопка отмены
    info_row = [
        InlineKeyboardButton(
            f"{calendar.month_abbr[month]} {year}", callback_data="IGNORE"
        ),
        InlineKeyboardButton("🔙 В личный кабинет", callback_data="profile"),
    ]
    keyboard.append(nav_row)
    keyboard.append(info_row)
    return InlineKeyboardMarkup(keyboard)
