import logging
import os

import azure.functions as func

import telegram
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import Dispatcher, Filters

from . import get_hit
from . import messages


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(get_hit.create_log_message(main.__name__, 'Python HTTP trigger function processed a request.'))

    try:
        # Start Bot
        swr_bot = telegram.Bot(
            token=os.environ['bot_key'])
        logging.info(get_hit.create_log_message(main.__name__, 'Bot successfull started'))

        # Start Dispatcher
        dispatcher = Dispatcher(swr_bot, None, workers=0, use_context=True)
        logging.info(get_hit.create_log_message(main.__name__, 'Dispatcher process successfull started'))

        # Register Handlers
        register_handlers(dispatcher)

        # Process request
        update = telegram.Update.de_json(req.get_json(), swr_bot)
        logging.info(get_hit.create_log_message(main.__name__, 'Start update processing'))
        dispatcher.process_update(update)

        return func.HttpResponse("ok")

    except Exception as err:
        logging.error(get_hit.create_log_message(main.__name__, f'An error occurred: {err}'))

        return func.HttpResponse(
            "Please pass a query string to get a result",
            status_code=400
        )


def register_handlers(bot_dispatcher: telegram.ext.dispatcher):
    # Register all the bot handlers

    logging.info(get_hit.create_log_message(register_handlers.__name__, 'Registering all the bot handlers'))

    start_handler = telegram.ext.CommandHandler('start', start_cmd)
    bot_dispatcher.add_handler(start_handler)

    help_handler = telegram.ext.CommandHandler('hilfe', help_cmd)
    bot_dispatcher.add_handler(help_handler)

    help_handler = telegram.ext.CommandHandler('hilfe2', help2_cmd)
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

    echo_handler = telegram.ext.MessageHandler(Filters.text, echo_cmd)
    bot_dispatcher.add_handler(echo_handler)

    logging.info(get_hit.create_log_message(register_handlers.__name__, 'All Handlers successfull registered'))


def start_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Start Handler

    logging.info(get_hit.create_log_message(start_cmd.__name__, 'Start handler triggered'))
    message = messages.START_MESSAGE['de']

    logging.info(get_hit.create_log_message(start_cmd.__name__, 'Send message'))

    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def help_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Help Handler

    logging.info(get_hit.create_log_message(help_cmd.__name__, 'Help handler triggered'))
    message = messages.HELP_MESSAGE['de']

    logging.info(get_hit.create_log_message(help_cmd.__name__, 'Send message'))

    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def help2_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Help Handler

    logging.info(get_hit.create_log_message(help2_cmd.__name__, 'Extended Help handler triggered'))
    message = messages.HELP_MESSAGE2['de']

    logging.info(get_hit.create_log_message(help2_cmd.__name__, 'Send message'))

    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def artist_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Handler to search for an artist

    logging.info(get_hit.create_log_message(artist_cmd.__name__, 'Artist search invoked'))

    if len(the_context.args) == 0:
        logging.info(get_hit.create_log_message(artist_cmd.__name__, f'No search string'))
        message = messages.NO_EMPTY_SEARCH['de']

    else:
        search_text = ' '.join(the_context.args)
        logging.info(get_hit.create_log_message(artist_cmd.__name__, f'Search query: {search_text}'))
        criteria = get_hit.get_search_criteria(search_text)

        keys = ['artist']

        message = get_hit.perform_search(criteria, keys)

    logging.info(get_hit.create_log_message(artist_cmd.__name__, 'Send message'))

    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def title_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Handler to search for a title

    logging.info(get_hit.create_log_message(title_cmd.__name__, 'Title search invoked'))

    if len(the_context.args) == 0:
        logging.info(get_hit.create_log_message(title_cmd.__name__, 'No search string'))
        message = messages.NO_EMPTY_SEARCH['de']

    else:
        search_text = ' '.join(the_context.args)
        logging.info(get_hit.create_log_message(title_cmd.__name__, f'Search query: {search_text}'))

        criteria = get_hit.get_search_criteria(search_text)

        keys = ['name']

        message = get_hit.perform_search(criteria, keys)

    logging.info(get_hit.create_log_message(title_cmd.__name__, 'Send message'))

    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def pos_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):

    logging.info(get_hit.create_log_message(pos_cmd.__name__, 'Start searching for a special position'))

    if len(the_context.args) == 0:
        logging.info(get_hit.create_log_message(pos_cmd.__name__, 'No search string'))
        message = messages.NO_EMPTY_SEARCH['de']

    elif not ''.join(the_context.args).strip().isdigit():

        logging.info(get_hit.create_log_message(pos_cmd.__name__, 'Search string is no digit, invoke transformation'))
        number = get_hit.get_num_from_word(''.join(the_context.args).strip())

        if number == 0:

            logging.info(get_hit.create_log_message(pos_cmd.__name__, 'Search string is no number'))
            message = messages.NO_NUM['de']

        else:
            logging.info(get_hit.create_log_message(pos_cmd.__name__, f'Search rank: {str(number)}'))
            message = get_hit.perform_rank_search(number)

    else:
        search_text = ''.join(the_context.args)
        logging.info(get_hit.create_log_message(pos_cmd.__name__, f'Search rank: {search_text}'))

        message = get_hit.perform_rank_search(int(search_text))

    logging.info(get_hit.create_log_message(pos_cmd.__name__, 'Send message'))

    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def echo_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Handler to answer the "simple" queries

    logging.info(get_hit.create_log_message(echo_cmd.__name__, 'Echo handler invoked'))

    if len(my_update.message.text) == 0:
        logging.info(get_hit.create_log_message(echo_cmd.__name__, 'No search string'))
        message = messages.NO_EMPTY_SEARCH['de']

    else:

        logging.info(get_hit.create_log_message(echo_cmd.__name__, 'Get search criteria'))
        criteria = get_hit.get_search_criteria(my_update.message.text)

        keys = ['rank', 'artist', 'name']

        logging.info(get_hit.create_log_message(echo_cmd.__name__, 'Start full text search'))
        message = get_hit.perform_search(criteria, keys)

    logging.info(get_hit.create_log_message(echo_cmd.__name__, 'Send message'))
    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def top_ten_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Top 10 Handler

    logging.info(get_hit.create_log_message(top_ten_cmd.__name__, 'Top 10 search invoked'))
    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=get_hit.get_top_ten(),
                                 parse_mode='Markdown')


def count_cmd(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Handler to count the hits of one artist in the charts

    logging.info(get_hit.create_log_message(count_cmd.__name__, 'Artist count invoked'))
    search_string = ' '.join(the_context.args)

    count = get_hit.get_count(search_string)

    if count == 0:
        logging.info(get_hit.create_log_message(count_cmd.__name__, 'No hits found'))
        message = messages.NO_HIT_COUNT['de']
    else:
        message = messages.hit_count(search_string, count, 'de')

    logging.info(get_hit.create_log_message(count_cmd.__name__, 'Send message'))
    the_context.bot.send_message(chat_id=my_update.message.chat_id,
                                 text=message,
                                 parse_mode='Markdown')


def error_handler(my_update: telegram.update, the_context: telegram.ext.CallbackContext):
    # Common error handler

    try:
        raise the_context.error

    except Exception as err:
        logging.error(f'An error occurred: {err}')
