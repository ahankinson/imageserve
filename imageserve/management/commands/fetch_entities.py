from django.core.management.base import BaseCommand
from imageserve.models import Manuscript
from imageserve.ismi.entity import update_manuscripts
from imageserve.management.commands import fetch_manuscripts
from imageserve.management.commands import fetch_witnesses
from imageserve.management.commands import fetch_texts
from imageserve.management.commands import fetch_people


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        fetch_manuscripts.fetch_manuscripts()
        fetch_witnesses.fetch_witnesses()
        fetch_texts.fetch_texts()
        fetch_people.fetch_people()