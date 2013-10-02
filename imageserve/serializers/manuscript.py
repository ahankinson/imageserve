from rest_framework import serializers
from imageserve.models.manuscript import Manuscript
from imageserve.serializers.witness import WitnessSerializer


class ManuscriptSerializer(serializers.HyperlinkedModelSerializer):
    # composer = ComposerSerializer()
    ms_name = serializers.Field(source="ms_name")
    has_unknown_witnesses = serializers.Field(source="has_unknown_witnesses")
    witnesses = WitnessSerializer()

    class Meta:
        model = Manuscript