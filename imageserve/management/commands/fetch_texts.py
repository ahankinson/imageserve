from django.core.management.base import BaseCommand
from imageserve.models import Witness
from imageserve.ismi.text import fetch_witness_texts

def fetch_texts():
    wits = Witness.objects.all()
    fetch_witness_texts(wits)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        fetch_texts()