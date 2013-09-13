import os
from django.db import models


class FolderField(models.FilePathField):
    """
    In Django 1.5 this is implemented already, but this is just
    a shortcut so we can use folders instead of files.
    """
    def __init__(self, *args, **kwargs):
        d = kwargs['path']
        kwargs['choices'] = [(name, name) for name in os.listdir(d)
                             if os.path.isdir(os.path.join(d, name))]
        super(FolderField, self).__init__(*args, **kwargs)