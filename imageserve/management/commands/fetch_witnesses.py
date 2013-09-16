from django.core.management.base import BaseCommand
from imageserve.models import Manuscript
from imageserve.ismi.witness import fetch_mss_witnesses


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        mss = Manuscript.objects.all()
        fetch_mss_witnesses(mss)