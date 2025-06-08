import logging
import os
from datetime import datetime

import openai
from dotenv import load_dotenv
from telegram import BotCommand
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from data.study_structure.English import English
from database import get_pending_reminders, init_db, sync_study_structure
from handlers.button_callback import button_callback
from handlers.cancel import cancel
from handlers.lesson import end_lesson, lesson_chat, start_lesson
from handlers.profile import profile
from handlers.schedule.selection_date import REQUEST_TEXT, receive_text, selection_date
from handlers.schedule.shedule_send import send_reminder
from handlers.start import start

# Настройка логирования для удобства отладки и мониторинга
logging.basicConfig(
    format="%(asctime)s -%(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


# Установка доступных команд для бота (отображаются в интерфейсе Telegram)
async def set_bot_commands(app: Application):
    """
    Установка всплывающих подсказок команд
    """
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("profile", "Личный кабинет"),
    ]
    await app.bot.set_my_commands(commands)


def main():

    # Инициализация бд
    init_db()
    application = (
        ApplicationBuilder().token(BOT_TOKEN).post_init(set_bot_commands).build()
    )
    sync_study_structure(English)
    application.add_handler(CommandHandler("end_lesson", end_lesson))
    application.add_handler(
        MessageHandler(filters.Regex(r"^/lesson_\\d+$"), start_lesson)
    )
    # Обработка сообщений во время урока
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, lesson_chat)
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex(r"^/cancel_\d+$"), cancel)
    )
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(selection_date, pattern="^topic_")],
        states={
            REQUEST_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text)
            ],
        },
        fallbacks=[CommandHandler("profile", profile)],
    )
    application.add_handler(conv_handler)
    # При старте подгружаются все отложенные задачи
    for rem_id, chat_id, remind_time, message in get_pending_reminders():
        # Вычисляется задержка до момента времени напоминание (remind_time)
        delay = (remind_time - datetime.now()).total_seconds()
        if delay < 0:
            delay = 0  # Если время прошло - отправить сразу
        application.job_queue.run_once(
            send_reminder,
            when=delay,
            chat_id=chat_id,
            data={"message": message, "reminder_id": rem_id},
        )
    application.add_handler(
        CallbackQueryHandler(button_callback)
    )  # Обработка нажатий на кнопки
    application.run_polling()


if __name__ == "__main__":
    main()
