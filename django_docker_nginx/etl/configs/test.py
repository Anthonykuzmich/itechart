import psycopg2
from elasticsearch import Elasticsearch
from backoff_decorator import backoff


def connect_elasticsearch():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if not es.ping():
        raise ValueError("Connection failed")
    return es

dsn = {
    "dbname": "movies",
    "user": "postgres",
    "password": "123qwe",
    "host": "0.0.0.0",
    "port": 5432,
}

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
        print(cursor.fetchall())

if __name__ == '__main__':
    connect_elasticsearch()
    extract_data()