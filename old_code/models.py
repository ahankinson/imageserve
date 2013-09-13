import os
import unicodedata
from lxml import etree, html
from django.db import models
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django_extensions.db.fields import json
from conf import IMG_DIR
from imageserve.helpers import get_by_ismi_id, get_name, get_rel
from imageserve.forms import IntegerListField, FolioPagesField, FolioPages
from imageserve.settings import NO_DATA_MSG, CACHE_ENABLED
from south.modelsinspector import add_introspection_rules


add_introspection_rules([], ["^imageserve\.models\.IsmiIdField"])
add_introspection_rules([], ["^imageserve\.models\.FolderField"])