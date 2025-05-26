from telegram import Update
from telegram.ext import ContextTypes

from database import add_user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /start — приветствует пользователя,
    регает его в БД и объясняет, что делать дальше
    """
    user = update.effective_user
    add_user(
        user.id,
        user.first_name,
        user.last_name or "",
        user.username or "",
    )
    await update.message.reply_text(
        f"Дарова, {user.first_name}! Я фрик!\n"
        "Отправь /profile для отображения личного кабинета\n"
    )
