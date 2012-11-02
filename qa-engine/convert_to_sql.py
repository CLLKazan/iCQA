# -*- coding: utf-8 -*-

from datetime import datetime
import sys
import re
import time
import codecs
import HTMLParser
from lxml import etree


now = datetime.now()
unescape = HTMLParser.HTMLParser().unescape
FILES = ('posts.xml', 'users.xml', 'votes.xml')
MAX_VALUES = 50
msstrip = re.compile(r'^(.*)\.\d+')
tagmap = {}
nodetags = []
accepted_answers = {}
revisions = []


def readTime(ts):
    if not ts: return ''
    noms = msstrip.match(ts)
    if noms:
        ts = noms.group(1)
    try:
        return datetime(*time.strptime(ts, '%Y-%m-%dT%H:%M:%S')[0:6])
    except ValueError:
        return datetime(*time.strptime(ts, '%Y-%m-%d')[0:3])


def writew(header, itervalues, func, check=lambda x: True):
    counter = 0
    for item in itervalues:
        if not check(item):
            continue

        if counter % MAX_VALUES == 0:
            sys.stdout.write(u';\n' + header.encode('utf-8'))
            values = func(item)
        else:
            values = u',\n' + func(item)
        sys.stdout.write(values.encode('utf-8'))
        counter += 1


def readTagnames(ts, postid):
    if not ts: return ''
    tagnames = ts.replace(u'ö', '-').replace(u'é', '').replace(u'à', '')\
      .replace('><', ' ').replace('>', '').replace('<', '')

    for name in tagnames.split(' '):
        otag = tagmap.get(name,
            {'name': name, 'used_count': 0,
            'created_by_id': 1, 'id': len(tagmap) + 1,
            'created_at': now})
        otag['used_count'] += 1
        tagmap[name] = otag
        nodetags.append((postid, otag['id']))

    return tagnames


def create_and_activate_revision(post):
    revisions.append(u"('%s','',%s,'%s',%s,'Initial revision',1,'%s')" % (
        mysql_escape(post.get('Title', '')), post.get('OwnerUserId', 1), '',
        post['Id'], readTime(post['CreationDate'])))
    return len(revisions)


def get_state(post):
    return ('(wiki)' if post.get('CommunityOwnedDate') else '') + ('(accepted)' if post.get('AcceptedAnswerId') else '')


def parse(line):
    ret = {}
    for item in re.finditer('(\w+)="([^"]*)"', line):
        v = unescape(item.group(2))
        ret.update({item.group(1): re.sub("(?<![\\\])(')", "\\'", v)})
    return ret


def mysql_escape(string):
    return re.sub("(?<![\\\])(')", "\\'", string)


def convert(path):
    fname = path.split('/')[-1].lower()
    context = etree.iterparse(sys.argv[1], events=('end',), tag='row')
    if fname == 'posts.xml':
        header = """INSERT INTO forum_node
            (id, title, tagnames, author_id, body, node_type, parent_id,
            added_at, score, state_string, last_activity_by_id, last_activity_at,
            active_revision_id, extra_count, marked) VALUES """

        def make_sql(obj):
            state = get_state(obj)
            return u"(%s,'%s','%s',%s,'%s','%s',%s,'%s',%s,'%s',%s,'%s',%s,%s,%s)" % (
                    obj['Id'], mysql_escape(obj.get('Title', '')),
                    mysql_escape(readTagnames(obj.get('Tags', ''), obj['Id'])),
                    obj.get('OwnerUserId', '1'), mysql_escape(obj['Body']),
                    'question' if obj['PostTypeId'] == '1' else 'answer',
                    obj.get('ParentId', 'NULL'), readTime(obj['CreationDate']),
                    obj['Score'], state, obj.get('LastEditorUserId', '1'),
                    readTime(obj.get('LastActivityDate')),
                    create_and_activate_revision(obj),
                    obj['ViewCount'] if obj.get('ViewCount') else '0',
                    '1' if state else '0')

        def finalize():
            tags_header = """INSERT INTO forum_tag
                (id, name, created_by_id, created_at, used_count) VALUES """
            writew(tags_header,
                   tagmap.itervalues(),
                   lambda x: u"(%s, '%s',%s,'%s',%s)" % (x['id'], mysql_escape(x['name']),
                        x['created_by_id'], x['created_at'], x['used_count']))
            nodetags_header = u"INSERT INTO forum_node_tags(node_id,tag_id) VALUES "
            writew(nodetags_header, nodetags, lambda x: u"(%s,%s)" % x)
            revisions_header = """INSERT INTO forum_noderevision
                (title, tagnames, author_id, body, node_id,
                    summary, revision, revised_at) VALUES """
            writew(revisions_header, revisions, lambda x: x)

    elif fname == 'users.xml':
        pass
    elif fname == 'votes.xml':
        pass

    #writew(header,
    #       codecs.open(path, 'r', 'utf-8').readlines(),
    #       lambda x: make_sql(parse(x)),
    #       lambda x: 'row' in x)
    counter = 0
    for event, elem in context:
        if counter % MAX_VALUES == 0:
            sys.stdout.write(u';\n' + header.encode('utf-8'))
            values = make_sql(elem.attrib)
        else:
            values = u',\n' + make_sql(elem.attrib)
        sys.stdout.write(values.encode('utf-8'))
        counter += 1
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context
    finalize()


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].split('/')[-1].lower() not in FILES:
        print "Please provide path to one of the following files:"
        print FILES
    else:
        sys.stdout.write("SET FOREIGN_KEY_CHECKS = 0")
        convert(sys.argv[1])
        sys.stdout.write(";\nSET FOREIGN_KEY_CHECKS = 1;\n")
