from django.utils.translation import ugettext as _
from utils import PickledObjectField
from threading import Thread
from forum.utils import html
from base import *
import re

class ActionQuerySet(CachedQuerySet):
    def obj_from_datadict(self, datadict):
        cls = ActionProxyMetaClass.types.get(datadict['action_type'], None)
        if cls:
            obj = cls()
            obj.__dict__.update(datadict)
            return obj
        else:
            return super(ActionQuerySet, self).obj_from_datadict(datadict)

    def get(self, *args, **kwargs):            
        action = super(ActionQuerySet, self).get(*args, **kwargs).leaf()

        if not isinstance(action, self.model):
            raise self.model.DoesNotExist()

        return action

class ActionManager(CachedManager):
    use_for_related_fields = True

    def get_query_set(self):
        qs = ActionQuerySet(self.model)

        if self.model is not Action:
            return qs.filter(action_type=self.model.get_type())
        else:
            return qs

    def get_for_types(self, types, *args, **kwargs):
        kwargs['action_type__in'] = [t.get_type() for t in types]
        return self.get(*args, **kwargs)


class Action(BaseModel):
    user = models.ForeignKey('User', related_name="actions")
    real_user = models.ForeignKey('User', related_name="proxied_actions", null=True)
    ip   = models.CharField(max_length=16)
    node = models.ForeignKey('Node', null=True, related_name="actions")
    action_type = models.CharField(max_length=16)
    action_date = models.DateTimeField(default=datetime.datetime.now)

    extra = PickledObjectField()

    canceled = models.BooleanField(default=False)
    canceled_by = models.ForeignKey('User', null=True, related_name="canceled_actions")
    canceled_at = models.DateTimeField(null=True)
    canceled_ip = models.CharField(max_length=16)

    hooks = {}

    objects = ActionManager()

    @property
    def at(self):
        return self.action_date

    @property
    def by(self):
        return self.user

    def repute_users(self):
        pass

    def process_data(self, **data):
        pass

    def process_action(self):
        pass

    def cancel_action(self):
        pass

    @property
    def verb(self):
        return ""

    def describe(self, viewer=None):
        return self.__class__.__name__

    def get_absolute_url(self):
        if self.node:
            return self.node.get_absolute_url()
        else:
            return self.user.get_profile_url()

    def repute(self, user, value):
        repute = ActionRepute(action=self, user=user, value=value)
        repute.save()
        return repute

    def cancel_reputes(self):
        for repute in self.reputes.all():
            cancel = ActionRepute(action=self, user=repute.user, value=(-repute.value), by_canceled=True)
            cancel.save()

    def leaf(self):
        leaf_cls = ActionProxyMetaClass.types.get(self.action_type, None)

        if leaf_cls is None:
            return self

        leaf = leaf_cls()
        d = self._as_dict()
        leaf.__dict__.update(self._as_dict())
        l = leaf._as_dict()
        return leaf

    @classmethod
    def get_type(cls):
        return re.sub(r'action$', '', cls.__name__.lower())

    def save(self, data=None, threaded=True, *args, **kwargs):
        isnew = False

        if not self.id:
            self.action_type = self.__class__.get_type()
            isnew = True

        if data:
            self.process_data(**data)

        super(Action, self).save(*args, **kwargs)

        if isnew:
            if (self.node is None) or (not self.node.nis.wiki):
                self.repute_users()
            self.process_action()
            self.trigger_hooks(threaded, True)

        return self

    def delete(self, *args, **kwargs):
        self.cancel_action()
        super(Action, self).delete(*args, **kwargs)

    def cancel(self, user=None, ip=None):
        if not self.canceled:
            self.canceled = True
            self.canceled_at = datetime.datetime.now()
            self.canceled_by = (user is None) and self.user or user
            if ip:
                self.canceled_ip = ip
            self.save()
            self.cancel_reputes()
            self.cancel_action()
        #self.trigger_hooks(False)

    @classmethod
    def get_current(cls, **kwargs):
        kwargs['canceled'] = False

        try:
            return cls.objects.get(**kwargs)
        except cls.MultipleObjectsReturned:
            logging.error("Got multiple values for action %s with args %s", cls.__name__,
                          ", ".join(["%s='%s'" % i for i in kwargs.items()]))
            raise
        except cls.DoesNotExist:
            return None

    @classmethod
    def hook(cls, fn):
        if not Action.hooks.get(cls, None):
            Action.hooks[cls] = []

        Action.hooks[cls].append(fn)

    def trigger_hooks(self, threaded, new=True):
        if threaded:
            thread = Thread(target=trigger_hooks, args=[self, Action.hooks, new])
            thread.setDaemon(True)
            thread.start()
        else:
            trigger_hooks(self, Action.hooks, new)

    class Meta:
        app_label = 'forum'

def trigger_hooks(action, hooks, new):
    for cls, hooklist in hooks.items():
        if isinstance(action, cls):
            for hook in hooklist:
                try:
                    hook(action=action, new=new)
                except Exception, e:
                    import traceback
                    logging.error("Error in %s hook: %s" % (cls.__name__, str(e)))
                    logging.error(traceback.format_exc())

class ActionProxyMetaClass(BaseMetaClass):
    types = {}

    def __new__(cls, *args, **kwargs):
        new_cls = super(ActionProxyMetaClass, cls).__new__(cls, *args, **kwargs)
        cls.types[new_cls.get_type()] = new_cls

        class Meta:
            proxy = True

        new_cls.Meta = Meta
        return new_cls

class ActionProxy(Action):
    __metaclass__ = ActionProxyMetaClass

    def friendly_username(self, viewer, user):
        return (viewer == user) and _('You') or user.username

    def friendly_ownername(self, owner, user):
        return (owner == user) and _('your') or user.username

    def viewer_or_user_verb(self, viewer, user, viewer_verb, user_verb):
        return (viewer == user) and viewer_verb or user_verb

    def hyperlink(self, url, title, **attrs):
        return html.hyperlink(url, title, **attrs)

    def describe_node(self, viewer, node):
        node_link = self.hyperlink(node.get_absolute_url(), node.headline)

        if node.parent:
            node_desc = _("on %(link)s") % {'link': node_link}
        else:
            node_desc = node_link

        return _("%(user)s %(node_name)s %(node_desc)s") % {
        'user': self.hyperlink(node.author.get_profile_url(), self.friendly_ownername(viewer, node.author)),
        'node_name': node.friendly_name,
        'node_desc': node_desc,
        }

    def affected_links(self, viewer):
        return ", ".join([self.hyperlink(u.get_profile_url(), self.friendly_username(viewer, u)) for u in set([r.user for r in self.reputes.all()])])

    class Meta:
        proxy = True

class DummyActionProxyMetaClass(type):
    def __new__(cls, *args, **kwargs):
        new_cls = super(DummyActionProxyMetaClass, cls).__new__(cls, *args, **kwargs)
        ActionProxyMetaClass.types[new_cls.get_type()] = new_cls
        return new_cls

class DummyActionProxy(object):
    __metaclass__ = DummyActionProxyMetaClass

    hooks = []

    def __init__(self, ip=None):
        self.ip = ip

    def process_data(self, **data):
        pass

    def process_action(self):
        pass

    def save(self, data=None):
        self.process_action()

        if data:
            self.process_data(**data)

        for hook in self.__class__.hooks:
            hook(self, True)

    @classmethod
    def get_type(cls):
        return re.sub(r'action$', '', cls.__name__.lower())

    @classmethod
    def hook(cls, fn):
        cls.hooks.append(fn)


class ActionRepute(models.Model):
    action = models.ForeignKey(Action, related_name='reputes')
    date = models.DateTimeField(default=datetime.datetime.now)
    user = models.ForeignKey('User', related_name='reputes')
    value = models.IntegerField(default=0)
    by_canceled = models.BooleanField(default=False)

    @property
    def positive(self):
        if self.value > 0: return self.value
        return 0

    @property
    def negative(self):
        if self.value < 0: return self.value
        return 0

    def _add_to_rep(self, value):
        if self.user.reputation + value < 0:
            return 0
        else:
            return models.F('reputation') + value

    def save(self, *args, **kwargs):
        super(ActionRepute, self).save(*args, **kwargs)
        self.user.reputation = self._add_to_rep(self.value)
        self.user.save()

    def delete(self):
        self.user.reputation = self._add_to_rep(-self.value)
        self.user.save()
        super(ActionRepute, self).delete()

    class Meta:
        app_label = 'forum'

