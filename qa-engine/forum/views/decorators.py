from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import simplejson
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.utils.translation import ungettext, ugettext as _
from forum.modules import ui, decorate
from datetime import datetime, date
from forum.settings import ONLINE_USERS
import logging

def login_required(func, request, *args, **kwargs):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('auth_signin'))
    else:
        return func(request, *args, **kwargs)

def render(template=None, tab=None, tab_title='', weight=500, tabbed=True):
    def decorator(func):        
        def decorated(context, request, *args, **kwargs):
            if request.user.is_authenticated():
                ONLINE_USERS[request.user] = datetime.now()

            if isinstance(context, HttpResponse):
                return context

            if tab is not None:
                context['tab'] = tab

            return render_to_response(context.pop('template', template), context,
                                      context_instance=RequestContext(request))

        if tabbed and tab and tab_title:
            ui.register(ui.PAGE_TOP_TABS,
                        ui.PageTab(tab, tab_title, lambda: reverse(func.__name__), weight=weight))
            
        return decorate.result.withfn(decorated, needs_params=True)(func)

    return decorator

class CommandException(Exception):
    pass

class RefreshPageCommand(HttpResponse):
    def __init__(self):
        super(RefreshPageCommand, self).__init__(
                content=simplejson.dumps({'commands': {'refresh_page': []}, 'success': True}),
                mimetype="application/json")

def command(func, request, *args, **kwargs):
    try:
        response = func(request, *args, **kwargs)

        if isinstance(response, HttpResponse):
            return response

        response['success'] = True
    except Exception, e:
        import traceback
        #traceback.print_exc()

        if isinstance(e, CommandException):
            response = {
            'success': False,
            'error_message': e.message
            }
        else:
            logging.error("%s: %s" % (func.__name__, str(e)))
            logging.error(traceback.format_exc())
            response = {
            'success': False,
            'error_message': _("We're sorry, but an unknown error ocurred.<br />Please try again in a while.")
            }

    if request.is_ajax():
        return HttpResponse(simplejson.dumps(response), mimetype="application/json")
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

