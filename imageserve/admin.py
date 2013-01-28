from django.contrib import admin
from imageserve.settings import JSON_INTERFACE
from imageserve.helpers import register_defs
from imageserve import models
from json import loads
from urllib import urlopen

admin.site.register(models.Manuscript)
admin.site.register(models.ManuscriptGroup)
admin.site.register(models.AttDisplaySetting)
admin.site.register(models.RelDisplaySetting)

register_defs()