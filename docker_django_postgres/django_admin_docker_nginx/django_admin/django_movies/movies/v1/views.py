from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import Movie


class MovieListApi(BaseListView):
    model = Movie
    http_method_names = ['get']
    paginate_by = 50

    def get_queryset(self):
        movies = Movie.objects.values().annotate(
            genres=ArrayAgg('genres__name', distinct=True),
            actors=ArrayAgg('actors__name', distinct=True),
            writers=ArrayAgg('writers__name', distinct=True)).order_by('-imdb_rating')
        return movies

    def get_context_data(self, **kwargs):
        data = self.get_queryset()

        page = self.request.GET.get("page")
        paginator = Paginator(data, self.paginate_by)
        try:
            page_obj = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            page_obj = paginator.page(1)

        prev_page = (
            page_obj.previous_page_number()
            if page_obj.has_previous()
            else None
        )
        next_page = (
            page_obj.next_page_number()
            if page_obj.has_next()
            else None
        )
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": prev_page,
            "next": next_page,
            "results": list(page_obj),
        }
        return context

    def render_to_response(self, context):
        return JsonResponse(context, safe=False)


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
