db_configurations = ('''
create table IF NOT EXISTS movies
(
    id char(10) primary key,
    title       text,
    description text,
    genre       text,
    director    text,
    imdb_rating NUMERIC(3,1) NULL
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
movie_actors (movie_id, id, actor_id);

CREATE UNIQUE INDEX IF NOT EXISTS film_work_writer ON
movie_writers (movie_id, id, writer_id);
''')
