from django.contrib import admin
from imageserve import JSON_INTERFACE
from imageserve.models import Manuscript, ManuscriptGroup, AttDisplaySetting, RelDisplaySetting
from json import loads
from urllib import urlopen

admin.site.register(Manuscript)
admin.site.register(ManuscriptGroup)
admin.site.register(AttDisplaySetting)
admin.site.register(RelDisplaySetting)

u = urlopen(JSON_INTERFACE+"method=get_defs")
defs = loads(u.read())['defs']
u.close()
witness_def = [d for d in defs if d.get('ov') == 'WITNESS'][0]
text_def = [d for d in defs if d.get('ov') == 'TEXT'][0]
del u
del defs

for att in witness_def['atts']:
    if not AttDisplaySetting.objects.filter(name=att['ov']):
        sett = AttDisplaySetting(name=att['ov'], on_ent=True)
        sett.save()

for att in text_def['atts']:
    if not AttDisplaySetting.objects.filter(name=att['ov']):
        sett = AttDisplaySetting(name=att['ov'], on_ent=False)
        sett.save()

for rel in witness_def['src_rels']:
    if not RelDisplaySetting.objects.filter(name=rel['name']):
        sett = RelDisplaySetting(name=rel['name'], rel_type='src', on_ent=True)
        sett.save()

for rel in text_def['src_rels']:
    if not RelDisplaySetting.objects.filter(name=rel['name']):
        sett = RelDisplaySetting(name=rel['name'], rel_type='src', on_ent=False)
        sett.save()

for rel in witness_def['tar_rels']:
    if not RelDisplaySetting.objects.filter(name=rel['name']):
        sett = RelDisplaySetting(name=rel['name'], rel_type='tar', on_ent=True)
        sett.save() 

for rel in text_def['tar_rels']:
    if not RelDisplaySetting.objects.filter(name=rel['name']):
        sett = RelDisplaySetting(name=rel['name'], rel_type='tar', on_ent=False)
        sett.save()