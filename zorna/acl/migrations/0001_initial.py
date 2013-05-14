# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ACLVerbPermission'
        db.create_table('zorna_verbs_permissions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('codename', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('acl', ['ACLVerbPermission'])

        # Adding unique constraint on 'ACLVerbPermission', fields ['content_type', 'codename']
        db.create_unique('zorna_verbs_permissions', ['content_type_id', 'codename'])

        # Adding model 'ACLPermission'
        db.create_table('zorna_permissions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acl.ACLVerbPermission'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='acl_group', null=True, to=orm['account.UserGroup'])),
            ('acltype', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
        ))
        db.send_create_signal('acl', ['ACLPermission'])

        # Adding unique constraint on 'ACLPermission', fields ['permission', 'object_id', 'content_type', 'user', 'group']
        db.create_unique('zorna_permissions', ['permission_id', 'object_id', 'content_type_id', 'user_id', 'group_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'ACLPermission', fields ['permission', 'object_id', 'content_type', 'user', 'group']
        db.delete_unique('zorna_permissions', ['permission_id', 'object_id', 'content_type_id', 'user_id', 'group_id'])

        # Removing unique constraint on 'ACLVerbPermission', fields ['content_type', 'codename']
        db.delete_unique('zorna_verbs_permissions', ['content_type_id', 'codename'])

        # Deleting model 'ACLVerbPermission'
        db.delete_table('zorna_verbs_permissions')

        # Deleting model 'ACLPermission'
        db.delete_table('zorna_permissions')


    models = {
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
        'acl.aclpermission': {
            'Meta': {'unique_together': "(('permission', 'object_id', 'content_type', 'user', 'group'),)", 'object_name': 'ACLPermission', 'db_table': "'zorna_permissions'"},
            'acltype': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'acl_group'", 'null': 'True', 'to': "orm['account.UserGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acl.ACLVerbPermission']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'acl.aclverbpermission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'ACLVerbPermission', 'db_table': "'zorna_verbs_permissions'"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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

    complete_apps = ['acl']
