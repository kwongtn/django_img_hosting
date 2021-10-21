# syntax=docker/dockerfile:1

FROM python:3.9-alpine
ENV PYTHONUNBUFFERED=1

RUN mkdir code
WORKDIR /code

RUN pip install --upgrade pip

RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers \
    && pip install Pillow

RUN pip install django \
    graphene_django \
    django-filter \
    django-elasticsearch-dsl
    