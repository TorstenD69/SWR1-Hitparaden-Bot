# -*- coding: utf-8 -*-

import requests
import logging
from requests.exceptions import HTTPError

from . import num_list


def http_request() -> dict:

    try:
        swr1_url = 'https://vote.swr.de/swr/voting/abstimmung/ergebnis/R444448?_format=json'
        logging.info(create_log_message(http_request.__name__, f'Get the hit list from URL: {swr1_url}'))
        response = requests.get(swr1_url)

       # If the response was successful, no Exception will be raised
        response.raise_for_status()

    except HTTPError as http_err:
        logging.error(create_log_message(http_request.__name__, f'HTTP error occurred: {http_err}'))

    except Exception as err:
        logging.error(create_log_message(http_request.__name__, f'Other error occurred: {err}'))

    else:
        logging.info(create_log_message(http_request.__name__, f'http_Request with URL: {swr1_url} successfull'))
        return(response.json())


def get_search_criteria(search_query: str) -> dict:

    and_list = []
    or_list = []

    logging.info(create_log_message(get_search_criteria.__name__, f'Start parsing the search query: {search_query}'))
    while len(search_query) > 0:

        if search_query.startswith('+'):
            if search_query[1] == '"':
                search_query = add_phrase_to_list(search_query, 2, and_list, '"')

            else:
                search_query = add_phrase_to_list(search_query, 1, and_list, ' ')

        elif search_query.startswith('"'):
            search_query = add_phrase_to_list(search_query, 1, or_list, '"')

        else:
            search_query = add_phrase_to_list(search_query, 0, or_list, ' ')

    search_criteria = {'or': or_list, 'and': and_list}
    logging.info(create_log_message(get_search_criteria.__name__,
                                    f'Parsing query finished, search criteria: {search_criteria}'))

    return(search_criteria)


def add_phrase_to_list(search_text: str, start_pos: int, search_list: list, separator) -> str:

    logging.info(create_log_message(add_phrase_to_list.__name__,
                                    f'Start adding the phrase {search_text} to the search criteria'))

    end_pos = search_text.find(separator, start_pos)

    if end_pos > -1:
        search_list.append(search_text[start_pos: end_pos])

    else:
        search_list.append(search_text[start_pos:len(search_text)])

    if end_pos + 1 == len(search_text) or end_pos == -1:
        return_string = ''

    else:
        return_string = search_text[end_pos + 1:len(search_text)].strip()

    logging.info(create_log_message(add_phrase_to_list.__name__,
                                    f'Start adding the phrase {search_text} to the search criteria'))

    return (return_string)


def perform_search(search_criteria: dict, search_keys: list) -> str:

    temp_list = []
    hit_list = http_request()

    logging.info(create_log_message(perform_search.__name__, f'Search started. Search criteria: {search_criteria}'))

    if len(search_criteria['or']) > 0:
        logging.info(create_log_message(perform_search.__name__, 'Invoke OR search'))
        temp_list = perform_or_search(hit_list, search_criteria['or'], search_keys)

    if len(temp_list) == 0:
        temp_list = hit_list

    if len(search_criteria['and']) > 0:
        logging.info(create_log_message(perform_search.__name__, 'Invoke AND search'))
        temp_list = perform_and_search(temp_list, search_criteria['and'], search_keys)

    count = 1
    search_result = ''
    for entry in temp_list:
        search_result += create_result_entry(entry, count)
        count += 1

    logging.info(create_log_message(perform_search.__name__, 'Search completed'))

    return (search_result)


def perform_or_search(hit_list: dict, search_words: list, key_list: list) -> list:

    search_result = []

    logging.info(create_log_message(perform_or_search.__name__,
                                    f'Start performing OR search. Search words: {search_words}, search keys: {key_list}'))
    for hit in hit_list:

        entry = ''
        for key in key_list:
            entry += str(hit[key]) + ' '

        for word in search_words:

            if word.lower() in entry.lower():

                search_result.append(hit)
                logging.info(create_log_message(perform_or_search.__name__, f'Hit found: {hit}'))

    return(search_result)


def perform_and_search(hit_list: dict, search_words: list, key_list: list) -> list:

    search_result = []

    logging.info(create_log_message(perform_and_search.__name__,
                                    f'Start performing AND search. Search words: {search_words}, search keys: {key_list}'))

    for hit in hit_list:

        entry = ''
        for key in key_list:
            entry += str(hit[key]) + ' '

        contains = True
        for word in search_words:

            if word.lower() not in entry.lower():
                contains = False
                break

        if contains:
            logging.info(create_log_message(perform_and_search.__name__, f'Hit found: {hit}'))
            search_result.append(hit)

    return (search_result)


def perform_rank_search(rank: int) -> str:

    logging.info(create_log_message(perform_rank_search.__name__,
                                    f'Start performing rank search. Rank: {str(rank)}'))

    hit_list = http_request()

    found = 0
    search_result = ''
    for hit in hit_list:
        if int(hit['rank']) == rank:
            logging.info(create_log_message(perform_rank_search.__name__, f'Entry found: {hit}'))
            search_result += create_result_entry(hit, found)
            found += 1

    return(search_result)


def get_top_ten():

    logging.info(create_log_message(get_top_ten.__name__,
                                    f'Start performing Top 10 search.'))

    hit_list = http_request()

    top_ten = ''
    for i in range(0, 10):
        top_ten += create_result_entry(hit_list[i], i)

    return(top_ten)


def get_count(artist: str) -> int:

    logging.info(create_log_message(get_count.__name__,
                                    f'Start counting hits from an Artist. Artist to count: {artist}'))
    hit_list = http_request()

    count = 0
    for hit in hit_list:
        if hit['artist'].lower().strip() == artist.lower().strip():
            logging.info(create_log_message(get_count.__name__, f'Hit from Artist found: {hit}'))
            count += 1

    return (count)


def create_result_entry(record: dict, count: int) -> str:

    result = ''
    if count > 0:
        result += '----------\n'

    result += f'*Platz:    {str(record["rank"])}*\n'
    result += f'Künstler: {record["artist"]}\n'
    result += f'Titel:    {record["name"]}\n'

    #if len(record['hookUrl']) > 0:
    #    result += record['hookUrl'] + '\n'

    return(result)


def get_num_from_word(num_in_words: str) -> int:

    if num_in_words in num_list.NUM_LIST.keys():
        logging.info(create_log_message(get_num_from_word.__name__, f'Number found: {str(num_list.NUM_LIST[num_in_words])}'))
        return(int(num_list.NUM_LIST[num_in_words]))

    else:
        logging.info(create_log_message(get_num_from_word.__name__, f'No number found'))
        return(0)


def create_log_message(function_name: str, text: str) -> str:

    log_message = f'< {function_name} > - {text}'
    return (log_message)


if __name__ == '__main__':
    print('nn')
