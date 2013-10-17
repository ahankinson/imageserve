from django.db import models


class RelationshipDisplay(models.Model):
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
        app_label = "imageserve"

    # def ent_getter(self, ID):
    #     """
    #     Since not all relations are on the actual witness displayed
    #     in the viewer, this method finds the appropriate entity for the
    #     relation this setting concerns.
    #     """
    #     curr_ent = get_by_ismi_id(ID)
    #     if self.on_ent == 'self':
    #         return curr_ent

    #     src_rels = curr_ent.data.get('src_rels', None)
    #     if src_rels:
    #         src_match = [r for r in src_rels if r['name'] == self.on_ent]

    #         if src_match:
    #             return get_by_ismi_id(src_match[0]['tar_id'])

    #     else:
    #         tar_rels = curr_ent.data.get('tar_rels', None)
    #         if tar_rels:
    #             tar_match = [r for r in tar_rels if r['name'] == self.on_ent]
    #             return get_by_ismi_id(tar_match[0]['src_id'])

    # def get_vals(self, ID):
    #     """
    #     Given the id of a witness, return the values of this relation
    #     as they would appear in the metadata view for the witness in question.
    #     """
    #     vals = None
    #     ent = self.ent_getter(ID)
    #     vals = []

    #     src_rels = ent.data.get('src_rels', None)
    #     if src_rels:
    #         src_match = [r for r in src_rels if r['name'] == self.name]
    #         if src_match:
    #             src_match = [get_by_ismi_id(r['tar_id']) for r in src_match]
    #             vals += [get_name(e, show_id=self.show_id) for e in src_match]

    #     tar_rels = ent.data.get('tar_rels', None)
    #     if tar_rels:
    #         tar_match = [r for r in tar_rels if r['name'] == self.name]
    #         if tar_match:
    #             tar_match = [get_by_ismi_id(r['src_id']) for r in tar_match]
    #             vals += [get_name(e, show_id=self.show_id) for e in tar_match]

    #     if not vals:
    #         vals = [NO_DATA_MSG]

    #     for i, val in enumerate(vals):
    #         if isinstance(val, basestring):
    #             if not filter(lambda c: not 'A' in unicodedata.bidirectional(c), val.replace(' ', '')):
    #                 vals[i] = u'<p dir=\"RTL\">{0}</p>'.format(val)

    #     return vals

    def __unicode__(self):
        return u"{0}".format(self.name)

    # def save(self, *args, **kwargs):
    #     if self.display_name is None:
    #         self.display_name = u'{0} {1} {2}'.format(self.src_oc, self.name, self.tar_oc)
    #     super(RelDisplaySetting, self).save(*args, **kwargs)
