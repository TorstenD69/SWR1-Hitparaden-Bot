import logging
import os

import azure.functions as func

import telegram
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import Dispatcher, Filters

from . import get_hit
from. import messages


def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Start Bot
        swr_bot = telegram.Bot(
            token=os.environ['bot_key'])
        logging.info('Bot successfull started')

        # Start Dispatcher
        dispatcher = Dispatcher(swr_bot, None, workers=0, use_context=True)
        logging.info('Dispatcher process successfull started')

        # Register Handlers
        register_handlers(dispatcher)

        # Process request
        update = telegram.Update.de_json(req.get_json(), swr_bot)
        logging.info('Start update processing')
        dispatcher.process_update(update)

        return func.HttpResponse("ok")

    except Exception as err:
        logging.error(f'An error occurred: {err}')

        return func.HttpResponse(
            "Please pass a query string to get a result",
            status_code=400
        )


def register_handlers(bot_dispatcher: telegram.ext.dispatcher):
    # Register all the bot handlers

    logging.info(f'Registering all the bot handlers')

    start_handler = telegram.ext.CommandHandler('start', start_cmd)
    bot_dispatcher.add_handler(start_handler)

    help_handler = telegram.ext.CommandHandler('hilfe', help_cmd)
    bot_dispatcher.add_handler(help_handler)

    top_ten_handler = telegram.ext.CommandHandler('10', top_ten_cmd)
    bot_dispatcher.add_handler(top_ten_handler)

    count_handler = telegram.ext.CommandHandler('anzahl', count_cmd)
    bot_dispatcher.add_handler(count_handler)

    artist_handler = telegram.ext.CommandHandler('musiker', artist_cmd)
    bot_dispatcher.add_handler(artist_handler)

    artist_handler = telegram.ext.CommandHandler('titel', title_cmd)
    bot_dispatcher.add_handler(artist_handler)

    artist_handler = telegram.ext.CommandHandler('platz', pos_cmd)
    bot_dispatcher.add_handler(artist_handler)

    bot_dispatcher.add_error_handler('error_handler')

    echo_handler = telegram.ext.MessageHandler(Filters.text, answer_cmd)
    bot_dispatcher.add_handler(echo_handler)

    logging.info('All Handlers successfull registered')


def start_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Start Handler

    logging.info(f'Start handler successfull triggered')
    message = messages.START_MESSAGE['de']

    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def help_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Help Handler

    logging.info(f'Help handler successfull triggered')
    message = messages.HELP_MESSAGE['de']

    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def artist_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Handler to search for an artist

    logging.info(f'Start searching for an artist')

    if len(the_context.args) == 0:
        logging.info(f'No search string')
        message = 'Die Suche darf *nicht* leer sein. Du musst einen Künstlernamen angeben.'

    else:
        search_text = ' '.join(the_context.args)
        logging.info(f'Search query: {search_text}')
        query = {'type': 'artist', 'query': search_text}

        message = get_hit.perform_search(query)

    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def title_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Handler to search for a title

    logging.info(f'Start searching for a title')

    if len(the_context.args) == 0:
        logging.info(f'No search string')
        message = 'Die Suche darf *nicht* leer sein. Du musst einen Titel angeben.'

    else:
        search_text = ' '.join(the_context.args)
        logging.info(f'Search query: {search_text}')

        query = {'type': 'title', 'query': search_text}

        message = get_hit.perform_search(query)

    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def pos_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):

    logging.info(f'Start searching for a special position')

    if len(the_context.args) == 0:
        logging.info(f'No search string')
        message = 'Die Suche darf *nicht* leer sein. Du musst eine Platzierung angeben.'

    elif not ''.join(the_context.args).strip().isdigit():
        logging.info(f'Search string was no number')
        message = 'Um nach einer Platzierung zu suchen musst Du eine Zahl eingeben.'

    else:
        search_text = ''.join(the_context.args)
        logging.info(f'Search query: {search_text}')
        query = {'type': 'rank', 'query': int(search_text)}

        message = get_hit.perform_search(query)

    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def answer_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Handler to answer the "simple" queries

    logging.info(f'Create search query')

    search_query = {'type': 'full', 'query': my_update.message.text}

    result = get_hit.perform_search(search_query)
    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=result,
                                 parse_mode='Markdown')


def top_ten_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Top 10 Handler

    logging.info(f'Send Top 10 of the charts')
    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=get_hit.get_top_ten(),
                                 parse_mode='Markdown')


def count_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Handler to count the hits of one artist in the charts

    logging.info(f'Count hits of an artist and send')
    search_string = ' '.join(the_context.args)
    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=get_hit.get_count(search_string),
                                 parse_mode='Markdown')


def error_handler(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Common error handler

    try:
        raise the_context.error

    except Exception as err:
        logging.error(f'An error occurred: {err}')
