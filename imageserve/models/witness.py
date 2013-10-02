import re
from django.db import models
from django_extensions.db.fields import json


class Witness(models.Model):
    ismi_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=512, null=True, blank=True, db_index=True)
    manuscript = models.ForeignKey("imageserve.Manuscript", blank=True, null=True, related_name="witnesses")
    data = json.JSONField(default="[]", blank=True, null=True)
    folios = models.CharField(max_length=256, null=True, blank=True)
    start_page = models.CharField(max_length=256, null=True, blank=True)
    end_page = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        ordering = ["folios"]
        app_label = "imageserve"
        verbose_name_plural = "Witnesses"

    @property
    def known(self):
        return not self.name.startswith("UNKNOWN_")

    @property
    def manuscript_name(self):
        return self.manuscript.ms_name

    @property
    def titles(self):
        return self.texts.all()

    @property
    def start_folio(self):
        if self.folios:
            f = re.match(r'(?P<first>\d+[a|b]?)(?:-?)(?P<last>\d+[a|b]?)?', self.folios)
            if f:
                return f.group('first')
        return None

    @property
    def end_folio(self):
        if self.folios:
            f = re.match(r'(?P<first>\d+[a|b]?)(?:-?)(?P<last>\d+[a|b]?\(.*\)?)?', self.folios)
            if f:
                return f.group('last')
        return None

    def __unicode__(self):
        return u"{0}".format(self.ismi_id)
