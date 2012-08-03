# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting field 'Award.object_id'
        db.delete_column('forum_award', 'object_id')

        # Deleting field 'Award.content_type'
        db.delete_column('forum_award', 'content_type_id')

        # Adding unique constraint on 'Award', fields ['action']
        db.create_unique('forum_award', ['action_id'])

        # Deleting field 'Badge.multiple'
        db.delete_column('forum_badge', 'multiple')

        # Deleting field 'Badge.name'
        db.delete_column('forum_badge', 'name')

        # Deleting field 'Badge.slug'
        db.delete_column('forum_badge', 'slug')

        # Deleting field 'Badge.description'
        db.delete_column('forum_badge', 'description')
    
    
    def backwards(self, orm):
        
        # Adding field 'Award.object_id'
        db.add_column('forum_award', 'object_id', self.gf('django.db.models.fields.PositiveIntegerField')(default=1), keep_default=False)

        # Adding field 'Award.content_type'
        db.add_column('forum_award', 'content_type', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['contenttypes.ContentType']), keep_default=False)

        # Removing unique constraint on 'Award', fields ['action']
        db.delete_unique('forum_award', ['action_id'])

        # Adding field 'Badge.multiple'
        db.add_column('forum_badge', 'multiple', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'Badge.name'
        db.add_column('forum_badge', 'name', self.gf('django.db.models.fields.CharField')(default=1, max_length=50), keep_default=False)

        # Adding field 'Badge.slug'
        db.add_column('forum_badge', 'slug', self.gf('django.db.models.fields.SlugField')(blank=True, default=1, max_length=50, db_index=True), keep_default=False)

        # Adding field 'Badge.description'
        db.add_column('forum_badge', 'description', self.gf('django.db.models.fields.CharField')(default=1, max_length=300), keep_default=False)
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'forum.action': {
            'Meta': {'object_name': 'Action'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'canceled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'canceled_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'canceled_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'canceled_actions'", 'null': 'True', 'to': "orm['forum.User']"}),
            'canceled_ip': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'extra': ('forum.models.utils.PickledObjectField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'null': 'True', 'to': "orm['forum.Node']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': "orm['forum.User']"})
        },
        'forum.actionrepute': {
            'Meta': {'object_name': 'ActionRepute'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reputes'", 'to': "orm['forum.Action']"}),
            'by_canceled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reputes'", 'to': "orm['forum.User']"}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'forum.authkeyuserassociation': {
            'Meta': {'object_name': 'AuthKeyUserAssociation'},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'provider': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'auth_keys'", 'to': "orm['forum.User']"})
        },
        'forum.award': {
            'Meta': {'unique_together': "(('user', 'badge', 'node'),)", 'object_name': 'Award'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'award'", 'unique': 'True', 'to': "orm['forum.Action']"}),
            'awarded_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'badge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Badge']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Node']", 'null': 'True'}),
            'trigger': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'awards'", 'null': 'True', 'to': "orm['forum.Action']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']"})
        },
        'forum.badge': {
            'Meta': {'object_name': 'Badge'},
            'awarded_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'awarded_to': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'badges'", 'through': "'Award'", 'to': "orm['forum.User']"}),
            'cls': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'forum.flag': {
            'Meta': {'unique_together': "(('user', 'node'),)", 'object_name': 'Flag'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'flag'", 'unique': 'True', 'to': "orm['forum.Action']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Node']"}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']"}),
            'flagged_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
        },
        'forum.keyvalue': {
            'Meta': {'object_name': 'KeyValue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'value': ('forum.models.utils.PickledObjectField', [], {'null': 'True'})
        },
        'forum.markedtag': {
            'Meta': {'object_name': 'MarkedTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_selections'", 'to': "orm['forum.Tag']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tag_selections'", 'to': "orm['forum.User']"})
        },
        'forum.node': {
            'Meta': {'object_name': 'Node'},
            'abs_parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'all_children'", 'null': 'True', 'to': "orm['forum.Node']"}),
            'active_revision': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'active'", 'unique': 'True', 'null': 'True', 'to': "orm['forum.NodeRevision']"}),
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nodes'", 'to': "orm['forum.User']"}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'deleted': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deleted_node'", 'unique': 'True', 'null': 'True', 'to': "orm['forum.Action']"}),
            'extra_action': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'extra_node'", 'null': 'True', 'to': "orm['forum.Action']"}),
            'extra_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'extra_ref': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Node']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_moderation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'moderated_node'", 'unique': 'True', 'null': 'True', 'to': "orm['forum.Action']"}),
            'last_activity_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_activity_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']", 'null': 'True'}),
            'last_edited': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'edited_node'", 'unique': 'True', 'null': 'True', 'to': "orm['forum.Action']"}),
            'marked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'node_type': ('django.db.models.fields.CharField', [], {'default': "'node'", 'max_length': '16'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['forum.Node']"}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tagnames': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'nodes'", 'to': "orm['forum.Tag']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'wiki': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'forum.noderevision': {
            'Meta': {'unique_together': "(('node', 'revision'),)", 'object_name': 'NodeRevision'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'noderevisions'", 'to': "orm['forum.User']"}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': "orm['forum.Node']"}),
            'revised_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'revision': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'tagnames': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'forum.openidassociation': {
            'Meta': {'object_name': 'OpenIdAssociation'},
            'assoc_type': ('django.db.models.fields.TextField', [], {'max_length': '64'}),
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issued': ('django.db.models.fields.IntegerField', [], {}),
            'lifetime': ('django.db.models.fields.IntegerField', [], {}),
            'secret': ('django.db.models.fields.TextField', [], {'max_length': '255'}),
            'server_url': ('django.db.models.fields.TextField', [], {'max_length': '2047'})
        },
        'forum.openidnonce': {
            'Meta': {'object_name': 'OpenIdNonce'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'salt': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'server_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'timestamp': ('django.db.models.fields.IntegerField', [], {})
        },
        'forum.questionsubscription': {
            'Meta': {'object_name': 'QuestionSubscription'},
            'auto_subscription': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_view': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 5, 3, 11, 46, 22, 80000)'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Node']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']"})
        },
        'forum.subscriptionsettings': {
            'Meta': {'object_name': 'SubscriptionSettings'},
            'all_questions': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'all_questions_watched_tags': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'enable_notifications': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member_joins': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '1'}),
            'new_question': ('django.db.models.fields.CharField', [], {'default': "'d'", 'max_length': '1'}),
            'new_question_watched_tags': ('django.db.models.fields.CharField', [], {'default': "'i'", 'max_length': '1'}),
            'notify_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'notify_answers': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'notify_comments': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'notify_comments_own_post': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'notify_reply_to_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'questions_answered': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'questions_asked': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'questions_commented': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'questions_viewed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'subscribed_questions': ('django.db.models.fields.CharField', [], {'default': "'i'", 'max_length': '1'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'subscription_settings'", 'unique': 'True', 'to': "orm['forum.User']"})
        },
        'forum.tag': {
            'Meta': {'object_name': 'Tag'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_tags'", 'to': "orm['forum.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'deleted_tags'", 'null': 'True', 'to': "orm['forum.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marked_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'marked_tags'", 'through': "'MarkedTag'", 'to': "orm['forum.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'used_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'forum.user': {
            'Meta': {'object_name': 'User', '_ormbases': ['auth.User']},
            'about': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bronze': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email_isvalid': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'gold': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'real_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'reputation': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'silver': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'subscriptions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'subscribers'", 'through': "'QuestionSubscription'", 'to': "orm['forum.Node']"}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'forum.validationhash': {
            'Meta': {'unique_together': "(('user', 'type'),)", 'object_name': 'ValidationHash'},
            'expiration': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 5, 4, 11, 46, 28, 428000)'}),
            'hash_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seed': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']"})
        },
        'forum.vote': {
            'Meta': {'unique_together': "(('user', 'node'),)", 'object_name': 'Vote'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vote'", 'unique': 'True', 'to': "orm['forum.Action']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Node']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']"}),
            'value': ('django.db.models.fields.SmallIntegerField', [], {}),
            'voted_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
        }
    }
    
    complete_apps = ['forum']
