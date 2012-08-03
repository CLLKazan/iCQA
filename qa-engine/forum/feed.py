try:
    from django.contrib.syndication.views import Feed, FeedDoesNotExist, add_domain
    old_version = False
except:
    from django.contrib.syndication.feeds import Feed, FeedDoesNotExist, add_domain
    old_version = True

from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from models import Question
from forum import settings
from forum.modules import decorate
from forum.utils.pagination import generate_uri

@decorate(add_domain, needs_origin=False)
def add_domain(domain, url, *args, **kwargs):
    return "%s%s" % (settings.APP_BASE_URL, url)

class BaseNodeFeed(Feed):
    if old_version:
        title_template = "feeds/rss_title.html"
        description_template = "feeds/rss_description.html"

    def __init__(self, request, title, description, url):
        self._title = title
        self._description = mark_safe(unicode(description))
        self._url = url

        if old_version:
            super(BaseNodeFeed, self).__init__('', request)

    def title(self):
        return self._title

    def link(self):
        return self._url

    def description(self):
        return self._description

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.html

    def item_link(self, item):
        return item.leaf.get_absolute_url()

    def item_author_name(self, item):
        return item.author.username

    def item_author_link(self, item):
        return item.author.get_profile_url()

    def item_pubdate(self, item):
        return item.added_at

    if old_version:
        def __call__(self, request):
            feedgen = self.get_feed('')
            response = HttpResponse(mimetype=feedgen.mime_type)
            feedgen.write(response, 'utf-8')
            return response


class RssQuestionFeed(BaseNodeFeed):
    def __init__(self, request, question_list, title, description):
        url = request.path + "&" + generate_uri(request.GET, (_('page'), _('pagesize'), _('sort')))
        super(RssQuestionFeed, self).__init__(request, title, description, url)

        self._question_list = question_list

    def item_categories(self, item):
        return item.tagname_list()  

    def items(self):
       return self._question_list[:30]

class RssAnswerFeed(BaseNodeFeed):
    if old_version:
        title_template = "feeds/rss_answer_title.html"

    def __init__(self, request, question, include_comments=False):
        super(RssAnswerFeed, self).__init__(request, _("Answers to: %s") % question.title, question.html, question.get_absolute_url())
        self._question = question
        self._include_comments = include_comments

    def items(self):
        if self._include_comments:
            qs = self._question.all_children
        else:
            qs = self._question.answers

        return qs.filter_state(deleted=False).order_by('-added_at')[:30]

    def item_title(self, item):
        if item.node_type == "answer":
            return _("Answer by %s") % item.author.username
        else:
            return _("Comment by %(cauthor)s on %(pauthor)s's %(qora)s") % dict(
                cauthor=item.author.username, pauthor=item.parent.author.username, qora=(item.parent.node_type == "answer" and _("answer") or _("question"))
            )




