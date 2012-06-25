# encoding:utf-8
import datetime
import logging
from urllib import unquote
from forum import settings as django_settings
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponsePermanentRedirect
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template import RequestContext
from django import template
from django.utils.html import *
from django.utils import simplejson
from django.db.models import Q, Count
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict
from django.views.decorators.cache import cache_page
from django.utils.http import urlquote  as django_urlquote
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

from forum.utils.html import sanitize_html, hyperlink
from forum.utils.diff import textDiff as htmldiff
from forum.utils import pagination
from forum.forms import *
from forum.models import *
from forum.forms import get_next_url
from forum.actions import QuestionViewAction
from forum.http_responses import HttpResponseUnauthorized
from forum.feed import RssQuestionFeed, RssAnswerFeed
from forum.utils.pagination import generate_uri
import decorators

class HottestQuestionsSort(pagination.SortBase):
    def apply(self, questions):
        return questions.annotate(new_child_count=Count('all_children')).filter(
                all_children__added_at__gt=datetime.datetime.now() - datetime.timedelta(days=1)).order_by('-new_child_count')


class QuestionListPaginatorContext(pagination.PaginatorContext):
    def __init__(self, id='QUESTIONS_LIST', prefix='', default_pagesize=30):
        super (QuestionListPaginatorContext, self).__init__(id, sort_methods=(
            (_('active'), pagination.SimpleSort(_('active'), '-last_activity_at', _("Most <strong>recently updated</strong> questions"))),
            (_('newest'), pagination.SimpleSort(_('newest'), '-added_at', _("most <strong>recently asked</strong> questions"))),
            (_('hottest'), HottestQuestionsSort(_('hottest'), _("most <strong>active</strong> questions in the last 24 hours</strong>"))),
            (_('mostvoted'), pagination.SimpleSort(_('most voted'), '-score', _("most <strong>voted</strong> questions"))),
        ), pagesizes=(15, 30, 50), default_pagesize=default_pagesize, prefix=prefix)

class AnswerSort(pagination.SimpleSort):
    def apply(self, answers):
        if not settings.DISABLE_ACCEPTING_FEATURE:
            return answers.order_by(*(['-marked'] + list(self._get_order_by())))
        else:
            return super(AnswerSort, self).apply(answers)

class AnswerPaginatorContext(pagination.PaginatorContext):
    def __init__(self, id='ANSWER_LIST', prefix='', default_pagesize=10):
        super (AnswerPaginatorContext, self).__init__(id, sort_methods=(
            (_('oldest'), AnswerSort(_('oldest answers'), 'added_at', _("oldest answers will be shown first"))),
            (_('newest'), AnswerSort(_('newest answers'), '-added_at', _("newest answers will be shown first"))),
            (_('votes'), AnswerSort(_('popular answers'), ('-score', 'added_at'), _("most voted answers will be shown first"))),
        ), default_sort=_('votes'), pagesizes=(5, 10, 20), default_pagesize=default_pagesize, prefix=prefix)

class TagPaginatorContext(pagination.PaginatorContext):
    def __init__(self):
        super (TagPaginatorContext, self).__init__('TAG_LIST', sort_methods=(
            (_('name'), pagination.SimpleSort(_('by name'), 'name', _("sorted alphabetically"))),
            (_('used'), pagination.SimpleSort(_('by popularity'), '-used_count', _("sorted by frequency of tag use"))),
        ), default_sort=_('used'), pagesizes=(30, 60, 120))
    

def feed(request):
    return RssQuestionFeed(
                request,
                Question.objects.filter_state(deleted=False).order_by('-last_activity_at'),
                settings.APP_TITLE + _(' - ')+ _('latest questions'),
                settings.APP_DESCRIPTION)(request)

@decorators.render('index.html')
def index(request):
    paginator_context = QuestionListPaginatorContext()
    paginator_context.base_path = reverse('questions')
    return question_list(request,
                         Question.objects.all(),
                         base_path=reverse('questions'),
                         feed_url=reverse('latest_questions_feed'),
                         paginator_context=paginator_context)

@decorators.render('questions.html', 'unanswered', _('unanswered'), weight=400)
def unanswered(request):
    return question_list(request,
                         Question.objects.exclude(id__in=Question.objects.filter(children__marked=True).distinct()),
                         _('open questions without an accepted answer'),
                         None,
                         _("Unanswered Questions"))

@decorators.render('questions.html', 'questions', _('questions'), weight=0)
def questions(request):
    return question_list(request, Question.objects.all(), _('questions'))

@decorators.render('questions.html')
def tag(request, tag):
    try:
        tag = Tag.active.get(name=unquote(tag))
    except Tag.DoesNotExist:
        raise Http404

    return question_list(request,
                         Question.objects.filter(tags=tag),
                         mark_safe(_('questions tagged <span class="tag">%(tag)s</span>') % {'tag': tag}),
                         None,
                         mark_safe(_('Questions Tagged With %(tag)s') % {'tag': tag}),
                         False)

@decorators.render('questions.html', 'questions', tabbed=False)
def user_questions(request, mode, user, slug):
    user = get_object_or_404(User, id=user)

    if mode == _('asked-by'):
        questions = Question.objects.filter(author=user)
        description = _("Questions asked by %s")
    elif mode == _('answered-by'):
        questions = Question.objects.filter(children__author=user, children__node_type='answer').distinct()
        description = _("Questions answered by %s")
    elif mode == _('subscribed-by'):
        if not (request.user.is_superuser or request.user == user):
            return HttpResponseUnauthorized(request)
        questions = user.subscriptions

        if request.user == user:
            description = _("Questions you subscribed %s")
        else:
            description = _("Questions subscribed by %s")
    else:
        raise Http404


    return question_list(request, questions,
                         mark_safe(description % hyperlink(user.get_profile_url(), user.username)),
                         page_title=description % user.username)

def question_list(request, initial,
                  list_description=_('questions'),
                  base_path=None,
                  page_title=_("All Questions"),
                  allowIgnoreTags=True,
                  feed_url=None,
                  paginator_context=None):

    questions = initial.filter_state(deleted=False)

    if request.user.is_authenticated() and allowIgnoreTags:
        questions = questions.filter(~Q(tags__id__in = request.user.marked_tags.filter(user_selections__reason = 'bad')))

    if page_title is None:
        page_title = _("Questions")

    if request.GET.get('type', None) == 'rss':
        questions = questions.order_by('-added_at')
        return RssQuestionFeed(request, questions, page_title, list_description)(request)

    keywords =  ""
    if request.GET.get("q"):
        keywords = request.GET.get("q").strip()

    #answer_count = Answer.objects.filter_state(deleted=False).filter(parent__in=questions).count()
    #answer_description = _("answers")

    if not feed_url:
        req_params = "&".join(generate_uri(request.GET, (_('page'), _('pagesize'), _('sort'))))
        if req_params:
            req_params = '&' + req_params

        feed_url = mark_safe(escape(request.path + "?type=rss" + req_params))

    return pagination.paginated(request, ('questions', paginator_context or QuestionListPaginatorContext()), {
    "questions" : questions.distinct(),
    "questions_count" : questions.count(),
    "keywords" : keywords,
    "list_description": list_description,
    "base_path" : base_path,
    "page_title" : page_title,
    "tab" : "questions",
    'feed_url': feed_url,
    })


def search(request):
    if request.method == "GET" and "q" in request.GET:
        keywords = request.GET.get("q")
        search_type = request.GET.get("t")

        if not keywords:
            return HttpResponseRedirect(reverse(index))
        if search_type == 'tag':
            return HttpResponseRedirect(reverse('tags') + '?q=%s' % urlquote(keywords.strip()))
        elif search_type == "user":
            return HttpResponseRedirect(reverse('users') + '?q=%s' % urlquote(keywords.strip()))
        else:
            return question_search(request, keywords)
    else:
        return render_to_response("search.html", context_instance=RequestContext(request))

@decorators.render('questions.html')
def question_search(request, keywords):
    can_rank, initial = Question.objects.search(keywords)

    if can_rank:
        paginator_context = QuestionListPaginatorContext()
        paginator_context.sort_methods[_('ranking')] = pagination.SimpleSort(_('relevance'), '-ranking', _("most relevant questions"))
        paginator_context.force_sort = _('ranking')
    else:
        paginator_context = None

    return question_list(request, initial,
                         _("questions matching '%(keywords)s'") % {'keywords': keywords},
                         None,
                         _("questions matching '%(keywords)s'") % {'keywords': keywords},
                         paginator_context=paginator_context)


@decorators.render('tags.html', 'tags', _('tags'), weight=100)
def tags(request):
    stag = ""
    tags = Tag.active.all()

    if request.method == "GET":
        stag = request.GET.get("q", "").strip()
        if stag:
            tags = tags.filter(name__icontains=stag)

    return pagination.paginated(request, ('tags', TagPaginatorContext()), {
        "tags" : tags,
        "stag" : stag,
        "keywords" : stag
    })

def update_question_view_times(request, question):
    last_seen_in_question = request.session.get('last_seen_in_question', {})

    last_seen = last_seen_in_question.get(question.id, None)

    if (not last_seen) or (last_seen < question.last_activity_at):
        QuestionViewAction(question, request.user, ip=request.META['REMOTE_ADDR']).save()
        last_seen_in_question[question.id] = datetime.datetime.now()
        request.session['last_seen_in_question'] = last_seen_in_question

def match_question_slug(id, slug):
    slug_words = slug.split('-')
    qs = Question.objects.filter(title__istartswith=slug_words[0])

    for q in qs:
        if slug == urlquote(slugify(q.title)):
            return q

    return None

def answer_redirect(request, answer):
    pc = AnswerPaginatorContext()

    sort = pc.sort(request)

    if sort == _('oldest'):
        filter = Q(added_at__lt=answer.added_at)
    elif sort == _('newest'):
        filter = Q(added_at__gt=answer.added_at)
    elif sort == _('votes'):
        filter = Q(score__gt=answer.score) | Q(score=answer.score, added_at__lt=answer.added_at)
    else:
        raise Http404()

    count = answer.question.answers.filter(Q(marked=True) | filter).exclude(state_string="(deleted)").count()
    pagesize = pc.pagesize(request)

    page = count / pagesize
    
    if count % pagesize:
        page += 1
        
    if page == 0:
        page = 1

    return HttpResponsePermanentRedirect("%s?%s=%s#%s" % (
        answer.question.get_absolute_url(), _('page'), page, answer.id))

@decorators.render("question.html", 'questions')
def question(request, id, slug='', answer=None):
    try:
        question = Question.objects.get(id=id)
    except:
        if slug:
            question = match_question_slug(id, slug)
            if question is not None:
                return HttpResponseRedirect(question.get_absolute_url())

        raise Http404()

    if question.nis.deleted and not request.user.can_view_deleted_post(question):
        raise Http404

    if request.GET.get('type', None) == 'rss':
        return RssAnswerFeed(request, question, include_comments=request.GET.get('comments', None) == 'yes')(request)

    if answer:
        answer = get_object_or_404(Answer, id=answer)

        if (question.nis.deleted and not request.user.can_view_deleted_post(question)) or answer.question != question:
            raise Http404

        if answer.marked:
            return HttpResponsePermanentRedirect(question.get_absolute_url())

        return answer_redirect(request, answer)

    if settings.FORCE_SINGLE_URL and (slug != slugify(question.title)):
        return HttpResponsePermanentRedirect(question.get_absolute_url())

    if request.POST:
        answer_form = AnswerForm(request.POST, user=request.user)
    else:
        answer_form = AnswerForm(user=request.user)

    answers = request.user.get_visible_answers(question)

    update_question_view_times(request, question)

    if request.user.is_authenticated():
        try:
            subscription = QuestionSubscription.objects.get(question=question, user=request.user)
        except:
            subscription = False
    else:
        subscription = False

    return pagination.paginated(request, ('answers', AnswerPaginatorContext()), {
    "question" : question,
    "answer" : answer_form,
    "answers" : answers,
    "similar_questions" : question.get_related_questions(),
    "subscription": subscription,
    })


REVISION_TEMPLATE = template.loader.get_template('node/revision.html')

def revisions(request, id):
    post = get_object_or_404(Node, id=id).leaf
    revisions = list(post.revisions.order_by('revised_at'))
    rev_ctx = []

    for i, revision in enumerate(revisions):
        rev_ctx.append(dict(inst=revision, html=template.loader.get_template('node/revision.html').render(template.Context({
        'title': revision.title,
        'html': revision.html,
        'tags': revision.tagname_list(),
        }))))

        if i > 0:
            rev_ctx[i]['diff'] = mark_safe(htmldiff(rev_ctx[i-1]['html'], rev_ctx[i]['html']))
        else:
            rev_ctx[i]['diff'] = mark_safe(rev_ctx[i]['html'])

        if not (revision.summary):
            rev_ctx[i]['summary'] = _('Revision n. %(rev_number)d') % {'rev_number': revision.revision}
        else:
            rev_ctx[i]['summary'] = revision.summary

    rev_ctx.reverse()

    return render_to_response('revisions.html', {
    'post': post,
    'revisions': rev_ctx,
    }, context_instance=RequestContext(request))



