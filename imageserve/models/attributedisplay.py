from django.db import models


class AttributeDisplay(models.Model):
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
        app_label = "imageserve"
        # unique_together = ('name', 'oc')

    # def ent_getter(self, ID):
    #     """
    #     Since not all attributes are on the actual witness displayed
    #     in the viewer, this method finds the appropriate entity for the
    #     attribute the setting concerns.
    #     """
    #     curr_ent = get_by_ismi_id(ID)
    #     if self.on_ent == 'self':
    #         return curr_ent
    #     src_match = [r for r in curr_ent['src_rels'] if r['name'] == self.on_ent]
    #     if src_match:
    #         return get_by_ismi_id(src_match[0]['tar_id'])
    #     else:
    #         tar_match = [r for r in curr_ent['tar_rels'] if r['name'] == self.on_ent]
    #         return get_by_ismi_id(tar_match[0]['src_id'])

    # def get_vals(self, ID):
    #     """
    #     Given the id of a (codex or witness, not yet decided),
    #     return the value of this attribute as it would appear
    #     in the metadata view for the (codex or witness) in question.
    #     """
    #     ent = self.ent_getter(ID)
    #     atts = ent.data.get('atts', None)

    #     if atts:
    #         match = [a for a in atts if a['name'] == self.name]
    #         if match:
    #             val = match[0].get('ov')
    #             if val is not None:
    #                 arabic = False
    #                 if self.content_type == 'arabic':
    #                     arabic = True
    #                 elif isinstance(val, basestring):
    #                     if not filter(lambda c: not 'A' in unicodedata.bidirectional(c), val.replace(' ', '')):
    #                         arabic = True
    #                 if arabic:
    #                     val = u'<p dir=\"RTL\">{0}</p>'.format(val)
    #                 if self.name == 'table_of_contents':
    #                     root = html.fromstring(val)
    #                     for a in root.xpath('.//a[@href]'):
    #                         u = a.attrib.get('href')
    #                         a.set('href', '#')
    #                         s = 'window.open(\"{0}\", \"_blank\")'.format(u)
    #                         a.attrib['onclick'] = s
    #                     val = etree.tostring(root, pretty_print=True)
    #                 return [val]
    #     return [NO_DATA_MSG]

    def __unicode__(self):
        return u"{0}".format(self.name)

    # def save(self, *args, **kwargs):
    #     if self.display_name is None:
    #         self.display_name = self.name
    #     super(AttDisplaySetting, self).save(*args, **kwargs)