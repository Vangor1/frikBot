import logging
import os
import re

import openai
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import database

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = logging.getLogger(__name__)


async def start_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Начинает диалог урока по команде /lesson_<reminder_id>
    """
    m = re.match(r"/lesson_(\d+)", update.message.text)
    if not m:
        await update.message.reply_text("Неверная команда")
        return
    reminder_id = int(m.group(1))
    details = database.get_reminder_details(reminder_id)
    if not details:
        await update.message.reply_text("Занятие не найдено")
        return
    topic = details.get("topic_name") or ""
    section = details.get("section_name") or ""
    instruction = (
        f"Ты — учитель английского языка в чате. Сегодня мы разбираем тему «{topic}» из раздела «{section}». " #noqa: E501
        "Ответ всегда должен строго соответствовать следующей структуре:\n" #noqa: E501
        "1) Приветствие;\n"
        "2) Краткое введение в тему;\n"
        "3) Лексика (новые слова и выражения с переводом на русский);\n"
        "4) Примеры предложений на английском и русском;\n"
        "5) Простые упражнения для закрепления.\n"
        "Ни при каких условиях не выходи за рамки указанной темы и раздела, отвечай только по сути и в заданном формате." #noqa: E501
    )
    context.user_data["lesson_reminder_id"] = reminder_id
    context.user_data["gpt_history"] = [{"role": "system", "content": instruction}]
    if reminder_id is not None:
        database.delete_reminder(reminder_id)
    await update.message.reply_text(f"Начинаем урок по теме: {topic}")


async def lesson_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает сообщения во время урока
    """
    if "gpt_history" not in context.user_data:
        return
    user_message = update.message.text
    history = context.user_data["gpt_history"]
    history.append({"role": "user", "content": user_message})
    try:
        responce = client.chat.completions.create(
            model="gpt-4.1-nano", messages=history
        )
    except Exception as exc:
        logger.exception("Ошибка при обращении к OpenAI", exc_info=exc)
        await update.message.reply_text(
            "Произошла ошибка при обращении к сервису. Попробуйте позже."
        )
        return
    answer = responce.choices[0].message.content
    history.append({"role": "assistant", "content": answer})
    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Завершить урок",
                    callback_data="end_lesson",
                ),
            ],
        ]
    )
    await update.message.reply_text(answer, reply_markup=markup, parse_mode="Markdown")
    return True


async def end_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Завершает урок и сохраняет оценку прогресса
    """
    query = update.callback_query
    message = query.message if query else update.message
    if query:
        await query.answer()
    logger.info("Запущен end_lesson")
    history = context.user_data.get("gpt_history")
    reminder_id = context.user_data.get("lesson_reminder_id")
    if not history or reminder_id is None:
        await message.reply_text("Урок не был начат")
        return
    history.append(
        {
            "role": "user",
            "content": "Оцени мой прогресс по шкале от 0 до 100 и дай короткий комментарий используя который ты сможешь продолжить урок в следующий раз.", #noqa: E501
        }
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano", messages=history
        )
    except Exception as exc:
        logger.exception("Ошибка при обращении к OpenAI", exc_info=exc)
        await message.reply_text(
            "Произошла ошибка при обращении к сервису. Попробуйте позже."
        )
        return
    result = response.choices[0].message.content
    score_match = re.search(r"(\d{1,3})", result)
    score = int(score_match.group(1)) if score_match else None
    database.add_lesson_progress(reminder_id, update.effective_chat.id, result, score)
    details = database.get_reminder_details(reminder_id)
    topic_id = details.get("topic_id")
    section_id = details.get("section_id")
    user_id = update.effective_chat.id
    if score is not None and topic_id:
        database.set_user_topic_grade(user_id, topic_id, score)
        avg = database.get_average_grade(user_id, section_id)
        if avg is not None:
            database.set_user_section_grade(user_id, section_id, int(avg))
    del context.user_data["gpt_history"]
    del context.user_data["lesson_reminder_id"]
    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "В профиль",
                    callback_data="profile",
                ),
            ],
        ]
    )
    await message.reply_text(result, reply_markup=markup, parse_mode="Markdown")
