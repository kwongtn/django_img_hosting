from PIL import Image as PILImage
import base64
import hashlib
from django.db import models
from django.conf import settings

# Create your models here.


class Keyword(models.Model):
    word = models.TextField(unique=True)

    def __str__(self):
        return self.word


class Image(models.Model):
    title = models.TextField()
    keywords = models.ForeignKey(
        Keyword,
        related_name='keywords',
        on_delete=models.CASCADE,
    )
    description = models.TextField()
    thumbnail_path = models.TextField()
    ori_path = models.TextField()
    img_str = models.TextField()

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


    def save_image(self):
        with open('.' + self.get_filename(True), "wb") as fh:
            fh.write(base64.standard_b64decode(self.base64_str))


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
