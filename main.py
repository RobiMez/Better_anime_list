"""BAL : robel mezemir ( robi ) <robelmezemir@gmail.com>"""
import json
import dotenv
import logging
from requests.models import parse_header_links
import urllib3
from os import getenv

from telegram import ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.database import Database
from appwrite.exception import AppwriteException

from jikanpy import Jikan
from jikanpy.exceptions import APIException
jikan = Jikan()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

TOKEN = dotenv.get_key('.env', 'TOKEN') or getenv('TOKEN')
COLLECTIONID = dotenv.get_key('.env', 'COLLECTIONID') or getenv('COLLECTIONID')
ENDPOINT = dotenv.get_key('.env', 'ENDPOINT') or getenv('ENDPOINT')
PROJECTID = dotenv.get_key('.env', 'PROJECTID') or getenv('PROJECTID')
APIKEY = dotenv.get_key('.env', 'APIKEY') or getenv('APIKEY')

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


client = Client()

(client
 .set_endpoint(F'http://{ENDPOINT}/v1')  # Your API Endpoint
 .set_project(PROJECTID)  # Your project ID
 .set_key(APIKEY)  # Your secret API key
 )
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
users = Users(client)
database = Database(client)


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="hi there ... create an account with /create_account ")


def create_account(update, context):
    user_id = update.effective_user.id
    try:
        result = users.create(f'{user_id}@gmail.com', password=f'{user_id}')
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=result)
    except AppwriteException as err:
        logging.error(err)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Already registered")


def anime_search(update, context):
    print('pew')
    if context.args:
        print('pow')
        query = context.args
        search_result = jikan.search(
            'anime', query=query, parameters={'limit': 5})
        search_result = search_result['results']
        print(search_result)
        for anime in search_result:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"[ <code>{str(anime['mal_id'])}</code> ] <i>{anime['title']}</i>",
                parse_mode=ParseMode.HTML)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="usage : /anime_search {query}")


def anime(update, context):
    query = context.args
    if len(query) > 0:
        try:
            anime = jikan.anime(int(query[0]))
            print(anime)
            syn = anime['synopsis']
            caption = f"<b>{anime['title']}</b> - <b>{anime['title_japanese']}</b>\n"
            caption = caption + f"Type : <i>{anime['type']}</i>\n"
            caption = caption + '\n\n'
            caption = caption + \
                f"Episodes : <code>{anime['episodes']}</code>\nSynopsis : "
            caption = caption + syn[:200] + (syn[200:] and '...')
            ck = [
                [
                    InlineKeyboardButton(
                        'Add to List',
                        callback_data=f"add_to_list-{int(query[0])}")],
            ]
            reply_markup = InlineKeyboardMarkup(ck)

            context.bot.send_photo(
                photo=f'{anime["image_url"]}',
                chat_id=update.effective_chat.id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup)

        except APIException as err:
            print(err)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f"Could not find an anime with id {int(query[0])} \n"
                    "Use /anime_search to double check the id."))
        except TypeError and ValueError as err:
            print(err)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    "/anime is used with a numeric id.\n"
                    "Use /anime_search if you are not sure of a specific series' id ."))
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Usage : /anime {id} ')


def choose_state(update, context, mal_id, doc_id=0):
    ck = [
        [
            InlineKeyboardButton(
                'Watching',
                callback_data=f"state-Watching-{mal_id}"),
            InlineKeyboardButton(
                'Completed',
                callback_data=f"state-Completed-{mal_id}")],
        [
            InlineKeyboardButton(
                'On Hold',
                callback_data=f"state-On_Hold-{mal_id}"),
            InlineKeyboardButton(
                'Dropped',
                callback_data=f"state-Dropped-{mal_id}")],
        [
            InlineKeyboardButton(
                'Plan To Watch',
                callback_data=f"state-Plan_To_Watch-{mal_id}")],

    ]
    reply_markup = InlineKeyboardMarkup(ck)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"what is the state of this anime?\n\n"
        ), parse_mode=ParseMode.HTML,
        reply_markup=reply_markup)


def update_state(update, context, mal_id, doc_id=0):
    ck = [
        [
            InlineKeyboardButton(
                'Watching',
                callback_data=f"state-Watching-{mal_id}"),
            InlineKeyboardButton(
                'Completed',
                callback_data=f"state-Completed-{mal_id}")],
        [
            InlineKeyboardButton(
                'On Hold',
                callback_data=f"state-On_Hold-{mal_id}"),
            InlineKeyboardButton(
                'Dropped',
                callback_data=f"state-Dropped-{mal_id}")],
        [
            InlineKeyboardButton(
                'Plan To Watch',
                callback_data=f"state-Plan_To_Watch-{mal_id}")],

    ]
    reply_markup = InlineKeyboardMarkup(ck)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"what is the state of this anime?\n\n"
        ), parse_mode=ParseMode.HTML,
        reply_markup=reply_markup)


def set_state(update, context):
    """
        Updates the database state and id,
        generally handles the insert and update side of things 
    """

    user_id = update.effective_user.id
    cqd = update.callback_query.data
    state = str(cqd.split('-')[1])
    mal_id = int(cqd.split('-')[-1])

    exists = database.list_documents(
        COLLECTIONID,
        filters=[f'userID={user_id}'])

    if exists['sum'] == 0:
        print('Data not found , create ')
        # been deleted or never existed
        payload = {
            "userID": user_id,
            "MalList": [mal_id],
            "state": [state]
        }
        database.create_document(COLLECTIONID, payload)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Successfully added {mal_id} to list ')
    else:
        # data exists , update
        print('Data exists , update ')
        doc_id = exists['documents'][0]['$id']
        print(exists)
        try:
            if mal_id in exists['documents'][0]['MalList']:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'{mal_id} is already on your list')
        except KeyError:
            # we dont have a mal list
            payload = {
                "userID": user_id,
                "MalList": [mal_id],
                "state": [state]
            }
            exists = database.list_documents(
                COLLECTIONID,
                filters=[f'userID={user_id}'])
            if exists['sum'] == 0:
                result = database.create_document(COLLECTIONID, payload)
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'Successfully added {mal_id} to list ')
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'already added {mal_id} to list ')
        else:
            print(doc_id)
            # update existing doc
            malist = list(exists['documents'][0]['MalList'])
            new_state = list(exists['documents'][0]['state'])
            new_state.append(str(state))
            malist.append(int(mal_id))
            payload = {
                "userID": user_id,
                "MalList": malist,
                "state": new_state
            }
            updated = database.update_document(
                COLLECTIONID,
                doc_id,
                payload)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'updated list with {mal_id}')
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=updated)


def delete_item(update, context):
    """
        deletes entry 
    """
    user_id = update.effective_user.id
    if not len(context.args) == 1:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Usage : /delete {id} ')
    else:
        # id of anime in question
        try:
            mal_id = int(context.args[0])
            # if doesnt exist ... ignore
            docs = database.list_documents(
                COLLECTIONID,
                filters=[f'userID={user_id}'])
            print(docs)
            if len(docs['documents']) == 0:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Nothing in your list to delete , start adding more via /anime.",
                    parse_mode=ParseMode.HTML)
            else:
                docs = docs['documents'][0]  # there should only be one doc
                doc_id = docs['$id']
                print(docs)
                mal_ids = docs['MalList']
                statuses = docs['state']
                print(mal_ids)
                print(statuses)
                last_items = len(mal_ids) == 1 and len(statuses) == 1
                correct_item = mal_id == mal_ids[0]
                if last_items and correct_item:
                    # delete the whole document as its the last item
                    database.delete_document(COLLECTIONID, doc_id)
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Removed {mal_id} From your list , List is now empty .",
                        parse_mode=ParseMode.HTML)
                elif not correct_item:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"{mal_id} isnt in your list ",
                        parse_mode=ParseMode.HTML)
                else:
                    pass
                    # update the doc and remove id
        except ValueError:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Usage : /delete {id} ')


def update_item(update, context):
    """
        updates entry state
    """
    user_id = update.effective_user.id
    user_id = update.effective_user.id
    if not len(context.args) == 1:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Usage : /update {id} ')
    else:
        try:
            mal_id = int(context.args[0])
            # if doesnt exist ... ignore
            choose_state(update, context, mal_id)
        except ValueError:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Usage : /update {id} ')


def add(update, context):
    user_id = update.effective_user.id
    cqd = update.callback_query.data
    mal_id = int(cqd.split('-')[-1])
    print(cqd)
    choose_state(update, context, mal_id)


def list_list(update, context):
    """
        Parses the documents in the users collection and displays 
        the users anime list , add support for images later 
    """
    user_id = update.effective_user.id

    docs = database.list_documents(
        COLLECTIONID,
        filters=[f'userID={user_id}'])

    if len(docs['documents']) == 0:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No items in your list , start adding them via /anime.",
            parse_mode=ParseMode.HTML)
    else:
        docs = docs['documents'][0]  # there should only be one doc
        print(docs)
        mal_ids = docs['MalList']
        statuses = docs['state']
        anime_list = '<i><b> Your list : </b></i>\n\n'
        i = 0
        for id in mal_ids:
            anime = jikan.anime(int(id))
            anime_list = anime_list + f'[ <code>{anime["mal_id"]}</code> ] '
            anime_list = anime_list + f'<b>{anime["title"]}</b>\n'
            anime_list = anime_list + f'State : {statuses[i]}\n\n'
            anime_list = anime_list + f'Status : {anime["status"]}\n'
            anime_list = anime_list + f'Episodes : {anime["episodes"]}\n'
            genres = [genre['name'] for genre in anime['genres']]
            genre_string = ""
            for genre in genres:
                genre_string = genre_string + f" {genre} ,"
            anime_list = anime_list + f'Genres : {genre_string[0:-1]}\n'
            anime_list = anime_list + '\n'
            print(anime)
            i += 1
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=anime_list,
            parse_mode=ParseMode.HTML)


def main():
    "Main Execution"
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    delete_handler = CommandHandler('delete', delete_item)
    dispatcher.add_handler(delete_handler)

    list_handler = CommandHandler('list', list_list)
    dispatcher.add_handler(list_handler)

    create_account_handler = CommandHandler('create_account', create_account)
    dispatcher.add_handler(create_account_handler)

    anime_search_handler = CommandHandler('anime_search', anime_search)
    dispatcher.add_handler(anime_search_handler)

    anime_handler = CommandHandler('anime', anime)
    dispatcher.add_handler(anime_handler)

    add_to_list = CallbackQueryHandler(add, pattern=r"add_to_list")
    dispatcher.add_handler(add_to_list)

    state = CallbackQueryHandler(set_state, pattern=r"state")
    dispatcher.add_handler(state)

    updater.start_polling()


if __name__ == '__main__':
    main()
