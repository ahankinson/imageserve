from django.core.management.base import BaseCommand
from imageserve.models import Witness
from imageserve.ismi.text import fetch_witness_texts


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        wits = Witness.objects.all()
        fetch_witness_texts(wits)