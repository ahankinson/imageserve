from os import listdir
from os.path import isdir, join
from django.db import models
from django.forms.fields import MultiValueField, IntegerField
from django.forms import MultiWidget
from django.forms.util import ValidationError as FormValidationError
from conf import IMG_DIR
from imageserve.helpers import get_by_ismi_id
from south.modelsinspector import add_introspection_rules

add_introspection_rules([],["^imageserve\.models\.FolderField"])
add_introspection_rules([],["^imageserve\.models\.WitnessListField"])

class WitnessListWidget(MultiWidget):
	def __init__(self, *args, **kwargs):
		fields = kwargs['fields']
		self.labels = [f.label for f in fields]
		data = {'widgets': (f.widget for f in fields)}
		super(WitnessListWidget, self).__init__(*args, **data)
	def decompress(self, value):
		print 'decompress called', value
		if value:
			return [i for _,i in eval(value)]
		return [None for w in self.labels]
	def format_output(self, rendered_widgets):
		z = zip(self.labels,rendered_widgets)
		rows = u'\n'.join(u'<tr><td>'+l+u': '+w+u'</td></tr>' for l,w in z)
		return u'<table>' + rows + u'</table>'

class WitnessListFormField(MultiValueField):
	def __init__(self, *args, **kwargs):
		self.witnesses = kwargs['witnesses']
		fields = tuple(IntegerField(
			label=get_by_ismi_id(w).get('ov')
		) for w in self.witnesses)
		data = {
			'fields': fields,
			'widget': WitnessListWidget(fields=fields),
			'label': 'Witnesses in this codex, with start pages'
		}
		super(WitnessListFormField, self).__init__(*args, **data)
	def compress(self, data_list):
		return zip(self.witnesses, data_list)

class WitnessListField(models.Field):
	description = """A list of the witnesses contained in a codex,
	along with the page in the codex they begin on"""
	__metaclass__ = models.SubfieldBase
	def __init__(self, *args, **kwargs):
		self.witnesses = kwargs.get('witnesses')
		super(WitnessListField, self).__init__(*args, **kwargs)
	def db_type(self, connection):
		return 'char(500)'
	def to_python(self, value):
		if isinstance(value, list):
			return value
		elif isinstance(value, basestring):
			return eval(value)
		else:
			return None
	def get_db_prep_value(self, value, connection, prepared):
		print 'get_db_prep_value called', value
		return str(value)
	def value_to_string(self, instance):
		value = self._get_val_from_obj(instance)
		return self.get_db_prep_value(value)
	def formfield(self, form_class=WitnessListFormField, **kwargs):
		defaults = {"witnesses": self.witnesses}
		defaults.update(kwargs)
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
	witnesses = WitnessListField(editable=False)
	
	def save(self, *args, **kwargs):
		self.num_files = len(listdir(join(IMG_DIR, self.directory)))
		if self.witnesses is None:
			c = get_by_ismi_id(self.ismi_id)
			wits = [r['src_id'] for r in c['tar_rels'] if r['name'] == 'is_part_of']
			w = self._meta.get_field_by_name('witnesses')[0]
			w.witnesses = wits
			w.editable = True
			self.witnesses = str([(w,None) for w in wits])
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
