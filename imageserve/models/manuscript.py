import os
from django.db import models
from django.conf import settings
from django_extensions.db.fields import json


class Manuscript(models.Model):
    """
    The model for all manuscripts in the RASI database. These correspond
    to Codex objects in the ISMI database for metadata purposes.
    """
    directory = models.FilePathField(path=settings.IMG_DIR, allow_files=False, allow_folders=True, unique=True, max_length=256)
    ismi_id = models.IntegerField(blank=True, null=True, verbose_name="ISMI ID")
    num_files = models.IntegerField(verbose_name="# Pages")
    has_folio_nums = models.BooleanField(default=True)
    folio_pgs = json.JSONField(editable=False, null=True)

    class Meta:
        app_label = "imageserve"
        ordering = ['directory']

    @property
    def ms_name(self):
        return os.path.basename(self.directory)

    def __unicode__(self):
        return u"{0}".format(self.ms_name)

    @property
    def has_unknown_witnesses(self):
        unknown_witnesses = self.witnesses.filter(name__startswith="UNKNOWN_")
        return unknown_witnesses.exists()


    # @property
    # def witnesses(self):
    #     """
    #     Return the witnesses for this object.
    #     """
    #     print("Calling witnesses")
    #     # TODO: make a test for this
    #     if self.ismi_id is not None:
    #         c = get_by_ismi_id(self.ismi_id)
    #         tar_rels = c.data.get('tar_rels', None)
    #         if tar_rels:
    #             rels = [r for r in tar_rels if r['name'] == 'is_part_of']
    #             return [r['src_id'] for r in rels]
    #     # do some error handling?
    #     return []


    # def num_witnesses(self):
    #     """
    #     This method is designed for the manuscript index view, which uses
    #     spanning rows in a table and so this method intentionally returns
    #     a value which is larger than the actual number of witnesses.
    #     """
    #     return len(self.witnesses) + 1

    # def witness_infos(self):
    #     """
    #     Generator for the authors & titles in this codex. Intended for
    #     use with the manuscript index view.
    #     """
    #     wits = self.witnesses
    #     if wits:
    #         titles = [get_rel(w, 'is_exemplar_of')[0] for w in wits]
    #         authors = [get_rel(w, 'was_created_by')[0] for w in wits]
    #         return zip(wits, titles, authors)

    # def clean(self, *args, **kwargs):
    #     self.num_files = len(os.listdir(os.path.join(IMG_DIR, self.directory)))
    #     if not self.folio_pgs:
    #         self.folio_pgs = FolioPages(num_pages=self.num_files)
    #     return super(Manuscript, self).clean(*args, **kwargs)

