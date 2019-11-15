import logging
import os

import azure.functions as func

import telegram
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import Dispatcher, Filters

from . import get_hit


def main(req: func.HttpRequest) -> func.HttpResponse:
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

    try:
        start_handler = telegram.ext.CommandHandler('start', start_cmd)
        bot_dispatcher.add_handler(start_handler)

        help_handler = telegram.ext.CommandHandler('hilfe', help_cmd)
        bot_dispatcher.add_handler(help_handler)

        top_ten_handler = telegram.ext.CommandHandler('10', top_ten_cmd)
        bot_dispatcher.add_handler(top_ten_handler)

        count_handler = telegram.ext.CommandHandler('count', count_cmd)
        bot_dispatcher.add_handler(count_handler)

        artist_handler = telegram.ext.CommandHandler('k', k_cmd)
        bot_dispatcher.add_handler(artist_handler)

        echo_handler = telegram.ext.MessageHandler(Filters.text, answer_cmd)
        bot_dispatcher.add_handler(echo_handler)

        logging.info('All Handlers successfull registered')

    except Exception as err:
        logging.error(f'An error occurred: {err}')


def start_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):

    # Start Handler
    message = '*SWR1 Hitparade 2019*\n\n\
Ich bins, der Hitparaden Bot.\n\
Wenn Du wissen möchtest, welcher Titel wo in der Hitparade 2019 gelandet ist, dann frag einfach mich.\
Gib dafür einfach einen Suchbegriff ein und los geht\'s. Wenn Du wissen willst wie es genau funktioniert, sende einfach /hilfe an mich. '

    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def help_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Help Handler

    message = '*Hitparaden Bot-Hilfe*\n\n\
Sende einfach einen beliebigen Text an mich und ich suche in der gesamten Liste der gewählten Titel nach diesem Text.\
Du kannst die Suche aber auch einschränken.\n\n\
Für die Suche nach einer bestimmten Platzierung beginne Deine Suche mit "Platz:" gefolgt von der gewünschten Platzierung.\
Für die Suche nach einem bestimmten Titel oder einem Künstler beginne Deine Suche einfach mit "Titel:" oder "Künstler:"\n\
Wenn Du einfach nur die ersten zehn Platzierungen wissen möchtest probiert doch mal /10 aus.'

    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def k_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Handler to search for an artist

    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=the_context.args,
                                 parse_mode='Markdown')

#    answer = get_hit.perform_key_search


def answer_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Handler to answer the "simple" queries

    try:
        logging.info(f'Create search query')
        search_query = get_hit.get_search_criteria(my_update.message.text)

        if search_query['type'] == 'err':
            logging.info(f'_The search query contains an error_')
            the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                         text=search_query['query'],
                                         parse_mode='Markdown')

        else:
            result = get_hit.perform_search(search_query)
            the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                         text=result,
                                         parse_mode='Markdown')

    except Exception as err:
        logging.error(f'An error occurred: {err}')


def top_ten_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Top 10 Handler

    try:
        logging.info(f'Send Top 10 of the charts')
        the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                     text=get_hit.get_top_ten(),
                                     parse_mode='Markdown')

    except Exception as err:
        logging.error(f'An error occurred: {err}')


def count_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Handler to count the hits of one artist in the charts

    try:
        logging.info(f'Count hits of an artist and send')
        the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                     text=get_hit.get_count(my_update.message.text[6:len(my_update.message.text)]),
                                     parse_mode='Markdown')

    except Exception as err:
        logging.error(f'An error occurred: {err}')
