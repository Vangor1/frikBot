import logging
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import db

logger = logging.getLogger(__name__)
# Переменная состояния разговора
WAIT_INPUT = 1


async def schedule_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Точка входа ConversationHandler для /schedule
    Запрашиваем время и текст
    """
    try:
        # парсинг времени и текст
        time_str = context.args[0]  # "HH:MM"
        message_text = " ".join(context.args[1:])
        remind_time = datetime.strptime(time_str, "%H:%M").time()
        record_reminder(remind_time, message_text, update, context)
        await update.message.reply_text(f"Напомининание установлено на {remind_time}")
        return ConversationHandler.END
    except (IndexError, ValueError):
        await update.message.reply_text(
            "Пожалуйста, введите время и текст напоминания в форме: \n"
            "ЧЧ:ММ Текст\n"
            "Или /cancel для отмены"
        )
        return WAIT_INPUT


async def schedule_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Получаем строку и пытаемся распарсарсить.
    Если всё ок сейвим и планируем, иначе просим повторить
    """
    text = update.message.text.strip()
    if " " not in text:
        await update.message.reply_text("Неправильно, попробуй ещё раз.")
        return WAIT_INPUT
    time_str, message_text = text.split(" ", 1)
    try:
        remind_time = datetime.strptime(time_str, "%H:%M").time()
    except (IndexError, ValueError):
        await update.message.reply_text("Неправильно, попробуй ещё раз.")
        return WAIT_INPUT
    record_reminder(remind_time, message_text, update, context)
    return ConversationHandler.END


async def schedule_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    /cancel - внутри диалога прерывает диалог
    """
    await update.message.reply_text("Установка напоминания отменена")
    return ConversationHandler.END


async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает команду /schedule
    Сохраняет напоминание в БД и ставит в очередь
    """
    try:
        # парсинг времени и текст
        time_str = context.args[0]  # "HH:MM"
        message_text = " ".join(context.args[1:])
        remind_time = datetime.strptime(time_str, "%H:%M").time()
    except (IndexError, ValueError):
        await update.message.reply_text("Неверный формат")
        return

    now = datetime.now()
    remind_datetime = datetime.combine(now.date(), remind_time)
    if remind_datetime <= now:  # Если время прошло переносится на следующий день
        remind_datetime += timedelta(days=1)
    chat_id = update.effective_chat.id
    # Сохранение напоминания в БД
    remind_id = db.add_reminder(chat_id, remind_datetime, message_text)
    # Вычисление задержки и планирование задачи
    delay = (remind_datetime - now).total_seconds()
    context.job_queue.run_once(
        send_reminder,
        when=delay,
        chat_id=chat_id,
        data={"message": message_text, "reminder_id": remind_id},
    )

    await update.message.reply_text(f"Напомининание установлено на {remind_time}")


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """
    Функция коллбэк, вызываемая планировщиком
    Отправляет напоминание и удаляет запись из БД
    """
    job = context.job
    chat_id = job.chat_id
    message_text = job.data.get("message")
    remind_id = job.data.get("reminder_id")
    try:  # Отправка пользователю текст напоминания
        await context.bot.send_message(
            chat_id=chat_id, text=f"Напоминание: {message_text}"
        )
        # Удаление записи из бд чтоб повторно не сработало
        if remind_id is not None:
            db.delete_reminder(remind_id)
    except Exception as e:
        logger.error(f"Ошибка {e} при отправке напоминания {message_text}")


async def record_reminder(
    remind_time, message_text, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """ """
    now = datetime.now()
    remind_datetime = datetime.combine(now.date(), remind_time)
    if remind_datetime <= now:  # Если время прошло переносится на следующий день
        remind_datetime += timedelta(days=1)
    chat_id = update.effective_chat.id
    # Сохранение напоминания в БД
    remind_id = db.add_reminder(chat_id, remind_datetime, message_text)
    # Вычисление задержки и планирование задачи
    delay = (remind_datetime - now).total_seconds()
    context.job_queue.run_once(
        send_reminder,
        when=delay,
        chat_id=chat_id,
        data={"message": message_text, "reminder_id": remind_id},
    )
