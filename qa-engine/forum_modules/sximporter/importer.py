# -*- coding: utf-8 -*-

from datetime import datetime
import time
import re
import os
import gc
from django.utils.translation import ugettext as _

from django.utils.encoding import force_unicode

try:
    from cPickle import loads, dumps
except ImportError:
    from pickle import loads, dumps

from copy import deepcopy
from base64 import b64encode, b64decode
from zlib import compress, decompress

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

def create_orm():
    from django.conf import settings
    from south.orm import FakeORM

    get_migration_number_re = re.compile(r'^((\d+)_.*)\.py$')

    migrations_folder = os.path.join(settings.SITE_SRC_ROOT, 'forum/migrations')

    highest_number = 0
    highest_file = None

    for f in os.listdir(migrations_folder):
        if os.path.isfile(os.path.join(migrations_folder, f)):
            m = get_migration_number_re.match(f)

            if m:
                found = int(m.group(2))

                if found > highest_number:
                    highest_number = found
                    highest_file = m.group(1)

    mod = __import__('forum.migrations.%s' % highest_file, globals(), locals(), ['forum.migrations'])
    return FakeORM(getattr(mod, 'Migration'), "forum")

orm = create_orm()

class SXTableHandler(ContentHandler):
    def __init__(self, fname, callback):
        self.in_row = False
        self.el_data = {}
        self.ch_data = ''

        self.fname = fname.lower()
        self.callback = callback

    def startElement(self, name, attrs):
        if name.lower() == self.fname:
            pass
        elif name.lower() == "row":
            self.in_row = True

    def characters(self, ch):
        self.ch_data += ch

    def endElement(self, name):
        if name.lower() == self.fname:
            pass
        elif name.lower() == "row":
            self.callback(self.el_data)

            self.in_row = False
            del self.el_data
            self.el_data = {}
        elif self.in_row:
            self.el_data[name.lower()] = self.ch_data.strip()
            del self.ch_data
            self.ch_data = ''


def readTable(path, name, callback):
    parser = make_parser()
    handler = SXTableHandler(name, callback)
    parser.setContentHandler(handler)

    f = os.path.join(path, "%s.xml" % name)
    parser.parse(f)


def dbsafe_encode(value):
    return force_unicode(b64encode(compress(dumps(deepcopy(value)))))

def getText(el):
    rc = ""
    for node in el.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc.strip()

msstrip = re.compile(r'^(.*)\.\d+')
def readTime(ts):
    noms = msstrip.match(ts)
    if noms:
        ts = noms.group(1)

    return datetime(*time.strptime(ts, '%Y-%m-%dT%H:%M:%S')[0:6])

#def readEl(el):
#    return dict([(n.tagName.lower(), getText(n)) for n in el.childNodes if n.nodeType == el.ELEMENT_NODE])

#def readTable(dump, name):
#    for e in minidom.parseString(dump.read("%s.xml" % name)).getElementsByTagName('row'):
#        yield readEl(e)
#return [readEl(e) for e in minidom.parseString(dump.read("%s.xml" % name)).getElementsByTagName('row')]

google_accounts_lookup = re.compile(r'^https?://www.google.com/accounts/')
yahoo_accounts_lookup = re.compile(r'^https?://me.yahoo.com/a/')

openid_lookups = [
        re.compile(r'^https?://www.google.com/profiles/(?P<uname>\w+(\.\w+)*)/?$'),
        re.compile(r'^https?://me.yahoo.com/(?P<uname>\w+(\.\w+)*)/?$'),
        re.compile(r'^https?://openid.aol.com/(?P<uname>\w+(\.\w+)*)/?$'),
        re.compile(r'^https?://(?P<uname>\w+(\.\w+)*).myopenid.com/?$'),
        re.compile(r'^https?://flickr.com/(\w+/)*(?P<uname>\w+(\.\w+)*)/?$'),
        re.compile(r'^https?://technorati.com/people/technorati/(?P<uname>\w+(\.\w+)*)/?$'),
        re.compile(r'^https?://(?P<uname>\w+(\.\w+)*).wordpress.com/?$'),
        re.compile(r'^https?://(?P<uname>\w+(\.\w+)*).blogspot.com/?$'),
        re.compile(r'^https?://(?P<uname>\w+(\.\w+)*).livejournal.com/?$'),
        re.compile(r'^https?://claimid.com/(?P<uname>\w+(\.\w+)*)/?$'),
        re.compile(r'^https?://(?P<uname>\w+(\.\w+)*).pip.verisignlabs.com/?$'),
        re.compile(r'^https?://getopenid.com/(?P<uname>\w+(\.\w+)*)/?$'),
        re.compile(r'^https?://[\w\.]+/(\w+/)*(?P<uname>\w+(\.\w+)*)/?$'),
        re.compile(r'^https?://(?P<uname>[\w\.]+)/?$'),
        ]

def final_username_attempt(sxu):
    openid = sxu.get('openid', None)

    if openid:
        if google_accounts_lookup.search(openid):
            return UnknownGoogleUser(sxu.get('id'))
        if yahoo_accounts_lookup.search(openid):
            return UnknownYahooUser(sxu.get('id'))

        for lookup in openid_lookups:
            if lookup.search(openid):
                return lookup.search(openid).group('uname')

    return UnknownUser(sxu.get('id'))

class UnknownUser(object):
    def __init__(self, id):
        self._id = id

    def __str__(self):
        return _("user-%(id)s") % {'id': self._id}

    def __unicode__(self):
        return self.__str__()

    def encode(self, *args):
        return self.__str__()

class UnknownGoogleUser(UnknownUser):
    def __str__(self):
        return _("user-%(id)s (google)") % {'id': self._id}

class UnknownYahooUser(UnknownUser):
    def __str__(self):
        return _("user-%(id)s (yahoo)") % {'id': self._id}


class IdMapper(dict):

    def __init__(self):
        self.default = 1

    def __getitem__(self, key):
        key = int(key)
        return super(IdMapper, self).get(key, self.default)

    def __setitem__(self, key, value):
        super(IdMapper, self).__setitem__(int(key), int(value))

class IdIncrementer():
    def __init__(self, initial):
        self.value = initial

    def inc(self):
        self.value += 1

openidre = re.compile('^https?\:\/\/')
def userimport(path, options):

    usernames = []
    openids = set()
    uidmapper = IdMapper()

    authenticated_user = options.get('authenticated_user', None)
    owneruid = options.get('owneruid', None)
    #check for empty values
    if not owneruid:
        owneruid = None
    else:
        owneruid = int(owneruid)

    def callback(sxu):
        create = True
        set_mapper_defaults = False

        if sxu.get('id') == '-1':
            return
        #print "\n".join(["%s : %s" % i for i in sxu.items()])

        if (owneruid and (int(sxu.get('id')) == owneruid)) or (
            (not owneruid) and len(uidmapper)):

            set_mapper_defaults = True

            if authenticated_user:
                osqau = orm.User.objects.get(id=authenticated_user.id)

                for assoc in orm.AuthKeyUserAssociation.objects.filter(user=osqau):
                    openids.add(assoc.key)

                uidmapper[owneruid] = osqau.id
                create = False

        sxbadges = sxu.get('badgesummary', None)
        badges = {'1':'0', '2':'0', '3':'0'}

        if sxbadges:
            badges.update(dict([b.split('=') for b in sxbadges.split()]))

        if create:
            username = unicode(sxu.get('displayname',
                               sxu.get('displaynamecleaned', sxu.get('realname', final_username_attempt(sxu)))))[:30]

            if username in usernames:
            #if options.get('mergesimilar', False) and sxu.get('email', 'INVALID') == user_by_name[username].email:
            #    osqau = user_by_name[username]
            #    create = False
            #    uidmapper[sxu.get('id')] = osqau.id
            #else:
                inc = 0

                while True:
                    inc += 1
                    totest = "%s %d" % (username[:29 - len(str(inc))], inc)

                    if not totest in usernames:
                        username = totest
                        break

            osqau = orm.User(
                    id           = sxu.get('id'),
                    username     = username,
                    password     = '!',
                    email        = sxu.get('email', ''),
                    is_superuser = sxu.get('usertypeid') == '5',
                    is_staff     = sxu.get('usertypeid') == '4',
                    is_active    = True,
                    date_joined  = readTime(sxu.get('creationdate')),
                    last_seen    = readTime(sxu.get('lastaccessdate')),
                    about         = sxu.get('aboutme', ''),
                    date_of_birth = sxu.get('birthday', None) and readTime(sxu['birthday']) or None,
                    email_isvalid = int(sxu.get('usertypeid')) > 2,
                    website       = sxu.get('websiteurl', ''),
                    reputation    = int(sxu.get('reputation')),
                    gold          = int(badges['1']),
                    silver        = int(badges['2']),
                    bronze        = int(badges['3']),
                    real_name     = sxu.get('realname', '')[:30],
                    location      = sxu.get('location', ''),
                    )

            osqau.save()

            user_joins = orm.Action(
                    action_type = "userjoins",
                    action_date = osqau.date_joined,
                    user = osqau
                    )
            user_joins.save()

            rep = orm.ActionRepute(
                    value = 1,
                    user = osqau,
                    date = osqau.date_joined,
                    action = user_joins
                    )
            rep.save()

            try:
                orm.SubscriptionSettings.objects.get(user=osqau)
            except:
                s = orm.SubscriptionSettings(user=osqau)
                s.save()

            uidmapper[osqau.id] = osqau.id
        else:
            new_about = sxu.get('aboutme', None)
            if new_about and osqau.about != new_about:
                if osqau.about:
                    osqau.about = "%s\n|\n%s" % (osqau.about, new_about)
                else:
                    osqau.about = new_about

            osqau.username = sxu.get('displayname',
                                     sxu.get('displaynamecleaned', sxu.get('realname', final_username_attempt(sxu))))
            osqau.email = sxu.get('email', '')
            osqau.reputation += int(sxu.get('reputation'))
            osqau.gold += int(badges['1'])
            osqau.silver += int(badges['2'])
            osqau.bronze += int(badges['3'])

            osqau.date_joined = readTime(sxu.get('creationdate'))
            osqau.website = sxu.get('websiteurl', '')
            osqau.date_of_birth = sxu.get('birthday', None) and readTime(sxu['birthday']) or None
            osqau.location = sxu.get('location', '')
            osqau.real_name = sxu.get('realname', '')

            #merged_users.append(osqau.id)
            osqau.save()

        if set_mapper_defaults:
            uidmapper[-1] = osqau.id
            uidmapper.default = osqau.id

        usernames.append(osqau.username)

        openid = sxu.get('openid', None)
        if openid and openidre.match(openid) and (not openid in openids):
            assoc = orm.AuthKeyUserAssociation(user=osqau, key=openid, provider="openidurl")
            assoc.save()
            openids.add(openid)

        openidalt = sxu.get('openidalt', None)
        if openidalt and openidre.match(openidalt) and (not openidalt in openids):
            assoc = orm.AuthKeyUserAssociation(user=osqau, key=openidalt, provider="openidurl")
            assoc.save()
            openids.add(openidalt)

    readTable(path, "Users", callback)

    #if uidmapper[-1] == -1:
    #    uidmapper[-1] = 1

    return uidmapper

def tagsimport(dump, uidmap):

    tagmap = {}

    def callback(sxtag):
        otag = orm.Tag(
                id = int(sxtag['id']),
                name = sxtag['name'],
                used_count = int(sxtag['count']),
                created_by_id = uidmap[sxtag.get('userid', 1)],
                )
        otag.save()

        tagmap[otag.name] = otag

    readTable(dump, "Tags", callback)

    return tagmap

def add_post_state(name, post, action):
    if not "(%s)" % name in post.state_string:
        post.state_string = "%s(%s)" % (post.state_string, name)
        post.save()

    try:
        state = orm.NodeState.objects.get(node=post, state_type=name)
        state.action = action
        state.save()
    except:
        state = orm.NodeState(node=post, state_type=name, action=action)
        state.save()

def remove_post_state(name, post):
    if "(%s)" % name in post.state_string:
        try:
            state = orm.NodeState.objects.get(state_type=name, post=post)
            state.delete()
        except:
            pass
    post.state_string = "".join("(%s)" % s for s in re.findall('\w+', post.state_string) if s != name)

def postimport(dump, uidmap, tagmap):
    all = []

    def callback(sxpost):
        nodetype = (sxpost.get('posttypeid') == '1') and "nodetype" or "answer"

        post = orm.Node(
                node_type = nodetype,
                id = sxpost['id'],
                added_at = readTime(sxpost['creationdate']),
                body = sxpost['body'],
                score = sxpost.get('score', 0),
                author_id = sxpost.get('deletiondate', None) and 1 or uidmap[sxpost.get('owneruserid', 1)]
                )

        post.save()

        create_action = orm.Action(
                action_type = (nodetype == "nodetype") and "ask" or "answer",
                user_id = post.author_id,
                node = post,
                action_date = post.added_at
                )

        create_action.save()

        if sxpost.get('lasteditoruserid', None):
            revise_action = orm.Action(
                    action_type = "revise",
                    user_id = uidmap[sxpost.get('lasteditoruserid')],
                    node = post,
                    action_date = readTime(sxpost['lasteditdate']),
                    )

            revise_action.save()
            post.last_edited = revise_action

        if sxpost.get('communityowneddate', None):
            wikify_action = orm.Action(
                    action_type = "wikify",
                    user_id = 1,
                    node = post,
                    action_date = readTime(sxpost['communityowneddate'])
                    )

            wikify_action.save()
            add_post_state("wiki", post, wikify_action)

        if sxpost.get('lastactivityuserid', None):
            post.last_activity_by_id = uidmap[sxpost['lastactivityuserid']]
            post.last_activity_at = readTime(sxpost['lastactivitydate'])

        if sxpost.get('posttypeid') == '1': #question
            post.node_type = "question"
            post.title = sxpost['title']

            tagnames = sxpost['tags'].replace(u'ö', '-').replace(u'é', '').replace(u'à', '')
            post.tagnames = tagnames

            post.extra_count = sxpost.get('viewcount', 0)

            add_tags_to_post(post, tagmap)

        else:
            post.parent_id = sxpost['parentid']

        post.save()

        all.append(int(post.id))
        create_and_activate_revision(post)

        del post

    readTable(dump, "Posts", callback)

    return all

def comment_import(dump, uidmap, posts):
    currid = IdIncrementer(max(posts))
    mapping = {}

    def callback(sxc):
        currid.inc()
        oc = orm.Node(
                id = currid.value,
                node_type = "comment",
                added_at = readTime(sxc['creationdate']),
                author_id = uidmap[sxc.get('userid', 1)],
                body = sxc['text'],
                parent_id = sxc.get('postid'),
                )

        if sxc.get('deletiondate', None):
            delete_action = orm.Action(
                    action_type = "delete",
                    user_id = uidmap[sxc['deletionuserid']],
                    action_date = readTime(sxc['deletiondate'])
                    )

            oc.author_id = uidmap[sxc['deletionuserid']]
            oc.save()

            delete_action.node = oc
            delete_action.save()

            add_post_state("deleted", oc, delete_action)
        else:
            oc.author_id = uidmap[sxc.get('userid', 1)]
            oc.save()

        create_action = orm.Action(
                action_type = "comment",
                user_id = oc.author_id,
                node = oc,
                action_date = oc.added_at
                )

        create_and_activate_revision(oc)

        create_action.save()
        oc.save()

        posts.append(int(oc.id))
        mapping[int(sxc['id'])] = int(oc.id)

    readTable(dump, "PostComments", callback)
    return posts, mapping


def add_tags_to_post(post, tagmap):
    tags = [tag for tag in [tagmap.get(name.strip()) for name in post.tagnames.split(u' ') if name] if tag]
    post.tagnames = " ".join([t.name for t in tags]).strip()
    post.tags = tags


def create_and_activate_revision(post):
    rev = orm.NodeRevision(
            author_id = post.author_id,
            body = post.body,
            node_id = post.id,
            revised_at = post.added_at,
            revision = 1,
            summary = 'Initial revision',
            tagnames = post.tagnames,
            title = post.title,
            )

    rev.save()
    post.active_revision_id = rev.id
    post.save()

def post_vote_import(dump, uidmap, posts):
    close_reasons = {}

    def close_callback(r):
        close_reasons[r['id']] = r['name']

    readTable(dump, "CloseReasons", close_callback)

    user2vote = []

    def callback(sxv):
        action = orm.Action(
                user_id=uidmap[sxv['userid']],
                action_date = readTime(sxv['creationdate']),
                )

        if not int(sxv['postid']) in posts: return
        node = orm.Node.objects.get(id=sxv['postid'])
        action.node = node

        if sxv['votetypeid'] == '1':
            answer = node
            question = orm.Node.objects.get(id=answer.parent_id)

            action.action_type = "acceptanswer"
            action.save()

            answer.marked = True

            question.extra_ref_id = answer.id

            answer.save()
            question.save()

        elif sxv['votetypeid'] in ('2', '3'):
            if not (action.node.id, action.user_id) in user2vote:
                user2vote.append((action.node.id, action.user_id))

                action.action_type = (sxv['votetypeid'] == '2') and "voteup" or "votedown"
                action.save()

                ov = orm.Vote(
                        node_id = action.node.id,
                        user_id = action.user_id,
                        voted_at = action.action_date,
                        value = sxv['votetypeid'] == '2' and 1 or -1,
                        action = action
                        )
                ov.save()
            else:
                action.action_type = "unknown"
                action.save()

        elif sxv['votetypeid'] in ('4', '12', '13'):
            action.action_type = "flag"
            action.save()

            of = orm.Flag(
                    node = action.node,
                    user_id = action.user_id,
                    flagged_at = action.action_date,
                    reason = '',
                    action = action
                    )

            of.save()

        elif sxv['votetypeid'] == '5':
            action.action_type = "favorite"
            action.save()

        elif sxv['votetypeid'] == '6':
            action.action_type = "close"
            action.extra = dbsafe_encode(close_reasons[sxv['comment']])
            action.save()

            node.marked = True
            node.save()

        elif sxv['votetypeid'] == '7':
            action.action_type = "unknown"
            action.save()

            node.marked = False
            node.save()

            remove_post_state("closed", node)

        elif sxv['votetypeid'] == '10':
            action.action_type = "delete"
            action.save()

        elif sxv['votetypeid'] == '11':
            action.action_type = "unknown"
            action.save()

            remove_post_state("deleted", node)

        else:
            action.action_type = "unknown"
            action.save()

        if sxv.get('targetrepchange', None):
            rep = orm.ActionRepute(
                    action = action,
                    date = action.action_date,
                    user_id = uidmap[sxv['targetuserid']],
                    value = int(sxv['targetrepchange'])
                    )

            rep.save()

        if sxv.get('voterrepchange', None):
            rep = orm.ActionRepute(
                    action = action,
                    date = action.action_date,
                    user_id = uidmap[sxv['userid']],
                    value = int(sxv['voterrepchange'])
                    )

            rep.save()

        if action.action_type in ("acceptanswer", "delete", "close"):
            state = {"acceptanswer": "accepted", "delete": "deleted", "close": "closed"}[action.action_type]
            add_post_state(state, node, action)

    readTable(dump, "Posts2Votes", callback)


def comment_vote_import(dump, uidmap, comments):
    user2vote = []
    comments2score = {}

    def callback(sxv):
        if sxv['votetypeid'] == "2":
            comment_id = comments[int(sxv['postcommentid'])]
            user_id = uidmap[sxv['userid']]

            if not (comment_id, user_id) in user2vote:
                user2vote.append((comment_id, user_id))

                action = orm.Action(
                        action_type = "voteupcomment",
                        user_id = user_id,
                        action_date = readTime(sxv['creationdate']),
                        node_id = comment_id
                        )
                action.save()

                ov = orm.Vote(
                        node_id = comment_id,
                        user_id = user_id,
                        voted_at = action.action_date,
                        value = 1,
                        action = action
                        )

                ov.save()

                if not comment_id in comments2score:
                    comments2score[comment_id] = 1
                else:
                    comments2score[comment_id] += 1

    readTable(dump, "Comments2Votes", callback)

    for cid, score in comments2score.items():
        orm.Node.objects.filter(id=cid).update(score=score)


def badges_import(dump, uidmap, post_list):

    sxbadges = {}

    def sxcallback(b):
        sxbadges[int(b['id'])] = b

    readTable(dump, "Badges", sxcallback)

    obadges = dict([(b.cls, b) for b in orm.Badge.objects.all()])
    user_badge_count = {}

    sx_to_osqa = {}

    for id, sxb in sxbadges.items():
        cls = "".join(sxb['name'].replace('&', 'And').split(' '))

        if cls in obadges:
            sx_to_osqa[id] = obadges[cls]
        else:
            osqab = orm.Badge(
                    cls = cls,
                    awarded_count = 0,
                    type = sxb['class']
                    )
            osqab.save()
            sx_to_osqa[id] = osqab

    osqaawards = []

    def callback(sxa):
        badge = sx_to_osqa[int(sxa['badgeid'])]

        user_id = uidmap[sxa['userid']]
        if not user_badge_count.get(user_id, None):
            user_badge_count[user_id] = 0

        action = orm.Action(
                action_type = "award",
                user_id = user_id,
                action_date = readTime(sxa['date'])
                )

        action.save()

        osqaa = orm.Award(
                user_id = uidmap[sxa['userid']],
                badge = badge,
                node_id = post_list[user_badge_count[user_id]],
                awarded_at = action.action_date,
                action = action
                )

        osqaa.save()
        badge.awarded_count += 1

        user_badge_count[user_id] += 1

    readTable(dump, "Users2Badges", callback)

    for badge in obadges.values():
        badge.save()

def save_setting(k, v):
    try:
        kv = orm.KeyValue.objects.get(key=k)
        kv.value = v
    except:
        kv = orm.KeyValue(key = k, value = v)

    kv.save()


def pages_import(dump, currid):
    currid = IdIncrementer(currid)
    registry = {}

    def callback(sxp):
        currid.inc()
        page = orm.Node(
                id = currid.value,
                node_type = "page",
                title = sxp['name'],
                body = b64decode(sxp['value']),
                extra = dbsafe_encode({
                'path': sxp['url'][1:],
                'mimetype': sxp['contenttype'],
                'template': (sxp['usemaster'] == "true") and "default" or "none",
                'render': "html",
                'sidebar': "",
                'sidebar_wrap': True,
                'sidebar_render': "html",
                'comments': False
                }),
                author_id = 1
                )

        create_and_activate_revision(page)

        page.save()
        registry[sxp['url'][1:]] = page.id

        create_action = orm.Action(
                action_type = "newpage",
                user_id = page.author_id,
                node = page
                )

        create_action.save()

        if sxp['active'] == "true" and sxp['contenttype'] == "text/html":
            pub_action = orm.Action(
                    action_type = "publish",
                    user_id = page.author_id,
                    node = page
                    )

            pub_action.save()
            add_post_state("published", page, pub_action)

    readTable(dump, "FlatPages", callback)

    save_setting('STATIC_PAGE_REGISTRY', dbsafe_encode(registry))

sx2osqa_set_map = {
u'theme.html.name': 'APP_TITLE',
u'theme.html.footer': 'CUSTOM_FOOTER',
u'theme.html.sidebar': 'SIDEBAR_UPPER_TEXT',
u'theme.html.sidebar-low': 'SIDEBAR_LOWER_TEXT',
u'theme.html.welcome': 'APP_INTRO',
u'theme.html.head': 'CUSTOM_HEAD',
u'theme.html.header': 'CUSTOM_HEADER',
u'theme.css': 'CUSTOM_CSS',
}

html_codes = (
('&amp;', '&'),
('&lt;', '<'),
('&gt;', '>'),
('&quot;', '"'),
('&#39;', "'"),
)

def html_decode(html):
    html = force_unicode(html)

    for args in html_codes:
        html = html.replace(*args)

    return html


def static_import(dump):
    sx_unknown = {}

    def callback(set):
        if unicode(set['name']) in sx2osqa_set_map:
            save_setting(sx2osqa_set_map[set['name']], dbsafe_encode(html_decode(set['value'])))
        else:
            sx_unknown[set['name']] = html_decode(set['value'])

    readTable(dump, "ThemeTextResources", callback)

    save_setting('SXIMPORT_UNKNOWN_SETS', dbsafe_encode(sx_unknown))

def disable_triggers():
    from south.db import db
    if db.backend_name == "postgres":
        db.execute_many(PG_DISABLE_TRIGGERS)
        db.commit_transaction()
        db.start_transaction()

def enable_triggers():
    from south.db import db
    if db.backend_name == "postgres":
        db.start_transaction()
        db.execute_many(PG_ENABLE_TRIGGERS)
        db.commit_transaction()

def reset_sequences():
    from south.db import db
    if db.backend_name == "postgres":
        db.start_transaction()
        db.execute_many(PG_SEQUENCE_RESETS)
        db.commit_transaction()

def reindex_fts():
    from south.db import db
    if db.backend_name == "postgres":
        db.start_transaction()
        db.execute_many("UPDATE forum_noderevision set id = id WHERE TRUE;")
        db.commit_transaction()


def sximport(dump, options):
    try:
        disable_triggers()
        triggers_disabled = True
    except:
        triggers_disabled = False

    uidmap = userimport(dump, options)
    tagmap = tagsimport(dump, uidmap)
    gc.collect()

    posts = postimport(dump, uidmap, tagmap)
    gc.collect()

    posts, comments = comment_import(dump, uidmap, posts)
    gc.collect()

    post_vote_import(dump, uidmap, posts)
    gc.collect()

    comment_vote_import(dump, uidmap, comments)
    gc.collect()

    badges_import(dump, uidmap, posts)

    pages_import(dump, max(posts))
    static_import(dump)
    gc.collect()

    from south.db import db
    db.commit_transaction()

    reset_sequences()

    if triggers_disabled:
        enable_triggers()
        reindex_fts()


PG_DISABLE_TRIGGERS = """
ALTER table auth_user DISABLE TRIGGER ALL;
ALTER table auth_user_groups DISABLE TRIGGER ALL;
ALTER table auth_user_user_permissions DISABLE TRIGGER ALL;
ALTER table forum_keyvalue DISABLE TRIGGER ALL;
ALTER table forum_action DISABLE TRIGGER ALL;
ALTER table forum_actionrepute DISABLE TRIGGER ALL;
ALTER table forum_subscriptionsettings DISABLE TRIGGER ALL;
ALTER table forum_validationhash DISABLE TRIGGER ALL;
ALTER table forum_authkeyuserassociation DISABLE TRIGGER ALL;
ALTER table forum_tag DISABLE TRIGGER ALL;
ALTER table forum_markedtag DISABLE TRIGGER ALL;
ALTER table forum_node DISABLE TRIGGER ALL;
ALTER table forum_nodestate DISABLE TRIGGER ALL;
ALTER table forum_node_tags DISABLE TRIGGER ALL;
ALTER table forum_noderevision DISABLE TRIGGER ALL;
ALTER table forum_node_tags DISABLE TRIGGER ALL;
ALTER table forum_questionsubscription DISABLE TRIGGER ALL;
ALTER table forum_vote DISABLE TRIGGER ALL;
ALTER table forum_flag DISABLE TRIGGER ALL;
ALTER table forum_badge DISABLE TRIGGER ALL;
ALTER table forum_award DISABLE TRIGGER ALL;
ALTER table forum_openidnonce DISABLE TRIGGER ALL;
ALTER table forum_openidassociation DISABLE TRIGGER ALL;
"""

PG_ENABLE_TRIGGERS = """
ALTER table auth_user ENABLE TRIGGER ALL;
ALTER table auth_user_groups ENABLE TRIGGER ALL;
ALTER table auth_user_user_permissions ENABLE TRIGGER ALL;
ALTER table forum_keyvalue ENABLE TRIGGER ALL;
ALTER table forum_action ENABLE TRIGGER ALL;
ALTER table forum_actionrepute ENABLE TRIGGER ALL;
ALTER table forum_subscriptionsettings ENABLE TRIGGER ALL;
ALTER table forum_validationhash ENABLE TRIGGER ALL;
ALTER table forum_authkeyuserassociation ENABLE TRIGGER ALL;
ALTER table forum_tag ENABLE TRIGGER ALL;
ALTER table forum_markedtag ENABLE TRIGGER ALL;
ALTER table forum_node ENABLE TRIGGER ALL;
ALTER table forum_nodestate ENABLE TRIGGER ALL;
ALTER table forum_node_tags ENABLE TRIGGER ALL;
ALTER table forum_noderevision ENABLE TRIGGER ALL;
ALTER table forum_node_tags ENABLE TRIGGER ALL;
ALTER table forum_questionsubscription ENABLE TRIGGER ALL;
ALTER table forum_vote ENABLE TRIGGER ALL;
ALTER table forum_flag ENABLE TRIGGER ALL;
ALTER table forum_badge ENABLE TRIGGER ALL;
ALTER table forum_award ENABLE TRIGGER ALL;
ALTER table forum_openidnonce ENABLE TRIGGER ALL;
ALTER table forum_openidassociation ENABLE TRIGGER ALL;
"""

PG_SEQUENCE_RESETS = """
SELECT setval('"auth_user_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "auth_user";
SELECT setval('"auth_user_groups_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "auth_user_groups";
SELECT setval('"auth_user_user_permissions_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "auth_user_user_permissions";
SELECT setval('"forum_keyvalue_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_keyvalue";
SELECT setval('"forum_action_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_action";
SELECT setval('"forum_actionrepute_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_actionrepute";
SELECT setval('"forum_subscriptionsettings_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_subscriptionsettings";
SELECT setval('"forum_validationhash_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_validationhash";
SELECT setval('"forum_authkeyuserassociation_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_authkeyuserassociation";
SELECT setval('"forum_tag_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_tag";
SELECT setval('"forum_markedtag_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_markedtag";
SELECT setval('"forum_node_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_node";
SELECT setval('"forum_nodestate_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_nodestate";
SELECT setval('"forum_node_tags_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_node_tags";
SELECT setval('"forum_noderevision_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_noderevision";
SELECT setval('"forum_node_tags_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_node_tags";
SELECT setval('"forum_questionsubscription_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_questionsubscription";
SELECT setval('"forum_vote_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_vote";
SELECT setval('"forum_flag_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_flag";
SELECT setval('"forum_badge_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_badge";
SELECT setval('"forum_award_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_award";
SELECT setval('"forum_openidnonce_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_openidnonce";
SELECT setval('"forum_openidassociation_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_openidassociation";
"""


    
    
