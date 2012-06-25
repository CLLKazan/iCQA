from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.utils import simplejson

def ajax_login_required(view_func):
    def wrap(request,*args,**kwargs):
        if request.user.is_authenticated():
            return view_func(request,*args,**kwargs)
        else:
            json = simplejson.dumps({'login_required':True})
            return HttpResponseForbidden(json,mimetype='application/json')
    return wrap

def ajax_method(view_func):
    def wrap(request,*args,**kwargs):
        if not request.is_ajax():
            raise Http404
        retval = view_func(request,*args,**kwargs)
        if isinstance(retval, HttpResponse):
            retval.mimetype = 'application/json'
            return retval
        else:
            json = simplejson.dumps(retval)
            return HttpResponse(json,mimetype='application/json')
    return wrap
            
