import graphene
from graphene.types import interface
from graphene.types.scalars import ID, Boolean, Int, String
from graphene.types.structures import List
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.forms import forms
from graphene_django.forms.mutation import DjangoModelFormMutation

from graphene import relay, ObjectType


from .models import Album, Image, ImageProcessor, Keyword


class KeywordNode(DjangoObjectType):
    class Meta:
        model = Keyword
        fields = '__all__'


class ImgNode(DjangoObjectType):
    class Meta:
        model = Image
        interfaces = (relay.Node, )
        filter_fields = {
            'title': ['iexact', 'icontains', 'istartswith'],
            'keywords': ['icontains'],
            'description': ['icontains', 'istartswith'],
        }
        fields = '__all__'

    keywords = graphene.List(KeywordNode)



class Query(ObjectType):
    image = relay.Node.Field(ImgNode)
    all_images = DjangoFilterConnectionField(ImgNode)


class ImgType(DjangoObjectType):
    class Meta:
        model = Image





class AddImg(graphene.Mutation):
    class Arguments:
        # Input arguments for mutation
        title = graphene.String(required=True)

        keywords = graphene.List(graphene.String)
        description = graphene.String()
        image_string = graphene.String()

    img = graphene.Field(ImgType)
    ok = Boolean()
    ori_path = String()
    thumbnail_path = String()
    id = Int()

    @classmethod
    def mutate(cls, root, info, title: str, keywords: List(str), description: str, image_string: str):
        imageProcessor = ImageProcessor(image_string)

        ori_path = imageProcessor.get_filename()
        thumbnail_path = imageProcessor.get_thumbnail_filename()

        img = Image(
            title=title,
            description=description,
            ori_path=ori_path,
            thumbnail_path=thumbnail_path
        )

        img.save()

        for k in keywords:
            kw = Keyword.objects.get_or_create(word=k)
            kw = Keyword.objects.get(word=k)

            img.keywords.add(kw)

        img.save()
        ok = True

        return AddImg(
            img=img,
            ok=ok,
            ori_path=ori_path,
            thumbnail_path=thumbnail_path,
            id=img.pk
        )

        )


class Mutation(graphene.ObjectType):
    add_image = AddImg.Field()
    update_image = ImgMutation.Field()
