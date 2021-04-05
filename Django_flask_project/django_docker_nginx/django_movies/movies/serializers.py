from rest_framework_elasticsearch.es_serializer import ElasticModelSerializer
from .models import Movie
from .search_indexes import BlogIndex

class ElasticBlogSerializer(ElasticModelSerializer):
    class Meta:
        model = Blog
        es_model = BlogIndex
        fields = ('pk', 'title', 'created_at', 'tags', 'body', 'is_published')