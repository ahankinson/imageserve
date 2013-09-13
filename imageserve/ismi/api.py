import requests
from django.conf import settings


def fetch(method, *args, **kwargs):
    args = None
    if kwargs:
        args = ["{0}={1}".format(k, v) for k,v in kwargs.iteritems()]
    url = "{0}method={1}&{2}".format(settings.JSON_INTERFACE, method, '&'.join(args))

    print('sending URL: {0}'.format(url))

    r = requests.get(url, verify=True)

    return r.json()
