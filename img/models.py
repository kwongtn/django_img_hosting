from PIL import Image as PILImage
import base64
import hashlib
from django.db import models
from django.conf import settings

# Create your models here.


class Album(models.Model):
    name = models.TextField()


class Keyword(models.Model):
    word = models.TextField()


class Image(models.Model):
    title = models.TextField()

    album = models.ManyToManyField(Album, related_name='images')

    # A space (or comma?) separated list of keywords
    keywords = models.ManyToManyField(Keyword, related_name='image')
    description = models.TextField()
    thumbnail_path = models.TextField()
    ori_path = models.TextField()

    def __str__(self):
        return self.title


class ImageProcessor():
    path = settings.STATIC_URL

    base64_str: str = ""
    extension: str = ""
    hash: str = ""

    thumbnail_size: int = 128

    def get_filename(self, withFilePath: bool = False) -> str:
        if withFilePath:
            return self.path + self.hash + "." + self.extension
        else:
            return self.hash + "." + self.extension

    def get_thumbnail_filename(self, withFilePath: bool = False) -> str:
        if withFilePath:
            return self.path + self.hash + "_thumb." + self.extension
        else:
            return self.hash + "_thumb." + self.extension

    def save_image(self):
        with open('.' + self.get_filename(True), "wb") as fh:
            fh.write(base64.standard_b64decode(self.base64_str))

    def save_thumbnail(self):
        with PILImage.open('.' + self.get_filename(True)) as im:
            im.thumbnail((self.thumbnail_size, self.thumbnail_size))

            if im.mode in ("RGBA", "P"):
                background = PILImage.new("RGB", im.size, (255, 255, 255))
                background.paste(im, mask = im.split()[3])
                im = background
                im = im.convert("RGB")

            im.save('.' + self.get_thumbnail_filename(True), "JPEG")

    def __init__(self, image_str, **kwargs):
        split_img: list[str] = image_str.split(',')
        if(len(split_img) > 1):
            self.base64_str = split_img[1]

            # self.extension = split_img[0].split(';')[0].split('/')[1]
            self.extension = 'jpg'

        else:
            self.base64_str = split_img[0]
            self.extension = 'jpg'

        # TODO: Error catching and conversions for those image that are not jpg

        self.hash = hashlib.sha1(self.base64_str.encode('utf-8')).hexdigest()

        self.save_image()
        self.save_thumbnail()
