import os
from django.core.management.base import BaseCommand
from django.conf import settings
from imageserve.models import Manuscript


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        """
        Looks through the IMG_DIR folder for all manuscripts and ensures the
        database contains a Manuscript object for each.
        """

        directories = os.listdir(settings.IMG_DIR)
        known_manuscripts = Manuscript.objects.values_list('directory', flat=True)
        unknown_manuscripts = set(known_manuscripts).symmetric_difference(set(directories))
        for name in unknown_manuscripts:
            if os.path.isdir(os.path.join(settings.IMG_DIR, name)):
                num_files = len(os.listdir(os.path.join(settings.IMG_DIR, name)))
                m = Manuscript(num_files=num_files)
                m.directory = os.path.join(settings.IMG_DIR, name)
                m.clean()
                m.save()
