# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'PollChoiceData', fields ['user', 'choice']
        db.delete_unique('pollit_pollchoicedata', ['user_id', 'choice_id'])

        # Adding field 'Poll.anonymous'
        db.add_column('pollit_poll', 'anonymous', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Poll.multiple_choice'
        db.add_column('pollit_poll', 'multiple_choice', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Poll.multiple_choice_limit'
        db.add_column('pollit_poll', 'multiple_choice_limit', self.gf('django.db.models.fields.PositiveIntegerField')(default=0), keep_default=False)

        # Changing field 'Poll.pub_date'
        db.alter_column('pollit_poll', 'pub_date', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'Poll.comment_status'
        db.alter_column('pollit_poll', 'comment_status', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'PollChoiceData.user'
        db.alter_column('pollit_pollchoicedata', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))


    def backwards(self, orm):
        
        # Deleting field 'Poll.anonymous'
        db.delete_column('pollit_poll', 'anonymous')

        # Deleting field 'Poll.multiple_choice'
        db.delete_column('pollit_poll', 'multiple_choice')

        # Deleting field 'Poll.multiple_choice_limit'
        db.delete_column('pollit_poll', 'multiple_choice_limit')

        # Changing field 'Poll.pub_date'
        db.alter_column('pollit_poll', 'pub_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'Poll.comment_status'
        db.alter_column('pollit_poll', 'comment_status', self.gf('django.db.models.fields.IntegerField')())

        # User chose to not deal with backwards NULL issues for 'PollChoiceData.user'
        # Thoughts: Because poll's can have anonymous users this value will 
        # be set to null. If we wanted to roll back the schema to the previous 
        # version we could create dummy user's per choice to replace the null values.
        raise RuntimeError("Cannot reverse this migration. 'PollChoiceData.user' and its values cannot be restored.")

        # Adding unique constraint on 'PollChoiceData', fields ['user', 'choice']
        db.create_unique('pollit_pollchoicedata', ['user_id', 'choice_id'])


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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'pollit.poll': {
            'Meta': {'ordering': "('-pub_date',)", 'object_name': 'Poll'},
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comment_status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'expire_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'multiple_choice': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'multiple_choice_limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2'}),
            'total_votes': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'pollit.pollchoice': {
            'Meta': {'ordering': "['order']", 'object_name': 'PollChoice'},
            'choice': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollit.Poll']"}),
            'votes': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'pollit.pollchoicedata': {
            'Meta': {'object_name': 'PollChoiceData'},
            'choice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollit.PollChoice']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['pollit.Poll']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['pollit']