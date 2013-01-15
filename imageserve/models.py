from os import listdir
from os.path import isdir, join
from django.db import models
from conf import IMG_DIR
from imageserve import get_by_ismi_id
from south.modelsinspector import add_introspection_rules

add_introspection_rules([],["^imageserve\.models\.FolderField"])

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
	on_ent = models.CharField(max_length=200, editable=False)
	
	def ent_getter(self, ID):
		"""
		Since not all attributes are on the actual witness displayed
		in the viewer, this method finds the appropriate entity for the
		attribute the setting concerns.
		"""
		curr_ent = get_by_ismi_id(ID)
		if self.on_ent == 'self':
			return curr_ent
		src_match = [r for r in curr_ent['src_rels'] if r['name'] == self.on_ent]
		if src_match:
			return get_by_ismi_id(src_match[0]['tar_id'])
		else:
			tar_match = [r for r in curr_ent['tar_rels'] if r['name'] == self.on_ent]
			return get_by_ismi_id(tar_match[0]['src_id'])
	
	def get_val(self, ID):
		"""
		Given the id of a (codex or witness, not yet decided),
		return the value of this attribute as it would appear
		in the metadata view for the (codex or witness) in question.
		"""
		ent = self.ent_getter(ID)
		match = [a for a in ent['atts'] if a['name'] == self.name]
		if match:
			val = match[0].get('ov')
			if val is not None:
				return val
			else:
				return "Data missing"
		else:
			return "Data missing"
	
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
	show_id = models.BooleanField()
	name = models.CharField(max_length=200, unique=True, editable=False)
	display_name = models.CharField(max_length=200, null=True)
	show = models.BooleanField(default=True)
	on_ent = models.CharField(max_length=200, editable=False)
	
	def ent_getter(self, ID):
		"""
		Since not all relations are on the actual witness displayed
		in the viewer, this method finds the appropriate entity for the
		relation this setting concerns.
		"""
		curr_ent = get_by_ismi_id(ID)
		if self.on_ent == 'self':
			return curr_ent
		src_match = [r for r in curr_ent['src_rels'] if r['name'] == self.on_ent]
		if src_match:
			return get_by_ismi_id(src_match[0]['tar_id'])
		else:
			tar_match = [r for r in curr_ent['tar_rels'] if r['name'] == self.on_ent]
			return get_by_ismi_id(tar_match[0]['src_id'])
	
	def get_val(self, ID):
		"""
		Given the id of a (codex or witness, not yet decided),
		return the value of this relation as it would appear
		in the metadata view for the (codex or witness) in question.
		"""
		ent = self.ent_getter(ID)
		if self.name == 'was_created_by':
			print self.on_ent
		src_match = [r for r in ent['src_rels'] if r['name'] == self.name]
		if src_match:
			return get_by_ismi_id(src_match[0]['tar_id'])['ov']
		else:
			tar_match = [r for r in ent['tar_rels'] if r['name'] == self.name]
			if tar_match:
				return get_by_ismi_id(tar_match[0]['src_id'])['ov']
			else:
				return "Data missing"
	
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
