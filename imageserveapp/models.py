from os import listdir
from os.path import isdir, join
from django.db import models
from conf import IMG_DIR
from south.modelsinspector import add_introspection_rules

add_introspection_rules([],["^imageserveapp\.models\.FolderField"])

class FolderField(models.FilePathField):
	'''
	In Django 1.5 this is implemented already, but this is just
	a shortcut so we can use folders instead of files.
	'''
	def __init__(self, *args, **kwargs):
		d = kwargs['path']
		kwargs['choices'] = [(name,name) for name in listdir(d) if isdir(join(d,name))]
		super(FolderField,self).__init__(*args, **kwargs)

class Manuscript(models.Model):
	directory = FolderField(path=IMG_DIR)
	ismi_id = models.IntegerField(blank=True, null=True)
	num_files = models.IntegerField(editable=False)
	
	def save(self, *args, **kwargs):
		self.num_files = len(listdir(join(IMG_DIR, self.directory)))
		super(Manuscript, self).save(*args, **kwargs)
	
	def __unicode__(self):
		return self.directory

class ManuscriptGroup(models.Model):
	pass