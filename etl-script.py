import sqlite3
from elasticsearch import Elasticsearch

conn = sqlite3.connect('db.sqlite')
cur = conn.cursor()
es = Elasticsearch()

# creation writer table in ES
cur.execute("DELETE FROM actors WHERE name='N/A'")
cur.execute("DELETE FROM writers WHERE name='N/A'")
cur.execute("UPDATE movies SET director = 'None' WHERE director = 'N/A'")
data = cur.execute('''
SELECT m.id, group_concat(a.name) actors_name, m.title, m.genre, m.director, w.name writer_name from actors a
INNER JOIN movie_actors ma on a.id = ma.actor_id
INNER JOIN movies m on m.id = ma.movie_id
INNER JOIN writers w on m.writer = w.id
GROUP BY m.id;
''').fetchall()
names = list(map(lambda x: x[0], cur.description))
for row in data:
    names_with_values = dict(zip(names, row))
    doc = {
        names[0]: names_with_values['id'],
        names[1]: names_with_values['actors_name'],
        names[2]: names_with_values['title'],
        names[3]: names_with_values['genre'],
        names[4]: names_with_values['director'],
        names[5]: names_with_values['writer_name']
    }
    res = es.index(index='movies', id=names_with_values['id'], body=doc)
conn.commit()
conn.close()
