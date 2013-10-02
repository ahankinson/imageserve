from rest_framework import generics
from rest_framework import permissions

from imageserve.models import Witness
from imageserve.serializers.witness import WitnessSerializer


class WitnessDetail(generics.RetrieveUpdateAPIView):
    model = Witness
    permission_classes = (permissions.AllowAny, )
    serializer_class = WitnessSerializer

    # def patch(self, request, *args, **kwargs):
    #     return HttpResponse()