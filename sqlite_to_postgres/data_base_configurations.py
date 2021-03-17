db_configurations = ('''
create table IF NOT EXISTS movies
(
    id char(10) primary key,
    title       text,
    description text,
    director    text,
    imdb_rating NUMERIC(3,1) NULL
);

CREATE TABLE IF NOT EXISTS genre 
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(40) NOT NULL
);

CREATE TABLE IF NOT EXISTS genre_movies
(
    id SERIAL PRIMARY KEY,
    movie_id char(10) NOT NULL,
    genre_id int NOT NULL
);

create table IF NOT EXISTS actors
(
    id  serial PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- auto-generated definition
create table IF NOT EXISTS movie_actors
(
    id serial PRIMARY KEY,
    movie_id char(10) NOT NULL ,
    actor_id int NOT NULL
);

create table IF NOT EXISTS writers
(
    id CHAR(40) PRIMARY KEY,
    name VARCHAR(40) NOT NULL
);

create table IF NOT EXISTS movie_writers
(   id serial primary key,
    movie_id char(10) not null,
    writer_id VARCHAR(40) not null
);


CREATE UNIQUE INDEX IF NOT EXISTS film_work_actor ON
movie_actors (movie_id, actor_id);

CREATE UNIQUE INDEX IF NOT EXISTS film_work_writer ON
movie_writers (movie_id, writer_id);

CREATE UNIQUE INDEX film_work_genre ON genre_movies
(movie_id, genre_id);
''')


