from rest_framework import serializers
from imageserve.models import Witness
from imageserve.serializers.text import TextSerializer

class WitnessSerializer(serializers.HyperlinkedModelSerializer):
    texts = TextSerializer()
    known = serializers.Field(source="known")

    class Meta:
        model = Witness


class KnownWitnessSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Witness
