from urllib import urlopen
from json import loads
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from imageserve.models import Manuscript
from imageserve.settings import JSON_INTERFACE
from stabi_codices import STABI_CODICES


class Command(BaseCommand):
    help = 'Updates as many ISMI IDs for Stabi codices as possible'

    def handle(self, *args, **options):
        u = urlopen(JSON_INTERFACE+"method=get_ents&oc=CODEX")
        ents = loads(u.read())['ents']
        u.close()
        pairs = []
        for ent in ents:
            if ent.get('ov'):
                ent['ov'] = ent['ov'].replace('.','').replace(' ','_')
        for directory in STABI_CODICES:
            matches = [e for e in ents if e.get('ov') == directory]
            if matches:
                pairs.append((directory, matches[0]['id']))
        for directory, ismi_id in pairs:
            print 'getting ISMI ID for', directory, '...',
            ms = Manuscript.objects.filter(directory=directory)
            if ms:
                try:
                    ms = Manuscript.objects.get(directory=directory)
                    ms.ismi_id = ismi_id
                    ms.clean()
                    ms.save()
                    print 'done.'
                except ValidationError:
                    print directory, 'failed.'
                    continue
            else:
                print directory, 'not found.'