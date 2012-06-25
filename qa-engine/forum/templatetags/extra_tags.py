import time
import os
import posixpath
import datetime
import math
import re
import logging
from django import template
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from forum.models import Question, Answer, QuestionRevision, AnswerRevision, NodeRevision
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.utils import simplejson
from forum import settings
from django.template.defaulttags import url as default_url
from forum import skins
from forum.utils import html
from extra_filters import decorated_int
from django.core.urlresolvers import reverse

register = template.Library()

GRAVATAR_TEMPLATE = ('<img class="gravatar" width="%(size)s" height="%(size)s" '
'src="http://www.gravatar.com/avatar/%(gravatar_hash)s'
'?s=%(size)s&amp;d=%(default)s&amp;r=%(rating)s" '
'alt="%(username)s\'s gravatar image" />')

@register.simple_tag
def gravatar(user, size):
    try:
        gravatar = user['gravatar']
        username = user['username']
    except (TypeError, AttributeError, KeyError):
        gravatar = user.gravatar
        username = user.username
    return mark_safe(GRAVATAR_TEMPLATE % {
    'size': size,
    'gravatar_hash': gravatar,
    'default': settings.GRAVATAR_DEFAULT_IMAGE,
    'rating': settings.GRAVATAR_ALLOWED_RATING,
    'username': template.defaultfilters.urlencode(username),
    })


@register.simple_tag
def get_score_badge(user):
    if user.is_suspended():
        return _("(suspended)")

    repstr = decorated_int(user.reputation, "")

    BADGE_TEMPLATE = '<span class="score" title="%(reputation)s %(reputationword)s">%(repstr)s</span>'
    if user.gold > 0 :
        BADGE_TEMPLATE = '%s%s' % (BADGE_TEMPLATE, '<span title="%(gold)s %(badgesword)s">'
        '<span class="badge1">&#9679;</span>'
        '<span class="badgecount">%(gold)s</span>'
        '</span>')
    if user.silver > 0:
        BADGE_TEMPLATE = '%s%s' % (BADGE_TEMPLATE, '<span title="%(silver)s %(badgesword)s">'
        '<span class="silver">&#9679;</span>'
        '<span class="badgecount">%(silver)s</span>'
        '</span>')
    if user.bronze > 0:
        BADGE_TEMPLATE = '%s%s' % (BADGE_TEMPLATE, '<span title="%(bronze)s %(badgesword)s">'
        '<span class="bronze">&#9679;</span>'
        '<span class="badgecount">%(bronze)s</span>'
        '</span>')
    BADGE_TEMPLATE = smart_unicode(BADGE_TEMPLATE, encoding='utf-8', strings_only=False, errors='strict')
    return mark_safe(BADGE_TEMPLATE % {
    'reputation' : user.reputation,
    'repstr': repstr,
    'gold' : user.gold,
    'silver' : user.silver,
    'bronze' : user.bronze,
    'badgesword' : _('badges'),
    'reputationword' : _('reputation points'),
    })


@register.simple_tag
def get_age(birthday):
    current_time = datetime.datetime(*time.localtime()[0:6])
    year = birthday.year
    month = birthday.month
    day = birthday.day
    diff = current_time - datetime.datetime(year, month, day, 0, 0, 0)
    return diff.days / 365

@register.simple_tag
def diff_date(date, limen=2):
    if not date:
        return _('unknown')

    now = datetime.datetime.now()
    diff = now - date
    days = diff.days
    hours = int(diff.seconds/3600)
    minutes = int(diff.seconds/60)

    if days > 2:
        if date.year == now.year:
            return date.strftime(_("%b %d at %H:%M").encode())
        else:
            return date.strftime(_("%b %d '%y at %H:%M").encode())
    elif days == 2:
        return _('2 days ago')
    elif days == 1:
        return _('yesterday')
    elif minutes >= 60:
        return ungettext('%(hr)d ' + _("hour ago"), '%(hr)d ' + _("hours ago"), hours) % {'hr':hours}
    elif diff.seconds >= 60:
        return ungettext('%(min)d ' + _("min ago"), '%(min)d ' + _("mins ago"), minutes) % {'min':minutes}
    else:
        return ungettext('%(sec)d ' + _("sec ago"), '%(sec)d ' + _("secs ago"), diff.seconds) % {'sec':diff.seconds}

@register.simple_tag
def media(url):
    url = skins.find_media_source(url)
    if url:
        # Create the URL prefix.
        url_prefix = settings.FORCE_SCRIPT_NAME + '/m/'

        # Make sure any duplicate forward slashes are replaced with a single
        # forward slash.
        url_prefix = re.sub("/+", "/", url_prefix)

        url = url_prefix + url
        return url

class ItemSeparatorNode(template.Node):
    def __init__(self, separator):
        sep = separator.strip()
        if sep[0] == sep[-1] and sep[0] in ('\'', '"'):
            sep = sep[1:-1]
        else:
            raise template.TemplateSyntaxError('separator in joinitems tag must be quoted')
        self.content = sep

    def render(self, context):
        return self.content

class BlockMediaUrlNode(template.Node):
    def __init__(self, nodelist):
        self.items = nodelist

    def render(self, context):
        prefix = settings.APP_URL + 'm/'
        url = ''
        if self.items:
            url += '/'
        for item in self.items:
            url += item.render(context)

        url = skins.find_media_source(url)
        url = prefix + url
        out = url
        return out.replace(' ', '')

@register.tag(name='blockmedia')
def blockmedia(parser, token):
    try:
        tagname = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("blockmedia tag does not use arguments")
    nodelist = []
    while True:
        nodelist.append(parser.parse(('endblockmedia')))
        next = parser.next_token()
        if next.contents == 'endblockmedia':
            break
    return BlockMediaUrlNode(nodelist)


@register.simple_tag
def fullmedia(url):
    domain = settings.APP_BASE_URL
    #protocol = getattr(settings, "PROTOCOL", "http")
    path = media(url)
    return "%s%s" % (domain, path)


class SimpleVarNode(template.Node):
    def __init__(self, name, value):
        self.name = name
        self.value = template.Variable(value)

    def render(self, context):
        context[self.name] = self.value.resolve(context)
        return ''

class BlockVarNode(template.Node):
    def __init__(self, name, block):
        self.name = name
        self.block = block

    def render(self, context):
        source = self.block.render(context)
        context[self.name] = source.strip()
        return ''


@register.tag(name='var')
def do_var(parser, token):
    tokens = token.split_contents()[1:]

    if not len(tokens) or not re.match('^\w+$', tokens[0]):
        raise template.TemplateSyntaxError("Expected variable name")

    if len(tokens) == 1:
        nodelist = parser.parse(('endvar',))
        parser.delete_first_token()
        return BlockVarNode(tokens[0], nodelist)
    elif len(tokens) == 3:
        return SimpleVarNode(tokens[0], tokens[2])

    raise template.TemplateSyntaxError("Invalid number of arguments")

class DeclareNode(template.Node):
    dec_re = re.compile('^\s*(\w+)\s*(:?=)\s*(.*)$')

    def __init__(self, block):
        self.block = block

    def render(self, context):
        source = self.block.render(context)

        for line in source.splitlines():
            m = self.dec_re.search(line)
            if m:
                clist = list(context)
                clist.reverse()
                d = {}
                d['_'] = _
                d['os'] = os
                d['html'] = html
                d['reverse'] = reverse
                for c in clist:
                    d.update(c)
                try:
                    context[m.group(1).strip()] = eval(m.group(3).strip(), d)
                except Exception, e:
                    logging.error("Error in declare tag, when evaluating: %s" % m.group(3).strip())
                    raise
        return ''

@register.tag(name='declare')
def do_declare(parser, token):
    nodelist = parser.parse(('enddeclare',))
    parser.delete_first_token()
    return DeclareNode(nodelist)
