import string
import random
import uuid

from django.db import models
from django.urls import reverse


class Actor(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'actor'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'genre'

    def __str__(self):
        return self.name


class Writer(models.Model):
    id = models.CharField(primary_key=True, max_length=40, editable=False,
                          default=uuid.uuid4())
    name = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'writer'

    def __str__(self):
        return self.name


class Movie(models.Model):
    id = models.CharField(primary_key=True, max_length=10, default=uuid.uuid4())
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    director = models.TextField(blank=True, null=True)
    imdb_rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'movie'

    def __str__(self):
        return self.title


class MovieGenre(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'movie_genre'
        unique_together = (('movie', 'genre'),)


class MovieActor(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'movie_actor'
        unique_together = (('movie', 'actor'),)


class MovieWriter(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    movie = models.ForeignKey(Movie, max_length=10, on_delete=models.CASCADE)
    writer = models.ForeignKey(Writer, max_length=40, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'movie_writer'
        unique_together = (('movie', 'writer'),)
