from rest_framework import serializers
from imageserve.models import Text

class TextSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Text
