from django.db import models

# Create your models here.


class Keyword(models.Model):
    word = models.TextField()

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

    def __str__(self):
        return self.title
