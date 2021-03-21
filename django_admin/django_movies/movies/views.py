from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from .models import Movie, MovieGenre, MovieActor, MovieWriter


class MovieListApi(BaseListView):
    model = Movie
    http_method_names = ['get']

    def get_queryset(self):
        movies = Movie.objects.values().annotate(
            genres=ArrayAgg('genres__name', distinct=True),
            actors=ArrayAgg('actors__name', distinct=True),
            writers=ArrayAgg('writers__name', distinct=True))
        return movies

    def get_context_data(self, **kwargs):
        context = super(MovieListApi, self).get_context_data(**kwargs)

        page = self.request.GET.get("page")
        paginator = Paginator(self.get_queryset(), 50)
        try:
            page_obj = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            page_obj = paginator.page(1)

        context["page_obj"] = page_obj
        return context

    def render_to_response(self, context):
        context = self.get_context_data()
        return JsonResponse(list(context['page_obj']), safe=False)


class MovieDetailApi(BaseDetailView):
    model = Movie
    http_method_names = ['get']

    def get_queryset(self):
        movie_id = self.kwargs.get('pk')
        movie = Movie.objects.filter(id__exact=movie_id).values().annotate(
            genres=ArrayAgg('genres__name', distinct=True),
            actors=ArrayAgg('actors__name', distinct=True),
            writers=ArrayAgg('writers__name', distinct=True))
        return movie

    def get_context_data(self, **kwargs):
        context = {
            'results': list(self.get_queryset())
        }
        return context

    def render_to_response(self, context, **response_kwarg):
        context = self.get_context_data()
        return JsonResponse(context, safe=False)
