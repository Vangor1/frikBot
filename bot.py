import logging
import asyncio
from datetime import time as dtime, datetime, timedelta
from handlers.start import start
from handlers.schedule import schedule
from telegram import Update
from telegram.ext import (Updater, CommandHandler, 
                          CallbackContext, ContextTypes,
                          ApplicationBuilder) 
from apscheduler.schedulers.background import BackgroundScheduler
from config import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s -%(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO)
logger=logging.getLogger(__name__)

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("schedule", schedule))

    application.run_polling()

if __name__ == '__main__':
    main()    