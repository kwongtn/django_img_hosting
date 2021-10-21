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


class ImgType(DjangoObjectType):
    class Meta:
        model = Image


class AlbumType(DjangoObjectType):
    class Meta:
        model = Album


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

    es_image = graphene.List(ImgType,
                             description_contains=graphene.List(
                                 graphene.String),
                             description_xcontains=graphene.List(
                                 graphene.String),
                             title_contains=graphene.List(graphene.String),
                             title_xcontains=graphene.List(graphene.String),
                             keyword_contains=graphene.List(graphene.String),
                             keyword_xcontains=graphene.List(graphene.String),
                             search=graphene.String(),
                             )

    def resolve_es_image(self, info, *args, **kwargs):
        s = ImageDocument.search()

        advSearchArr: dict(str, list(Q)) = {
            'must': [], 'must_not': []
        }
        if kwargs.get('description_contains') is not None:
            for elem in kwargs.get('description_contains'):
                advSearchArr['must'].append(Q('match', description=elem))

        if kwargs.get('description_xcontains') is not None:
            for elem in kwargs.get('description_xcontains'):
                advSearchArr['must_not'].append(Q('match', description=elem))

        if kwargs.get('title_contains') is not None:
            for elem in kwargs.get('title_contains'):
                advSearchArr['must'].append(Q('match', title=elem))

        if kwargs.get('title_xcontains') is not None:
            for elem in kwargs.get('title_xcontains'):
                advSearchArr['must_not'].append(Q('match', title=elem))

        if kwargs.get('keyword_contains') is not None:
            for elem in kwargs.get('keyword_contains'):
                advSearchArr['must'].append(Q('match', keyword__word=elem))

        if kwargs.get('keyword_xcontains') is not None:
            for elem in kwargs.get('keyword_xcontains'):
                advSearchArr['must_not'].append(Q('match', keyword__word=elem))

        if kwargs.get('search') is not None:
            s = s.query('multi_match', query=kwargs.get('search'),
                        fields=['title^3', 'keywords.word^2', 'description'],
                        type='phrase')

        if len(advSearchArr['must']) != 0 or len(advSearchArr['must_not']) != 0:
            q = Q('bool',
                  must=advSearchArr['must'],
                  must_not=advSearchArr['must_not'])
            s = s.query(q)

        return s.to_queryset()


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
        titles = graphene.List(String)

    # img_id = ID()
    ok = Boolean()
    # added = List(str)

    @classmethod
    def mutate(cls, root, info, id: int, images: List(int), titles: List(str)):
        a = Album(pk=id)

        for i in images:
            i = Image(pk=i)
            i.album.add(a)
            i.save()

        for t in titles:
            i = Image(title=t)
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
