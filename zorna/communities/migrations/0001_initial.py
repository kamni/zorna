# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Community'
        db.create_table('zorna_communities', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entity_content_type_communities_community_related', null=True, to=orm['contenttypes.ContentType'])),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='site_owner_communities_community_related', null=True, to=orm['sites.Site'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_owner_communities_community_related', null=True, to=orm['auth.User'])),
            ('modifier', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_modifier_communities_community_related', null=True, to=orm['auth.User'])),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('time_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('bgcolor', self.gf('django.db.models.fields.CharField')(max_length=6)),
        ))
        db.send_create_signal('communities', ['Community'])

        # Adding model 'MessageCommunity'
        db.create_table('zorna_community_messages', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entity_content_type_communities_messagecommunity_related', null=True, to=orm['contenttypes.ContentType'])),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='site_owner_communities_messagecommunity_related', null=True, to=orm['sites.Site'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_owner_communities_messagecommunity_related', null=True, to=orm['auth.User'])),
            ('modifier', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_modifier_communities_messagecommunity_related', null=True, to=orm['auth.User'])),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('time_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('reply', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['communities.MessageCommunity'], null=True)),
        ))
        db.send_create_signal('communities', ['MessageCommunity'])

        # Adding M2M table for field communities on 'MessageCommunity'
        db.create_table('zorna_community_messages_communities', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('messagecommunity', models.ForeignKey(orm['communities.messagecommunity'], null=False)),
            ('community', models.ForeignKey(orm['communities.community'], null=False))
        ))
        db.create_unique('zorna_community_messages_communities', ['messagecommunity_id', 'community_id'])

        # Adding M2M table for field users on 'MessageCommunity'
        db.create_table('zorna_community_messages_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('messagecommunity', models.ForeignKey(orm['communities.messagecommunity'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('zorna_community_messages_users', ['messagecommunity_id', 'user_id'])

        # Adding M2M table for field followers on 'MessageCommunity'
        db.create_table('zorna_community_messages_followers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('messagecommunity', models.ForeignKey(orm['communities.messagecommunity'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('zorna_community_messages_followers', ['messagecommunity_id', 'user_id'])

        # Adding model 'MessageCommunityExtra'
        db.create_table('zorna_community_messages_extra', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['communities.MessageCommunity'], null=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('communities', ['MessageCommunityExtra'])

        # Adding model 'AssignementCommunity'
        db.create_table('zorna_community_messages_assigments', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('communities', ['AssignementCommunity'])


    def backwards(self, orm):
        
        # Deleting model 'Community'
        db.delete_table('zorna_communities')

        # Deleting model 'MessageCommunity'
        db.delete_table('zorna_community_messages')

        # Removing M2M table for field communities on 'MessageCommunity'
        db.delete_table('zorna_community_messages_communities')

        # Removing M2M table for field users on 'MessageCommunity'
        db.delete_table('zorna_community_messages_users')

        # Removing M2M table for field followers on 'MessageCommunity'
        db.delete_table('zorna_community_messages_followers')

        # Deleting model 'MessageCommunityExtra'
        db.delete_table('zorna_community_messages_extra')

        # Deleting model 'AssignementCommunity'
        db.delete_table('zorna_community_messages_assigments')


    models = {
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
        'communities.assignementcommunity': {
            'Meta': {'object_name': 'AssignementCommunity', 'db_table': "'zorna_community_messages_assigments'"},
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'communities.community': {
            'Meta': {'object_name': 'Community', 'db_table': "'zorna_communities'"},
            'bgcolor': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_content_type_communities_community_related'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_modifier_communities_community_related'", 'null': 'True', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_owner_communities_community_related'", 'null': 'True', 'to': "orm['auth.User']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'site_owner_communities_community_related'", 'null': 'True', 'to': "orm['sites.Site']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'time_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        'communities.messagecommunity': {
            'Meta': {'object_name': 'MessageCommunity', 'db_table': "'zorna_community_messages'"},
            'communities': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['communities.Community']", 'symmetrical': 'False', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_content_type_communities_messagecommunity_related'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'message_followers'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'modifier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_modifier_communities_messagecommunity_related'", 'null': 'True', 'to': "orm['auth.User']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_owner_communities_messagecommunity_related'", 'null': 'True', 'to': "orm['auth.User']"}),
            'reply': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['communities.MessageCommunity']", 'null': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'site_owner_communities_messagecommunity_related'", 'null': 'True', 'to': "orm['sites.Site']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'time_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'message_users'", 'blank': 'True', 'to': "orm['auth.User']"})
        },
        'communities.messagecommunityextra': {
            'Meta': {'object_name': 'MessageCommunityExtra', 'db_table': "'zorna_community_messages_extra'"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['communities.MessageCommunity']", 'null': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['communities']
