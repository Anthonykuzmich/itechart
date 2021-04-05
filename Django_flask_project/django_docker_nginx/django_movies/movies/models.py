import uuid

from django.db import models
from model_utils.fields import AutoCreatedField, AutoLastModifiedField
from django.utils.translation import gettext_lazy as _
from django.db.models import signals

from elasticsearch import Elasticsearch, helpers, RequestsHttpConnection

ES_CLIENT = Elasticsearch(hosts={'0.0.0.0'})


class Actor(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'actor'
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'genre'
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return self.name


class Writer(models.Model):
    id = models.CharField(primary_key=True, max_length=36,
                          default=uuid.uuid4())
    name = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'writer'
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return self.name


def update_elasticsearch(sender, instance, created, **kwargs):
    # res = ES_CLIENT.index(index='movies_dab', body=kwargs, refresh=True)
    # doc = {
    #     names_of_colums[0]: instance.id,
    #     names_of_colums[5]: instance.imdb_rating,
    #     names_of_colums[2]: instance.genre,
    #     names_of_colums[1]: instance.title,
    #     names_of_colums[3]: instance.description,
    #     names_of_colums[4]: instance.director,
    #     'actors': {'name': list(instance.actors)},
    #     'writers': {'name': list(names_with_values["writers"])}
    # }
    print(instance.title)
    for a in instance.actors.all():
        print(a)


def hex_uuid():
    return uuid.uuid4()


class Movie(models.Model):
    id = models.CharField(primary_key=True, max_length=40, default=hex_uuid, editable=False)
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    director = models.TextField(blank=True, null=True)
    imdb_rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    genres = models.ManyToManyField(Genre, through='MovieGenre')
    actors = models.ManyToManyField(Actor, through='MovieActor')
    writers = models.ManyToManyField(Writer, through='MovieWriter')
    created_at = AutoCreatedField(_("created"))
    updated_at = AutoLastModifiedField(_("modified"))

    class Meta:
        managed = False
        db_table = 'movie'
        indexes = [models.Index(fields=['title'])]

    def __str__(self):
        return self.title


signals.post_init.connect(receiver=update_elasticsearch, sender=Movie)


class MovieGenre(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'movie_genre'
        unique_together = (('movie', 'genre'),)
        indexes = [models.Index(fields=['genre', 'movie'])]


class MovieActor(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'movie_actor'
        unique_together = (('movie', 'actor'),)
        indexes = [models.Index(fields=['actor', 'movie'])]


class MovieWriter(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    writer = models.ForeignKey(Writer, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'movie_writer'
        unique_together = (('movie', 'writer'),)
        indexes = [models.Index(fields=['writer', 'movie'])]
