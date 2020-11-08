import os
import sys
import time
from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser


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


def connect_to_db(attempts=5, delay=15, allow_local_infile=True, buffered=True):
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


def main(filename='csv_data/data.csv', tablename='my_table', ignore_first=True):
    '''Connect to database and load data from local file.
    :param filename: name of .csv file
    :param tablename: name of created table'''
    try:
        # connect
        conn = connect_to_db()
        cursor = conn.cursor()
        # ensure local_infile = 1
        cursor.execute("SHOW GLOBAL VARIABLES LIKE 'local_infile'")
        for row in cursor.fetchall():
            print(row)
        # create table & fulfill
        cursor.execute(f'CREATE TABLE {tablename} (text TEXT, number INT)')
        ignore_str = 'IGNORE 1 ROWS' if ignore_first else ''
        load_data_query = f'''
            LOAD DATA LOCAL INFILE "{filename}"
            INTO TABLE {tablename}
            COLUMNS TERMINATED BY ','
            OPTIONALLY ENCLOSED BY '"'
            ESCAPED BY '"'
            LINES TERMINATED BY '\n'
            {ignore_str}
            (text, number);
        '''
        assert(os.path.exists(filename))
        cursor.execute(load_data_query)
        conn.commit()
    except Error as e:
        print(e)
    except ConnectionError as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
