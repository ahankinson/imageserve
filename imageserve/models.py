from os import listdir
from os.path import isdir, join
from django.db import models
from django import forms
from django.contrib import admin
from conf import IMG_DIR
from imageserve.helpers import get_by_ismi_id
from south.modelsinspector import add_introspection_rules


add_introspection_rules([],["^imageserve\.models\.PageNumbersWidget"])
add_introspection_rules([],["^imageserve\.models\.PageNumbersFormField"])
add_introspection_rules([],["^imageserve\.models\.PageNumbersField"])
add_introspection_rules([],["^imageserve\.models\.FolderField"])

class PageNumbersWidget(forms.MultiWidget):
	def __init__(self, *args, **kwargs):
		print 'init called on widget with parameters', args, kwargs
		fields = kwargs['fields']
		self.labels = [f.label for f in fields]
		data = {'widgets': (forms.TextInput for f in fields)}
		super(WitnessListWidget, self).__init__(*args, **data)
	def decompress(self, value):
		print 'decompress called with value', value
		if value:
			return [i for _,i in eval(value)]
		else:
			return [None for w in self.labels]
	def value_from_datadict(self, data, files, name):
		print 'value_from_datadict called'
		super(WitnessListWidget, self).value_from_datadict(data, files, name)
	def format_output(self, rendered_widgets):
		print 'format_output called with rendered_widgets', rendered_widgets
		zipped = [": ".join(t) for t in zip(self.labels, rendered_widgets)]
		prerenders = [u'<tr><td>'+z+u'</td></tr>' for z in zipped]
		rows = u'\n'.join(prerenders)
		return u'<table>' + rows + u'</table>'

class PageNumbersFormField(forms.MultiValueField):
	def __init__(self, *args, **kwargs):
		print 'init called on formfield with kwargs', kwargs
		data = {
			'widget': WitnessListWidget(fields=kwargs['fields']),
			'label': 'Witnesses in this codex, with start pages'
		}
		kwargs.update(data)
		super(WitnessListFormField, self).__init__(*args, **kwargs)
	def compress(self, data_list):
		print 'compress called with data_list', data_list
		return zip(self.witnesses, data_list)

class PageNumbersField(models.CommaSeparatedIntegerField):
	description = """A list of the first page number of each witness
	contained in this codex"""
	__metaclass__ = models.SubfieldBase
	def __init__(self, *args, **kwargs):
		kwargs['max_length'] = 500
		super(WitnessListField, self).__init__(*args, **kwargs)
	def formfield(self, form_class=PageNumbersFormField, **kwargs):
		labels = [get_by_ismi_id(w).get('ov') for w in self.witnesses]
		fields = tuple(forms.IntegerField(label=l) for l in labels)
		defaults = {'fields': fields}
		defaults.update({k:v for k,v in kwargs.items() if k != 'max_length'})
		return form_class(**defaults)

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
	The model for all manuscripts in the RASI database. These correspond
	to Codex objects in the ISMI database for metadata purposes.
	"""
	directory = FolderField(path=IMG_DIR)
	ismi_id = models.IntegerField(blank=True, null=True)
	num_files = models.IntegerField(editable=False)
	witnesses = models.CommaSeparatedIntegerField(max_length=500, editable=False)
	page_numbers = PageNumbersField()
	
	def save(self, *args, **kwargs):
		self.num_files = len(listdir(join(IMG_DIR, self.directory)))
		if self.witnesses is None:
			c = get_by_ismi_id(self.ismi_id)
			wits = [r['src_id'] for r in c['tar_rels'] if r['name'] == 'is_part_of']
			self.witnesses = wits
		w = self._meta.get_field_by_name('witnesses')[0]
		w.editable = True
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
