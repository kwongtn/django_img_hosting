from django.contrib import admin

from .models import Image, Keyword

# Register your models here.

admin.site.register(Image)
admin.site.register(Keyword)