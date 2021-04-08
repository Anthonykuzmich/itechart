import json
from elasticsearch import Elasticsearch, helpers
import psycopg2
from redis import Redis

from configs.backoff_decorator import backoff
from configs.jsonfilestorage import JsonFileStorage, State, RedisStorage

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


@backoff()
def connect_elasticsearch():
    es = Elasticsearch()
    if not es.ping():
        raise ValueError("Connection failed")
    return es


def create_index(es_object, index_name='movies'):
    created = False
    # index settings
    settings = {
        "settings": {
            "refresh_interval": "1s",
            "analysis": {
                "filter": {
                    "english_stop": {"type": "stop", "stopwords": "_english_"},
                    "english_stemmer": {"type": "stemmer", "language": "english"},
                    "english_possessive_stemmer": {
                        "type": "stemmer",
                        "language": "possessive_english",
                    },
                    "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                    "russian_stemmer": {"type": "stemmer", "language": "russian"},
                },
                "analyzer": {
                    "ru_en": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "english_stop",
                            "english_stemmer",
                            "english_possessive_stemmer",
                            "russian_stop",
                            "russian_stemmer",
                        ],
                    }
                },
            },
        },
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "id": {"type": "keyword"},
                "imdb_rating": {"type": "float"},
                "genre": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {"raw": {"type": "keyword"}},
                },
                "description": {"type": "text", "analyzer": "ru_en"},
                "director": {"type": "text", "analyzer": "ru_en"},
                "actors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "name": {"type": "text", "analyzer": "ru_en"},
                    },
                },
                "writers": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "name": {"type": "text", "analyzer": "ru_en"},
                    },
                },
            },
        }
    }
    try:
        if not es_object.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            es_object.indices.create(index=index_name, body=settings)
            print('Created Index')
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created


@backoff()
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
            transform = transform_data()
            description = cursor.description
            names_of_colums = list(map(lambda x: x[0], description))
            names_with_values = dict(zip(names_of_colums, row))
            doc = {
                names_of_colums[0]: names_with_values["id"],
                names_of_colums[5]: float(names_with_values["imdb_rating"]),
                names_of_colums[2]: names_with_values["genre"],
                names_of_colums[1]: names_with_values["title"],
                names_of_colums[3]: names_with_values["description"],
                names_of_colums[4]: names_with_values["director"],
                'actors': {'name': list(names_with_values["actors"])},
                'writers': {'name': list(names_with_values["writers"])}
            }
            state = State('latest', doc)
            state.set_state()

            JsonFileStorage('state.json').load_json_state()
            try:
                transform.send(doc)
            except StopIteration:
                print('Extract')
            except RuntimeError:
                break


@coroutine
def transform_data():
    data = yield
    data['imdb_rating'] = str(data['imdb_rating'])
    transformed_data = json.dumps(data)
    loader = load_data(connect_elasticsearch(), 'movies')
    try:
        loader.send(transformed_data)
    except StopIteration:
        print('Transform')


@coroutine
def load_data(elastic_object, index_name):
    data_to_load = yield
    elastic_object.index(body=data_to_load, index=index_name)
    print('Load')


def get_last_state():
    return RedisStorage(Redis()).retrieve_state()
    # return JsonFileStorage('state.json').retrieve_state()


if __name__ == '__main__':
    es = Elasticsearch()
    create_index(es, index_name='movies')
    extract_data()
    transform_data()
    load_data(elastic_object=es, index_name='movies')
    print(get_last_state())
