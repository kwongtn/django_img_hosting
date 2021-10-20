from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Album, Image, Keyword


@registry.register_document
class ImageDocument(Document):
    keywords = fields.ObjectField(
        properties={
            'word': fields.TextField()
        }
    )

    album = fields.ObjectField(
        properties={
            'name': fields.TextField()
        }
    )

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
            'description',
            'thumbnail_path',
            'ori_path',
        ]
        related_models = [Album, Keyword]

    # def get_queryset(self):
    #     """Not mandatory but to improve performance we can select related in one sql request"""
    #     return super(ImageDocument, self).get_queryset().select_related(
    #         'keywords'
    #     )

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Car instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, Image):
            return related_instance.keywords
        elif isinstance(related_instance, Image):
            return related_instance.album
