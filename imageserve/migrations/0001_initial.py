# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Manuscript'
        db.create_table(u'imageserve_manuscript', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('directory', self.gf('django.db.models.fields.FilePathField')(path='/data7/srv/images', unique=True, max_length=256)),
            ('ismi_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('num_files', self.gf('django.db.models.fields.IntegerField')()),
            ('has_folio_nums', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('folio_pgs', self.gf('django.db.models.fields.TextField')(default='{}', null=True)),
        ))
        db.send_create_signal('imageserve', ['Manuscript'])

        # Adding model 'ManuscriptGroup'
        db.create_table(u'imageserve_manuscriptgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('imageserve', ['ManuscriptGroup'])

        # Adding M2M table for field manuscripts on 'ManuscriptGroup'
        m2m_table_name = db.shorten_name(u'imageserve_manuscriptgroup_manuscripts')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('manuscriptgroup', models.ForeignKey(orm['imageserve.manuscriptgroup'], null=False)),
            ('manuscript', models.ForeignKey(orm['imageserve.manuscript'], null=False))
        ))
        db.create_unique(m2m_table_name, ['manuscriptgroup_id', 'manuscript_id'])

        # Adding model 'Witness'
        db.create_table(u'imageserve_witness', (
            ('ismi_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=512, null=True, blank=True)),
            ('manuscript', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='witnesses', null=True, to=orm['imageserve.Manuscript'])),
            ('data', self.gf('django.db.models.fields.TextField')(default='[]', null=True, blank=True)),
            ('folios', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('start_page', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('end_page', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal('imageserve', ['Witness'])

        # Adding model 'Person'
        db.create_table(u'imageserve_person', (
            ('ismi_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('data', self.gf('django.db.models.fields.TextField')(default='[]', null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='people', null=True, to=orm['imageserve.Text'])),
        ))
        db.send_create_signal('imageserve', ['Person'])

        # Adding model 'Text'
        db.create_table(u'imageserve_text', (
            ('ismi_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('data', self.gf('django.db.models.fields.TextField')(default='[]', null=True, blank=True)),
            ('witness', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='texts', null=True, to=orm['imageserve.Witness'])),
        ))
        db.send_create_signal('imageserve', ['Text'])

        # Adding model 'AttributeDisplay'
        db.create_table(u'imageserve_attributedisplay', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('show', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('on_ent', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('oc', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('imageserve', ['AttributeDisplay'])

        # Adding model 'RelationshipDisplay'
        db.create_table(u'imageserve_relationshipdisplay', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('show_id', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('show', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('on_ent', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('src_oc', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('tar_oc', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('imageserve', ['RelationshipDisplay'])


    def backwards(self, orm):
        # Deleting model 'Manuscript'
        db.delete_table(u'imageserve_manuscript')

        # Deleting model 'ManuscriptGroup'
        db.delete_table(u'imageserve_manuscriptgroup')

        # Removing M2M table for field manuscripts on 'ManuscriptGroup'
        db.delete_table(db.shorten_name(u'imageserve_manuscriptgroup_manuscripts'))

        # Deleting model 'Witness'
        db.delete_table(u'imageserve_witness')

        # Deleting model 'Person'
        db.delete_table(u'imageserve_person')

        # Deleting model 'Text'
        db.delete_table(u'imageserve_text')

        # Deleting model 'AttributeDisplay'
        db.delete_table(u'imageserve_attributedisplay')

        # Deleting model 'RelationshipDisplay'
        db.delete_table(u'imageserve_relationshipdisplay')


    models = {
        'imageserve.attributedisplay': {
            'Meta': {'object_name': 'AttributeDisplay'},
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'oc': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'on_ent': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'show': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'imageserve.manuscript': {
            'Meta': {'ordering': "['directory']", 'object_name': 'Manuscript'},
            'directory': ('django.db.models.fields.FilePathField', [], {'path': "'/data7/srv/images'", 'unique': 'True', 'max_length': '256'}),
            'folio_pgs': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True'}),
            'has_folio_nums': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ismi_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'num_files': ('django.db.models.fields.IntegerField', [], {})
        },
        'imageserve.manuscriptgroup': {
            'Meta': {'object_name': 'ManuscriptGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manuscripts': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['imageserve.Manuscript']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'imageserve.person': {
            'Meta': {'object_name': 'Person'},
            'data': ('django.db.models.fields.TextField', [], {'default': "'[]'", 'null': 'True', 'blank': 'True'}),
            'ismi_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'text': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'people'", 'null': 'True', 'to': "orm['imageserve.Text']"})
        },
        'imageserve.relationshipdisplay': {
            'Meta': {'object_name': 'RelationshipDisplay'},
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'on_ent': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'show': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'show_id': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'src_oc': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tar_oc': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'imageserve.text': {
            'Meta': {'object_name': 'Text'},
            'data': ('django.db.models.fields.TextField', [], {'default': "'[]'", 'null': 'True', 'blank': 'True'}),
            'ismi_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'witness': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'texts'", 'null': 'True', 'to': "orm['imageserve.Witness']"})
        },
        'imageserve.witness': {
            'Meta': {'ordering': "['folios']", 'object_name': 'Witness'},
            'data': ('django.db.models.fields.TextField', [], {'default': "'[]'", 'null': 'True', 'blank': 'True'}),
            'end_page': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'folios': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'ismi_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'manuscript': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'witnesses'", 'null': 'True', 'to': "orm['imageserve.Manuscript']"}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'start_page': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['imageserve']