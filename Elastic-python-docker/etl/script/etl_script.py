import sqlite3
import time
import string
from elasticsearch import Elasticsearch
import json

host = [{"host": 'elasticsearch'}]

conn = sqlite3.connect('db.sqlite')
cur = conn.cursor()


def clear_data_table():
    cur.execute("delete from actors where name='N/A'")
    cur.execute("delete from writers where name='N/A'")
    cur.execute("update movies set director = null where director = 'None'")
    cur.execute("update movies set plot = null where plot = 'None'")
    cur.execute("update movies set imdb_rating = '0' where imdb_rating='N/A'")


def data_to_es():
    data = cur.execute('''
    with x as (SELECT m.id, group_concat(a.id) as actors_ids, group_concat(a.name) as actors_names
    FROM movies m
    LEFT JOIN movie_actors ma on m.id = ma.movie_id
    LEFT JOIN actors a on ma.actor_id = a.id
    GROUP BY m.id)
    
    
    SELECT m.id, genre, director, title, plot, imdb_rating, x.actors_ids, x.actors_names,
    CASE
    WHEN m.writers = '' THEN '[{"id": "' || m.writer || '"}]'
    ELSE m.writers
    END AS writers
    FROM movies m
    LEFT JOIN x ON m.id = x.id
    ''').fetchall()

    return data


def migrating_to_es():
    names_of_colums = list(map(lambda x: x[0], cur.description))
    for row in data_to_es():
        names_with_values = dict(zip(names_of_colums, row))

        doc = {
            names_of_colums[0]: names_with_values['id'],
            names_of_colums[1]: names_with_values['genre'],
            names_of_colums[2]: names_with_values['director'],
            names_of_colums[3]: names_with_values['title'],
            names_of_colums[4]: names_with_values['plot'],
            names_of_colums[5]: names_with_values['imdb_rating'],
            names_of_colums[6]: names_with_values['actors_ids'],
            names_of_colums[7]: names_with_values['actors_names'],
            names_of_colums[8]: names_with_values['writers']
        }
        writers = json.loads(names_with_values['writers'])
        for writer in writers:
            print(writer['id'])
        res = es.index(index='movies', id=names_with_values['id'], body=doc)


if __name__ == "__main__":
    es = Elasticsearch()
    for _ in range(100):
        try:
            # make sure the cluster is available
            es.cluster.health(wait_for_status='yellow')
        except ConnectionError:
            time.sleep(2)

    clear_data_table()
    data_to_es()
    # writers()
    migrating_to_es()
    conn.commit()
    conn.close()
