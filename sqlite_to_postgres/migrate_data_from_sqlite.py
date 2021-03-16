import json
import sqlite3
import psycopg2
from data_base_configurations import db_configurations

dsn = {
    "dbname": "movies_db",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
    "port": 5432,
}


class sqlite_open(object):


    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_class, exc, traceback):
        self.conn.commit()
        self.conn.close()


def creation_postgres_db_structure():
    with psycopg2.connect(**dsn) as conn, conn.cursor() as cursor:
        cursor.execute(db_configurations)


def clear_data_sqlite():
    with sqlite_open("db.sqlite") as cur:
        cur.execute("delete from actors where name='N/A'")
        cur.execute("delete from writers where name='N/A'")
        cur.execute("update movies set director = null where director='N/A'")
        cur.execute("update movies set plot = null where plot='N/A'")
        cur.execute("update movies set imdb_rating = '0' where imdb_rating='N/A'")


def data_to_es():
    with sqlite_open("db.sqlite") as cur:
        data = cur.execute(
            """
        with x as (SELECT m.id, group_concat(a.id) as actors_ids, group_concat(a.name) as actors_names
        FROM movies m
        LEFT JOIN movie_actors ma on m.id = ma.movie_id
        LEFT JOIN actors a on ma.actor_id = a.id
        GROUP BY m.id)
    
    
        SELECT m.id, genre, director, title, plot as description, imdb_rating, x.actors_ids, x.actors_names,
        CASE
        WHEN m.writers = '' THEN '[{"id": "' || m.writer || '"}]'
        ELSE m.writers
        END AS writers
        FROM movies m
        LEFT JOIN x ON m.id = x.id
        """
        ).fetchall()
        return {"data": data, "description": cur.description}


def migrate_movies():
    data = data_to_es()["data"]
    description = data_to_es()["description"]
    names_of_colums = list(map(lambda x: x[0], description))

    for row in data:
        names_with_values = dict(zip(names_of_colums, row))
        doc = {
            names_of_colums[0]: names_with_values["id"],
            names_of_colums[1]: names_with_values["genre"],
            names_of_colums[2]: names_with_values["director"],
            names_of_colums[3]: names_with_values["title"],
            names_of_colums[4]: names_with_values["description"],
            names_of_colums[5]: float(names_with_values["imdb_rating"]),
        }

        data = (
            names_with_values["id"],
            names_with_values["title"],
            names_with_values["description"],
            float(names_with_values["imdb_rating"]),
            names_with_values["genre"],
            names_with_values["director"],
        )

        with psycopg2.connect(**dsn) as conn, conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO movies (id, title, description, imdb_rating, genre, director ) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
                data,
            )


def migrate_writers():
    with sqlite_open("db.sqlite") as cur:
        writers = cur.execute("select * from writers").fetchall()
        for writer in writers:
            with psycopg2.connect(**dsn) as conn, conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO writers (id, name) VALUES (%s, %s)""", writer
                )


def migrate_movie_writers():
    with sqlite_open("db.sqlite") as cur:
        data = data_to_es()["data"]
        description = data_to_es()["description"]
        names_of_colums = list(map(lambda x: x[0], description))
        for row in data:
            names_with_values = dict(zip(names_of_colums, row))
            writers = json.loads(names_with_values["writers"])

            for writer in writers:
                with psycopg2.connect(**dsn) as conn, conn.cursor() as cursor:
                    data = (names_with_values["id"], writer["id"])
                    cursor.execute(
                        """INSERT INTO movie_writers (movie_id, writer_id) VALUES (%s, %s)""",
                        data,
                    )


def migrate_actors():
    with sqlite_open("db.sqlite") as cur:
        actors = cur.execute("select * from actors").fetchall()
        for actor in actors:
            with psycopg2.connect(**dsn) as conn, conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO actors (id, name) VALUES (%s, %s)""", actor
                )


def migrate_movie_actors():
    with sqlite_open("db.sqlite") as cur:
        movie_actors = cur.execute("select * from movie_actors").fetchall()
        for movie_actor in movie_actors:
            with psycopg2.connect(**dsn) as conn, conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO movie_actors (movie_id, actor_id) VALUES (%s, %s)""",
                    movie_actor,
                )


if __name__ == "__main__":
    with psycopg2.connect(**dsn) as conn, conn.cursor() as cursor:
        cursor.execute(
            "select * from information_schema.tables where table_name=%s", ("actors",)
        )
        if bool(cursor.rowcount):
            print("the table is already created")
        else:
            clear_data_sqlite()
            creation_postgres_db_structure()
            data_to_es()
            migrate_writers()
            migrate_movies()
            migrate_movie_writers()
            migrate_actors()
            migrate_movie_actors()
