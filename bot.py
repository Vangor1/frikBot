import logging
from datetime import datetime
from handlers.start import start
from handlers.schedule import (schedule, send_reminder)
from handlers.list import list_reminders
from handlers.cancel import cancel
import db
from telegram import BotCommand
from telegram.ext import (CommandHandler, ApplicationBuilder,
                          Application)
from config import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s -%(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO)
logger=logging.getLogger(__name__)
async def set_bot_commands(app:Application):
    """
    Установка всплывающих подсказок команд
    """
    commands= [
        BotCommand('start', 'Запустить бота'),
        BotCommand('schedule', 'Установить напоминание'),
        BotCommand('list','Показать все напоминания'),
        BotCommand('cancel','Отменить напоминание по ID')
    ]
    await app.bot.set_my_commands(commands)
def main():
    #Инициализация бд
    db.init_db()
    #Псотройка приложения и регистрация команд
    application = ApplicationBuilder().token(BOT_TOKEN).post_init(set_bot_commands).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("schedule", schedule))
    application.add_handler(CommandHandler("list", list_reminders))
    application.add_handler(CommandHandler("cancel", cancel))
    #При старте подгружаются все отложенные задачи
    for rem_id, chat_id, remind_time, message in db.get_pending_reminders():
        #Вычисляется задержка до момента времени напоминание (remind_time)
        delay=(remind_time-datetime.now()).total_seconds()
        if delay<0:
            delay=0 #Если время прошло - отправить сразу
        application.job_queue.run_once(
            send_reminder,
            when=delay,
            chat_id=chat_id,
            data={'message': message, 'reminder_id':rem_id}
        )
    application.run_polling()

if __name__ == '__main__':
    main()    