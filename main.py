"""BAL : robel mezemir ( robi ) <robelmezemir@gmail.com>"""
import json
import dotenv
import logging
import urllib3
from os import getenv

from telegram import ParseMode
from telegram import InlineQueryResultDocument
from telegram.ext import Updater 
from telegram.ext import CommandHandler 
from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.database import Database
from appwrite.exception import AppwriteException

from jikanpy import Jikan
jikan = Jikan()

import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

TOKEN = dotenv.get_key('.env','TOKEN') or getenv('TOKEN')
# COLLECTIONID = dotenv.get_key('.env','COLLECTIONID') or getenv('COLLECTIONID')
ENDPOINT = dotenv.get_key('.env','ENDPOINT') or getenv('ENDPOINT')
PROJECTID = dotenv.get_key('.env','PROJECTID') or getenv('PROJECTID')
APIKEY = dotenv.get_key('.env','APIKEY') or getenv('APIKEY')

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


client = Client()

(client
  .set_endpoint(F'http://{ENDPOINT}/v1') # Your API Endpoint
  .set_project(PROJECTID) # Your project ID
  .set_key(APIKEY) # Your secret API key
)
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
users = Users(client)
database = Database(client)


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="hi there ... create an account with /create_account ")

def create_account(update,context):
    user_id  = update.effective_user.id
    try :
        result = users.create(f'{user_id}@gmail.com',password=f'{user_id}')
        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=result)
    except AppwriteException as err:
        logging.error(err)
        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="Already registered")
def anime_search(update,context):
    if context.args :
        query = context.args
    else: 
        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="usage : /anime_search {query}")

    search_result = jikan.search('anime', query=query, parameters={'limit':5})
    search_result = search_result['results']
    print(search_result)
    for anime in search_result :
        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text= str(anime['mal_id']) + " " + anime['title'] )

def anime(update,context):
    query = context.args
    print(query)
    try:
        anime = jikan.anime(int(query[0]))
        print(anime)
        syn = anime['synopsis']
        caption = f"<b>{anime['title']}</b> - <b>{anime['title_japanese']}</b>\n"
        caption = caption + f"Type : <i>{anime['type']}</i>\n"
        caption = caption + '\n\n'
        caption = caption + f"Episodes : <code>{anime['episodes']}</code>\nSynopsis : "
        caption = caption + syn[:200] + (syn[200:] and '...')

        context.bot.send_photo(
            photo=f'{anime["image_url"]}',
            chat_id=update.effective_chat.id,
            caption=  caption,
            parse_mode=ParseMode.HTML)

    except TypeError as err :
        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=(f'{err}'
                "/anime is used with the numerical id of the anime \n"
                "use /anime_search if you are not sure of the id ."))

    # winter_2018_anime = jikan.season(year=2018, season='winter')
    # archive = jikan.season_archive()


def list_accounts(update,context):
    result = users.list()
    context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=result)
    
result = database.create_collection('[NAME]', [], [], [])



def main():
    "Main Execution"
    start_handler = CommandHandler('start', start)
    create_account_handler = CommandHandler('create_account', create_account)
    list_accounts_handler = CommandHandler('list_accounts', list_accounts)
    anime_search_handler = CommandHandler('anime_search', anime_search)
    anime_handler = CommandHandler('anime', anime)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(create_account_handler)
    dispatcher.add_handler(list_accounts_handler)
    dispatcher.add_handler(anime_search_handler)
    dispatcher.add_handler(anime_handler)
    
    updater.start_polling()
    
if __name__ == '__main__':
    main()
