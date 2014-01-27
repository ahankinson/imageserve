from django.conf import settings


def diva_settings(request):
    return {'OBJECT_DATA': settings.OBJECT_DATA,
            'IIPSERVER_URL': settings.IIPSERVER_URL,
            'IMG_DIR': settings.IMG_DIR}