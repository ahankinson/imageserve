from os import listdir
from os.path import isdir, join
from django.db import models
import dbsettings
from conf import IMG_DIR
from south.modelsinspector import add_introspection_rules
from imageserveapp import get_by_ismi_id, ismi_witness_def

add_introspection_rules([],["^imageserveapp\.models\.FolderField"])

class FolderField(models.FilePathField):
	"""
	In Django 1.5 this is implemented already, but this is just
	a shortcut so we can use folders instead of files.
	"""
	def __init__(self, *args, **kwargs):
		d = kwargs['path']
		kwargs['choices'] = [(name,name) for name in listdir(d)
		                     if isdir(join(d,name))]
		super(FolderField,self).__init__(*args, **kwargs)
	

class RelDisplaySettings(dbsettings.Group):
	"""
	Group of settings for how to display a single ISMI source-relation.
	"""
	name = dbsettings.StringValue(
		'the name for this relation to be displayed in the Metadata view'
	)
	show = dbsettings.BooleanValue(
		'whether to show this relation in the Metadata view'
	)
	show_id = dbsettings.BooleanValue(
		'whether to show the ID of the relation\'s '
		+'target/source in the Metadata view'
	)

# this is some deeply evil hackery. Oh Guido, forgive me for I have sinned.
# It's supposed to check with the ISMI database with the ismi_witness_def
# call, and then dynamically create classes for all of the attributes and
# relations, so that each one can have its own display settings. It actually
# seems to work perfectly and all the correct settings are maintained when
# you do syncdb or south migrations, so I'm going to count my lucky stars
# on this one.
w = ismi_witness_def()
for a in w['atts']:
	globals()[a['ov']+"_display_settings"] = type(
		str(a['ov']+"_display_settings"),
		(dbsettings.Group,),
		{
			'name': dbsettings.StringValue(
				'the name for this attribute to be '
				+'displayed in the Metadata view',
				default=a['ov'],
			),
			'show': dbsettings.BooleanValue(
				'whether to show this attribute in the Metadata view',
				default=True,
			),
		}
	)
	globals()[a['ov']] = type(
		str(a['ov']),
		(models.Model,),
		{
			'__module__': __name__,
			'display_settings': eval(a['ov']+"_display_settings()"),
		}
	)
for r in w['src_rels']+w['tar_rels']:
	globals()[r['name']+"_display_settings"] = type(
		str(r['name']+"_display_settings"),
		(dbsettings.Group,),
		{
			'name': dbsettings.StringValue(
				'the name for this relation to be '
				+'displayed in the Metadata view',
				default=r['name'],
			),
			'show': dbsettings.BooleanValue(
				'whether to show this relation in the Metadata view',
				default=True,
			),
			'show_id': dbsettings.BooleanValue(
				'whether to show the ID of the relation\'s '
				+'target/source in the Metadata view',
				default=False,
			)
		}
	)
	globals()[r['name']] = type(
		str(r['name']),
		(models.Model,),
		{
			'__module__': __name__,
			'display_settings': eval(r['name']+"_display_settings()"),
		}
	)

class Manuscript(models.Model):
	"""
	The model for all manuscripts in the RASI database.
	"""
	directory = FolderField(path=IMG_DIR)
	ismi_id = models.IntegerField(blank=True, null=True)
	num_files = models.IntegerField(editable=False)
	
	def author(self):
		"""
		Looks up the manuscript's author in the ISMI
		database and returns their name.
		
		TODO: use memcached for this, or wrap it in
		a metadata() method.
		"""
		ent = get_by_ismi_id(self.ismi_id)
		author_id = [rel for rel in ent['src_rels'] if
		             rel.get('name') == 'was_created_by'][0].get('tar_id')
		author = get_by_ismi_id(author_id)
		return author.get('ov')
	
	def title(self):
		"""
		Looks up the manuscript's ISMI entity and
		returns its title.
		
		TODO: use memcached for this, or wrap it in
		a metadata() method.
		"""
		ent = get_by_ismi_id(self.ismi_id)
		return ent.get('ov')
	
	def save(self, *args, **kwargs):
		self.num_files = len(listdir(join(IMG_DIR, self.directory)))
		super(Manuscript, self).save(*args, **kwargs)
	
	def __unicode__(self):
		return unicode(self.directory)

class ManuscriptGroup(models.Model):
	"""
	A group of manuscripts which fit
	under some common category.
	"""
	name = models.CharField(max_length=200, blank=True)
	manuscripts = models.ManyToManyField(Manuscript)
	
	def __unicode__(self):
		return unicode(self.name)
