# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Manuscript'
        db.create_table('imageserveapp_manuscript', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('directory', self.gf('imageserveapp.models.FolderField')(path='/Users/jamieklassen/Documents/Code/imageserve/imageserve/images/', max_length=100)),
            ('ismi_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('num_files', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('imageserveapp', ['Manuscript'])

        # Adding model 'ManuscriptGroup'
        db.create_table('imageserveapp_manuscriptgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('imageserveapp', ['ManuscriptGroup'])

    def backwards(self, orm):
        # Deleting model 'Manuscript'
        db.delete_table('imageserveapp_manuscript')

        # Deleting model 'ManuscriptGroup'
        db.delete_table('imageserveapp_manuscriptgroup')

    models = {
        'imageserveapp.manuscript': {
            'Meta': {'object_name': 'Manuscript'},
            'directory': ('imageserveapp.models.FolderField', [], {'path': "'/Users/jamieklassen/Documents/Code/imageserve/imageserve/images/'", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ismi_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'num_files': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'imageserveapp.manuscriptgroup': {
            'Meta': {'object_name': 'ManuscriptGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['imageserveapp']