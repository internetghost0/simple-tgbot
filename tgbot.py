#!/usr/bin/env python
# pylint: disable=unused-argument

import logging
import psutil
import subprocess
import PIL.ImageGrab
from io import BytesIO

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

reply_keyboard = [

    ["/screenshot", "/processes"],

    ["/vscode", "/chrome"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f'/start from id: {update.message.from_user.id}')
    await update.message.reply_text("Привет, это help bot, жду команду..", reply_markup=markup)

async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f'/screenshot from id: {update.message.from_user.id}')
    im = PIL.ImageGrab.grab()

    # BytesIO because no need to save file
    bio = BytesIO()
    bio.name = 'screenshot.png'
    im.save(bio, 'PNG')
    bio.seek(0)

    await update.message.reply_photo(bio)

async def list_processes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f'/processes from id: {update.message.from_user.id}')
    result = ''
    for proc in psutil.process_iter():
        try:
            result += f'{str(proc.pid).zfill(6)} ::: {proc.name()}\n'
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    await send_long_text(update, result)

async def open_vscode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f'/vscode from id: {update.message.from_user.id}')
    subprocess.run(["codium"])

async def open_chrome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f'/chrome from id: {update.message.from_user.id}')
    subprocess.run(["chromium"])

async def send_long_text(update: Update, text) -> None:
    limit = 3000
    for i in range(0, len(text), limit):
        await update.message.reply_text(text[i:i+limit] )

def main() -> None:

    application = Application.builder().token("TOKEN").build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('screenshot', screenshot))
    application.add_handler(CommandHandler('processes', list_processes))
    application.add_handler(CommandHandler('vscode', open_vscode))
    application.add_handler(CommandHandler('chrome', open_chrome))


    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
