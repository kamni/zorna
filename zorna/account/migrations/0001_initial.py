# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'UserGroup'
        db.create_table('zorna_usergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['account.UserGroup'])),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('account', ['UserGroup'])

        # Adding model 'UserProfile'
        db.create_table('zorna_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='user_profile', null=True, to=orm['auth.User'])),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('telephonenumber', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('mobile', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('street', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('activation_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('account', ['UserProfile'])

        # Adding M2M table for field groups on 'UserProfile'
        db.create_table('zorna_userprofile_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['account.userprofile'], null=False)),
            ('usergroup', models.ForeignKey(orm['account.usergroup'], null=False))
        ))
        db.create_unique('zorna_userprofile_groups', ['userprofile_id', 'usergroup_id'])

        # Adding model 'UserAvatar'
        db.create_table('zorna_useravatar', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('avatar', self.gf('django.db.models.fields.files.ImageField')(max_length=1024, blank=True)),
        ))
        db.send_create_signal('account', ['UserAvatar'])


    def backwards(self, orm):
        
        # Deleting model 'UserGroup'
        db.delete_table('zorna_usergroup')

        # Deleting model 'UserProfile'
        db.delete_table('zorna_userprofile')

        # Removing M2M table for field groups on 'UserProfile'
        db.delete_table('zorna_userprofile_groups')

        # Deleting model 'UserAvatar'
        db.delete_table('zorna_useravatar')


    models = {
        'account.useravatar': {
            'Meta': {'object_name': 'UserAvatar', 'db_table': "'zorna_useravatar'"},
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '1024', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'account.usergroup': {
            'Meta': {'object_name': 'UserGroup', 'db_table': "'zorna_usergroup'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['account.UserGroup']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'account.userprofile': {
            'Meta': {'object_name': 'UserProfile', 'db_table': "'zorna_userprofile'"},
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['account.UserGroup']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'street': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'telephonenumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_profile'", 'null': 'True', 'to': "orm['auth.User']"}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['account']
