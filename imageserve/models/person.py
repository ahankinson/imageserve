from django.db import models
from django_extensions.db.fields import json


class Person(models.Model):
    ismi_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=512)
    data = json.JSONField(default="[]", blank=True, null=True)
    text = models.ForeignKey('imageserve.Text', blank=True, null=True, related_name="people")

    class Meta:
        app_label = "imageserve"
        verbose_name_plural = "People"

    def __unicode__(self):
        return u"{0}".format(self.name)