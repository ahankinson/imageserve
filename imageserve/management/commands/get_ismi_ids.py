import os

from imageserve.ismi import api
from imageserve.ismi import parse

from django.core.management.base import BaseCommand
from django.conf import settings
from imageserve.models import Manuscript


class Command(BaseCommand):
    help = 'Updates as many ISMI IDs for Stabi codices as possible'

    def handle(self, *args, **kwargs):
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



    # def handle(self, *args, **options):
    #     u = requests.get("{0}method=get_ents&oc=CODEX".format(settings.JSON_INTERFACE))
    #     ents = json.loads(u.read())['ents']
    #     u.close()
    #     pairs = []
    #     for ent in ents:
    #         if ent.get('ov'):
    #             ent['ov'] = ent['ov'].replace('.','').replace(' ','_')
    #     for directory in STABI_CODICES:
    #         matches = [e for e in ents if e.get('ov') == directory]
    #         if matches:
    #             pairs.append((directory, matches[0]['id']))
    #     for directory, ismi_id in pairs:
    #         print("getting ISMI ID for {0} ...".format(directory))
    #         ms = Manuscript.objects.filter(directory=directory)
    #         if ms:
    #             try:
    #                 ms = Manuscript.objects.get(directory=directory)
    #                 ms.ismi_id = ismi_id
    #                 ms.clean()
    #                 ms.save()
    #                 print('done.')
    #             except ValidationError:
    #                 print ('{0} failed.'.format(directory))
    #                 continue
    #         else:
    #             print('{0} not found.'.format(directory))