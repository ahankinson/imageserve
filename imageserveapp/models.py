from os import listdir
from os.path import isdir, join
from django.db import models
from conf import IMG_DIR
from south.modelsinspector import add_introspection_rules
from imageserveapp import get_by_ismi_id

add_introspection_rules([],["^imageserveapp\.models\.FolderField"])

class FolderField(models.FilePathField):
	"""
	In Django 1.5 this is implemented already, but this is just
	a shortcut so we can use folders instead of files.
	"""
	def __init__(self, *args, **kwargs):
		d = kwargs['path']
		kwargs['choices'] = [(name,name) for name in listdir(d) if isdir(join(d,name))]
		super(FolderField,self).__init__(*args, **kwargs)

class Manuscript(models.Model):
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
		return self.directory

class ManuscriptGroup(models.Model):
	"""
	This will represent a group of manuscripts which fit
	under some common category, like styles/corpora or
	possibly permissions?
	"""
	pass

class MetadataConfiguration(models.Model):
	"""
	This will be some a kind of static object which holds
	preferences for which ISMI attributes and relations are
	included in a manuscript's metadata.
	"""
	pass