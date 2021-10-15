from django.conf import settings

import base64


def save_image(img_data: bytes, path: str):
    path = settings.STATIC_URL + path + '.jpg'
    with open("." + path, "wb") as fh:
        fh.write(img_data)

    return path