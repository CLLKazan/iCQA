import os
from itertools import groupby
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.views.static import serve
from forum import settings
from forum.modules import decorate
from forum.views.decorators import login_required
from forum.forms import FeedbackForm
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.db.models import Count
from forum.forms import get_next_url
from forum.models import Badge, Award, User, Page
from forum.badges.base import BadgesMeta
from forum.http_responses import HttpResponseNotFound, HttpResponseIntServerError
from forum import settings
from forum.utils.mail import send_template_email
from django.utils.safestring import mark_safe
from forum.templatetags.extra_filters import or_preview
import decorators
import re, sys, logging, traceback

def favicon(request):
    return HttpResponseRedirect(str(settings.APP_FAVICON))

def custom_css(request):
    return HttpResponse(or_preview(settings.CUSTOM_CSS, request), mimetype="text/css")

def static(request, title, content):
    return render_to_response('static.html', {'content' : content, 'title': title},
                              context_instance=RequestContext(request))

def media(request, skin, path):
    response = serve(request, "%s/media/%s" % (skin, path),
                 document_root=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'skins').replace('\\', '/'))
    content_type = response['Content-Type']
    if ('charset=' not in content_type):
        if (content_type.startswith('text') or content_type=='application/x-javascript'):
            content_type += '; charset=utf-8'
            response['Content-Type'] = content_type
    return response


def markdown_help(request):
    return render_to_response('markdown_help.html', context_instance=RequestContext(request))


def opensearch(request):
    return render_to_response('opensearch.html', {'settings' : settings}, context_instance=RequestContext(request))


def feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.user, data=request.POST)
        if form.is_valid():
            context = {
                 'user': request.user,
                 'email': request.user.is_authenticated() and request.user.email or form.cleaned_data.get('email', None),
                 'message': form.cleaned_data['message'],
                 'name': request.user.is_authenticated() and request.user.username or form.cleaned_data.get('name', None),
                 'ip': request.META['REMOTE_ADDR'],
            }

            recipients = User.objects.filter(is_superuser=True)
            send_template_email(recipients, "notifications/feedback.html", context)

            msg = _('Thanks for the feedback!')
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect(get_next_url(request))
    else:
        form = FeedbackForm(request.user, initial={'next':get_next_url(request)})

    return render_to_response('feedback.html', {'form': form}, context_instance=RequestContext(request))

feedback.CANCEL_MESSAGE=_('We look forward to hearing your feedback! Please, give it next time :)')

def privacy(request):
    return render_to_response('privacy.html', context_instance=RequestContext(request))

@decorate.withfn(login_required)
def logout(request):
    return render_to_response('logout.html', {
    'next' : get_next_url(request),
    }, context_instance=RequestContext(request))

@decorators.render('badges.html', 'badges', _('badges'), weight=300)
def badges(request):
    badges = [b.ondb for b in sorted(BadgesMeta.by_id.values(), lambda b1, b2: cmp(b1.name, b2.name))]

    if request.user.is_authenticated():
        my_badges = Award.objects.filter(user=request.user).values('badge_id').distinct()
    else:
        my_badges = []

    return {
        'badges' : badges,
        'mybadges' : my_badges,
    }

def badge(request, id, slug):
    badge = Badge.objects.get(id=id)
    awards = list(Award.objects.filter(badge=badge).order_by('user', 'awarded_at'))
    award_count = len(awards)

    awards = sorted([dict(count=len(list(g)), user=k) for k, g in groupby(awards, lambda a: a.user)],
                    lambda c1, c2: c2['count'] - c1['count'])

    return render_to_response('badge.html', {
    'award_count': award_count,
    'awards' : awards,
    'badge' : badge,
    }, context_instance=RequestContext(request))

def page(request):
    path = request.path[1:]

    if path in settings.STATIC_PAGE_REGISTRY:
        try:
            page = Page.objects.get(id=settings.STATIC_PAGE_REGISTRY[path])

            if (not page.published) and (not request.user.is_superuser):
                return HttpResponseNotFound(request)
        except:
            return HttpResponseNotFound(request)
    else:
        return HttpResponseNotFound(request)

    template = page.extra.get('template', 'default')
    sidebar = page.extra.get('sidebar', '')

    if template == 'default':
        base = 'base_content.html'
    elif template == 'sidebar':
        base = 'base.html'

        sidebar_render = page.extra.get('render', 'markdown')

        if sidebar_render == 'markdown':
            sidebar = page._as_markdown(sidebar)
        elif sidebar_render == 'html':
            sidebar = mark_safe(sidebar)

    else:
        return HttpResponse(page.body, mimetype=page.extra.get('mimetype', 'text/html'))

    render = page.extra.get('render', 'markdown')

    if render == 'markdown':
        body = page.as_markdown()
    elif render == 'html':
        body = mark_safe(page.body)
    else:
        body = page.body

    return render_to_response('page.html', {
    'page' : page,
    'body' : body,
    'sidebar': sidebar,
    'base': base,
    }, context_instance=RequestContext(request))


def error_handler(request):

    stacktrace = "".join(["\t\t%s\n" % l for l in traceback.format_exc().split("\n")])

    try:
        log_msg = """
        error executing request:
        PATH: %(path)s
        USER: %(user)s
        METHOD: %(method)s
        POST PARAMETERS:
        %(post)s
        GET PARAMETERS:
        %(get)s
        HTTP HEADERS:
        %(headers)s
        COOKIES:
        %(cookies)s
        EXCEPTION INFO:
        %(stacktrace)s
        """ % {
            'path': request.path,
            'user': request.user.is_authenticated() and ("%s (%s)" % (request.user.username, request.user.id)) or "<anonymous>",
            'method': request.method,
            'post': request.POST and "".join(["\t\t%s: %s\n" % (k, v) for k, v in request.POST.items()]) or "None",
            'get': request.GET and "".join(["\t\t%s: %s\n" % (k, v) for k, v in request.GET.items()]) or "None",
            'cookies': request.COOKIES and "".join(["\t\t%s: %s\n" % (k, v) for k, v in request.COOKIES.items()]) or "None",
            'headers': request.META and "".join(["\t\t%s: %s\n" % (k, v) for k, v in request.META.items()]) or "None",
            'stacktrace': stacktrace
        }
    except:
        log_msg = "error executing request:\n%s" % stacktrace


    logging.error(log_msg)
    return HttpResponseIntServerError(request)
