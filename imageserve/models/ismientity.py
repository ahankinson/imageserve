from django.db import models
from django_extensions.db.fields import json


class ISMIEntity(models.Model):
    ismi_id = models.IntegerField(primary_key=True)
    data = json.JSONField(default="[]", blank=True, null=True)

    class Meta:
        app_label = "imageserve"