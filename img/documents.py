from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Image


@registry.register_document
class ImageDocument(Document):
    class Index:
        name = 'images'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django: 
        model = Image
        fields = [
            'title',
            'keywords',
            'description',
            'thumbnail_path',
            'ori_path',
        ]
