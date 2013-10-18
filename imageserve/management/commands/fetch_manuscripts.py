import os

from imageserve.ismi import api
from imageserve.ismi import parse

from django.core.management.base import BaseCommand
from django.conf import settings
from imageserve.models import Manuscript

def fetch_manuscripts():
    r = api.fetch("get_ents", oc="CODEX")
    entities = r.get('ents', None)

    for entity in entities:
        if entity.get('ov', None):
            entity_name = parse.name(entity.get('ov'))
            entity_id = int(entity.get('id'))
            directory = os.path.join(settings.IMG_DIR, entity_name)
            ms = Manuscript.objects.filter(directory=directory)
            if ms.exists():
                print("Matching {0} with {1} ID {2}".format(ms[0].directory, entity_name, entity_id))
                ms.update(ismi_id=entity_id)
            else:
                print("Entry for {0} not found.".format(entity_name))



class Command(BaseCommand):
    help = 'Updates as many ISMI IDs for Stabi codices as possible'

    def handle(self, *args, **kwargs):
        fetch_manuscripts()