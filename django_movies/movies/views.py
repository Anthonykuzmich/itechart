from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from .models import Movie, MovieGenre, MovieActor, MovieWriter


class MovieListApi(BaseListView):
    model = Movie
    http_method_names = ['get']

    def get_queryset(self):
        movies = Movie.objects.all().values()
        for movie in movies:
            genre_query = MovieGenre.objects.filter(movie__id=f'{movie["id"]}').values('genre__name')
            movie["genres"] = [genre["genre__name"] for genre in genre_query]

            writer_query = MovieWriter.objects.filter(movie__id=f'{movie["id"]}').values('writer__name')
            movie["writers"] = [writer["writer__name"] for writer in writer_query]

            actor_query = MovieActor.objects.filter(movie__id=f'{movie["id"]}').values('actor__name')
            movie["actors"] = [actor["actor__name"] for actor in actor_query]

        return movies

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            'results': list(self.get_queryset())
        }
        return context

    def render_to_response(self, context):
        context = self.get_context_data()
        return JsonResponse(context, safe=False)


class MoviesDetailApi(BaseDetailView):
    model = Movie
    http_method_names = ['get']

    def get_queryset(self):
        id = self.kwargs.get('pk')
        movies = Movie.objects.filter(id=id)
        # for movie in movies:
        #     genre_query = MovieGenre.objects.filter(movie__id=f'{movie["id"]}').values('genre__name')
        #     movie["genres"] = [genre["genre__name"] for genre in genre_query]
        #
        #     writer_query = MovieWriter.objects.filter(movie__id=f'{movie["id"]}').values('writer__name')
        #     movie["writers"] = [writer["writer__name"] for writer in writer_query]
        #
        #     actor_query = MovieActor.objects.filter(movie__id=f'{movie["id"]}').values('actor__name')
        #     movie["actors"] = [actor["actor__name"] for actor in actor_query]

        return movies

    def get_context_data(self, **kwargs):
        context = {'results': self.get_queryset()}
        return context

    def render_to_response(self, context, **response_kwarg):
        context = self.get_context_data()
        return JsonResponse(context, safe=False)
