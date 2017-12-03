"""
Helper functions for MySQL
"""
import logging
import os
import sys

import pymysql
import pymysql.cursors

sys.path.append(os.path.dirname(__file__))  # required to locate util module when importing
import util

CONFIG = util.load_config('config.json')

def schema_exists():
    """Check if schema exists

    Returns
    -------
    Boolean: True if schema defined in config.json exists
    """
    connection = get_connection(False)

    query = 'SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s'
    try:
        with connection.cursor() as curr:
            curr.execute(query, (CONFIG['db_schema']))
            row_count = curr.rowcount
    finally:
        connection.close()

    return row_count > 0

def update_responses(responses):
    """Perform updates to response table via stored procedure.

    Parameters
    ----------
    responses: dict of tlds to response info tuples
    """
    connection = get_connection()

    print("Beginning database updates")
    row_count = 0
    try:
        with connection.cursor() as curr:
            for tld, data in responses.items():
                curr.callproc('update_or_insert_response', (tld,) + data)
                row_count += curr.rowcount
    except pymysql.Error as err:
        logging.exception('{:10s} {}'.format(tld, data))
        raise err
    except AttributeError as err:
        logging.exception('{:10s} {}'.format(tld, data))
        raise err
    else:
        connection.commit()
        print('Database updates successful. {:d} rows affected.'.format(row_count))
    finally:
        connection.close()

def init_db():
    """Initializes database with supplied config options. Running this
    will destroy an existing database with the same name.
    """
    db_queries = parse_queries_from_file('../sql/create_db.sql')
    db_queries.append(parse_queries_from_file('../sql/create_sp.sql', False))

    print('Initializing database "{}"'.format(CONFIG['db_schema']))

    connection = get_connection(include_db=False)
    try:
        with connection.cursor() as curr:
            for query in db_queries:
                curr.execute(query)
    except pymysql.InternalError as err:
        logging.exception('Failed to initialize database: %s', query)
        raise err
    except pymysql.Error as err:
        logging.exception('Failed to initialize database: %s', query)
        raise err
    else:
        connection.commit()
        print('Database successfully initialized')
    finally:
        connection.close()

def parse_queries_from_file(filepath, multiple=True):
    """Attempt to parse multiple queries from a SQL file

    Parameters
    ----------
    filepath: the relative path of the file to be read from
    multiple: if False, treat the file as a single query. Default is True

    Returns
    -------
    A `list` of queries. Returns a single string if `multiple` is `False`
    """
    sql_file = util.get_path(filepath)
    with open(sql_file, 'r') as sql_in:
        sql = sql_in.read().replace('<SCHEMA_NAME>', CONFIG['db_schema'])
    if multiple:
        queries = [q.strip() for q in sql.split(';') if q.strip() != '']
        return queries
    return sql.strip()

def get_connection(include_db=True):
    """Get DB connection with common configuration

    Parameters
    ----------
    include_db: False if schema should not be included in connection

    Returns
    -------
    Configured MySQL connection
    """
    connection = pymysql.connect(
        host=CONFIG['db_host'],
        port=CONFIG['db_port'],
        user=CONFIG['db_username'],
        password=CONFIG['db_password'],
        charset='utf8mb4'
    )
    if include_db:
        connection.select_db(CONFIG['db_schema'])
    return connection

if __name__ == '__main__':
    init_db()
