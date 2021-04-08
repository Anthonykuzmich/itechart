db_configurations = ('''
create table IF NOT EXISTS movie
(
    id char(40) primary key,
    title       text,
    description text,
    director    text,
    imdb_rating NUMERIC(3,1) NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS genre 
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(40) NOT NULL
);

CREATE TABLE IF NOT EXISTS movie_genre
(
    id SERIAL PRIMARY KEY,
    movie_id char(40) NOT NULL,
    genre_id int NOT NULL
);

create table IF NOT EXISTS actor
(
    id  serial PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- auto-generated definition
create table IF NOT EXISTS movie_actor
(
    id serial PRIMARY KEY,
    movie_id char(40) NOT NULL ,
    actor_id int NOT NULL
);

create table IF NOT EXISTS writer
(
    id CHAR(40) PRIMARY KEY,
    name VARCHAR(40) NOT NULL
);

create table IF NOT EXISTS movie_writer
(   id serial primary key,
    movie_id char(40) not null,
    writer_id char(40) not null
);


CREATE UNIQUE INDEX IF NOT EXISTS film_work_actor ON
movie_actor (movie_id, actor_id);

CREATE UNIQUE INDEX IF NOT EXISTS film_work_writer ON
movie_writer (movie_id, writer_id);

CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre  ON 
movie_genre (movie_id, genre_id);
''')


