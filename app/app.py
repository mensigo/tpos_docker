import time
import json
from flask import Flask
from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser

HOST = '0.0.0.0'
APP = Flask(__name__)


def read_config(filename='config.ini', section='mysql'):
    ''' Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    '''
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)
    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))
    return db


def connect_to_db(attempts=10, delay=15, allow_local_infile=True, buffered=True):
    '''Try to connect to database with reconnecting if necessary.
    :param attempts: number of attempts to recconect to database
    :param delay: period of time to wait between consequent attempts
    :param allow_local_infile: enable to load data into database from local file
    :param buffered: fetch the results immediately after executing queries
    :return MySQLConnection object
    '''
    dbconfig = read_config()
    for i in range(attempts+1):
        try:
            conn = MySQLConnection(
                **dbconfig,
                allow_local_infile=allow_local_infile,
                buffered=buffered)
            print('[SUCCESS] Connection is set.', flush=True)
            break
        except Error:
            if i < attempts:
                print(f'Reconnecting in {delay} sec (attempt {i+1} of {attempts})', flush=True)
                time.sleep(delay)
                print('Reconnecting...', flush=True)
            else:
                raise ConnectionError(f'[FAIL] Connection is not set ({attempts} attempts, {delay} delay)')
    return conn


def get_data(tablename='my_table', attempts=10, delay=5):
    '''Connect to database and load data from local file.
    :param tablename: name of the provided table
    :param attempts: number of attempts to take data from database
    :param delay: time period before constquent attempts to take data
    :return data as a list'''
    try:
        # connect
        conn = connect_to_db()
        cursor = conn.cursor()
        def foo(cursor, conn):
            cursor.execute(f'SELECT * FROM {tablename}')
            conn.commit()
            return cursor.fetchall()
        for i in range(attempts+1):
           # get data
            try:
                data = foo(cursor, conn)
                print('[SUCCESS] Data is taken.', flush=True)
                break
            except Error:
                if i < attempts:
                    print(f'Retaking data in {delay} sec (attempt {i+1} of {attempts})', flush=True)
                    time.sleep(delay)
                    print('Retaking...', flush=True)
                else:
                    raise ConnectionError(f'[FAIL] No data loaded ({attempts} attempts, {delay} delay)')
        return [{t: n} for (t, n) in data]
    except Error as e:
        print(e)
    except ConnectionError as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@APP.route('/', methods=['GET'])
def index(tablename='my_table'):
    '''Form respond
    param tablename: name of the provided table'''
    return json.dumps(get_data())


@APP.route('/health', methods=['GET'])
def health():
     return json.dumps(200)

@APP.errorhandler(404)
def page_not_found(e):
    return '404. Wrong request. Page not found.'


if __name__ == '__main__':
    get_data()  # wait data to be loaded
    APP.run(host=HOST)

