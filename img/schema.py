import graphene
from graphene.types import interface
from graphene.types.scalars import Boolean, String
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import base64
import hashlib

from graphene import relay, ObjectType

from .models import Keyword, Image, ImageProcessor


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



class AddImg(graphene.Mutation):
    class Arguments:
        # Input arguments for mutation
        title = graphene.String(required=True)

        # Temporary implementation
        keyword = graphene.String()
        # keywords = graphene.List(graphene.String)
        description = graphene.String()
        image_string = graphene.String()

    img = graphene.Field(ImgType)
    ok = Boolean()
    ori_path = String()
    thumbnail_path = String()

    @classmethod
    def mutate(cls, root, info, title: str, keyword: str, description: str, image_string: str):
        # Check if keywords exist, else add them
        # print(str(keywords))
        # for k in keywords:
        #     print(k)
        #     Keyword.objects.get_or_create(word=k)

        k = Keyword.objects.get_or_create(word=keyword)
        k = Keyword.objects.get(word=keyword)

        imageProcessor = ImageProcessor(image_string)

        ori_path = imageProcessor.get_filename()
        thumbnail_path = imageProcessor.get_thumbnail_filename()

        img = Image(
            title=title,
            keywords=k,
            description=description,
            ori_path=ori_path,
            thumbnail_path=thumbnail_path
        )

        img.save()
        ok = True

        return AddImg(
            img=img,
            ok=ok,
            ori_path=ori_path,
            thumbnail_path=thumbnail_path
        )


class Mutation(graphene.ObjectType):
    add_image = AddImg.Field()
