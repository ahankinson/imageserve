from os import listdir
from os.path import isdir, join
from django.db import models
from conf import IMG_DIR
from south.modelsinspector import add_introspection_rules

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
	

class AttDisplaySetting(models.Model):
	"""
	Global object in the database which holds the
	settings for whether and how a certain ISMI
	attribute (on either a Manuscript's associated
	WITNESS or the TEXT it is exemplar of) should
	be displayed in the Metadata view.
	"""
	name = models.CharField(max_length=200, unique=True, editable=False)
	display_name = models.CharField(max_length=200, null=True)
	show = models.BooleanField(default=True)
	on_ent = models.BooleanField(editable=False)
	
	def __unicode__(self):
		return unicode(self.name)
	
	def save(self, *args, **kwargs):
		if self.display_name is None:
			self.display_name = self.name
		super(AttDisplaySetting, self).save(*args, **kwargs)
	

class RelDisplaySetting(models.Model):
	"""
	Global object in the database which holds the
	settings for whether and how a certain ISMI
	relation (on either a Manuscipt's associated
	WITNESS or the TEXT it is exemplar of) should
	be displayed in the Metadata view.
	"""
	rel_type = models.CharField(choices=[('src','src'),('tar','tar')],
	                            max_length=200,
	                            editable=False)
	show_id = models.BooleanField()
	name = models.CharField(max_length=200, unique=True, editable=False)
	display_name = models.CharField(max_length=200, null=True)
	show = models.BooleanField(default=True)
	on_ent = models.BooleanField(editable=False)
	
	def __unicode__(self):
		return unicode(self.name)
	
	def save(self, *args, **kwargs):
		if self.display_name is None:
			self.display_name = self.name
		super(RelDisplaySetting, self).save(*args, **kwargs)

class Manuscript(models.Model):
	"""
	The model for all manuscripts in the RASI database.
	"""
	directory = FolderField(path=IMG_DIR)
	ismi_id = models.IntegerField(blank=True, null=True)
	num_files = models.IntegerField(editable=False)
	
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
