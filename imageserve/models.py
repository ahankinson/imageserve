import re
import os
from lxml import etree, html
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from conf import IMG_DIR
from imageserve.helpers import get_by_ismi_id, get_keyvals, get_name
from imageserve.forms import IntegerListField, PageRangeListField
from imageserve.forms import PageRange, PageRangeList
from imageserve.settings import NO_DATA_MSG
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
                if self.name == 'table_of_contents':
                    root = html.fromstring(val)
                    for a in root.xpath('.//a[@href]'):
                        u = a.attrib.get('href')
                        a.set('href', '#')
                        a.set('onclick', 'window.open("{0}", "_blank")'.format(u))
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
    relation (on either a Manuscipt's associated
    WITNESS or the TEXT it is exemplar of) should
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
        ent = self.ent_getter(ID)
        matches = []
        src_match = [r for r in ent['src_rels'] if r['name'] == self.name]
        if src_match:
            src_match = [get_by_ismi_id(r['tar_id']) for r in src_match]
            matches += [get_name(e, show_id=self.show_id) for e in src_match]
        tar_match = [r for r in ent['tar_rels'] if r['name'] == self.name]
        if tar_match:
            tar_match = [get_by_ismi_id(r['src_id']) for r in tar_match]
            matches += [get_name(e, show_id=self.show_id) for e in tar_match]
        if not matches:
            matches = [NO_DATA_MSG]
        return matches

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
    directory = FolderField(path=IMG_DIR, unique=True)
    ismi_id = IsmiIdField(blank=True, null=True)
    num_files = models.IntegerField(editable=False, verbose_name="# Pages")
    witnesses = IntegerListField(editable=False)
    witness_pages = PageRangeListField()
    witness_titles = models.CharField(max_length=2000,
                                      editable=False,
                                      null=True)
    witness_authors = models.CharField(max_length=2000,
                                       editable=False,
                                       null=True)
    # has_folio_nums = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['directory']

    def num_witnesses(self):
        """
        This method is designed for the manuscript index view, which uses
        spanning rows in a table and so this method intentionally returns
        a value which is larger than the actual number of witnesses.
        """
        if not self.witnesses:
            return 1
        return len(self.witnesses) + 1

    def witness_infos(self):
        """
        Generator for the authors & titles in this codex. Intended for
        use with the manuscript index view.
        """
        if self.witnesses:
            titles = self.witness_titles.split(',')
            authors = self.witness_authors.split(',')
            for i, (title, author) in enumerate(zip(titles, authors)):
                yield i, title, author

    def clean(self, *args, **kwargs):
        self.num_files = len(os.listdir(os.path.join(IMG_DIR, self.directory)))
        if not self.witnesses and self.ismi_id is not None:
            try:
                c = get_by_ismi_id(self.ismi_id)
            except KeyError:
                return super(Manuscript, self).clean(*args, **kwargs)
            if c['oc'] != 'CODEX':
                return super(Manuscript, self).clean(*args, **kwargs)
            rels = [r for r in c['tar_rels'] if r['name'] == 'is_part_of']
            wits = [r['src_id'] for r in rels]
            if len(wits) > 1:
                ents = [get_by_ismi_id(w) for w in wits]

                def get_pages(folio):
                    m = re.findall(r'(\d+)(a|b)?-(\d+)(a|b)?', folio)
                    if m:
                        first, first_ind, second, second_ind = m[0]
                        first = int(first)*2 - 1
                        if 'b' == first_ind:
                            first += 1
                        second = int(second)*2
                        if 'a' == second_ind:
                            second -= 1
                        return PageRange(first, second)
                    return PageRange(None, None)
                folios = []
                for e in ents:
                    folios_att = [a for a in e['atts'] if a['name'] == 'folios']
                    if folios_att:
                        folios_att = folios_att[0]
                        folios.append(folios_att['nov'])
                    else:
                        folios.append('')
                pages = PageRangeList(map(get_pages, folios))
                self.witnesses, self.witness_pages = \
                    zip(*sorted(zip(wits, pages),
                                    key=lambda t: t[1].first))
            else:
                self.witnesses = wits
                self.witness_pages = \
                    PageRangeList([PageRange(1, self.num_files)])
            get_title = lambda w: get_keyvals(RelDisplaySetting.objects.get(
                                             name='is_exemplar_of'),
                                             w)[1][0]
            get_author = lambda w: get_keyvals(RelDisplaySetting.objects.get(
                                              name='was_created_by'),
                                              w)[1][0]
            self.witness_titles = ",".join(map(get_title, wits))
            self.witness_authors = ",".join(map(get_author, wits))
        if self.witnesses and self.witness_pages:
            self.witnesses, self.witness_pages = \
                zip(*sorted(zip(self.witnesses, self.witness_pages),
                            key=lambda t: t[1].first))
            get_title = lambda w: get_keyvals(RelDisplaySetting.objects.get(
                                             name='is_exemplar_of'),
                                             w)[1][0]
            get_author = lambda w: get_keyvals(RelDisplaySetting.objects.get(
                                              name='was_created_by'),
                                              w)[1][0]
            self.witness_titles = ",".join(map(get_title, self.witnesses))
            self.witness_authors = ",".join(map(get_author, self.witnesses))
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
