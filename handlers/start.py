from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user =update.effective_user
    await update.message.reply_text(f"Дарова, {user.first_name}! Я фрик"
                              "Отправь /schedule ЧЧ:ММ Текст собщения для установления напоминания")