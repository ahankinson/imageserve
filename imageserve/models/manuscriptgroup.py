from django.db import models


class ManuscriptGroup(models.Model):
    """
    A group of manuscripts which fit
    under some common category.
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    manuscripts = models.ManyToManyField(Manuscript, blank=True, null=True)

    class Meta:
        app_label = "imageserve"
        permissions = (
            ('view_manuscript_group', 'Can View Manuscripts in Group'),
        )

    def __unicode__(self):
        return unicode(self.name)