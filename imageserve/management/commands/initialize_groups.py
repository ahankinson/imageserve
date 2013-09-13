import os

from django.core.management.base import BaseCommand
from django.conf import settings
from imageserve.models import Manuscript, ManuscriptGroup

class Command(BaseCommand):
    help = 'Creates or updates a ManuscriptGroup for the Stabi codices'
    
    def handle(self, *args, **options):
        allms, created = ManuscriptGroup.objects.get_or_create(name="All")
        allms.manuscripts = Manuscript.objects.all()

        mg, created = ManuscriptGroup.objects.get_or_create(name="Stabi Codices")
        for directory in settings.STABI_CODICES:
            try:
                ms = Manuscript.objects.get(directory=os.path.join(settings.IMG_DIR, directory))
                mg.manuscripts.add(ms)
            except Manuscript.DoesNotExist:
                print('{0} not found'.format(directory))
                continue
        mg.save()