from django.core.management.base import BaseCommand
from imageserve.models import Text
from imageserve.ismi.person import fetch_text_people
# from imageserve.ismi.witness import fetch_mss_witnesses


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        texts = Text.objects.all()
        fetch_text_people(texts)