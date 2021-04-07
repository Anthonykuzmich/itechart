import decimal
import json
from decimal import Decimal

import psycopg2

from configs.backoff_decorator import backoff


dsn = {
    "dbname": "movies",
    "user": "postgres",
    "password": "123qwe",
    "host": "0.0.0.0",
    "port": 5432,
}


def coroutine(fn):
    def start(*args, **kwargs):
        g = fn(*args, **kwargs)
        next(g)
        return g

    return start


# @backoff()
def extract_data():
    with psycopg2.connect(**dsn) as conn, conn.cursor() as cursor:
        cursor.execute('''select m.id, m.title, array_agg(DISTINCT g.name) as genre,m.description, m.director, m.imdb_rating,
        array_agg(DISTINCT w.name) as writers, array_agg(DISTINCT a.name) as actors, m.updated_at from movie m
        LEFT JOIN movie_actor ma on m.id = ma.movie_id
        LEFT JOIN actor a on ma.actor_id = a.id
        LEFT JOIN movie_writer mw on m.id = mw.movie_id
        LEFT JOIN writer w on mw.writer_id = w.id
        LEFT JOIN movie_genre mg on m.id = mg.movie_id
        LEFT JOIN genre g on mg.genre_id = g.id
        group by m.id ORDER BY m.updated_at DESC''')
        data = cursor.fetchall()
        for row in data:
            transform_func = transform()
            description = cursor.description
            names_of_colums = list(map(lambda x: x[0], description))
            names_with_values = dict(zip(names_of_colums, row))
            try:
                transform_func.send(names_with_values)
            except StopIteration:
                print('next row')


# class DecimalEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, decimal.Decimal):
#             # wanted a simple yield str(o) in the next line,
#             # but that would mean a yield on the line with super(...),
#             # which wouldn't work (see my comment below), so...
#             return (str(o) for o in [o])
#         return super(DecimalEncoder, self).default(o)

@coroutine
def transform():
    data = yield
    data['imdb_rating'] = str(data['imdb_rating'])
    data['updated_at'] = str(data['updated_at'])
    data = json.dumps(data)
    print(data)


@coroutine
def load():

    extract_data()
    transform()

