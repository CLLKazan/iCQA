import os, tarfile, datetime, logging, re, ConfigParser, shutil, zipfile

from django.core.cache import cache
from django.utils.translation import ugettext as _
from forum.models import *
from forum.settings import APP_URL
from forum.templatetags.extra_tags import diff_date
import xml.etree.ElementTree
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Comment, _encode, ProcessingInstruction, QName, fixtag, _escape_attrib, _escape_cdata
from forum import settings
from django.conf import settings as djsettings
import settings as selfsettings

CACHE_KEY = "%s_exporter_state" % APP_URL
EXPORT_STEPS = []

TMP_FOLDER = os.path.join(os.path.dirname(__file__), 'tmp')

DATE_AND_AUTHOR_INF_SECTION = 'DateAndAuthor'
OPTIONS_INF_SECTION = 'Options'
META_INF_SECTION = 'Meta'

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

def Etree_pretty__write(self, file, node, encoding, namespaces,
                        level=0, identator="    "):
    tag = node.tag
    if tag is Comment:
        file.write(level * identator + "<!-- %s -->" % _escape_cdata(node.text, encoding))
    elif tag is ProcessingInstruction:
        file.write("<?%s?>" % _escape_cdata(node.text, encoding))
    else:
        items = node.items()
        xmlns_items = [] # new namespaces in this scope
        try:
            if isinstance(tag, QName) or tag[:1] == "{":
                tag, xmlns = fixtag(tag, namespaces)
                if xmlns: xmlns_items.append(xmlns)
        except TypeError:
            raise #_raise_serialization_error(tag)
        file.write("\n" + level * identator + "<" + _encode(tag, encoding))
        if items or xmlns_items:
            items.sort() # lexical order
            for k, v in items:
                try:
                    if isinstance(k, QName) or k[:1] == "{":
                        k, xmlns = fixtag(k, namespaces)
                        if xmlns: xmlns_items.append(xmlns)
                except TypeError:
                    raise #_raise_serialization_error(k)
                try:
                    if isinstance(v, QName):
                        v, xmlns = fixtag(v, namespaces)
                        if xmlns: xmlns_items.append(xmlns)
                except TypeError:
                    raise #_raise_serialization_error(v)
                file.write(u" %s=\"%s\"" % (_encode(k, encoding),
                                            _escape_attrib(v, encoding)))
            for k, v in xmlns_items:
                file.write(u" %s=\"%s\"" % (_encode(k, encoding),
                                            _escape_attrib(v, encoding)))
        if node.text or len(node):
            file.write(">")
            if node.text:
                file.write(_escape_cdata(node.text, encoding))
            for n in node:
                self._write(file, n, encoding, namespaces, level + 1, identator)
            if node.text and len(node.text) < 125:
                file.write("</" + _encode(tag, encoding) + ">")
            else:
                file.write("\n" + level * identator + "</" + _encode(tag, encoding) + ">")
        else:
            file.write(" />")
        for k, v in xmlns_items:
            del namespaces[v]
    if node.tail:
        file.write(_escape_cdata(node.tail.replace("\n", (level * identator )+ "\n"), encoding))

def make_date(date, with_time=True):
    try:
        return date.strftime(with_time and DATETIME_FORMAT or DATE_FORMAT)
    except ValueError, e:
        return date.replace(year=1900).strftime(with_time and DATETIME_FORMAT or DATE_FORMAT)


def ET_Element_add_tag(el, tag_name, content = None, **attrs):
    tag = ET.SubElement(el, tag_name)

    if content:
        try:
            tag.text = unicode(content)
        except:
            tag.text = u''

    for k, v in attrs.items():
        tag.set(k, unicode(v))

    return tag

GOOD_TAG_NAME = re.compile("^\w+$")

def make_extra(el, v):
    if v is None:
        return


    if isinstance(v, (int, long, str, unicode, float, bool, dict, list, tuple)):
        if isinstance(v, tuple):
            t = 'list'
        else:
            t = v.__class__.__name__
    else:
        t = 'unknown'

    value = el.add('value', type=t)

    if isinstance(v, (list, tuple)):
        for i in v:
            item = value.add('item')
            make_extra(item, i)

    elif isinstance(v, dict):
        for k, i in v.items():
            item = value.add('item', key=k)
            make_extra(item, i)
    else:
        value.text = unicode(v)

def write_to_file(root, tmp, filename):
    tree = ET.ElementTree(root)
    tree.write(os.path.join(tmp, filename), encoding='UTF-8')

def create_targz(tmp, files, start_time, options, user, state, set_state, file_format):
    now = datetime.datetime.now()
    domain = re.match('[\w-]+\.[\w-]+(\.[\w-]+)*', djsettings.APP_URL)
    if domain:
        domain = '_'.join(domain.get(0).split('.'))
    else:
        domain = 'localhost'

    fname = "%s-%s" % (domain, now.strftime('%Y%m%d%H%M'))
    if file_format == 'zip':
        full_fname = "%s.zip" % fname
    else:
        full_fname = "%s.tar.gz" % fname

    if file_format == 'zip':
        t = zipfile.ZipFile(os.path.join(selfsettings.EXPORTER_BACKUP_STORAGE, full_fname), 'w')

        def add_to_file(f, a):
            t.write(f, a)
    else:
        t = tarfile.open(os.path.join(selfsettings.EXPORTER_BACKUP_STORAGE, full_fname), mode = 'w:gz')

        def add_to_file(f, a):
            t.add(f, a)

    state['overall']['status'] = _('Compressing xml files')
    set_state()

    for f in files:
        add_to_file(os.path.join(tmp, f), "/%s" % f)

    if options.get('uplodaded_files', False):
        state['overall']['status'] = _('Importing uploaded files')
        set_state()
        export_upfiles(t)

    if options.get('import_skins_folder', False):
        state['overall']['status'] = _('Importing skins folder')
        set_state()
        export_skinsfolder(t)

    state['overall']['status'] = _('Writing inf file.')
    set_state()

    inf = ConfigParser.SafeConfigParser()

    inf.add_section(DATE_AND_AUTHOR_INF_SECTION)

    inf.set(DATE_AND_AUTHOR_INF_SECTION, 'file-name', full_fname)
    inf.set(DATE_AND_AUTHOR_INF_SECTION, 'author', unicode(user.id))
    inf.set(DATE_AND_AUTHOR_INF_SECTION, 'site', djsettings.APP_URL)
    inf.set(DATE_AND_AUTHOR_INF_SECTION, 'started', start_time.strftime(DATETIME_FORMAT))
    inf.set(DATE_AND_AUTHOR_INF_SECTION, 'finished', now.strftime(DATETIME_FORMAT))

    inf.add_section(OPTIONS_INF_SECTION)
    inf.set(OPTIONS_INF_SECTION, 'anon-data', str(options.get('anon_data', False)))
    inf.set(OPTIONS_INF_SECTION, 'with-upfiles', str(options.get('uplodaded_files', False)))
    inf.set(OPTIONS_INF_SECTION, 'with-skins', str(options.get('import_skins_folder', False)))

    inf.add_section(META_INF_SECTION)

    for id, s in state.items():
        inf.set(META_INF_SECTION, id, str(s['count']))

    with open(os.path.join(tmp, '%s.backup.inf' % fname), 'wb') as inffile:
        inf.write(inffile)

    add_to_file(os.path.join(tmp, '%s.backup.inf' % fname), '/backup.inf')
    state['overall']['status'] = _('Saving backup file')
    set_state()
    t.close()
    return full_fname


def export_upfiles(tf):
    folder = str(settings.UPFILES_FOLDER)

    if os.path.exists(folder):
        tf.add(folder, arcname='/upfiles')


def export_skinsfolder(tf):
    folder = djsettings.TEMPLATE_DIRS[0]

    if os.path.exists(folder):
        tf.add(folder, arcname='/skins')


def export(options, user):
    original__write = xml.etree.ElementTree.ElementTree._write
    xml.etree.ElementTree.ElementTree._write = Etree_pretty__write
    xml.etree.ElementTree._ElementInterface.add = ET_Element_add_tag

    start_time = datetime.datetime.now()
    tmp = TMP_FOLDER
    anon_data = options.get('anon_data', False)

    steps = [s for s in EXPORT_STEPS if not (anon_data and s['fn'].is_user_data())]

    state = dict([(s['id'], {
        'status': _('Queued'), 'count': s['fn'].count(start_time), 'parsed': 0
    }) for s in steps] + [
        ('overall', {
            'status': _('Starting'), 'count': sum([s['fn'].count(start_time) for s in steps]), 'parsed': 0
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

    def run(fn, name):
        def ping():
            ping_state(name)

        state['overall']['status'] = _('Exporting %s') % s['name']
        state[name]['status'] = _('Exporting')

        root, fname = fn(ping, start_time, anon_data)

        state[name]['status'] = _('Writing temp file')
        state['overall']['status'] = _('Writing %s temp file') % s['name']

        set_state()

        write_to_file(root, tmp, fname)
        state[name]['status'] = _('Done')

        set_state()

        return fname

    try:
        dump_files = []

        for s in steps:
            dump_files.append(run(s['fn'], s['id']))

        state['overall']['status'] = _('Compressing files')
        set_state()

        fname = create_targz(tmp, dump_files, start_time, options, user, state, set_state, options['file_format'])
        full_state['running'] = False
        full_state['errors'] = False
        state['overall']['status'] = _('Done')
        state['overall']['fname'] = fname

        set_state()
    except Exception, e:
        full_state['running'] = False
        full_state['errors'] = "%s: %s" % (e.__class__.__name__, unicode(e))
        set_state()
        
        import traceback
        logging.error("Error executing xml backup: \n %s" % (traceback.format_exc()))
    finally:
        xml.etree.ElementTree.ElementTree._write = original__write
        del xml.etree.ElementTree._ElementInterface.add


def exporter_step(queryset, root_tag_name, el_tag_name, name, date_lock=None, user_data=False):

    def decorator(fn):
        def qs(lock):
            if date_lock:
                return queryset.filter(**{"%s__lte" % date_lock: lock})
            return queryset

        def decorated(ping, lock, anon_data):
            root = ET.Element(root_tag_name)

            for item in qs(lock).order_by('id').select_related():
                el = root.add(el_tag_name)
                fn(item, el, anon_data)
                ping()

            return root, "%s.xml" % root_tag_name

        def count(lock):
            return qs(lock).count()

        def is_user_data():
            return user_data

        decorated.count = count
        decorated.is_user_data = is_user_data

        EXPORT_STEPS.append(dict(id=root_tag_name, name=name, fn=decorated))

        return decorated

    return decorator

@exporter_step(Tag.objects.all(), 'tags', 'tag', _('Tags'))
def export_tags(t, el, anon_data):
    el.add('name', t.name)
    if not anon_data:
        el.add('author', t.created_by.id)
    el.add('used', t.used_count)


@exporter_step(User.objects.all(), 'users', 'user', _('Users'), 'date_joined', True)
def export_users(u, el, anon_data):
    el.add('id', u.id)
    el.add('username', u.username)
    el.add('password', u.password)
    el.add('email', u.email, validated=u.email_isvalid and 'true' or 'false')
    el.add('reputation', u.reputation)
    el.add('badges', bronze=u.bronze, silver=u.silver, gold=u.gold)
    el.add('joindate', make_date(u.date_joined))
    el.add('active', u.is_active and 'true' or 'false')

    el.add('realname', u.real_name)
    el.add('bio', u.about)
    el.add('location', u.location)
    el.add('website', u.website)
    el.add('birthdate', u.date_of_birth and make_date(u.date_of_birth, with_time=False) or "")

    roles = el.add('roles')

    if u.is_superuser:
        roles.add('role', 'superuser')

    if u.is_staff:
        roles.add('role', 'moderator')

    auth = el.add('authKeys')
    for a in u.auth_keys.all():
        key = auth.add('key')
        key.add('provider', a.provider)
        key.add('key', a.key)


    ss = u.subscription_settings

    notify = el.add('notifications', enabled=ss.enable_notifications and 'true' or 'false')

    notify.add('notify', **dict([(t, ss.__dict__.get(t, 'n') == 'i' and 'true' or 'false') for t in ['member_joins', 'new_question', 'new_question_watched_tags', 'subscribed_questions']]))

    notify.add('autoSubscribe', **dict([(t, ss.__dict__.get(t, False) and 'true' or 'false') for t in [
            'all_questions', 'all_questions_watched_tags', 'questions_asked', 'questions_answered', 'questions_commented', 'questions_viewed']]))

    notify.add('notifyOnSubscribed', **dict([(t, ss.__dict__.get("notify_%s" % t, False) and 'true' or 'false') for t in [
            'answers', 'reply_to_comments', 'comments_own_post', 'comments', 'accepted']]))

    notify.add('digest', ss.send_digest and 'on' or 'off')

    watched = el.add('watchedTags')
    rejected = el.add('rejectedTags')

    for m in u.tag_selections.all():
        if m.reason == 'good':
            watched.add('tag', m.tag.name)
        else:
            rejected.add('tag', m.tag.name)

    

@exporter_step(Node.objects.all(), 'nodes', 'node', _('Nodes'), 'added_at')
def export_nodes(n, el, anon_data):
    el.add('id', n.id)
    el.add('type', n.node_type)

    if not anon_data:
        el.add('author', n.author.id)
    el.add('date', make_date(n.added_at))
    el.add('parent', n.parent and n.parent.id or "")
    el.add('absparent', n.abs_parent and n.abs_parent or "")

    act = el.add('lastactivity')
    act.add('by', n.last_activity_by and n.last_activity_by.id or "")
    act.add('at', n.last_activity_at and make_date(n.last_activity_at) or "")

    el.add('title', n.title)
    el.add('body', n.body)

    el.add('score', n.score)

    tags = el.add('tags')

    for t in n.tagname_list():
        tags.add('tag', t)

    try:
        active = n.active_revision and n.active_revision.revision or n.revisions.order_by('revision')[0].revision
    except IndexError:
        active = 0

    revs = el.add('revisions', active=active)

    for r in n.revisions.order_by('revision'):
        rev = revs.add('revision')
        rev.add('number', r.revision)
        rev.add('summary', r.summary)
        if not anon_data:
            rev.add('author', r.author.id)
        rev.add('date', make_date(r.revised_at))

        rev.add('title', r.title)
        rev.add('body', r.body)
        rev.add('tags', ", ".join(r.tagname_list()))

    el.add('marked', n.marked and 'true' or 'false')
    el.add('extraRef', n.extra_ref and n.extra_ref.id or "")
    make_extra(el.add('extraData'), n.extra)
    el.add('extraCount', n.extra_count and n.extra_count or "")


@exporter_step(Action.objects.all(), 'actions', 'action', _('Actions'), 'action_date')
def export_actions(a, el, anon_data):
    el.add('id', a.id)
    el.add('type', a.action_type)
    el.add('date', make_date(a.action_date))

    if not anon_data:
        el.add('user', a.user.id)
        el.add('realUser', a.real_user and a.real_user.id or "")
        el.add('ip', a.ip)
    el.add('node', a.node and a.node.id or "")

    make_extra(el.add('extraData'), a.extra)

    canceled = el.add('canceled', state=a.canceled and 'true' or 'false')

    if a.canceled:
        if not anon_data:
            canceled.add('user', a.canceled_by.id)
            canceled.add('ip', a.canceled_ip)

        canceled.add('date', make_date(a.canceled_at))        

    if not anon_data:
        reputes = el.add('reputes')

        for r in a.reputes.all():
            repute = reputes.add('repute', byCanceled=r.by_canceled and 'true' or 'false')
            repute.add('user', r.user.id)
            repute.add('value', r.value)


#@exporter_step(NodeState.objects.all(), 'states', 'state', _('Node states'), 'action__action_date')
#def export_states(s, el, anon_data):
#    el.add('type', s.state_type)
#    el.add('node', s.node.id)
#    el.add('trigger', s.action.id)


#@exporter_step(Badge.objects.all(), 'badges', 'badge', _('Badges'), user_data=True)
#def export_badges(b, el, anon_data):
#    el.add('type', ["", 'gold', 'silver', 'bronze'][b.type])
#    el.add('name', b.cls)
#    el.add('count', b.awarded_count)


@exporter_step(Award.objects.all(), 'awards', 'award', _('Awards'), 'awarded_at', True)
def export_awards(a, el, anon_data):
    el.add('badge', a.badge.cls)
    el.add('user', a.user.id)
    el.add('node', a.node and a.node.id or "")
    el.add('trigger', a.trigger and a.trigger.id or "")
    el.add('action', a.action.id)

@exporter_step(KeyValue.objects.all(), 'settings', 'setting', _('Settings'))
def export_settings(s, el, anon_data):
    el.add('key', s.key)
    make_extra(el.add('value'), s.value)








        








