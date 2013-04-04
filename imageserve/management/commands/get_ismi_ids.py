from django.core.management.base import BaseCommand
from imageserve.models import Manuscript
from csv import reader
import os

class Command(BaseCommand):
    help = 'Updates as many ISMI IDs for Stabi codices as possible'

    def handle(self, *args, **options):
        path = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))
        )
        fp = open(path+'/ismi_ids.csv','r')
        rdr = reader(fp)
        for directory, ismi_id in list(rdr)[1:]:
            print 'getting ISMI ID for', directory, '...',
            ms = Manuscript.objects.filter(directory=directory)
            if ms:
                try:
                    ms = Manuscript.objects.get(directory=directory)
                    ms.ismi_id = ismi_id
                    ms.clean()
                    ms.save()
                    print 'done.'
                except:
                    print directory, 'failed.'
                    continue
            else:
                print directory, 'not found.'