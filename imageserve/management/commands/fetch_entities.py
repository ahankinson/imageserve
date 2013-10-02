from django.core.management.base import BaseCommand
from imageserve.models import Manuscript
from imageserve.ismi.entity import update_manuscripts


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        mss = Manuscript.objects.all()
        update_manuscripts(mss)