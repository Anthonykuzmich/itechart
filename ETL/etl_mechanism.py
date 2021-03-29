import json
from elasticsearch import Elasticsearch, helpers
from pydantic import BaseModel, ValidationError
import psycopg2
from configs.backoff_decorator import backoff

dsn = {
    "dbname": "movies",
    "user": "postgres",
    "password": "123qwe",
    "host": "0.0.0.0",
    "port": 5432,
}



@backoff()
def connect_elasticsearch():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if not es.ping():
        raise ValueError("Connection failed")
    return es


def create_index(es_object, index_name='movies'):
    created = False
    # index settings
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "members": {
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "text"
                    },
                    "title": {
                        "type": "text"
                    },
                    "genre": {
                        "type": "nested",
                        "properties": {
                            "name": {"type": "text"}
                        },
                    },
                    "description": {
                        "type": "text"
                    },
                    "director": {
                        "type": "text"
                    },
                    "imdb_rating": {
                        "type": "float"
                    },
                    "writers": {
                        "type": "nested",
                        "properties": {
                            "name": {"type": "text"}
                        },
                    },
                    "actors": {
                        "type": "nested",
                        "properties": {
                            "name": {"type": "text"}
                        },
                    },
                }
            }
        }
    }
    try:
        if not es_object.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            es_object.indices.create(index=index_name, ignore=400, body=settings)
            print('Created Index')
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created


class Movie(BaseModel):
    id: str
    title: str
    genre: list
    description: str = None
    director: str = None
    imdb_rating: float
    writers: list
    actors: list


@backoff()
def extract_data():
    with psycopg2.connect(**dsn) as conn, conn.cursor() as cursor:
        cursor.execute('''select m.id, m.title, array_agg(DISTINCT g.name) as genre,m.description, m.director, m.imdb_rating,
        array_agg(DISTINCT w.name) as writers, array_agg(DISTINCT a.name) as actors from movie m
        LEFT JOIN movie_actor ma on m.id = ma.movie_id
        LEFT JOIN actor a on ma.actor_id = a.id
        LEFT JOIN movie_writer mw on m.id = mw.movie_id
        LEFT JOIN writer w on mw.writer_id = w.id
        LEFT JOIN movie_genre mg on m.id = mg.movie_id
        LEFT JOIN genre g on mg.genre_id = g.id
        group by m.id;''')
        data = cursor.fetchall()
        description = cursor.description
        return {'data': data, 'description': description}


def transform_data():
    data = extract_data()['data']
    description = extract_data()['description']
    names_of_colums = list(map(lambda x: x[0], description))
    for row in data:
        names_with_values = dict(zip(names_of_colums, row))
        doc = {
            names_of_colums[0]: names_with_values["id"],
            names_of_colums[1]: names_with_values["title"],
            names_of_colums[2]: names_with_values["genre"],
            names_of_colums[3]: names_with_values["description"],
            names_of_colums[4]: names_with_values["director"],
            names_of_colums[5]: float(names_with_values["imdb_rating"]),
            names_of_colums[6]: list(names_with_values["writers"]),
            names_of_colums[7]: list(names_with_values["actors"])
        }
        doc = json.dumps(doc)
        try:
            movie = Movie.parse_raw(doc)
            return 'the data is valid'
        except ValidationError as e:
            print(str(e))

        yield doc


def load_data(elastic_object, data, index_name):
    try:
        helpers.bulk(client=elastic_object, actions=data, index=index_name)
        print('Data was successfully inserted!!!')
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))


if __name__ == '__main__':
    es = connect_elasticsearch()
    create_index(es)
    extract_data()
    transform_data()
    load_data(elastic_object=es, data=transform_data(), index_name='movies')
