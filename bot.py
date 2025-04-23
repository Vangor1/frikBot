import logging
from datetime import datetime
from handlers.start import start
from handlers.schedule import (schedule, send_reminder)
from telegram import Update
import db
from telegram.ext import (CommandHandler, ApplicationBuilder) 
from apscheduler.schedulers.background import BackgroundScheduler
from config import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s -%(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO)
logger=logging.getLogger(__name__)

def main():
    db.init_db()

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("schedule", schedule))

    for rem_id, chat_id, remind_time, message in db.get_pending_reminders():
        delay=(remind_time-datetime.now()).total_seconds()
        if delay<0:
            delay=0
    application.job_queue.run_once(
        send_reminder,
        when=delay,
        chat_id=chat_id,
        data={'message': message, 'reminder_id':rem_id}
    )
    application.run_polling()

if __name__ == '__main__':
    main()    