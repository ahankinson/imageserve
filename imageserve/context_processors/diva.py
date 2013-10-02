from django.conf import settings


def diva_settings(request):
    return {'DIVASERVE_URL': settings.DIVASERVE_URL,
            'IIPSERVER_URL': settings.IIPSERVER_URL,
            'IMG_DIR': settings.IMG_DIR}