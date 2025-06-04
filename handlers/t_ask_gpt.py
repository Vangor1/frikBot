import os

import openai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def start_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши мне сообщение, и я спрошу ChatGPT.")


async def ask_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = client.chat.completions.create(
        model="gpt-4.1-nano", messages=[{"role": "user", "content": user_message}]
    )
    gpt_reply = response.choices[0].message.content
    await update.message.reply_text(gpt_reply)
