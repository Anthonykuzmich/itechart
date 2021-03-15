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


def creation_movie_writers_table():
    names_of_colums = list(map(lambda x: x[0], cur.description))
    cur.execute(
        "CREATE TABLE IF NOT EXISTS movie_writers (movie_id text NOT NULL, writer_id text NOT NULL)"
    )
    conn.commit()
    for row in data_to_es():
        names_with_values = dict(zip(names_of_colums, row))
        writers = json.loads(names_with_values['writers'])

        for writer in writers:
            cur.execute('''INSERT INTO movie_writers (movie_id, writer_id) VALUES (?, ?)''', (names_with_values['id'],
                                                                                              writer['id']))

    conn.commit()


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

    data = cur.execute('''with x as (SELECT m.id, group_concat(a.id) as actors_ids, group_concat(a.name) as actors_names
    FROM movies m
    LEFT JOIN movie_actors ma on m.id = ma.movie_id
    LEFT JOIN actors a on ma.actor_id = a.id
    GROUP BY m.id)


    SELECT m.id, genre, director, title, plot, imdb_rating, x.actors_ids, x.actors_names,
    CASE
    WHEN m.writers = '' THEN '[{"id": "' || m.writer || '"}]'
    ELSE m.writers
    END AS writers, GROUP_CONCAT(DISTINCT w.id) as writers_ids, GROUP_CONCAT(DISTINCT w.name) as writers_names
    FROM writers w
        LEFT JOIN movie_writers mw on w.id = mw.writer_id
        left join movies m on mw.movie_id = m.id
        left join x on m.id=x.id
group by m.id''')
    names_of_colums = list(map(lambda x: x[0], cur.description))

    for row in data:
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
            names_of_colums[9]: names_with_values['writers_ids'],
            names_of_colums[10]: [names_with_values['writers_names']]
        }
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
    creation_movie_writers_table()
    data_to_es()
    migrating_to_es()
    conn.commit()
    conn.close()
