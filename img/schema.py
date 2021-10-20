from img.documents import ImageDocument
from .models import Album, Image, ImageProcessor, Keyword
import graphene
from graphene.types import interface
from graphene.types.scalars import ID, Boolean, Int, String
from graphene.types.structures import List
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.forms import forms
from graphene_django.forms.mutation import DjangoModelFormMutation

from graphene import relay, ObjectType


class KeywordNode(DjangoObjectType):
    id = graphene.ID(source='pk', required=True)

    class Meta:
        model = Keyword
        fields = '__all__'


class ImgNode(DjangoObjectType):
    id = graphene.ID(source='pk', required=True)

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


class AlbumNode(DjangoObjectType):
    id = graphene.ID(source='pk', required=True)

    class Meta:
        model = Album
        interfaces = (relay.Node, )
        filter_fields = {
            'name': ['iexact', 'icontains', 'istartswith'],
        }
        fields = '__all__'

        images = graphene.Field(ImgNode)


class Query(ObjectType):
    image = relay.Node.Field(ImgNode)
    all_images = DjangoFilterConnectionField(ImgNode)
    album = relay.Node.Field(AlbumNode)
    all_albums = DjangoFilterConnectionField(AlbumNode)


class ImgType(DjangoObjectType):
    class Meta:
        model = Image


class AlbumType(DjangoObjectType):
    class Meta:
        model = Album


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


class AddAlbum(graphene.Mutation):
    class Arguments:
        # Input arguments for mutation
        name = graphene.String(required=True)

    ok = Boolean()
    id = Int()

    @classmethod
    def mutate(cls, root, info, name: str):
        album = Album(name=name)
        album.save()

        ok = True

        return AddAlbum(ok=ok, id=album.pk)


class AddImageToAlbum(graphene.Mutation):
    class Arguments:
        # Input arguments for mutation
        id = graphene.Int(required=True)
        images = graphene.List(Int)

    # img_id = ID()
    ok = Boolean()
    # added = List(str)

    @classmethod
    def mutate(cls, root, info, id: int, images: List(int)):
        a = Album(pk=id)

        for i in images:
            i = Image(pk=i)
            i.album.add(a)
            i.save()

        ok = True

        return AddImageToAlbum(
            ok=ok,
            # added=images
        )


class DeleteAlbum(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = Boolean()

    @classmethod
    def mutate(cls, root, info, id: int):
        a = Album.objects.get(pk=id)
        a.delete()

        ok = True

        return DeleteAlbum(
            ok=ok
        )


class DeleteImageFromAlbum(graphene.Mutation):
    class Arguments:
        album_id = graphene.Int(required=True)
        ids = graphene.List(Int, required=True)

    ok = Boolean()

    @classmethod
    def mutate(cls, root, info, album_id: int, image_ids: List(int)):

        a = Album.objects.get(pk=album_id)

        for image_id in image_ids:
            img = Image.objects.get(pk=image_id)
            img.album.remove(a)

        ok = True

        return DeleteImageFromAlbum(
            ok=ok
        )


class Mutation(graphene.ObjectType):
    add_image = AddImg.Field()
    add_album = AddAlbum.Field()
    add_image_to_album = AddImageToAlbum.Field()
    delete_album = DeleteAlbum.Field()
    delete_image_from_album = DeleteImageFromAlbum.Field()
