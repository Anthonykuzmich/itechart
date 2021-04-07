from functools import wraps
import time

import psycopg2
from elasticsearch import Elasticsearch


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            start_sleep = start_sleep_time
            f = factor
            border_sleep = border_sleep_time
            while border_sleep_time > start_sleep_time:
                try:
                    print('The connection was successfully set')
                    return func()
                except Exception:
                    if start_sleep < border_sleep:
                        print(f'Connecting to the database in....({start_sleep} seconds)')
                        start_sleep = start_sleep * 2 ** f
                        time.sleep(start_sleep)
                    elif start_sleep > border_sleep:
                        print('Try to connect later :(')
                        break

        return inner

    return func_wrapper


if __name__ == '__main__':

    @backoff(0.1, 2, 10)
    def some_func():
        print('workkkkk')
        connection = psycopg2.connect(dbname='movies_database', user='postgres',
                                      password='123qwe', host='localhost')


    @backoff()
    def connect_elasticsearch():
        es = None
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        if not es.ping():
            raise ValueError("Connection failed")
        return es


    connect_elasticsearch()
