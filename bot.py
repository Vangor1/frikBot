import logging
from datetime import datetime

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

import db
from config import BOT_TOKEN
from data.study_structure.English import English
from handlers.button_callback import button_callback
from handlers.cancel import cancel
from handlers.profile import profile
from handlers.schedule.selection_date import REQUEST_TEXT, receive_text, selection_date
from handlers.schedule.shedule_send import send_reminder
from handlers.start import start

# Настройка логирования для удобства отладки и мониторинга
logging.basicConfig(
    format="%(asctime)s -%(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


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
    db.init_db()
    application = (
        ApplicationBuilder().token(BOT_TOKEN).post_init(set_bot_commands).build()
    )
    db.sync_study_structure(English)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex(r"^/cancel_\d+$"), cancel)
    )
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(selection_date, pattern="^day_")],
        states={
            REQUEST_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text)
            ],
        },
        fallbacks=[CommandHandler("profile", profile)],
    )
    application.add_handler(conv_handler)
    # При старте подгружаются все отложенные задачи
    for rem_id, chat_id, remind_time, message in db.get_pending_reminders():
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
