# -*- coding: utf-8 -*-

from datetime import datetime
import sys
import os.path
import re
import time
from lxml import etree
import MySQLdb
import sqlite3
from django.utils.encoding import smart_str, smart_unicode
import gc

now = datetime.now()
FILES = ('Users.xml', 'Posts.xml', 'Votes.xml')
MAX_VALUES = 250
msstrip = re.compile(r'^(.*)\.\d+')

OSQA_DB_USERNAME = 'osqa'
OSQA_DB_PASSWORD = 'osqapass'
OSQA_DB_NAME = 'test'


def escape(string):
    return smart_unicode(MySQLdb.escape_string(smart_str(string)))


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
    postsmap = {}
    usermap = {}
    current_post_id = 0
    revision_id = 0
    parent_is_not_available = {}
    header = """INSERT INTO forum_node
            (id, title, tagnames, author_id, body, node_type, parent_id,
            added_at, score, state_string, last_activity_by_id, last_activity_at,
            active_revision_id, extra_count, marked) VALUES """.encode("utf-8")

    def __init__(self, usermap):
        self.usermap = usermap

        self.con = sqlite3.connect("/media/DATA/sqlite.db")
        cur = self.con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS tags " +
                    "(name TEXT, used_count INT, PRIMARY KEY(name ASC))")
        cur.execute("CREATE TABLE IF NOT EXISTS revisions (data TEXT)")

        con = MySQLdb.connect('localhost', OSQA_DB_USERNAME, OSQA_DB_PASSWORD, OSQA_DB_NAME)
        with con:
            cur = con.cursor()
            cur.execute("SELECT MAX(id) FROM forum_node")
            row = cur.fetchone()
            self.current_post_id = row[0] if row[0] else 0

            cur.execute("SELECT MAX(id) FROM forum_noderevision")
            row = cur.fetchone()
            self.revision_id = row[0] if row[0] else 0

    def get_state(self, post):
        # TODO: add states to `forum_nodestate` and create actions
        if post.get('AcceptedAnswerId'):
            self.accepted_answers[post.get('AcceptedAnswerId')] = post['Id']
        accepted_state = ''
        if post['Id'] in self.accepted_answers:
            accepted_state = '(accepted)'
            del self.accepted_answers[post['Id']]
        return accepted_state + ('(wiki)' if post.get('CommunityOwnedDate') else '')

    def readTagnames(self, ts):
        if not ts: return ''
        tagnames = ts.replace(u'ö', '-').replace(u'é', '').replace(u'à', '')\
                     .replace('><', ' ').replace('>', '').replace('<', '')

        cur = self.con.cursor()
        for name in tagnames.split(' '):
            cur.execute("SELECT rowid, name, used_count FROM tags WHERE name=?", (name,))
            otag = cur.fetchone()
            if otag is None:
                cur.execute("INSERT INTO tags VALUES(?,?)", (name, 1))
                self.nodetags.append((self.current_post_id, cur.lastrowid))
            else:
                cur.execute("UPDATE tags SET used_count=used_count+1 WHERE rowid=?", (otag[0],))
                self.nodetags.append((self.current_post_id, otag[0]))

        return tagnames

    def create_and_activate_revision(self, title, owner_id, creation_date, body):
        cur = self.con.cursor()
        self.revision_id += 1
        values = u"(%d, '%s','',%d,'%s',%s,'Initial revision',1,'%s')" % (
                    self.revision_id, title, owner_id, '',  # writing empty body
                    self.current_post_id, readTime(creation_date) )
        cur.execute("INSERT INTO revisions VALUES(?)", (values,) )
        return self.revision_id

    def make_sql(self, obj):
        self.current_post_id += 1
        self.postsmap[long(obj['Id'])] = self.current_post_id

        state = self.get_state(obj)
        title = escape(obj.get('Title', ''))
        body = escape(obj['Body'])
        owner_id = self.usermap.get(int(obj['OwnerUserId']), 1) if 'OwnerUserId' in obj else 1
        parent_id = str(self.postsmap.get(int(obj['ParentId']), 0)) if 'ParentId' in obj else 'NULL'
        if parent_id == 0:
            self.parent_is_not_available[self.current_post_id] = int(obj['ParentId'])
        last_editor_user_id = self.usermap.get(int(obj['LastEditorUserId']), 1) if 'LastEditorUserId' in obj else 1

        return u"(%d,'%s','%s',%d,'%s','%s',%s,'%s',%s,'%s',%d,'%s',%s,%s,%d)" % (
                self.current_post_id, title,
                escape(self.readTagnames(obj.get('Tags', ''))),
                owner_id, body, 'question' if obj['PostTypeId'] == '1' else 'answer',
                parent_id, readTime(obj['CreationDate']),
                obj['Score'], state, last_editor_user_id,
                readTime(obj.get('LastActivityDate')),
                self.create_and_activate_revision(title, owner_id, obj['CreationDate'], body),
                obj['ViewCount'] if obj.get('ViewCount') else u'0',
                1 if state else 0)

    def finalize(self):
        tags_header = """INSERT INTO forum_tag
            (id, name, created_by_id, created_at, used_count) VALUES """
        f = open(getFilePath("posts-misc.sql"), "w")
        cur = self.con.cursor()

        writew(f, tags_header, cur.execute("SELECT rowid, name, used_count FROM tags"),
               lambda x: u"(%s, '%s',%s,'%s',%s)" % (x[0], escape(x[1]), 1, now, x[2]) )

        nodetags_header = u"INSERT INTO forum_node_tags(node_id,tag_id) VALUES "
        writew(f, nodetags_header, self.nodetags, lambda x: u"(%s,%s)" % x)
        revisions_header = """INSERT INTO forum_noderevision
            (id, title, tagnames, author_id, body, node_id,
                summary, revision, revised_at) VALUES """

        writew(f, revisions_header, cur.execute("SELECT data FROM revisions"), lambda x: x[0])
        f.write(";\n")

        for post_id in self.accepted_answers:
            f.write("UPDATE forum_node SET state_string=CONCAT(state_string, '(accepted)') WHERE id=%d;\n" % self.postsmap[int(post_id)])

        for post_id, parent_id in self.parent_is_not_available.iteritems():
            f.write("UPDATE forum_node SET parent_id=%d WHERE id=%d;\n" % (self.postsmap[parent_id], post_id))

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

            if not counter % 100:
                gc.collect()

        print "Almost done..."
        writer.close()
        self.finalize()

        return self.postsmap


class UsersConverter():
    header_auth = """INSERT INTO auth_user
            (id, username, email, password, is_active, date_joined)
            VALUES """
    header_forum = """INSERT INTO forum_user
            (user_ptr_id, last_seen, about, website,
                reputation, gold, silver, bronze, real_name, location)
            VALUES """
    usernames = {}
    existing_users = {}  # {email: id}
    usermap = {}
    last_user_id = 0

    def __init__(self):
        con = MySQLdb.connect('localhost', OSQA_DB_USERNAME, OSQA_DB_PASSWORD, OSQA_DB_NAME)
        with con:
            cur = con.cursor()
            cur.execute("SELECT id, email FROM auth_user")
            user_emails = cur.fetchall()
            for row in user_emails:
                self.existing_users[row[1]] = row[0]

            if len(user_emails) > 0:
                self.last_user_id = max(user_emails, key=lambda x: x[0])[0] + 1
            else:
                self.last_user_id = 1

    def make_sql_forum(self, obj):
        return u"(%d, '%s', '%s', '%s', %s, 0, 0, 0, '%s', '%s')" % (
                self.current_id,  readTime(obj.get('LastAccessDate')),
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
        return u"(%d, '%s', '%s', '!', 1, '%s')" % (
               self.current_id, name, obj['EmailHash'],
               readTime(obj.get('DateJoined')),
        )

    def processUserId(self, obj):
        if obj['EmailHash'] in self.existing_users:
            self.usermap[long(obj["Id"])] = self.existing_users[obj['EmailHash']]
            return True
        self.usermap[long(obj["Id"])] = self.last_user_id
        self.current_id = self.last_user_id
        self.last_user_id += 1
        return False

    def convert(self, context, files_count):
        files_count = (files_count // 2) or 1
        writer_auth = Writer(files_count, "auth_user")
        writer_forum = Writer(files_count, "forum_user")
        counter = 0
        mod = MAX_VALUES * files_count
        for event, elem in context:
            if int(elem.attrib['Id']) < 0 or self.processUserId(elem.attrib):
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

        return self.usermap


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
    vote_header = """INSERT IGNORE INTO forum_vote (user_id, node_id, value,
        action_id, voted_at) VALUES """

    def __init__(self, usermap, postsmap):
        self.usermap = usermap
        self.postsmap = postsmap

        con = MySQLdb.connect('localhost', OSQA_DB_USERNAME, OSQA_DB_PASSWORD, OSQA_DB_NAME)
        with con:
            cur = con.cursor()
            cur.execute("SELECT MAX(id) FROM forum_action")
            row = cur.fetchone()
            self.action_id = row[0] + 1 if row[0] else 1

    def get_action(self, code):
        return code in self.actions and self.actions[code] or "unknown"

    def make_sql(self, obj):
        if int(obj['PostId']) not in self.postsmap:
            return None, None
        user_id = self.usermap.get(int(obj['UserId']), 1) if 'UserId' in obj else 1
        post_id = self.postsmap[int(obj['PostId'])]
        creation_date = readTime(obj['CreationDate'])

        sql_vote = u"(%s, %s, %d, %d, '%s')" % (
            user_id, post_id, ['VoteTypeId'] == '2' and 1 or -1,
            self.action_id, creation_date
        )
        sql_action = u"(%d, %d, %d, '%s', '%s')" % (
            self.action_id, user_id, post_id,
            self.get_action(obj['VoteTypeId']), creation_date,
        )

        return sql_vote, sql_action

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

            values_vote, values_action = self.make_sql(elem.attrib)

            if values_vote is None:
                continue
            if counter % mod < files_count:
                writer_vote.write(values_vote.encode('utf-8'))
                writer_action.write(values_action.encode('utf-8'))
            else:
                writer_vote.write((u',\n' + values_vote).encode('utf-8'))
                writer_action.write((u',\n' + values_action).encode('utf-8'))

            counter += 1
            self.action_id += 1
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        writer_vote.close()
        writer_action.close()


def convert(path, files_count):
    print "Processing 'users.xml'"
    usersConverter = UsersConverter()
    context = etree.iterparse(os.path.join(path, FILES[0]), events=('end',), tag='row')
    usermap = usersConverter.convert(context, files_count)
    del context

    print "Processing 'posts.xml'"
    postsConverter = PostsConverter(usermap)
    context = etree.iterparse(os.path.join(path, FILES[1]), events=('end',), tag='row')
    postsmap = postsConverter.convert(context, files_count)
    del context

    print "Processing 'votes.xml'"
    votesConverter = VotesConverter(usermap, postsmap)
    context = etree.iterparse(os.path.join(path, FILES[2]), events=('end',), tag='row')
    votesConverter.convert(context, files_count)
    del context


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Please provide path to the directory with:"
        print FILES
    else:
        files_count = int(sys.argv[2]) if len(sys.argv) > 2 else 6
        convert(sys.argv[1], files_count)
