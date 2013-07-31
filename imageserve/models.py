import os
import unicodedata
from lxml import etree, html
from django.db import models
from django.core.exceptions import ValidationError
from django.core.cache import cache
from conf import IMG_DIR
from imageserve.helpers import get_by_ismi_id, get_name, get_rel
from imageserve.forms import IntegerListField, FolioPagesField, FolioPages
from imageserve.settings import NO_DATA_MSG, CACHE_ENABLED
from south.modelsinspector import add_introspection_rules


add_introspection_rules([], ["^imageserve\.models\.IsmiIdField"])
add_introspection_rules([], ["^imageserve\.models\.FolderField"])


# MODEL FIELDS
class FolderField(models.FilePathField):
    """
    In Django 1.5 this is implemented already, but this is just
    a shortcut so we can use folders instead of files.
    """
    def __init__(self, *args, **kwargs):
        d = kwargs['path']
        kwargs['choices'] = [(name, name) for name in os.listdir(d)
                             if os.path.isdir(os.path.join(d, name))]
        super(FolderField, self).__init__(*args, **kwargs)


class IsmiIdField(models.IntegerField):
    """
    Custom model field which must be a valid ID of a
    Codex object from the ISMI database.
    """
    def to_python(self, value):
        try:
            c = get_by_ismi_id(value)
        except KeyError:
            raise ValidationError("Invalid ISMI ID")
        if c['oc'] != 'CODEX':
            raise ValidationError("ISMI entity must be of type CODEX")
        return value


# MODELS

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
    SHOW_CHOICES = [(ALWAYS_SHOW, 'always show'),
                    (SHOW_IF_SET, 'show if attribute has been set'),
                    (NEVER_SHOW, 'never show')]
    name = models.CharField(max_length=200, unique=True, editable=False)
    display_name = models.CharField(max_length=200, null=True)
    show = models.IntegerField(choices=SHOW_CHOICES, default=ALWAYS_SHOW)
    on_ent = models.CharField(max_length=200, editable=False)
    content_type = models.CharField(max_length=200, editable=False)
    oc = models.CharField(max_length=200, editable=False)
    
    class Meta:
        unique_together = ('name', 'oc')

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

    def get_vals(self, ID):
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
                arabic = False
                if self.content_type == 'arabic':
                    arabic = True
                elif isinstance(val, basestring):
                    if not filter(lambda c: not 'A' in unicodedata.bidirectional(c), val.replace(' ', '')):
                        arabic = True
                if arabic:
                    val = u'<p dir=\"RTL\">{0}</p>'.format(val)
                if self.name == 'table_of_contents':
                    root = html.fromstring(val)
                    for a in root.xpath('.//a[@href]'):
                        u = a.attrib.get('href')
                        a.set('href', '#')
                        s = 'window.open(\"{0}\", \"_blank\")'.format(u)
                        a.attrib['onclick'] = s
                    val = etree.tostring(root, pretty_print=True)
                return [val]
        return [NO_DATA_MSG]

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
    relation (on either a Manuscript's associated
    CODEX, one of the WITNESSes contained therein or
    the TEXT it is exemplar of) should
    be displayed in the Metadata view.
    """
    ALWAYS_SHOW = 0
    SHOW_IF_SET = 1
    NEVER_SHOW = 2
    SHOW_CHOICES = [(ALWAYS_SHOW, 'always show'),
                    (SHOW_IF_SET, 'show if attribute has been set'),
                    (NEVER_SHOW, 'never show')]
    show_id = models.BooleanField()
    name = models.CharField(max_length=200, unique=True, editable=False)
    display_name = models.CharField(max_length=200, null=True)
    show = models.IntegerField(choices=SHOW_CHOICES, default=ALWAYS_SHOW)
    on_ent = models.CharField(max_length=200, editable=False)
    src_oc = models.CharField(max_length=200, editable=False)
    tar_oc = models.CharField(max_length=200, editable=False)

    class Meta:
        unique_together = ('src_oc', 'name', 'tar_oc')

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

    def get_vals(self, ID):
        """
        Given the id of a witness, return the values of this relation
        as they would appear in the metadata view for the witness in question.
        """
        vals = None
        if CACHE_ENABLED:
            vals = cache.get('rels', {}).get(ID, {}).get(self.name)

        if vals is None:
            ent = self.ent_getter(ID)
            vals = []
            src_match = [r for r in ent['src_rels'] if r['name'] == self.name]
            if src_match:
                src_match = [get_by_ismi_id(r['tar_id']) for r in src_match]
                vals += [get_name(e, show_id=self.show_id) for e in src_match]
            tar_match = [r for r in ent['tar_rels'] if r['name'] == self.name]
            if tar_match:
                tar_match = [get_by_ismi_id(r['src_id']) for r in tar_match]
                vals += [get_name(e, show_id=self.show_id) for e in tar_match]
            if not vals:
                vals = [NO_DATA_MSG]
            if CACHE_ENABLED:
                d = cache.get('rels', {})
                if ID in d:
                    d[ID].update(rel_name=vals)
                else:
                    d[ID] = {self.name: vals}
                cache.set('rels', d)
        for i, val in enumerate(vals):
            if isinstance(val, basestring):
                if not filter(lambda c: not 'A' in unicodedata.bidirectional(c), val.replace(' ', '')):
                    vals[i] = u'<p dir=\"RTL\">{0}</p>'.format(val)
        return vals

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        if self.display_name is None:
            self.display_name = u'{0} {1} {2}'.format(self.src_oc, self.name, self.tar_oc)
        super(RelDisplaySetting, self).save(*args, **kwargs)


class Manuscript(models.Model):
    """
    The model for all manuscripts in the RASI database. These correspond
    to Codex objects in the ISMI database for metadata purposes.
    """
    directory = FolderField(path=IMG_DIR, unique=True)
    ismi_id = IsmiIdField(blank=True, null=True)
    num_files = models.IntegerField(editable=False, verbose_name="# Pages")
    has_folio_nums = models.BooleanField(default=True)
    folio_pgs = FolioPagesField(editable=False, null=True)

    class Meta:
        ordering = ['directory']

    @property
    def witnesses(self):
        """
        Return the witnesses for this object.
        """
        # TODO: make a test for this
        if self.ismi_id is not None:
            c = get_by_ismi_id(self.ismi_id)
            rels = [r for r in c['tar_rels'] if r['name'] == 'is_part_of']
            return [r['src_id'] for r in rels]
        # do some error handling?
        return []


    def num_witnesses(self):
        """
        This method is designed for the manuscript index view, which uses
        spanning rows in a table and so this method intentionally returns
        a value which is larger than the actual number of witnesses.
        """
        return len(self.witnesses) + 1

    def witness_infos(self):
        """
        Generator for the authors & titles in this codex. Intended for
        use with the manuscript index view.
        """
        wits = self.witnesses
        if wits:
            titles = [get_rel(w, 'is_exemplar_of')[0] for w in wits]
            authors = [get_rel(w, 'was_created_by')[0] for w in wits]
            return zip(wits, titles, authors)

    def clean(self, *args, **kwargs):
        self.num_files = len(os.listdir(os.path.join(IMG_DIR, self.directory)))
        if not self.folio_pgs:
            self.folio_pgs = FolioPages(num_pages=self.num_files)
        return super(Manuscript, self).clean(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.directory)


class ManuscriptGroup(models.Model):
    """
    A group of manuscripts which fit
    under some common category.
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    manuscripts = models.ManyToManyField(Manuscript, blank=True, null=True)

    class Meta:
        permissions = (
            ('view_manuscript_group', 'Can View Manuscripts in Group'),
        )

    def __unicode__(self):
        return unicode(self.name)


class CacheTable(models.Model):
    """docstring for CacheTable"""
    cache_key = models.CharField(max_length=255, primary_key=True)
    value = models.TextField()
    expires = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        db_table = "is_cache_table"
