from django.db import models
from django_extensions.db.fields import json


class ISMIEntity(models.Model):
    ismi_id = models.IntegerField(primary_key=True)
    ismi_type = models.CharField(max_length=32)
    data = json.JSONField(default="[]", blank=True, null=True)
    synced = models.BooleanField(default=False)
    manuscript = models.ManyToManyField("imageserve.Manuscript", blank=True, null=True, related_name="entities")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.ismi_id)

    class Meta:
        app_label = "imageserve"
        verbose_name_plural = "ISMI Entities"