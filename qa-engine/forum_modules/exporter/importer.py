import os, tarfile, datetime, ConfigParser, logging

from django.utils.translation import ugettext as _
from django.core.cache import cache

from south.db import db

from xml.sax import make_parser
from xml.sax.handler import ContentHandler, ErrorHandler

from forum.templatetags.extra_tags import diff_date

from exporter import TMP_FOLDER, DATETIME_FORMAT, DATE_FORMAT, META_INF_SECTION, CACHE_KEY
from orm import orm
import commands, settings

NO_DEFAULT = object()

import string

class SafeReader():
    def __init__(self, loc):
        self.base = open(loc)

    def read(self, *args):
        return "".join(c for c in self.base.read(*args) if c in string.printable)

    def readLine(self, *args):
        return "".join(c for c in self.base.readLine(*args) if c in string.printable)

    def close(self):
        self.base.close()


class ContentElement():
    def __init__(self, content):
        self._content = content

    def content(self):
        return self._content.strip()

    def as_bool(self):
        return self.content() == "true"

    def as_date(self, default=NO_DEFAULT):
        try:
            return datetime.datetime.strptime(self.content(), DATE_FORMAT)
        except:
            if default == NO_DEFAULT:
                return datetime.date.fromtimestamp(0)
            else:
                return default
            

    def as_datetime(self, default=NO_DEFAULT):
        try:
            return datetime.datetime.strptime(self.content(), DATETIME_FORMAT)
        except:
            if default == NO_DEFAULT:
                return datetime.datetime.fromtimestamp(0)
            else:
                return default

    def as_int(self, default=0):
        try:
            return int(self.content())
        except:
            return default

    def __str__(self):
        return self.content()


class RowElement(ContentElement):
    def __init__(self, name, attrs, parent=None):
        self.name = name.lower()
        self.parent = parent
        self.attrs = dict([(k.lower(), ContentElement(v)) for k, v in attrs.items()])
        self._content = u''
        self.sub_elements = {}

        if parent:
            parent.add(self)

    def add_to_content(self, ch):
        self._content += unicode(ch)

    def add(self, sub):
        curr = self.sub_elements.get(sub.name, None)

        if not curr:
            curr = []
            self.sub_elements[sub.name] = curr

        curr.append(sub)

    def get(self, name, default=None):
        return self.sub_elements.get(name.lower(), [default])[-1]

    def get_list(self, name):
        return self.sub_elements.get(name.lower(), [])

    def get_listc(self, name):
        return [r.content() for r in self.get_list(name)]

    def getc(self, name, default=""):
        el = self.get(name, None)

        if el:
            return el.content()
        else:
            return default

    def get_attr(self, name, default=""):
        return self.attrs.get(name.lower(), default)

    def as_pickled(self, default=None):
        value_el = self.get('value')

        if value_el:
            return value_el._as_pickled(default)
        else:
            return default

    TYPES_MAP = dict([(c.__name__, c) for c in (int, long, str, unicode, float)])

    def _as_pickled(self, default=None):
        type = self.get_attr('type').content()

        try:
            if type == 'dict':
                return dict([ (item.get_attr('key'), item.as_pickled()) for item in self.get_list('item') ])
            elif type == 'list':
                return [item.as_pickled() for item in self.get_list('item')]
            elif type == 'bool':
                return self.content().lower() == 'true'
            elif type in RowElement.TYPES_MAP:
                return RowElement.TYPES_MAP[type](self.content())
            else:
                return self.content()
        except:
            return default




class TableHandler(ContentHandler):
    def __init__(self, root_name, row_name, callback, callback_args = [], ping = None):
        self.root_name = root_name.lower()
        self.row_name = row_name.lower()
        self.callback = callback
        self.callback_args = callback_args
        self.ping = ping

        self._reset()

    def _reset(self):
        self.curr_element = None
        self.in_tag = None

    def startElement(self, name, attrs):
        name = name.lower()

        if name == self.root_name.lower():
            pass
        elif name == self.row_name:
            self.curr_element = RowElement(name, attrs)
        else:
            self.curr_element = RowElement(name, attrs, self.curr_element)

    def characters(self, ch):
        if self.curr_element:
            self.curr_element.add_to_content(ch)

    def endElement(self, name):
        name = name.lower()

        if name == self.root_name:
            pass
        elif name == self.row_name:
            self.callback(self.curr_element, *self.callback_args)
            if self.ping:
                self.ping()

            self._reset()
        else:
            self.curr_element = self.curr_element.parent


class SaxErrorHandler(ErrorHandler):
    def error(self, e):
        raise e

    def fatalError(self, e):
        raise e

    def warning(self, e):
        raise e

def disable_triggers():
    if db.backend_name == "postgres":
        db.start_transaction()
        db.execute_many(commands.PG_DISABLE_TRIGGERS)
        db.commit_transaction()

def enable_triggers():
    if db.backend_name == "postgres":
        db.start_transaction()
        db.execute_many(commands.PG_ENABLE_TRIGGERS)
        db.commit_transaction()

def reset_sequences():
    if db.backend_name == "postgres":
        db.start_transaction()
        db.execute_many(commands.PG_SEQUENCE_RESETS)
        db.commit_transaction()

def reset_fts_indexes():
    pass

FILE_HANDLERS = []

def start_import(fname, tag_merge, user):

    start_time = datetime.datetime.now()
    steps = [s for s in FILE_HANDLERS]

    with open(os.path.join(TMP_FOLDER, 'backup.inf'), 'r') as inffile:
        inf = ConfigParser.SafeConfigParser()
        inf.readfp(inffile)

        state = dict([(s['id'], {
            'status': _('Queued'), 'count': int(inf.get(META_INF_SECTION, s['id'])), 'parsed': 0
        }) for s in steps] + [
            ('overall', {
                'status': _('Starting'), 'count': int(inf.get(META_INF_SECTION, 'overall')), 'parsed': 0
            })
        ])

    full_state = dict(running=True, state=state, time_started="")

    def set_state():
        full_state['time_started'] = diff_date(start_time)
        cache.set(CACHE_KEY, full_state)

    set_state()

    def ping_state(name):
        state[name]['parsed'] += 1
        state['overall']['parsed'] += 1
        set_state()

    data = {
        'is_merge': True,
        'tag_merge': tag_merge
    }

    def run(fn, name):
        def ping():
            ping_state(name)

        state['overall']['status'] = _('Importing %s') % s['name']
        state[name]['status'] = _('Importing')


        fn(TMP_FOLDER, user, ping, data)

        state[name]['status'] = _('Done')

        set_state()

        return fname

    #dump = tarfile.open(fname, 'r')
    #dump.extractall(TMP_FOLDER)

    try:

        disable_triggers()
        db.start_transaction()

        for h in FILE_HANDLERS:
            run(h['fn'], h['id'])

        db.commit_transaction()
        enable_triggers()

        settings.MERGE_MAPPINGS.set_value(dict(merged_nodes=data['nodes_map'], merged_users=data['users_map']))

        reset_sequences()
    except Exception, e:
        full_state['running'] = False
        full_state['errors'] = "%s: %s" % (e.__class__.__name__, unicode(e))
        set_state()

        import traceback
        logging.error("Error executing xml import: \n %s" % (traceback.format_exc()))

def file_handler(file_name, root_tag, el_tag, name, args_handler=None, pre_callback=None, post_callback=None):
    def decorator(fn):
        def decorated(location, current_user, ping, data):
            if pre_callback:
                pre_callback(current_user, data)

            if (args_handler):
                args = args_handler(current_user, data)
            else:
                args = []

            parser = make_parser()
            handler = TableHandler(root_tag, el_tag, fn, args, ping)
            parser.setContentHandler(handler)
            #parser.setErrorHandler(SaxErrorHandler())

            parser.parse(SafeReader(os.path.join(location, file_name)))

            if post_callback:
                post_callback()

        FILE_HANDLERS.append(dict(id=root_tag, name=name, fn=decorated))
        return decorated
    return decorator

def verify_existence(row):
    try:
        return orm.User.objects.get(email=row.getc('email'))
    except:
        for key in row.get('authKeys').get_list('key'):
            key = key=key.getc('key')

            if not ("google.com" in key or "yahoo.com" in key):
                try:
                    return orm.AuthKeyUserAssociation.objects.get(key=key).user
                except:
                    pass

    return None

def user_import_pre_callback(user, data):
    data['users_map'] = {}

@file_handler('users.xml', 'users', 'user', _('Users'), pre_callback=user_import_pre_callback, args_handler=lambda u, d: [u, d['is_merge'], d['users_map']])
def user_import(row, current_user, is_merge, users_map):
    existent = is_merge and verify_existence(row) or None

    roles = row.get('roles').get_listc('role')
    valid_email = row.get('email').get_attr('validated').as_bool()
    badges = row.get('badges')

    if existent:
        user = existent

        user.reputation += row.get('reputation').as_int()
        user.gold += badges.get_attr('gold').as_int()
        user.silver += badges.get_attr('gold').as_int()
        user.bronze += badges.get_attr('gold').as_int()

    else:
        username = row.getc('username')

        if is_merge:
            username_count = 0

            while orm.User.objects.filter(username=username).count():
                username_count += 1
                username = "%s %s" % (row.getc('username'), username_count)

        user = orm.User(
                id           = (not is_merge) and row.getc('id') or None,
                username     = username,
                password     = row.getc('password'),
                email        = row.getc('email'),
                email_isvalid= valid_email,
                is_superuser = (not is_merge) and 'superuser' in roles,
                is_staff     = ('moderator' in roles) or (is_merge and 'superuser' in roles),
                is_active    = row.get('active').as_bool(),
                date_joined  = row.get('joindate').as_datetime(),
                about         = row.getc('bio'),
                date_of_birth = row.get('birthdate').as_date(None),
                website       = row.getc('website'),
                reputation    = row.get('reputation').as_int(),
                gold          = badges.get_attr('gold').as_int(),
                silver        = badges.get_attr('silver').as_int(),
                bronze        = badges.get_attr('bronze').as_int(),
                real_name     = row.getc('realname'),
                location      = row.getc('location'),
        )

    user.save()

    users_map[row.get('id').as_int()] = user.id

    authKeys = row.get('authKeys')

    for key in authKeys.get_list('key'):
        if (not is_merge) or orm.AuthKeyUserAssociation.objects.filter(key=key.getc('key')).count() == 0:
            orm.AuthKeyUserAssociation(user=user, key=key.getc('key'), provider=key.getc('provider')).save()

    if not existent:
        notifications = row.get('notifications')

        attributes = dict([(str(k), v.as_bool() and 'i' or 'n') for k, v in notifications.get('notify').attrs.items()])
        attributes.update(dict([(str(k), v.as_bool()) for k, v in notifications.get('autoSubscribe').attrs.items()]))
        attributes.update(dict([(str("notify_%s" % k), v.as_bool()) for k, v in notifications.get('notifyOnSubscribed').attrs.items()]))

        ss = orm.SubscriptionSettings(user=user, enable_notifications=notifications.get_attr('enabled').as_bool(), **attributes)

        if current_user.id == row.get('id').as_int():
            ss.id = current_user.subscription_settings.id

        ss.save()
        

def pre_tag_import(user, data):
    data['tag_mappings'] = dict([ (t.name, t) for t in orm.Tag.objects.all() ])


@file_handler('tags.xml', 'tags', 'tag', _('Tags'), pre_callback=pre_tag_import, args_handler=lambda u, d: [d['is_merge'], d['tag_merge'], d['users_map'], d['tag_mappings']])
def tag_import(row, is_merge, tag_merge, users_map, tag_mappings):
    created_by = row.get('used').as_int()
    created_by = users_map.get(created_by, created_by)

    tag_name = row.getc('name')
    tag_name = tag_merge and tag_merge.get(tag_name, tag_name) or tag_name

    if is_merge and tag_name in tag_mappings:
        tag = tag_mappings[tag_name]
        tag.used_count += row.get('used').as_int()
    else:
        tag = orm.Tag(name=tag_name, used_count=row.get('used').as_int(), created_by_id=created_by)
        tag_mappings[tag.name] = tag

    tag.save()

def pre_node_import(user, data):
    data['nodes_map'] = {}

@file_handler('nodes.xml', 'nodes', 'node', _('Nodes'), pre_callback=pre_node_import,
              args_handler=lambda u, d: [d['is_merge'], d['tag_merge'], d['tag_mappings'], d['nodes_map'], d['users_map']])
def node_import(row, is_merge, tag_merge, tags, nodes_map, users_map):

    ntags = []

    for t in row.get('tags').get_list('tag'):
        t = t.content()
        ntags.append(tags[tag_merge and tag_merge.get(t, t) or t])

    author = row.get('author').as_int()

    last_act = row.get('lastactivity')
    last_act_user = last_act.get('by').as_int(None)

    parent = row.get('parent').as_int(None)
    abs_parent = row.get('absparent').as_int(None)

    node = orm.Node(
            id            = (not is_merge) and row.getc('id') or None,
            node_type     = row.getc('type'),
            author_id     = users_map.get(author, author),
            added_at      = row.get('date').as_datetime(),
            parent_id     = nodes_map.get(parent, parent),
            abs_parent_id = nodes_map.get(abs_parent, abs_parent),
            score         = row.get('score').as_int(0),

            last_activity_by_id = last_act_user and users_map.get(last_act_user, last_act_user) or last_act_user,
            last_activity_at    = last_act.get('at').as_datetime(None),

            title         = row.getc('title'),
            body          = row.getc('body'),
            tagnames      = " ".join([t.name for t in ntags]),

            marked        = row.get('marked').as_bool(),
            extra_ref_id  = row.get('extraRef').as_int(None),
            extra_count   = row.get('extraCount').as_int(0),
            extra         = row.get('extraData').as_pickled()
    )

    node.save()

    nodes_map[row.get('id').as_int()] = node.id

    node.tags = ntags

    revisions = row.get('revisions')
    active = revisions.get_attr('active').as_int()

    if active == 0:
        active = orm.NodeRevision(
            author_id = node.author_id,
            body = row.getc('body'),
            node = node,
            revised_at = row.get('date').as_datetime(),
            revision = 1,
            summary = _('Initial revision'),
            tagnames = " ".join([t.name for t in ntags]),
            title = row.getc('title'),
        )

        active.save()
    else:
        for r in revisions.get_list('revision'):
            author = row.get('author').as_int()

            rev = orm.NodeRevision(
                author_id = users_map.get(author, author),
                body = r.getc('body'),
                node = node,
                revised_at = r.get('date').as_datetime(),
                revision = r.get('number').as_int(),
                summary = r.getc('summary'),
                tagnames = " ".join(r.getc('tags').split(',')),
                title = r.getc('title'),
            )

            rev.save()
            if rev.revision == active:
                active = rev

    node.active_revision = active
    node.save()

POST_ACTION = {}

def post_action(*types):
    def decorator(fn):
        for t in types:
            POST_ACTION[t] = fn
        return fn
    return decorator

def pre_action_import_callback(user, data):
    data['actions_map'] = {}

def post_action_import_callback():
    with_state = orm.Node.objects.filter(id__in=orm.NodeState.objects.values_list('node_id', flat=True).distinct())

    for n in with_state:
        n.state_string = "".join(["(%s)" % s for s in n.states.values_list('state_type')])
        n.save()

@file_handler('actions.xml', 'actions', 'action', _('Actions'), post_callback=post_action_import_callback,
              pre_callback=pre_action_import_callback, args_handler=lambda u, d: [d['nodes_map'], d['users_map'], d['actions_map']])
def actions_import(row, nodes, users, actions_map):
    node = row.get('node').as_int(None)
    user = row.get('user').as_int()
    real_user = row.get('realUser').as_int(None)

    action = orm.Action(
        #id           = row.get('id').as_int(),
        action_type  = row.getc('type'),
        action_date  = row.get('date').as_datetime(),
        node_id      = nodes.get(node, node),
        user_id      = users.get(user, user),
        real_user_id = users.get(real_user, real_user),
        ip           = row.getc('ip'),
        extra        = row.get('extraData').as_pickled(),
    )

    canceled = row.get('canceled')
    if canceled.get_attr('state').as_bool():
        by = canceled.get('user').as_int()
        action.canceled = True
        action.canceled_by_id = users.get(by, by)
        action.canceled_at = canceled.getc('date') #.as_datetime(),
        action.canceled_ip = canceled.getc('ip')

    action.save()

    actions_map[row.get('id').as_int()] = action.id

    for r in row.get('reputes').get_list('repute'):
        by_canceled = r.get_attr('byCanceled').as_bool()

        orm.ActionRepute(
            action = action,
            user_id = users[r.get('user').as_int()],
            value = r.get('value').as_int(),

            date = by_canceled and action.canceled_at or action.action_date,
            by_canceled = by_canceled
        ).save()

    if (not action.canceled) and (action.action_type in POST_ACTION):
        POST_ACTION[action.action_type](row, action, users, nodes, actions_map)




# Record of all persisted votes.
persisted_votes = []
@post_action('voteup', 'votedown', 'voteupcomment')
def vote_action(row, action, users, nodes, actions):
    # Check to see if the vote has already been registered.
    if not (action.user_id, action.node_id) in persisted_votes:
        # Persist the vote action.
        orm.Vote(user_id=action.user_id, node_id=action.node_id, action=action,
                 voted_at=action.action_date, value=(action.action_type != 'votedown') and 1 or -1).save()

        # Record the vote action.  This will help us avoid duplicates.
        persisted_votes.append((action.user_id, action.node_id))


def state_action(state):
    def fn(row, action, users, nodes, actions):
        if orm.NodeState.objects.filter(state_type = state, node = action.node_id).count():
            return

        orm.NodeState(
            state_type = state,
            node_id = action.node_id,
            action = action
        ).save()
    return fn

post_action('wikify')(state_action('wiki'))
post_action('delete')(state_action('deleted'))
post_action('acceptanswer')(state_action('accepted'))
post_action('publish')(state_action('published'))


@post_action('flag')
def flag_action(row, action, users, nodes, actions):
    orm.Flag(user_id=action.user_id, node_id=action.node_id, action=action, reason=action.extra or "").save()


def award_import_args(user, data):
    return [ dict([ (b.cls, b) for b in orm.Badge.objects.all() ]) , data['nodes_map'], data['users_map'], data['actions_map']]


@file_handler('awards.xml', 'awards', 'award', _('Awards'), args_handler=award_import_args)
def awards_import(row, badges, nodes, users, actions):
    badge_type = badges.get(row.getc('badge'), None)

    if not badge_type:
        return

    action = row.get('action').as_int(None)
    trigger = row.get('trigger').as_int(None)
    node = row.get('node').as_int(None)
    user = row.get('user').as_int()

    if orm.Award.objects.filter(badge=badges[row.getc('badge')], user=users.get(user, user), node=nodes.get(node, node)).count():
        return

    award = orm.Award(
        user_id = users.get(user, user),
        badge = badge_type,
        node_id = nodes.get(node, node),
        action_id = actions.get(action, action),
        trigger_id = actions.get(trigger, trigger)
    ).save()


#@file_handler('settings.xml', 'settings', 'setting', _('Settings'))
def settings_import(row):
    orm.KeyValue(key=row.getc('key'), value=row.get('value').as_pickled())








    
