from rest_framework import generics
from rest_framework import permissions

from imageserve.models import Text
from imageserve.serializers.text import TextSerializer


class TextDetail(generics.RetrieveUpdateAPIView):
    model = Text
    permission_classes = (permissions.AllowAny, )
    serializer_class = TextSerializer

    # def patch(self, request, *args, **kwargs):
    #     return HttpResponse()