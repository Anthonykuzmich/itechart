from django.contrib import admin
from .models import Movie, Actor, Genre, Writer, MovieActor, MovieGenre, MovieWriter


class ActorInline(admin.TabularInline):
    model = MovieActor
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('actor')


class WriterInline(admin.TabularInline):
    model = MovieWriter
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('writer')


class GenreInline(admin.TabularInline):
    model = MovieGenre
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('genre')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    # отображение полей в списке
    list_display = ('title', 'description', 'imdb_rating')
    fields = (
        'title', 'description', 'director', 'imdb_rating',
    )
    inlines = [
        GenreInline, ActorInline, WriterInline
    ]
    list_filter = ('imdb_rating',)
    search_fields = ('title', 'description', 'id')


@admin.register(Writer)
class WriterAdmin(admin.ModelAdmin):
    list_display = ('name',)
    fields = ('name',)


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
