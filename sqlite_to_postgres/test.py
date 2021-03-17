import sqlite3


class sqlite_open(object):
    """
    Simple CM for sqlite3 databases. Commits everything at exit.
    """

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_class, exc, traceback):
        self.conn.commit()
        self.conn.close()


def create_tables():
    with sqlite_open('db.sqlite') as cur:
        cur.execute('''CREATE TABLE genre (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name VARCHAR(40) NOT NULL
        );''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS genre_movies
(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    movie_id char(10) NOT NULL,
    genre_id int NOT NULL
                );''')


def migrate_genre():
    with sqlite_open('db.sqlite') as cur:
        genres = cur.execute('SELECT distinct genre from movies').fetchall()
        genre_list = []
        for genre in genres:
            for g in genre:
                g = g.split(',')
                for i in g:
                    genre_list.append(i)
        genres = set(genre_list)
        genre = tuple(genres)
        list_genres = []
        for g in genre:
            g = g.strip()
            list_genres.append(g)
        list_genres = set(list_genres)
        list_genres = tuple(list_genres)
        for genre in list_genres:

            cur.execute('INSERT INTO genre (name) VALUES (?)', (genre,))
        return genres


def migrate_movie_genre():
    with sqlite_open('db.sqlite') as cur:
        genre = cur.execute("select id, name from genre").fetchall()
        for gen in genre:
            test = cur.execute("select id, genre from movies where genre like (?)", ['%' + gen[1] + '%']).fetchall()
            for t in test:
                movie_genre = (t[0], gen[0])
                cur.execute('''INSERT INTO genre_movies (movie_id, genre_id) VALUES (?, ?)''',
                            movie_genre)


create_tables()
migrate_genre()
migrate_movie_genre()
