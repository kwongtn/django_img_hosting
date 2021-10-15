import graphene
from graphene.types import interface
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from graphene import relay, ObjectType

from .models import Keyword, Image


class KeywordNode(DjangoObjectType):
    class Meta:
        model = Keyword
        interfaces = (relay.Node, )
        filter_fields = ['word', 'keywords']


class ImgNode(DjangoObjectType):
    class Meta:
        model = Image
        interfaces = (relay.Node, )
        filter_fields = {
            'title': ['iexact', 'icontains', 'istartswith'],
            'keywords': ['exact'],
            'description': ['icontains', 'istartswith'],
        }


class Query(ObjectType):
    image = relay.Node.Field(ImgNode)
    all_images = DjangoFilterConnectionField(ImgNode)

    keyword = relay.Node.Field(KeywordNode)
    all_keywords = DjangoFilterConnectionField(KeywordNode)
