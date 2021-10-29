"""BAL : robel mezemir ( robi ) <robelmezemir@gmail.com>"""
import dotenv
import logging
from os import getenv
from telegram.ext import Updater
from telegram.ext import CommandHandler

import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

token = dotenv.get_key('.env','TOKEN') or getenv('TOKEN')

updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="hi there ... create an account ig ")


def main():
    "Main Execution"
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    updater.start_polling()
    
if __name__ == '__main__':
    main()
