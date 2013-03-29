from django.contrib import admin
# from imageserve.settings import JSON_INTERFACE
from imageserve.helpers import register_defs, register_manuscripts
from imageserve import models
# from imageserve import forms
# from json import loads
# from urllib import urlopen

admin.site.register(models.Manuscript, models.ManuscriptAdmin)
admin.site.register(models.ManuscriptGroup)
admin.site.register(models.AttDisplaySetting)
admin.site.register(models.RelDisplaySetting)

register_defs()
register_manuscripts()
