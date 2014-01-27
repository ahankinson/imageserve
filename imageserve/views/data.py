import json
import httplib2

from django.http import HttpResponse, HttpResponseServerError
from django.conf import settings

class JsonResponse(HttpResponse):
    def __init__(self, content, content_type='application/json', status=None):
        super(JsonResponse, self).__init__(
            content=json.dumps(content),
            status=status,
            content_type=content_type)


def data_proxy(request, msname):
    req_url = "{0}/{1}".format("http://images.rasi.mcgill.ca/data", msname)
    h = httplib2.Http()
    resp, content = h.request(req_url, "GET")
    return HttpResponse(content)