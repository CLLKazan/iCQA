# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'User'
        db.create_table('forum_user', (
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('hide_ignored_questions', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('is_approved', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('email_isvalid', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('real_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('about', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('silver', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('reputation', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('gravatar', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('tag_filter_setting', self.gf('django.db.models.fields.CharField')(default='ignored', max_length=16)),
            ('gold', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('last_seen', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('email_key', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('bronze', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('questions_per_page', self.gf('django.db.models.fields.SmallIntegerField')(default=10)),
        ))
        db.send_create_signal('forum', ['User'])

        # Adding model 'Activity'
        db.create_table(u'activity', (
            ('is_auditted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forum.User'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('active_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('activity_type', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal('forum', ['Activity'])

        # Adding model 'SubscriptionSettings'
        db.create_table('forum_subscriptionsettings', (
            ('questions_asked', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('questions_viewed', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('notify_comments', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('new_question', self.gf('django.db.models.fields.CharField')(default='d', max_length=1)),
            ('all_questions', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('new_question_watched_tags', self.gf('django.db.models.fields.CharField')(default='i', max_length=1)),
            ('questions_answered', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('notify_comments_own_post', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('questions_commented', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('subscribed_questions', self.gf('django.db.models.fields.CharField')(default='i', max_length=1)),
            ('notify_reply_to_comments', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('member_joins', self.gf('django.db.models.fields.CharField')(default='n', max_length=1)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='subscription_settings', unique=True, to=orm['forum.User'])),
            ('notify_answers', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('enable_notifications', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('all_questions_watched_tags', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notify_accepted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('forum', ['SubscriptionSettings'])

        # Adding model 'ValidationHash'
        db.create_table('forum_validationhash', (
            ('hash_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('seed', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('expiration', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 4, 7, 10, 36, 23, 812000))),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forum.User'])),
        ))
        db.send_create_signal('forum', ['ValidationHash'])

        # Adding unique constraint on 'ValidationHash', fields ['user', 'type']
        db.create_unique('forum_validationhash', ['user_id', 'type'])

        # Adding model 'AuthKeyUserAssociation'
        db.create_table('forum_authkeyuserassociation', (
            ('added_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='auth_keys', to=orm['forum.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('provider', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('forum', ['AuthKeyUserAssociation'])

        # Adding model 'Vote'
        db.create_table(u'vote', (
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('voted_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='votes', to=orm['forum.User'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('vote', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('forum', ['Vote'])

        # Adding unique constraint on 'Vote', fields ['content_type', 'object_id', 'user']
        db.create_unique(u'vote', ['content_type_id', 'object_id', 'user_id'])

        # Adding model 'FlaggedItem'
        db.create_table(u'flagged_item', (
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('flagged_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='flaggeditems', to=orm['forum.User'])),
        ))
        db.send_create_signal('forum', ['FlaggedItem'])

        # Adding unique constraint on 'FlaggedItem', fields ['content_type', 'object_id', 'user']
        db.create_unique(u'flagged_item', ['content_type_id', 'object_id', 'user_id'])

        # Adding model 'Comment'
        db.create_table(u'comment', (
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('added_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comments', to=orm['forum.User'])),
        ))
        db.send_create_signal('forum', ['Comment'])

        # Adding model 'Tag'
        db.create_table(u'tag', (
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_tags', to=orm['forum.User'])),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='deleted_tags', null=True, to=orm['forum.User'])),
            ('used_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('deleted_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('forum', ['Tag'])

        # Adding model 'MarkedTag'
        db.create_table('forum_markedtag', (
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_selections', to=orm['forum.Tag'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tag_selections', to=orm['forum.User'])),
        ))
        db.send_create_signal('forum', ['MarkedTag'])

        # Adding model 'Question'
        db.create_table(u'question', (
            ('wiki', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('vote_up_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('answer_accepted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('offensive_flag_count', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('closed_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('deleted_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_activity_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='last_active_in_questions', to=orm['forum.User'])),
            ('view_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('locked_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='questions', to=orm['forum.User'])),
            ('comment_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('html', self.gf('django.db.models.fields.TextField')()),
            ('vote_down_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('last_edited_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='last_edited_questions', null=True, to=orm['forum.User'])),
            ('favourite_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=180)),
            ('answer_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('last_activity_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('closed_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='closed_questions', null=True, to=orm['forum.User'])),
            ('close_reason', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('tagnames', self.gf('django.db.models.fields.CharField')(max_length=125)),
            ('locked_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='locked_questions', null=True, to=orm['forum.User'])),
            ('added_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='deleted_questions', null=True, to=orm['forum.User'])),
            ('wikified_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('last_edited_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('forum', ['Question'])

        # Adding M2M table for field followed_by on 'Question'
        db.create_table(u'question_followed_by', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('question', models.ForeignKey(orm['forum.question'], null=False)),
            ('user', models.ForeignKey(orm['forum.user'], null=False))
        ))
        db.create_unique(u'question_followed_by', ['question_id', 'user_id'])

        # Adding M2M table for field tags on 'Question'
        db.create_table(u'question_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('question', models.ForeignKey(orm['forum.question'], null=False)),
            ('tag', models.ForeignKey(orm['forum.tag'], null=False))
        ))
        db.create_unique(u'question_tags', ['question_id', 'tag_id'])

        # Adding model 'QuestionSubscription'
        db.create_table('forum_questionsubscription', (
            ('last_view', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 4, 6, 10, 36, 23, 725000))),
            ('auto_subscription', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forum.Question'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forum.User'])),
        ))
        db.send_create_signal('forum', ['QuestionSubscription'])

        # Adding model 'FavoriteQuestion'
        db.create_table(u'favorite_question', (
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forum.Question'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('added_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_favorite_questions', to=orm['forum.User'])),
        ))
        db.send_create_signal('forum', ['FavoriteQuestion'])

        # Adding model 'QuestionRevision'
        db.create_table(u'question_revision', (
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='questionrevisions', to=orm['forum.User'])),
            ('tagnames', self.gf('django.db.models.fields.CharField')(max_length=125)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='revisions', to=orm['forum.Question'])),
            ('revised_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('revision', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('forum', ['QuestionRevision'])

        # Adding model 'AnonymousQuestion'
        db.create_table('forum_anonymousquestion', (
            ('wiki', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('ip_addr', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forum.User'], null=True)),
            ('tagnames', self.gf('django.db.models.fields.CharField')(max_length=125)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('added_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=180)),
            ('session_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('forum', ['AnonymousQuestion'])

        # Adding model 'Answer'
        db.create_table(u'answer', (
            ('wiki', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('vote_up_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('offensive_flag_count', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('deleted_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('locked_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answers', to=orm['forum.User'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answers', to=orm['forum.Question'])),
            ('comment_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('html', self.gf('django.db.models.fields.TextField')()),
            ('vote_down_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_edited_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='last_edited_answers', null=True, to=orm['forum.User'])),
            ('accepted_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('accepted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('locked_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='locked_answers', null=True, to=orm['forum.User'])),
            ('added_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='deleted_answers', null=True, to=orm['forum.User'])),
            ('wikified_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_edited_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('forum', ['Answer'])

        # Adding model 'AnswerRevision'
        db.create_table(u'answer_revision', (
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answerrevisions', to=orm['forum.User'])),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('revised_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('answer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='revisions', to=orm['forum.Answer'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('revision', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('forum', ['AnswerRevision'])

        # Adding model 'AnonymousAnswer'
        db.create_table('forum_anonymousanswer', (
            ('wiki', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('ip_addr', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forum.User'], null=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='anonymous_answers', to=orm['forum.Question'])),
            ('added_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=180)),
            ('session_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('forum', ['AnonymousAnswer'])

        # Adding model 'Badge'
        db.create_table(u'badge', (
            ('multiple', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('awarded_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('type', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('forum', ['Badge'])

        # Adding unique constraint on 'Badge', fields ['name', 'type']
        db.create_unique(u'badge', ['name', 'type'])

        # Adding model 'Award'
        db.create_table(u'award', (
            ('awarded_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('notified', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='awards', to=orm['forum.User'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('badge', self.gf('django.db.models.fields.related.ForeignKey')(related_name='award_badge', to=orm['forum.Badge'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('forum', ['Award'])

        # Adding unique constraint on 'Award', fields ['content_type', 'object_id', 'user', 'badge']
        db.create_unique(u'award', ['content_type_id', 'object_id', 'user_id', 'badge_id'])

        # Adding model 'Repute'
        db.create_table(u'repute', (
            ('positive', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forum.Question'])),
            ('negative', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('reputation_type', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forum.User'])),
            ('reputed_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reputation', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('forum', ['Repute'])

        # Adding model 'KeyValue'
        db.create_table('forum_keyvalue', (
            ('value', self.gf('forum.models.utils.PickledObjectField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('forum', ['KeyValue'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'User'
        db.delete_table('forum_user')

        # Deleting model 'Activity'
        db.delete_table(u'activity')

        # Deleting model 'SubscriptionSettings'
        db.delete_table('forum_subscriptionsettings')

        # Deleting model 'ValidationHash'
        db.delete_table('forum_validationhash')

        # Removing unique constraint on 'ValidationHash', fields ['user', 'type']
        db.delete_unique('forum_validationhash', ['user_id', 'type'])

        # Deleting model 'AuthKeyUserAssociation'
        db.delete_table('forum_authkeyuserassociation')

        # Deleting model 'Vote'
        db.delete_table(u'vote')

        # Removing unique constraint on 'Vote', fields ['content_type', 'object_id', 'user']
        db.delete_unique(u'vote', ['content_type_id', 'object_id', 'user_id'])

        # Deleting model 'FlaggedItem'
        db.delete_table(u'flagged_item')

        # Removing unique constraint on 'FlaggedItem', fields ['content_type', 'object_id', 'user']
        db.delete_unique(u'flagged_item', ['content_type_id', 'object_id', 'user_id'])

        # Deleting model 'Comment'
        db.delete_table(u'comment')

        # Deleting model 'Tag'
        db.delete_table(u'tag')

        # Deleting model 'MarkedTag'
        db.delete_table('forum_markedtag')

        # Deleting model 'Question'
        db.delete_table(u'question')

        # Removing M2M table for field followed_by on 'Question'
        db.delete_table('question_followed_by')

        # Removing M2M table for field tags on 'Question'
        db.delete_table('question_tags')

        # Deleting model 'QuestionSubscription'
        db.delete_table('forum_questionsubscription')

        # Deleting model 'FavoriteQuestion'
        db.delete_table(u'favorite_question')

        # Deleting model 'QuestionRevision'
        db.delete_table(u'question_revision')

        # Deleting model 'AnonymousQuestion'
        db.delete_table('forum_anonymousquestion')

        # Deleting model 'Answer'
        db.delete_table(u'answer')

        # Deleting model 'AnswerRevision'
        db.delete_table(u'answer_revision')

        # Deleting model 'AnonymousAnswer'
        db.delete_table('forum_anonymousanswer')

        # Deleting model 'Badge'
        db.delete_table(u'badge')

        # Removing unique constraint on 'Badge', fields ['name', 'type']
        db.delete_unique(u'badge', ['name', 'type'])

        # Deleting model 'Award'
        db.delete_table(u'award')

        # Removing unique constraint on 'Award', fields ['content_type', 'object_id', 'user', 'badge']
        db.delete_unique(u'award', ['content_type_id', 'object_id', 'user_id', 'badge_id'])

        # Deleting model 'Repute'
        db.delete_table(u'repute')

        # Deleting model 'KeyValue'
        db.delete_table('forum_keyvalue')
    
    
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
        'forum.activity': {
            'Meta': {'object_name': 'Activity', 'db_table': "u'activity'"},
            'active_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'activity_type': ('django.db.models.fields.SmallIntegerField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_auditted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']"})
        },
        'forum.anonymousanswer': {
            'Meta': {'object_name': 'AnonymousAnswer'},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_addr': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'anonymous_answers'", 'to': "orm['forum.Question']"}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '180'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'wiki': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'forum.anonymousquestion': {
            'Meta': {'object_name': 'AnonymousQuestion'},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_addr': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '180'}),
            'tagnames': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'wiki': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'forum.answer': {
            'Meta': {'object_name': 'Answer', 'db_table': "u'answer'"},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'accepted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': "orm['forum.User']"}),
            'comment_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'deleted_answers'", 'null': 'True', 'to': "orm['forum.User']"}),
            'html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_edited_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_edited_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_edited_answers'", 'null': 'True', 'to': "orm['forum.User']"}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'locked_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'locked_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'locked_answers'", 'null': 'True', 'to': "orm['forum.User']"}),
            'offensive_flag_count': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': "orm['forum.Question']"}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'vote_down_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'vote_up_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'wiki': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'wikified_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'forum.answerrevision': {
            'Meta': {'object_name': 'AnswerRevision', 'db_table': "u'answer_revision'"},
            'answer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': "orm['forum.Answer']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answerrevisions'", 'to': "orm['forum.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revised_at': ('django.db.models.fields.DateTimeField', [], {}),
            'revision': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
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
            'Meta': {'unique_together': "(('content_type', 'object_id', 'user', 'badge'),)", 'object_name': 'Award', 'db_table': "u'award'"},
            'awarded_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'badge': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'award_badge'", 'to': "orm['forum.Badge']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notified': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'awards'", 'to': "orm['forum.User']"})
        },
        'forum.badge': {
            'Meta': {'unique_together': "(('name', 'type'),)", 'object_name': 'Badge', 'db_table': "u'badge'"},
            'awarded_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'awarded_to': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'badges'", 'through': "'Award'", 'to': "orm['forum.User']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'multiple': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'type': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'forum.comment': {
            'Meta': {'object_name': 'Comment', 'db_table': "u'comment'"},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['forum.User']"})
        },
        'forum.favoritequestion': {
            'Meta': {'object_name': 'FavoriteQuestion', 'db_table': "u'favorite_question'"},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Question']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_favorite_questions'", 'to': "orm['forum.User']"})
        },
        'forum.flaggeditem': {
            'Meta': {'unique_together': "(('content_type', 'object_id', 'user'),)", 'object_name': 'FlaggedItem', 'db_table': "u'flagged_item'"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'flagged_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'flaggeditems'", 'to': "orm['forum.User']"})
        },
        'forum.keyvalue': {
            'Meta': {'object_name': 'KeyValue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'value': ('forum.models.utils.PickledObjectField', [], {})
        },
        'forum.markedtag': {
            'Meta': {'object_name': 'MarkedTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_selections'", 'to': "orm['forum.Tag']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tag_selections'", 'to': "orm['forum.User']"})
        },
        'forum.question': {
            'Meta': {'object_name': 'Question', 'db_table': "u'question'"},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'answer_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'answer_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions'", 'to': "orm['forum.User']"}),
            'close_reason': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'closed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'closed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'closed_questions'", 'null': 'True', 'to': "orm['forum.User']"}),
            'comment_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'deleted_questions'", 'null': 'True', 'to': "orm['forum.User']"}),
            'favorited_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'favorite_questions'", 'through': "'FavoriteQuestion'", 'to': "orm['forum.User']"}),
            'favourite_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'followed_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'followed_questions'", 'to': "orm['forum.User']"}),
            'html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_activity_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_activity_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'last_active_in_questions'", 'to': "orm['forum.User']"}),
            'last_edited_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_edited_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_edited_questions'", 'null': 'True', 'to': "orm['forum.User']"}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'locked_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'locked_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'locked_questions'", 'null': 'True', 'to': "orm['forum.User']"}),
            'offensive_flag_count': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subscribers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'subscriptions'", 'through': "'QuestionSubscription'", 'to': "orm['forum.User']"}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '180'}),
            'tagnames': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'questions'", 'to': "orm['forum.Tag']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'view_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'vote_down_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'vote_up_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'wiki': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'wikified_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'forum.questionrevision': {
            'Meta': {'object_name': 'QuestionRevision', 'db_table': "u'question_revision'"},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questionrevisions'", 'to': "orm['forum.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': "orm['forum.Question']"}),
            'revised_at': ('django.db.models.fields.DateTimeField', [], {}),
            'revision': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'tagnames': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'forum.questionsubscription': {
            'Meta': {'object_name': 'QuestionSubscription'},
            'auto_subscription': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_view': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 4, 6, 10, 36, 23, 725000)'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Question']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']"})
        },
        'forum.repute': {
            'Meta': {'object_name': 'Repute', 'db_table': "u'repute'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'negative': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'positive': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Question']"}),
            'reputation': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'reputation_type': ('django.db.models.fields.SmallIntegerField', [], {}),
            'reputed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
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
            'Meta': {'object_name': 'Tag', 'db_table': "u'tag'"},
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
            'bronze': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email_isvalid': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'email_key': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'gold': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'gravatar': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'hide_ignored_questions': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'questions_per_page': ('django.db.models.fields.SmallIntegerField', [], {'default': '10'}),
            'real_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'reputation': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'silver': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'tag_filter_setting': ('django.db.models.fields.CharField', [], {'default': "'ignored'", 'max_length': '16'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'forum.validationhash': {
            'Meta': {'unique_together': "(('user', 'type'),)", 'object_name': 'ValidationHash'},
            'expiration': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 4, 7, 10, 36, 23, 863000)'}),
            'hash_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seed': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']"})
        },
        'forum.vote': {
            'Meta': {'unique_together': "(('content_type', 'object_id', 'user'),)", 'object_name': 'Vote', 'db_table': "u'vote'"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['forum.User']"}),
            'vote': ('django.db.models.fields.SmallIntegerField', [], {}),
            'voted_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }
    
    complete_apps = ['forum']
