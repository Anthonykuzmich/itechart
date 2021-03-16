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


def migrate_writers():
    with sqlite_open('db.sqlite') as cur:
        writers = cur.execute('select * from writers').fetchall()
        for writer in writers:
            print(writer)

migrate_writers()
