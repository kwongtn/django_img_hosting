import graphene
from graphene.types import interface
from graphene.types.scalars import Boolean, String
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import base64
import hashlib

from graphene import relay, ObjectType

from functions.img_saver import save_image

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

    @classmethod
    def mutate(cls, root, info, title, keyword, description, image_string):
        # Check if keywords exist, else add them
        # print(str(keywords))
        # for k in keywords:
        #     print(k)
        #     Keyword.objects.get_or_create(word=k)

        k = Keyword.objects.get_or_create(word=keyword)
        k = Keyword.objects.get(word=keyword)

        # Process & save the image
        # print(image_string)
        hash = hashlib.sha1(image_string.encode('utf-8')).hexdigest()

        # print(base64.standard_b64decode(image_string))
        save_path = save_image(base64.standard_b64decode(image_string), hash)

        img = Image(
            title=title,
            keywords=k,
            description=description,
            img_str=image_string,
            ori_path=save_path
        )

        img.save()
        ok = True

        return AddImg(img=img, ok=ok)


class Mutation(graphene.ObjectType):
    add_image = AddImg.Field()
