from django.contrib import admin
from imageserve.settings import JSON_INTERFACE
from imageserve.models import Manuscript, ManuscriptGroup, AttDisplaySetting, RelDisplaySetting
from json import loads
from urllib import urlopen

admin.site.register(Manuscript)
admin.site.register(ManuscriptGroup)
admin.site.register(AttDisplaySetting)
admin.site.register(RelDisplaySetting)

def register_defs():
	"""
	Gets all the relevant definitions for attributes and relations
	from the ISMI database and creates Setting objects for them.
	"""
	u = urlopen(JSON_INTERFACE+"method=get_defs")
	defs = loads(u.read())['defs']
	u.close()
	witness_def = [d for d in defs if d.get('ov') == 'WITNESS'][0]
	text_def = [d for d in defs if d.get('ov') == 'TEXT'][0]
	
	for att in witness_def['atts']:
	    if not AttDisplaySetting.objects.filter(name=att['ov']):
	        sett = AttDisplaySetting(name=att['ov'], on_ent='self')
	        sett.save()

	for att in text_def['atts']:
	    if not AttDisplaySetting.objects.filter(name=att['ov']):
	        sett = AttDisplaySetting(name=att['ov'], on_ent='is_exemplar_of')
	        sett.save()

	for rel in witness_def['src_rels']:
	    if not RelDisplaySetting.objects.filter(name=rel['name']) and rel['name'] != 'was_created_by':
	        sett = RelDisplaySetting(name=rel['name'], on_ent='self')
	        sett.save()

	for rel in text_def['src_rels']:
	    if not RelDisplaySetting.objects.filter(name=rel['name']):
	        sett = RelDisplaySetting(name=rel['name'], on_ent='is_exemplar_of')
	        sett.save()

	for rel in witness_def['tar_rels']:
	    if not RelDisplaySetting.objects.filter(name=rel['name']):
	        sett = RelDisplaySetting(name=rel['name'], on_ent='self')
	        sett.save() 

	for rel in text_def['tar_rels']:
	    if not RelDisplaySetting.objects.filter(name=rel['name']):
	        sett = RelDisplaySetting(name=rel['name'], on_ent='is_exemplar_of')
	        sett.save()

register_defs()