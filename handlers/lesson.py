import os
import re

import openai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes

import database

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
        f'Ты — учитель английского языка, объясняющий тему "{topic}" '
        f'из раздела "{section}". Ты даёшь подробные, но понятные объяснения, '
        "приводишь примеры и задаёшь простые упражнения для закрепления."
    )
    context.user_data["lesson_reminder_id"] = reminder_id
    context.user_data["gpt_history"] = [{"role": "system", "content": instruction}]
    await update.message.reply_text(f"Начинаем урок по теме: {topic}")


async def lesson_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает сообщения во время урока
    """
    user_message = update.message.text
    history = context.user_data["gpt_history"]
    history.append({"role": "user", "content": user_message})
    responce = client.chat.completions.create(model="gpt-4.1-nano", messages=history)
    answer = responce.choices[0].message.content
    history.append({"role": "assistant", "content": answer})
    await update.message.reply_text(answer)
    return True


async def end_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Завершает урок и сохраняет оценку прогресса
    """
    history = context.user_data.get("gpt_history")
    reminder_id = context.user_data.get("lesson_reminder_id")
    if not history or reminder_id is None:
        await update.message.reply_text("Урок не был начат")
        return
    history.append(
        {
            "role": "user",
            "content": """Оцени мой прогресс по шкале от 0 до 100 и дай короткий
            комментарий используя который ты сможешь
            продолжить урок в следующий раз.""",
        }
    )
    response = client.chat.completions.create(model="gpt-4.1-nano", messages=history)
    result = response.choices[0].message.content
    score_match = re.search(r"(\d{1,3})", result)
    score = int(score_match.group(1)) if score_match else None
    database.add_lesson_progress(reminder_id, update.effective_chat.id, result, score)
    del context.user_data["gpt_history"]
    del context.user_data["lesson_reminder_id"]
    await update.message.reply_text(result)
