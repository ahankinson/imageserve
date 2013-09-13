from django.db import models


class CacheTable(models.Model):
    """docstring for CacheTable"""
    cache_key = models.CharField(max_length=255, primary_key=True)
    value = models.TextField()
    expires = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        app_label = "imageserve"
        db_table = "is_cache_table"
