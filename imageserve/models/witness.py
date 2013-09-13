from django.db import models
from django_extensions.db.fields import json


class Witness(models.Model):
    ismi_id = models.IntegerField(primary_key=True)
    manuscript = models.ForeignKey("imageserve.Manuscript", blank=True, null=True, related_name="witnesses")
    data = json.JSONField(default="[]", blank=True, null=True)

    class Meta:
        app_label = "imageserve"

    def __unicode__(self):
        return u"{0}".format(self.ismi_id)
