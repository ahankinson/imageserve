from django.contrib import admin
from imageserve.settings import JSON_INTERFACE
from imageserve.helpers import register_defs
from imageserve.models import Manuscript, ManuscriptGroup, AttDisplaySetting, RelDisplaySetting
from json import loads
from urllib import urlopen

admin.site.register(Manuscript)
admin.site.register(ManuscriptGroup)
admin.site.register(AttDisplaySetting)
admin.site.register(RelDisplaySetting)

register_defs()