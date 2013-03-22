"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from imageserve.helpers import *
from imageserve.models import AttDisplaySetting


class DisplaySettingTest(TestCase):
    def setUp(self):
        register_defs()
        self.ids = [63326, 58563, 127137, 459500, 192396,
                    65097, 98889, 65592, 72863, 76031]
    
    def testAtts(self):
        for iden in self.ids:
            ent = get_by_ismi_id(iden)
            for att in ent['atts']:
                try:
                    s = AttDisplaySetting.objects.get(name=att['name'])
                    self.assertEqual(get_keyval(s,iden)[1], att['ov'])
                except:
                    continue
