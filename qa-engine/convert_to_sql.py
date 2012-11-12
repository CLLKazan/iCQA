# -*- coding: utf-8 -*-

from datetime import datetime
import sys
import os.path
import re
import time
from lxml import etree
from MySQLdb import escape_string
from django.utils.encoding import smart_str, smart_unicode


now = datetime.now()
FILES = ('posts.xml', 'users.xml', 'votes.xml')
MAX_VALUES = 50
msstrip = re.compile(r'^(.*)\.\d+')


def escape(string):
    return smart_unicode(escape_string(smart_str(string)))


def readTime(ts):
    if not ts: return ''
    noms = msstrip.match(ts)
    if noms:
        ts = noms.group(1)
    try:
        return datetime(*time.strptime(ts, '%Y-%m-%dT%H:%M:%S')[0:6])
    except ValueError:
        return datetime(*time.strptime(ts, '%Y-%m-%d')[0:3])


def getFilePath(name):
    root_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(root_dir, name)


def writew(f, header, itervalues, func, check=lambda x: True):
    counter = 0
    for item in itervalues:
        if not check(item):
            continue

        if counter % MAX_VALUES == 0:
            f.write(u';\n' + header.encode('utf-8'))
            values = func(item)
        else:
            values = u',\n' + func(item)
        f.write(values.encode('utf-8'))
        counter += 1


class Writer():
    count = 6
    current = 0

    def __init__(self, count, name):
        self.count = count
        self.FILES = [open(getFilePath("%s-%s.sql" % (name, i)), "w") for i in xrange(count)]

    def write(self, string, is_header=False):
        if is_header:
            for f in self.FILES:
                f.write(string)
        else:
            self.FILES[self.current].write(string)
            self.current = (self.current + 1) % self.count

    def close(self):
        for f in self.FILES:
            f.write(";\n")
            f.close()


class PostsConverter():
    tagmap = {}
    nodetags = []
    accepted_answers = {}
    revisions = []
    header = """INSERT INTO forum_node
            (id, title, tagnames, author_id, body, node_type, parent_id,
            added_at, score, state_string, last_activity_by_id, last_activity_at,
            active_revision_id, extra_count, marked) VALUES """.encode("utf-8")

    def get_state(self, post):
        return ('(wiki)' if post.get('CommunityOwnedDate') else '') + \
               ('(accepted)' if post.get('AcceptedAnswerId') else '')

    def readTagnames(self, ts, postid):
        if not ts: return ''
        tagnames = ts.replace(u'ö', '-').replace(u'é', '').replace(u'à', '')\
          .replace('><', ' ').replace('>', '').replace('<', '')

        for name in tagnames.split(' '):
            otag = self.tagmap.get(name,
                {'name': name, 'used_count': 0,
                'created_by_id': 1, 'id': len(self.tagmap) + 1,
                'created_at': now})
            otag['used_count'] += 1
            self.tagmap[name] = otag
            self.nodetags.append((postid, otag['id']))

        return tagnames

    def create_and_activate_revision(self, post):
        self.revisions.append(u"('%s','',%s,'%s',%s,'Initial revision',1,'%s')" % (
            escape(post.get('Title', '')), post.get('OwnerUserId', 1), '',
            post['Id'], readTime(post['CreationDate'])))
        return len(self.revisions)

    def make_sql(self, obj):
        state = self.get_state(obj)
        return u"(%s,'%s','%s',%s,'%s','%s',%s,'%s',%s,'%s',%s,'%s',%s,%s,%d)" % (
                obj['Id'], escape(obj.get('Title', '')),
                escape(self.readTagnames(obj.get('Tags', ''), obj['Id'])),
                obj.get('OwnerUserId', '1'), escape(obj['Body']),
                'question' if obj['PostTypeId'] == '1' else 'answer',
                obj.get('ParentId', 'NULL'), readTime(obj['CreationDate']),
                obj['Score'], state, obj.get('LastEditorUserId', '1'),
                readTime(obj.get('LastActivityDate')),
                self.create_and_activate_revision(obj),
                obj['ViewCount'] if obj.get('ViewCount') else u'0',
                1 if state else 0)

    def finalize(self):
        tags_header = """INSERT INTO forum_tag
            (id, name, created_by_id, created_at, used_count) VALUES """
        f = open(getFilePath("posts-misc.sql"), "w")
        writew(f, tags_header,
               self.tagmap.itervalues(),
               lambda x: u"(%s, '%s',%s,'%s',%s)" % (x['id'], escape(x['name']),
                    x['created_by_id'], x['created_at'], x['used_count']))
        nodetags_header = u"INSERT INTO forum_node_tags(node_id,tag_id) VALUES "
        writew(f, nodetags_header, self.nodetags, lambda x: u"(%s,%s)" % x)
        revisions_header = """INSERT INTO forum_noderevision
            (title, tagnames, author_id, body, node_id,
                summary, revision, revised_at) VALUES """
        writew(f, revisions_header, self.revisions, lambda x: x)
        f.write(";\n")
        f.close()

    def convert(self, context, files_count):
        writer = Writer(files_count, "posts")
        counter = 0
        mod = MAX_VALUES * files_count
        for event, elem in context:
            if counter % mod == 0:
                writer.write(u';\n' + self.header, True)
            if counter % mod < files_count:
                values = self.make_sql(elem.attrib)
            else:
                values = u',\n' + self.make_sql(elem.attrib)
            writer.write(values.encode('utf-8'))
            counter += 1
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        writer.close()
        self.finalize()


class UsersConverter():
    header_auth = """INSERT INTO auth_user
            (id, username, email, password, is_active, date_joined)
            VALUES """
    header_forum = """INSERT INTO forum_user
            (user_ptr_id, last_seen, about, website,
                reputation, gold, silver, bronze, real_name, location)
            VALUES """
    usernames = {}

    def make_sql_forum(self, obj):
        return u"(%s, '%s', '%s', '%s', %s, 0, 0, 0, '%s', '%s')" % (
                obj['Id'],  readTime(obj.get('LastAccessDate')),
                escape(obj.get('AboutMe', '')),
                escape(obj.get('WebSiteUrl', '')),
                obj['Reputation'], escape(obj.get('RealName', '')[:30]),
                escape(obj.get('Location', ''))
        )

    def make_sql_auth(self, obj):
        name = escape(obj['DisplayName'].strip())
        if name in self.usernames:
            name = name + obj['Id']
        self.usernames[name] = True
        return u"(%s, '%s', '%s', '!', 1, '%s')" % (
               obj['Id'], name, obj.get('EmailHash', ''),
               readTime(obj.get('DateJoined')),
        )

    def convert(self, context, files_count):
        files_count = (files_count // 2) or 1
        writer_auth = Writer(files_count, "auth_user")
        writer_forum = Writer(files_count, "forum_user")
        counter = 0
        mod = MAX_VALUES * files_count
        for event, elem in context:
            if int(elem.attrib['Id']) < 0:
                continue
            if counter % mod == 0:
                writer_auth.write(u';\n' + self.header_auth, True)
                writer_forum.write(u';\n' + self.header_forum, True)
            if counter % mod < files_count:
                values_auth = self.make_sql_auth(elem.attrib)
                values_forum = self.make_sql_forum(elem.attrib)
            else:
                values_auth = u',\n' + self.make_sql_auth(elem.attrib)
                values_forum = u',\n' + self.make_sql_forum(elem.attrib)
            writer_auth.write(values_auth.encode('utf-8'))
            writer_forum.write(values_forum.encode('utf-8'))
            counter += 1
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        writer_auth.close()
        writer_forum.close()


class VotesConverter():

    actions = {
        '1': "acceptanswer",
        '2': "voteup",
        '3': "votedown",
        '4': "flag",
        '5': "favorite",
        '6': "close",
        '10': "delete",
        '12': "flag",
        '13': "flag",
    }

    action_id = 1

    action_header = """INSERT INTO forum_action (id, user_id, node_id,
        action_type, action_date) VALUES """
    #actionrepute_header = """INSERT INTO forum_actionrepute (action_id,
    #    date, user_id, value) VALUES """
    vote_header = """INSERT IGNORE INTO forum_vote (id, user_id, node_id, value,
        action_id, voted_at) VALUES """

    def get_action(self, code):
        return code in self.actions and self.actions[code] or "unknown"

    def make_sql_vote(self, obj):
        return u"(%s, %s, %s, %d, %d, '%s')" % (
            obj['Id'], obj.get('UserId', '1'), obj['PostId'],
            obj['VoteTypeId'] == '2' and 1 or -1, self.action_id,
            readTime(obj['CreationDate'])
        )

    def make_sql_action(self, obj):
        return u"(%d, %s, %s, '%s', '%s')" % (
            self.action_id, obj.get('UserId', '1'), obj['PostId'],
            self.get_action(obj['VoteTypeId']), readTime(obj['CreationDate']),
        )

    def convert(self, context, files_count):
        files_count = (files_count // 2) or 1
        writer_vote = Writer(files_count, "forum_vote")
        writer_action = Writer(files_count, "forum_action")
        counter = 0
        mod = MAX_VALUES * files_count
        for event, elem in context:
            if counter % mod == 0:
                writer_vote.write(u';\n' + self.vote_header, True)
                writer_action.write(u';\n' + self.action_header, True)
            if counter % mod < files_count:
                values_vote = self.make_sql_vote(elem.attrib)
                values_action = self.make_sql_action(elem.attrib)
            else:
                values_vote = u',\n' + self.make_sql_vote(elem.attrib)
                values_action = u',\n' + self.make_sql_action(elem.attrib)
            writer_vote.write(values_vote.encode('utf-8'))
            writer_action.write(values_action.encode('utf-8'))
            counter += 1
            self.action_id += 1
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        writer_vote.close()
        writer_action.close()


def convert(path, files_count):
    fname = path.split('/')[-1].lower()
    context = etree.iterparse(sys.argv[1], events=('end',), tag='row')

    if fname == 'posts.xml':
        converter = PostsConverter()
    elif fname == 'users.xml':
        converter = UsersConverter()
    elif fname == 'votes.xml':
        converter = VotesConverter()

    converter.convert(context, files_count)

    del context


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].split('/')[-1].lower() not in FILES:
        print "Please provide path to one of the following files:"
        print FILES
    else:
        files_count = int(sys.argv[2]) if len(sys.argv) > 1 else 6
        convert(sys.argv[1], files_count)
