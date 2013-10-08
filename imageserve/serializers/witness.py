from rest_framework import serializers
from imageserve.models import Witness
from imageserve.serializers.text import TextSerializer

class WitnessSerializer(serializers.HyperlinkedModelSerializer):
    texts = TextSerializer()
    known = serializers.Field(source="known")
    data = serializers.CharField(required=False)

    class Meta:
        model = Witness
        fields = ('ismi_id',
                  'texts',
                  'known',
                  'folios',
                  'start_page',
                  'end_page',
                  'name',
                  'data')


# class KnownWitnessSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Witness
