import string
import random

from django.db import models
from django.urls import reverse


class Actors(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'actors'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'genre'

    def __str__(self):
        return self.name


class Writers(models.Model):
    id = models.CharField(primary_key=True, max_length=40, editable=False, default=''.join(random.choices(string.ascii_uppercase
                                                                                          + string.digits, k=40)))
    name = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'writers'

    def __str__(self):
        return self.name


def get_absolute_url():
    return reverse('')


class Movie(models.Model):
    id = models.CharField(primary_key=True, max_length=10, default=''.join(random.choices(string.ascii_uppercase
                                                                                          + string.digits, k=9)))
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    director = models.TextField(blank=True, null=True)
    imdb_rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'movies'

    def __str__(self):
        return self.title


class GenreMovies(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'genre_movies'
        unique_together = (('movie', 'genre'),)


class MovieActors(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actors, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'movie_actors'
        unique_together = (('movie', 'actor'),)


class MovieWriters(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    movie = models.ForeignKey(Movie, max_length=10, on_delete=models.CASCADE)
    writer = models.ForeignKey(Writers, max_length=40, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'movie_writers'
        unique_together = (('movie', 'writer'),)
