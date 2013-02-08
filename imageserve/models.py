from os import listdir
from os.path import isdir, join
from django.db import models
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from conf import IMG_DIR
from imageserve.helpers import get_by_ismi_id, get_keyval
from south.modelsinspector import add_introspection_rules
import re


add_introspection_rules([],["^imageserve\.models\.WitnessListWidget"])
add_introspection_rules([],["^imageserve\.models\.WitnessListFormField"])
add_introspection_rules([],["^imageserve\.models\.WitnessListField"])
add_introspection_rules([],["^imageserve\.models\.IsmiIdField"])
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
    ALWAYS_SHOW = 0
    SHOW_IF_SET = 1
    NEVER_SHOW = 2
    SHOW_CHOICES = [(ALWAYS_SHOW,'always show'),
                    (SHOW_IF_SET, 'show if attribute has been set'),
                    (NEVER_SHOW, 'never show')]
    name = models.CharField(max_length=200, unique=True, editable=False)
    display_name = models.CharField(max_length=200, null=True)
    show = models.IntegerField(choices=SHOW_CHOICES, default=ALWAYS_SHOW)
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
        return NO_DATA_MSG
    
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
    ALWAYS_SHOW = 0
    SHOW_IF_SET = 1
    NEVER_SHOW = 2
    SHOW_CHOICES = [(ALWAYS_SHOW,'always show'),
                    (SHOW_IF_SET, 'show if attribute has been set'),
                    (NEVER_SHOW, 'never show')]
    show_id = models.BooleanField()
    name = models.CharField(max_length=200, unique=True, editable=False)
    display_name = models.CharField(max_length=200, null=True)
    show = models.IntegerField(choices=SHOW_CHOICES, default=ALWAYS_SHOW)
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
        src_match = [r for r in ent['src_rels'] if r['name'] == self.name]
        if src_match:
            return get_by_ismi_id(src_match[0]['tar_id'])['ov']
        else:
            tar_match = [r for r in ent['tar_rels'] if r['name'] == self.name]
            if tar_match:
                return get_by_ismi_id(tar_match[0]['src_id'])['ov']
        return NO_DATA_MSG
    
    def __unicode__(self):
        return unicode(self.name)
    
    def save(self, *args, **kwargs):
        if self.display_name is None:
            self.display_name = self.name
        super(RelDisplaySetting, self).save(*args, **kwargs)
    
class IsmiIdField(models.IntegerField):
    '''
    Custom model field which must be a valid ID of a
    Codex object from the ISMI database.
    '''
    def to_python(self, value):
        c = None
        try:
            c = get_by_ismi_id(value)
        except KeyError:
            raise ValidationError("Invalid ISMI ID")
        if c['oc'] != 'CODEX':
            raise ValidationError("ISMI entity must be of type CODEX")
        return value
    
class WitnessListFormField(forms.MultiValueField):
    def compress(self, data_list):
        return u','.join(map(unicode, data_list))
    
class WitnessListField(models.Field):
    __metaclass__ = models.SubfieldBase
    def db_type(self, connection):
        return 'char(500)'
    def to_python(self, value):
        if value:
            if isinstance(value, basestring):
                return eval(value)
            elif isinstance(value, (list, tuple)):
                return list(value)
            else:
                return [value]
        return None
    def get_prep_value(self, value):
        if isinstance(value, (list, tuple, basestring)):
            return unicode(value)
        else:
            return unicode([value])
    def formfield(self, form_class=WitnessListFormField, **kwargs):
        if kwargs.get('max_length'):
            kwargs.pop('max_length')
        return form_class(**kwargs)
    
class WitnessListWidget(forms.MultiWidget):
    def __init__(self, *args, **kwargs):
        self.witnesses = kwargs.pop('witnesses')
        widgets = [forms.TextInput for w in self.witnesses]
        super(WitnessListWidget, self).__init__(widgets, **kwargs)
    def decompress(self, value):
        if value:
            if isinstance(value, (list, tuple)):
                return list(value)
        return [None for w in self.witnesses]
    def format_output(self, rendered_widgets):
        labels = [get_by_ismi_id(w).get('ov') for w in self.witnesses]
        zipped = [": ".join(t) for t in zip(labels, rendered_widgets)]
        prerenders = [u'<tr><td>'+z+u'</td></tr>' for z in zipped]
        rows = u'\n'.join(prerenders)
        return u'<table>' + rows + u'</table>'
    
class Manuscript(models.Model):
    """
    The model for all manuscripts in the RASI database. These correspond
    to Codex objects in the ISMI database for metadata purposes.
    """
    directory = FolderField(path=IMG_DIR, unique=True)
    ismi_id = IsmiIdField(blank=True, null=True)
    num_files = models.IntegerField(editable=False)
    witnesses = models.CommaSeparatedIntegerField(max_length=500, editable=False)
    witness_pages = WitnessListField()
    witness_titles = models.CharField(max_length=2000, editable=False)
    witness_authors = models.CharField(max_length=2000, editable=False)
    
    def num_witnesses(self):
        """
        This method is designed for the manuscript index view, which uses
        spanning rows in a table and so this method intentionally returns
        a value which is larger than the actual number of witnesses.
        """
        return len(eval(self.witnesses)) + 1
    
    def witness_infos(self):
        """
        Generator for the authors & titles in this codex. Intended for
        use with the manuscript index view.
        """
        titles = self.witness_titles.split(',')
        authors = self.witness_authors.split(',')
        for i, (title, author) in enumerate(zip(titles, authors)):
            yield i, title, author
    
    def clean(self, *args, **kwargs):
        self.num_files = len(listdir(join(IMG_DIR, self.directory)))
        if self.witnesses == u'':
            c = get_by_ismi_id(self.ismi_id)
            rels = [r for r in c['tar_rels'] if r['name'] == 'is_part_of']
            wits = [r['src_id'] for r in rels]
            if len(wits) > 1:
                ents = [get_by_ismi_id(w) for w in wits]
                def _first_page(folio):
                    pgs = folio.split('-')
                    if len(pgs) > 1:
                        return int(re.findall('\d+', pgs[0])[0])*2 # a folio is 2 pages
                    return None
                folios = []
                for e in ents:
                    folios_att = [a for a in e['atts'] if a['name'] == 'folios']
                    if folios_att:
                        folios_att = folios_att[0]
                        folios.append(folios_att['nov'])
                    else:
                        folios.append('')
                pages = map(_first_page, folios)
                sorted_wits = sorted(zip(wits, pages), key = lambda t:t[1])
                self.witnesses = [w for w,_ in sorted_wits]
                self.witness_pages = [p for _,p in sorted_wits]
            else:
                self.witnesses = wits
                self.witness_pages = [1]
            get_title = lambda w: get_keyval(RelDisplaySetting.objects.get(
                                             name='is_exemplar_of'),
                                             w)[1]
            get_author = lambda w: get_keyval(RelDisplaySetting.objects.get(
                                             name='was_created_by'),
                                             w)[1]
            self.witness_titles = ",".join(map(get_title,wits))
            self.witness_authors = ",".join(map(get_author,wits))
        (self.witnesses, self.witness_pages,
        witness_titles,
        witness_authors) = zip(*sorted(
                            zip(list(eval(self.witnesses)), self.witness_pages,
                                self.witness_titles.split(','),
                                self.witness_authors.split(',')),
                            key = lambda t: t[1]))
        self.witness_titles = unicode(",".join(witness_titles))
        self.witness_authors = unicode(",".join(witness_authors))
        return super(Manuscript, self).clean(*args, **kwargs)
    
    def __unicode__(self):
        return unicode(self.directory)
    
class ManuscriptAdminForm(forms.ModelForm):
    '''
    Custom admin form to take care of dynamically generating
    the form widget corresponding to the page numbers of the
    witnesses in a codex.
    '''
    class Meta:
        model = Manuscript
    def __init__(self, *args, **kwargs):
        super(ManuscriptAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            wits = eval(instance.witnesses) # despite its scariness, this safely yields a tuple
            self.fields['witness_pages'] = \
                WitnessListFormField(fields=tuple(forms.IntegerField() for w in wits),
                                     widget=WitnessListWidget(witnesses=wits))
    
class ManuscriptAdmin(admin.ModelAdmin):
    form = ManuscriptAdminForm
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.exclude = ()
        else:
            # there is no instance, so don't display
            # the witnesses contained in it
            self.exclude = ('witness_pages',)
        return super(ManuscriptAdmin, self).get_form(request, obj, **kwargs)

class ManuscriptGroup(models.Model):
    """
    A group of manuscripts which fit
    under some common category.
    """
    name = models.CharField(max_length=200, blank=True)
    manuscripts = models.ManyToManyField(Manuscript)
    users = models.ManyToManyField(User, blank=True)
    public = models.BooleanField(default=False)
    
    def __unicode__(self):
        return unicode(self.name)
