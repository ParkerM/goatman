from multiprocessing import Pool
from datetime import datetime
import logging

import requests

from lib import util
from lib import mysqlhelper

POOL_SIZE = 10
CONFIG = util.load_config('config.json')

def main():
    """Main function for updating database with web responses.
    """
    if not mysqlhelper.schema_exists():
        logging.error('Schema "%s" not found. Did you run db-init?', CONFIG['db_schema'])
        return

    domain_name = CONFIG['domain_name']

    url_set = util.fetch_tlds(domain_name)
    print(len(url_set), "TLD's found.")

    responses = dict(fetch_data(url_set))

    mysqlhelper.update_responses(responses)

def fetch_data(url_set):
    """Initiate async get requests for a set of URL's

    Parameters
    ----------
    url_set: A set of URL's

    Returns
    -------
    dict: Dict of TLD's to tuples containing response info
    """
    begin_time = datetime.now()

    print('Beginning request execution')
    p = Pool(POOL_SIZE)
    results = p.map(get_response, url_set)

    end_time = datetime.now()

    print("Execution duration:", end_time - begin_time)

    return results

def get_response(url):
    """Get some info from the response of the given URL

    Parameters
    ----------
    url: URL to GET

    Returns
    -------
    tuple: (URL, HTTP status code, Response headers, Response body)
    """
    url_p = 'http://' + url[1]
    logging.info('Sending request for %s', url_p)

    try:
        response = requests.get(
            url_p,
            headers=CONFIG['request_headers'],
            allow_redirects=False,
            timeout=60
        )
    except requests.exceptions.ConnectionError:
        logging.info('Connection to %s failed.', url[1])
        response_data = (url_p, 0, None, None)
    else:
        header_string = '\r\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items())
        encoded_body = response.content.decode('utf-8', 'ignore')
        response_data = (url_p, response.status_code, header_string, encoded_body)
    return url[0], response_data

if __name__ == '__main__':
    main()
