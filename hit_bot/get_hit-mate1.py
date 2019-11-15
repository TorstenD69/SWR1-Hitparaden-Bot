# -*- coding: utf-8 -*-

import requests
import logging
from requests.exceptions import HTTPError


def http_request() -> dict:

    try:
        swr1_url = 'https://vote.swr.de/swr/voting/abstimmung/ergebnis/R444448?_format=json'
        response = requests.get(swr1_url)

       # If the response was successful, no Exception will be raised
        response.raise_for_status()

    except HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')

    except Exception as err:
        logging.error(f'Other error occurred: {err}')

    else:
        logging.info(f'http_Request with URL: {swr1_url} successfull')
        return(response.json())


def get_search_criteria(search_term: str) -> dict:

    try:
        if search_term.startswith('Platz:'):
            if search_term.split(':')[1].strip().isdigit():
                query = {'type': 'rank', 'query': int(search_term.split(':')[1].strip())}

            else:
                query = {'type': 'err', 'query': 'Um nach einer Platzierung zu suchen musst Du eine Zahl eingeben.'}

        elif search_term.startswith('Künstler:'):
            query = {'type': 'artist', 'query': search_term.split(':')[1].strip()}

        elif search_term.startswith('Titel:'):
            query = {'type': 'name', 'query': search_term.split(':')[1].strip()}

        else:
            query = {'type': 'full', 'query': search_term}

        logging.info(f'Search criteria found: {query}')
        return query

    except Exception as err:
        logging.error(f'An error occurred: {err}')


def perform_search(query: dict) -> str:

    try:

        hit_list = http_request()

        if query['type'] == 'rank':
            result = perform_rank_search(hit_list, int(query['query']))

        elif query['type'] == 'full':
            result = perform_fulltext_search(hit_list, query['query'])

        else:
            result = perform_key_search(hit_list, query)

        if len(result) == 0:
            result = 'Die Suche war leider erfolglos. Probier es doch gleich noch einmal.'

        return(result)

    except Exception as err:
        logging.error(f'An error occurred: {err}')


def perform_rank_search(list: dict, rank: int) -> str:

    try:
        found = 0
        hit = ''
        for entry in list:
            if int(entry['rank']) == rank:
                logging.info(f'Entry found: {entry}')
                hit += create_result_entry(entry, found)
                found += 1

        return(hit)

    except Exception as err:
        logging.error(f'An error occurred: {err}')


def perform_fulltext_search(list: dict, query_string: str) -> str:

    try:
        found = 0
        hit = ''
        for entry in list:
            if str(entry['rank']).count(query_string) > 0:
                logging.info(f'Entry found: {entry}')
                hit += create_result_entry(entry, found)
                found += 1

            elif entry['artist'].lower().count(query_string.lower()) > 0:
                logging.info(f'Entry found: {entry}')
                hit += create_result_entry(entry, found)
                found += 1

            elif entry['name'].lower().count(query_string.lower()) > 0:
                logging.info(f'Entry found: {entry}')
                hit += create_result_entry(entry, found)
                found += 1

        return(hit)

    except Exception as err:
        logging.error(f'An error occurred: {err}')


def perform_key_search(list: dict, query: dict) -> str:

    try:
        found = 0
        hit = ''
        for entry in list:
            if entry[query['type']].lower() == query['query'].lower():
                logging.info(f'Entry found: {entry}')
                hit += create_result_entry(entry, found)
                found += 1

        return(hit)

    except Exception as err:
        logging.error(f'An error occurred: {err}')


def get_top_ten():

    try:
        hit_list = http_request()

        top_ten = ''
        for i in range(0, 10):
            top_ten += create_result_entry(hit_list[i], i)

        return(top_ten)

    except Exception as err:
        logging.error(f'An error occurred: {err}')


def get_count(artist: str) -> str:

    try:
        logging.info(f'Artist to count: {artist}')
        hit_list = http_request()

        count = 0
        for hit in hit_list:
            if hit['artist'].lower() == artist.lower():
                count += 1

        if count == 0:
            result = '*Schade*\nDer Künstler hatte keinen Hit in der Hitparade. Probier es doch gleich noch einmal.'

        else:
            result = str(count)

        return (result)

    except Exception as err:
        logging.error(f'An error occurred: {err}')


def create_result_entry(record: dict, count: int) -> str:

    result = ''
    if count > 0:
        result += '----------\n'

    result += f'*Platz:    {str(record["rank"])}*\n'
    result += f'Künstler: {record["artist"]}\n'
    result += f'Titel:    {record["name"]}\n'
    #result += record['hookUrl'] + '\n'

    return(result)


if __name__ == '__main__':
    print('nn')
