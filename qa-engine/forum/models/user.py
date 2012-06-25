from base import *
from utils import PickledObjectField
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User as DjangoUser, AnonymousUser as DjangoAnonymousUser
from django.db.models import Q
try:
    from hashlib import md5
except:
    from md5 import new as md5

import string
from random import Random

from django.utils.translation import ugettext as _
import logging

class AnonymousUser(DjangoAnonymousUser):
    reputation = 0
    
    def get_visible_answers(self, question):
        return question.answers.filter_state(deleted=False)

    def can_view_deleted_post(self, post):
        return False

    def can_vote_up(self):
        return False

    def can_vote_down(self):
        return False
    
    def can_vote_count_today(self):
        return 0

    def can_flag_offensive(self, post=None):
        return False

    def can_view_offensive_flags(self, post=None):
        return False

    def can_comment(self, post):
        return False

    def can_like_comment(self, comment):
        return False

    def can_edit_comment(self, comment):
        return False

    def can_delete_comment(self, comment):
        return False

    def can_convert_to_comment(self, answer):
        return False
    
    def can_convert_to_question(self, answer):
        return False
    
    def can_convert_comment_to_answer(self, comment):
        return False

    def can_accept_answer(self, answer):
        return False

    def can_create_tags(self):
        return False

    def can_edit_post(self, post):
        return False

    def can_wikify(self, post):
        return False

    def can_cancel_wiki(self, post):
        return False

    def can_retag_questions(self):
        return False

    def can_close_question(self, question):
        return False

    def can_reopen_question(self, question):
        return False

    def can_delete_post(self, post):
        return False

    def can_upload_files(self):
        return False

    def is_a_super_user_or_staff(self):
        return False

def true_if_is_super_or_staff(fn):
    def decorated(self, *args, **kwargs):
        return self.is_superuser or self.is_staff or fn(self, *args, **kwargs)

    return decorated

def false_if_validation_required_to(item):
    def decorator(fn):
        def decorated(self, *args, **kwargs):
            if item in settings.REQUIRE_EMAIL_VALIDATION_TO and not self.email_isvalid:
                return False
            else:
                return fn(self, *args, **kwargs)
        return decorated
    return decorator

class User(BaseModel, DjangoUser):
    is_approved = models.BooleanField(default=False)
    email_isvalid = models.BooleanField(default=False)

    reputation = models.PositiveIntegerField(default=0)
    gold = models.PositiveIntegerField(default=0)
    silver = models.PositiveIntegerField(default=0)
    bronze = models.PositiveIntegerField(default=0)

    last_seen = models.DateTimeField(default=datetime.datetime.now)
    real_name = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    about = models.TextField(blank=True)

    subscriptions = models.ManyToManyField('Node', related_name='subscribers', through='QuestionSubscription')

    vote_up_count = DenormalizedField("actions", canceled=False, action_type="voteup")
    vote_down_count = DenormalizedField("actions", canceled=False, action_type="votedown")

    def __unicode__(self):
        return self.username

    @property
    def prop(self):
        prop = self.__dict__.get('_prop', None)

        if prop is None:
            prop = UserPropertyDict(self)
            self._prop = prop

        return prop

    @property
    def is_siteowner(self):
        #todo: temporary thing, for now lets just assume that the site owner will always be the first user of the application
        return self.id == 1

    @property
    def decorated_name(self):
        if settings.SHOW_STATUS_DIAMONDS:
            if self.is_superuser:
                return u"%s \u2666\u2666" % self.username

            if self.is_staff:
                return u"%s \u2666" % self.username

        return self.username

    @property
    def last_activity(self):
        try:
            return self.actions.order_by('-action_date')[0].action_date
        except:
            return self.last_seen

    @property
    def gravatar(self):
        return md5(self.email.lower()).hexdigest()
    
    def save(self, *args, **kwargs):
        if self.reputation < 0:
            self.reputation = 0

        new = not bool(self.id)

        super(User, self).save(*args, **kwargs)

        if new:
            sub_settings = SubscriptionSettings(user=self)
            sub_settings.save()

    def get_messages(self):
        messages = []
        for m in self.message_set.all():
            messages.append(m.message)
        return messages

    def delete_messages(self):
        self.message_set.all().delete()

    @models.permalink
    def get_profile_url(self):
        return ('user_profile', (), {'id': self.id, 'slug': slugify(self.username)})

    def get_absolute_url(self):
        return self.get_profile_url()

    @models.permalink
    def get_asked_url(self):
        return ('user_questions', (), {'mode': _('asked-by'), 'user': self.id, 'slug': slugify(self.username)})

    @models.permalink
    def get_answered_url(self):
        return ('user_questions', (), {'mode': _('answered-by'), 'user': self.id, 'slug': slugify(self.username)})

    @models.permalink
    def get_subscribed_url(self):
        return ('user_questions', (), {'mode': _('subscribed-by'), 'user': self.id, 'slug': slugify(self.username)})

    def get_profile_link(self):
        profile_link = u'<a href="%s">%s</a>' % (self.get_profile_url(), self.username)
        return mark_safe(profile_link)

    def get_visible_answers(self, question):
        return question.answers.filter_state(deleted=False)

    def get_vote_count_today(self):
        today = datetime.date.today()
        return self.actions.filter(canceled=False, action_type__in=("voteup", "votedown"),
                                   action_date__gte=(today - datetime.timedelta(days=1))).count()

    def get_reputation_by_upvoted_today(self):
        today = datetime.datetime.now()
        sum = self.reputes.filter(reputed_at__range=(today - datetime.timedelta(days=1), today)).aggregate(
                models.Sum('value'))
        #todo: redo this, maybe transform in the daily cap
        #if sum.get('value__sum', None) is not None: return sum['value__sum']
        return 0

    def get_flagged_items_count_today(self):
        today = datetime.date.today()
        return self.actions.filter(canceled=False, action_type="flag",
                                   action_date__gte=(today - datetime.timedelta(days=1))).count()
    
    def can_vote_count_today(self):
        votes_today = settings.MAX_VOTES_PER_DAY
        
        if settings.USER_REPUTATION_TO_MAX_VOTES:
            votes_today = votes_today + int(self.reputation)
        
        return votes_today
    
    @true_if_is_super_or_staff
    def can_view_deleted_post(self, post):
        return post.author == self

    @true_if_is_super_or_staff
    def can_vote_up(self):
        return self.reputation >= int(settings.REP_TO_VOTE_UP)

    @true_if_is_super_or_staff
    def can_vote_down(self):
        return self.reputation >= int(settings.REP_TO_VOTE_DOWN)

    @false_if_validation_required_to('flag')
    def can_flag_offensive(self, post=None):
        if post is not None and post.author == self:
            return False
        return self.is_superuser or self.is_staff or self.reputation >= int(settings.REP_TO_FLAG)

    @true_if_is_super_or_staff
    def can_view_offensive_flags(self, post=None):
        if post is not None and post.author == self:
            return True
        return self.reputation >= int(settings.REP_TO_VIEW_FLAGS)

    @true_if_is_super_or_staff
    @false_if_validation_required_to('comment')
    def can_comment(self, post):
        return self == post.author or self.reputation >= int(settings.REP_TO_COMMENT
                ) or (post.__class__.__name__ == "Answer" and self == post.question.author)

    @true_if_is_super_or_staff
    def can_like_comment(self, comment):
        return self != comment.author and (self.reputation >= int(settings.REP_TO_LIKE_COMMENT))

    @true_if_is_super_or_staff
    def can_edit_comment(self, comment):
        return (comment.author == self and comment.added_at >= datetime.datetime.now() - datetime.timedelta(minutes=60)
        ) or self.is_superuser

    @true_if_is_super_or_staff
    def can_delete_comment(self, comment):
        return self == comment.author or self.reputation >= int(settings.REP_TO_DELETE_COMMENTS)

    @true_if_is_super_or_staff
    def can_convert_comment_to_answer(self, comment):
        return self == comment.author or self.reputation >= int(settings.REP_TO_CONVERT_COMMENTS_TO_ANSWERS)

    def can_convert_to_comment(self, answer):
        return (not answer.marked) and (self.is_superuser or self.is_staff or answer.author == self or self.reputation >= int
                (settings.REP_TO_CONVERT_TO_COMMENT))
    
    def can_convert_to_question(self, answer):
        return (not answer.marked) and (self.is_superuser or self.is_staff or answer.author == self or self.reputation >= int
                (settings.REP_TO_CONVERT_TO_QUESTION))

    @true_if_is_super_or_staff
    def can_accept_answer(self, answer):
        return self == answer.question.author and (settings.USERS_CAN_ACCEPT_OWN or answer.author != answer.question.author)

    @true_if_is_super_or_staff
    def can_create_tags(self):
        return self.reputation >= int(settings.REP_TO_CREATE_TAGS)

    @true_if_is_super_or_staff
    def can_edit_post(self, post):
        return self == post.author or self.reputation >= int(settings.REP_TO_EDIT_OTHERS
                                                             ) or (post.nis.wiki and self.reputation >= int(
                settings.REP_TO_EDIT_WIKI))

    @true_if_is_super_or_staff
    def can_wikify(self, post):
        return self == post.author or self.reputation >= int(settings.REP_TO_WIKIFY)

    @true_if_is_super_or_staff
    def can_cancel_wiki(self, post):
        return self == post.author

    @true_if_is_super_or_staff
    def can_retag_questions(self):
        return self.reputation >= int(settings.REP_TO_RETAG)

    @true_if_is_super_or_staff
    def can_close_question(self, question):
        return (self == question.author and self.reputation >= int(settings.REP_TO_CLOSE_OWN)
        ) or self.reputation >= int(settings.REP_TO_CLOSE_OTHERS)

    @true_if_is_super_or_staff
    def can_reopen_question(self, question):
        return self == question.author and self.reputation >= int(settings.REP_TO_REOPEN_OWN)

    @true_if_is_super_or_staff
    def can_delete_post(self, post):
        if post.node_type == "comment":
            return self.can_delete_comment(post)

        return (self == post.author and (post.__class__.__name__ == "Answer" or
        not post.answers.exclude(author__id=self.id).count()))

    @true_if_is_super_or_staff
    def can_upload_files(self):
        return self.reputation >= int(settings.REP_TO_UPLOAD)

    @true_if_is_super_or_staff
    def is_a_super_user_or_staff(self):
        return False

    def email_valid_and_can_ask(self):
        return 'ask' not in settings.REQUIRE_EMAIL_VALIDATION_TO or self.email_isvalid

    def email_valid_and_can_answer(self):
        return 'answer' not in settings.REQUIRE_EMAIL_VALIDATION_TO or self.email_isvalid

    def check_password(self, old_passwd):
        self.__dict__.update(self.__class__.objects.filter(id=self.id).values('password')[0])
        return DjangoUser.check_password(self, old_passwd)

    @property
    def suspension(self):
        if self.__dict__.get('_suspension_dencache_', False) != None:
            try:
                self.__dict__['_suspension_dencache_'] = self.reputes.get(action__action_type="suspend", action__canceled=False).action
            except ObjectDoesNotExist:
                self.__dict__['_suspension_dencache_'] = None
            except MultipleObjectsReturned:
                logging.error("Multiple suspension actions found for user %s (%s)" % (self.username, self.id))
                self.__dict__['_suspension_dencache_'] = self.reputes.filter(action__action_type="suspend", action__canceled=False
                                                                             ).order_by('-action__action_date')[0]

        return self.__dict__['_suspension_dencache_']

    def _pop_suspension_cache(self):
        self.__dict__.pop('_suspension_dencache_', None)

    def is_suspended(self):
        if not self.is_active:
            suspension = self.suspension

            if suspension and suspension.extra.get('bantype', None) == 'forxdays' and (
            datetime.datetime.now() > suspension.action_date + datetime.timedelta(
                    days=int(suspension.extra.get('forxdays', 365)))):
                suspension.cancel()
            else:
                return True

        return False

    class Meta:
        app_label = 'forum'

class UserProperty(BaseModel):
    user = models.ForeignKey(User, related_name='properties')
    key = models.CharField(max_length=16)
    value = PickledObjectField()

    class Meta:
        app_label = 'forum'
        unique_together = ('user', 'key')

    def cache_key(self):
        return self._generate_cache_key("%s:%s" % (self.user.id, self.key))

    @classmethod
    def infer_cache_key(cls, querydict):
        if 'user' in querydict and 'key' in querydict:
            return cls._generate_cache_key("%s:%s" % (querydict['user'].id, querydict['key']))

        return None

class UserPropertyDict(object):
    def __init__(self, user):
        self.__dict__['_user'] = user

    def __get_property(self, name):
        if self.__dict__.get('__%s__' % name, None):
            return self.__dict__['__%s__' % name]
        try:
            user = self.__dict__['_user']
            prop = UserProperty.objects.get(user=user, key=name)
            self.__dict__['__%s__' % name] = prop
            self.__dict__[name] = prop.value
            return prop
        except:
            return None


    def __getattr__(self, name):
        if self.__dict__.get(name, None):
            return self.__dict__[name]

        prop = self.__get_property(name)

        if prop:
            return prop.value
        else:
            return None

    def __setattr__(self, name, value):
        current = self.__get_property(name)

        if value is not None:
            if current:
                current.value = value
                self.__dict__[name] = value
                current.save(full_save=True)
            else:
                user = self.__dict__['_user']
                prop = UserProperty(user=user, value=value, key=name)
                prop.save()
                self.__dict__[name] = value
                self.__dict__['__%s__' % name] = prop
        else:
            if current:
                current.delete()
                del self.__dict__[name]
                del self.__dict__['__%s__' % name]


class SubscriptionSettings(models.Model):
    user = models.OneToOneField(User, related_name='subscription_settings', editable=False)

    enable_notifications = models.BooleanField(default=True)

    #notify if
    member_joins = models.CharField(max_length=1, default='n')
    new_question = models.CharField(max_length=1, default='n')
    new_question_watched_tags = models.CharField(max_length=1, default='i')
    subscribed_questions = models.CharField(max_length=1, default='i')

    #auto_subscribe_to
    all_questions = models.BooleanField(default=False)
    all_questions_watched_tags = models.BooleanField(default=False)
    questions_viewed = models.BooleanField(default=False)

    #notify activity on subscribed
    notify_answers = models.BooleanField(default=True)
    notify_reply_to_comments = models.BooleanField(default=True)
    notify_comments_own_post = models.BooleanField(default=True)
    notify_comments = models.BooleanField(default=False)
    notify_accepted = models.BooleanField(default=False)

    send_digest = models.BooleanField(default=True)

    class Meta:
        app_label = 'forum'

from forum.utils.time import one_day_from_now

class ValidationHashManager(models.Manager):
    def _generate_md5_hash(self, user, type, hash_data, seed):
        return md5("%s%s%s%s" % (seed, "".join(map(str, hash_data)), user.id, type)).hexdigest()

    def create_new(self, user, type, hash_data=[], expiration=None):
        seed = ''.join(Random().sample(string.letters+string.digits, 12))
        hash = self._generate_md5_hash(user, type, hash_data, seed)

        obj = ValidationHash(hash_code=hash, seed=seed, user=user, type=type)

        if expiration is not None:
            obj.expiration = expiration

        try:
            obj.save()
        except:
            return None

        return obj

    def validate(self, hash, user, type, hash_data=[]):
        try:
            obj = self.get(hash_code=hash)
        except:
            return False

        if obj.type != type:
            return False

        if obj.user != user:
            return False

        valid = (obj.hash_code == self._generate_md5_hash(obj.user, type, hash_data, obj.seed))

        if valid:
            if obj.expiration < datetime.datetime.now():
                obj.delete()
                return False
            else:
                obj.delete()
                return True

        return False

class ValidationHash(models.Model):
    hash_code = models.CharField(max_length=255, unique=True)
    seed = models.CharField(max_length=12)
    expiration = models.DateTimeField(default=one_day_from_now)
    type = models.CharField(max_length=12)
    user = models.ForeignKey(User)

    objects = ValidationHashManager()

    class Meta:
        unique_together = ('user', 'type')
        app_label = 'forum'

    def __str__(self):
        return self.hash_code

class AuthKeyUserAssociation(models.Model):
    key = models.CharField(max_length=255, null=False, unique=True)
    provider = models.CharField(max_length=64)
    user = models.ForeignKey(User, related_name="auth_keys")
    added_at = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        app_label = 'forum'
