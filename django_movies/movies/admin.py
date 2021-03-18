from django.contrib import admin
from .models import Movie, Actors, Genre, Writers, MovieActors, GenreMovies


class ActorInline(admin.TabularInline):
    model = MovieActors
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('actor', )


class GenreInline(admin.TabularInline):
    model = GenreMovies
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
        GenreInline, ActorInline
    ]


admin.site.register(Actors)
admin.site.register(Genre)
admin.site.register(Writers)
