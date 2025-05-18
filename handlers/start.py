from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /start — приветствует пользователя и объясняет, что делать дальше
    """
    user = update.effective_user
    await update.message.reply_text(
        f"Дарова, {user.first_name}! Я фрик"
        "Отправь /schedule ЧЧ:ММ Текст собщения для установления напоминания"
    )
