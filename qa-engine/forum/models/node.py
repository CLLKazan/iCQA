from base import *
import re
from tag import Tag

import markdown
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags
from forum.utils.html import sanitize_html
from forum.settings import SUMMARY_LENGTH
from utils import PickledObjectField

class NodeContent(models.Model):
    title      = models.CharField(max_length=300)
    tagnames   = models.CharField(max_length=125)
    author     = models.ForeignKey(User, related_name='%(class)ss')
    body       = models.TextField()

    @property
    def user(self):
        return self.author

    @property
    def html(self):
        return self.body

    @classmethod
    def _as_markdown(cls, content, *extensions):
        try:
            return mark_safe(sanitize_html(markdown.markdown(content, extensions=extensions)))
        except Exception, e:
            import traceback
            logging.error("Caught exception %s in markdown parser rendering %s %s:\s %s" % (
                str(e), cls.__name__, str(e), traceback.format_exc()))
            return ''

    def as_markdown(self, *extensions):
        return self._as_markdown(self.body, *extensions)

    @property
    def headline(self):
        return self.title

    def tagname_list(self):
        if self.tagnames:
            t = [name.strip() for name in self.tagnames.split(u' ') if name]
            return [name.strip() for name in self.tagnames.split(u' ') if name]
        else:
            return []

    def tagname_meta_generator(self):
        return u','.join([tag for tag in self.tagname_list()])

    class Meta:
        abstract = True
        app_label = 'forum'

class NodeMetaClass(BaseMetaClass):
    types = {}

    def __new__(cls, *args, **kwargs):
        new_cls = super(NodeMetaClass, cls).__new__(cls, *args, **kwargs)

        if not new_cls._meta.abstract and new_cls.__name__ is not 'Node':
            NodeMetaClass.types[new_cls.get_type()] = new_cls

        return new_cls

    @classmethod
    def setup_relations(cls):
        for node_cls in NodeMetaClass.types.values():
            NodeMetaClass.setup_relation(node_cls)

    @classmethod
    def setup_relation(cls, node_cls):
        name = node_cls.__name__.lower()

        def children(self):
            return node_cls.objects.filter(parent=self)

        def parent(self):
            if (self.parent is not None) and self.parent.node_type == name:
                return self.parent.leaf

            return None

        Node.add_to_class(name + 's', property(children))
        Node.add_to_class(name, property(parent))


class NodeQuerySet(CachedQuerySet):
    def obj_from_datadict(self, datadict):
        cls = NodeMetaClass.types.get(datadict.get("node_type", ""), None)
        if cls:
            obj = cls()
            obj.__dict__.update(datadict)
            return obj
        else:
            return super(NodeQuerySet, self).obj_from_datadict(datadict)

    def get(self, *args, **kwargs):
        node = super(NodeQuerySet, self).get(*args, **kwargs).leaf

        if not isinstance(node, self.model):
            raise self.model.DoesNotExist()

        return node

    def any_state(self, *args):
        filter = None

        for s in args:
            s_filter = models.Q(state_string__contains="(%s)" % s)
            filter = filter and (filter | s_filter) or s_filter

        if filter:
            return self.filter(filter)
        else:
            return self

    def all_states(self, *args):
        filter = None

        for s in args:
            s_filter = models.Q(state_string__contains="(%s)" % s)
            filter = filter and (filter & s_filter) or s_filter

        if filter:
            return self.filter(filter)
        else:
            return self

    def filter_state(self, **kwargs):
        apply_bool = lambda q, b: b and q or ~q
        return self.filter(*[apply_bool(models.Q(state_string__contains="(%s)" % s), b) for s, b in kwargs.items()])

    def children_count(self, child_type):
        return NodeMetaClass.types[child_type].objects.filter_state(deleted=False).filter(parent__in=self).count()


class NodeManager(CachedManager):
    use_for_related_fields = True

    def get_query_set(self):
        qs = NodeQuerySet(self.model)

        # If the node is an answer, question or comment we filter the Node model by type
        if self.model is not Node:
            qs = qs.filter(node_type=self.model.get_type())

        return qs

    def get_for_types(self, types, *args, **kwargs):
        kwargs['node_type__in'] = [t.get_type() for t in types]
        return self.get(*args, **kwargs)

    def filter_state(self, **kwargs):
        return self.all().filter_state(**kwargs)


class NodeStateDict(object):
    def __init__(self, node):
        self.__dict__['_node'] = node

    def __getattr__(self, name):
        if self.__dict__.get(name, None):
            return self.__dict__[name]

        try:
            node = self.__dict__['_node']
            action = NodeState.objects.get(node=node, state_type=name).action
            self.__dict__[name] = action
            return action
        except:
            return None

    def __setattr__(self, name, value):
        current = self.__getattr__(name)

        if value:
            if current:
                current.action = value
                current.save()
            else:
                node = self.__dict__['_node']
                state = NodeState(node=node, action=value, state_type=name)
                state.save()
                self.__dict__[name] = value

                if not "(%s)" % name in node.state_string:
                    node.state_string = "%s(%s)" % (node.state_string, name)
                    node.save()
        else:
            if current:
                node = self.__dict__['_node']
                node.state_string = "".join("(%s)" % s for s in re.findall('\w+', node.state_string) if s != name)
                node.save()
                current.node_state.delete()
                del self.__dict__[name]


class NodeStateQuery(object):
    def __init__(self, node):
        self.__dict__['_node'] = node

    def __getattr__(self, name):
        node = self.__dict__['_node']
        return "(%s)" % name in node.state_string


class Node(BaseModel, NodeContent):
    __metaclass__ = NodeMetaClass

    node_type            = models.CharField(max_length=16, default='node')
    parent               = models.ForeignKey('Node', related_name='children', null=True)
    abs_parent           = models.ForeignKey('Node', related_name='all_children', null=True)

    added_at             = models.DateTimeField(default=datetime.datetime.now)
    score                 = models.IntegerField(default=0)

    state_string          = models.TextField(default='')
    last_edited           = models.ForeignKey('Action', null=True, unique=True, related_name="edited_node")

    last_activity_by       = models.ForeignKey(User, null=True)
    last_activity_at       = models.DateTimeField(null=True, blank=True)

    tags                 = models.ManyToManyField('Tag', related_name='%(class)ss')
    active_revision       = models.OneToOneField('NodeRevision', related_name='active', null=True)

    extra = PickledObjectField()
    extra_ref = models.ForeignKey('Node', null=True)
    extra_count = models.IntegerField(default=0)

    marked = models.BooleanField(default=False)

    comment_count = DenormalizedField("children", node_type="comment", canceled=False)
    flag_count = DenormalizedField("flags")

    friendly_name = _("post")

    objects = NodeManager()

    def __unicode__(self):
        return self.headline

    @classmethod
    def _generate_cache_key(cls, key, group="node"):
        return super(Node, cls)._generate_cache_key(key, group)
        
    @classmethod
    def get_type(cls):
        return cls.__name__.lower()

    @property
    def leaf(self):
        leaf_cls = NodeMetaClass.types.get(self.node_type, None)

        if leaf_cls is None:
            return self

        leaf = leaf_cls()
        leaf.__dict__ = self.__dict__
        return leaf

    @property
    def nstate(self):
        state = self.__dict__.get('_nstate', None)

        if state is None:
            state = NodeStateDict(self)
            self._nstate = state

        return state

    @property
    def nis(self):
        nis = self.__dict__.get('_nis', None)

        if nis is None:
            nis = NodeStateQuery(self)
            self._nis = nis

        return nis

    @property
    def last_activity(self):
        try:
            return self.actions.order_by('-action_date')[0].action_date
        except:
            return self.last_seen

    @property
    def state_list(self):
        return [s.state_type for s in self.states.all()]

    @property
    def deleted(self):
        return self.nis.deleted

    @property
    def absolute_parent(self):
        if not self.abs_parent_id:
            return self

        return self.abs_parent

    @property
    def summary(self):
        return strip_tags(self.html)[:SUMMARY_LENGTH]

    @models.permalink
    def get_revisions_url(self):
        return ('revisions', (), {'id': self.id})

    def update_last_activity(self, user, save=False, time=None):
        if not time:
            time = datetime.datetime.now()

        self.last_activity_by = user
        self.last_activity_at = time

        if self.parent:
            self.parent.update_last_activity(user, save=True, time=time)

        if save:
            self.save()

    def _create_revision(self, user, number, **kwargs):
        revision = NodeRevision(author=user, revision=number, node=self, **kwargs)
        revision.save()
        return revision

    def create_revision(self, user, **kwargs):
        number = self.revisions.aggregate(last=models.Max('revision'))['last'] + 1
        revision = self._create_revision(user, number, **kwargs)
        self.activate_revision(user, revision, extensions=['urlize'])
        return revision

    def activate_revision(self, user, revision, extensions=['urlize']):
        self.title = revision.title
        self.tagnames = revision.tagnames
        
        from forum.utils.userlinking import auto_user_link
        
        self.body = auto_user_link(self, self._as_markdown(revision.body, *extensions))

        self.active_revision = revision
        self.update_last_activity(user)

        self.save()

    def _list_changes_in_tags(self):
        dirty = self.get_dirty_fields()

        if not 'tagnames' in dirty:
            return None
        else:
            if self._original_state['tagnames']:
                old_tags = set(name for name in self._original_state['tagnames'].split(u' '))
            else:
                old_tags = set()
            new_tags = set(name for name in self.tagnames.split(u' ') if name)

            return dict(
                    current=list(new_tags),
                    added=list(new_tags - old_tags),
                    removed=list(old_tags - new_tags)
                    )

    def _last_active_user(self):
        return self.last_edited and self.last_edited.by or self.author

    def _process_changes_in_tags(self):
        tag_changes = self._list_changes_in_tags()

        if tag_changes is not None:
            for name in tag_changes['added']:
                try:
                    tag = Tag.objects.get(name=name)
                except:
                    tag = Tag.objects.create(name=name, created_by=self._last_active_user())

                if not self.nis.deleted:
                    tag.add_to_usage_count(1)
                    tag.save()

            if not self.nis.deleted:
                for name in tag_changes['removed']:
                    try:
                        tag = Tag.objects.get(name=name)
                        tag.add_to_usage_count(-1)
                        tag.save()
                    except:
                        pass

            return True

        return False

    def mark_deleted(self, action):
        self.nstate.deleted = action
        self.save()

        if action:
            for tag in self.tags.all():
                tag.add_to_usage_count(-1)
                tag.save()
        else:
            for tag in Tag.objects.filter(name__in=self.tagname_list()):
                tag.add_to_usage_count(1)
                tag.save()

    def delete(self, *args, **kwargs):
        self.active_revision = None
        self.save()

        for n in self.children.all():
            n.delete()

        for a in self.actions.all():
            a.cancel()

        super(Node, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.id:
            self.node_type = self.get_type()
            super(BaseModel, self).save(*args, **kwargs)
            self.active_revision = self._create_revision(self.author, 1, title=self.title, tagnames=self.tagnames,
                                                         body=self.body)
            self.activate_revision(self.author, self.active_revision)
            self.update_last_activity(self.author, time=self.added_at)

        if self.parent_id and not self.abs_parent_id:
            self.abs_parent = self.parent.absolute_parent
        
        tags_changed = self._process_changes_in_tags()
        
        super(Node, self).save(*args, **kwargs)
        
        if tags_changed: self.tags = list(Tag.objects.filter(name__in=self.tagname_list()))

    class Meta:
        app_label = 'forum'


class NodeRevision(BaseModel, NodeContent):
    node       = models.ForeignKey(Node, related_name='revisions')
    summary    = models.CharField(max_length=300)
    revision   = models.PositiveIntegerField()
    revised_at = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        unique_together = ('node', 'revision')
        app_label = 'forum'


class NodeState(models.Model):
    node       = models.ForeignKey(Node, related_name='states')
    state_type = models.CharField(max_length=16)
    action     = models.OneToOneField('Action', related_name="node_state")

    class Meta:
        unique_together = ('node', 'state_type')
        app_label = 'forum'


