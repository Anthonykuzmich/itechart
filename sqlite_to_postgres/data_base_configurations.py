db_configurations = ('''
create table movies
(
    id uuid primary key,
    title       VARCHAR(100) NOT NULL,
    description text not null ,
    genre       VARCHAR(100) NOT NULL,
    director    VARCHAR(100) NOT NULL,
    imdb_rating NUMERIC(3,1) NULL
);


create table actors
(
    id  uuid PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- auto-generated definition
create table movie_actors
(
    id uuid PRIMARY KEY,
    movie_id uuid NOT NULL ,
    actor_id uuid NOT NULL
);

create table writers
(
    id uuid primary key,
    name VARCHAR(40) NOT NULL
);

create table movie_writers
(   id uuid primary key,
    movie_id  uuid not null,
    writer_id uuid not null
);


CREATE UNIQUE INDEX film_work_actor ON
movie_actors (movie_id, actor_id);

CREATE UNIQUE INDEX film_work_writer ON
movie_writers (movie_id, writer_id);
''')
