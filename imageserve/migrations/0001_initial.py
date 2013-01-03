# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AttDisplaySetting'
        db.create_table('imageserve_attdisplaysetting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('show', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('on_ent', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('imageserve', ['AttDisplaySetting'])

        # Adding model 'RelDisplaySetting'
        db.create_table('imageserve_reldisplaysetting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rel_type', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('show_id', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('show', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('on_ent', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('imageserve', ['RelDisplaySetting'])

        # Adding model 'Manuscript'
        db.create_table('imageserve_manuscript', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('directory', self.gf('imageserve.models.FolderField')(path='/Users/jamieklassen/Documents/Code/imageserve/images/', max_length=100)),
            ('ismi_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('num_files', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('imageserve', ['Manuscript'])

        # Adding model 'ManuscriptGroup'
        db.create_table('imageserve_manuscriptgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('imageserve', ['ManuscriptGroup'])

        # Adding M2M table for field manuscripts on 'ManuscriptGroup'
        db.create_table('imageserve_manuscriptgroup_manuscripts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('manuscriptgroup', models.ForeignKey(orm['imageserve.manuscriptgroup'], null=False)),
            ('manuscript', models.ForeignKey(orm['imageserve.manuscript'], null=False))
        ))
        db.create_unique('imageserve_manuscriptgroup_manuscripts', ['manuscriptgroup_id', 'manuscript_id'])


    def backwards(self, orm):
        # Deleting model 'AttDisplaySetting'
        db.delete_table('imageserve_attdisplaysetting')

        # Deleting model 'RelDisplaySetting'
        db.delete_table('imageserve_reldisplaysetting')

        # Deleting model 'Manuscript'
        db.delete_table('imageserve_manuscript')

        # Deleting model 'ManuscriptGroup'
        db.delete_table('imageserve_manuscriptgroup')

        # Removing M2M table for field manuscripts on 'ManuscriptGroup'
        db.delete_table('imageserve_manuscriptgroup_manuscripts')


    models = {
        'imageserve.attdisplaysetting': {
            'Meta': {'object_name': 'AttDisplaySetting'},
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'on_ent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'imageserve.manuscript': {
            'Meta': {'object_name': 'Manuscript'},
            'directory': ('imageserve.models.FolderField', [], {'path': "'/Users/jamieklassen/Documents/Code/imageserve/images/'", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ismi_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'num_files': ('django.db.models.fields.IntegerField', [], {})
        },
        'imageserve.manuscriptgroup': {
            'Meta': {'object_name': 'ManuscriptGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manuscripts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['imageserve.Manuscript']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'imageserve.reldisplaysetting': {
            'Meta': {'object_name': 'RelDisplaySetting'},
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'on_ent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rel_type': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_id': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['imageserve']