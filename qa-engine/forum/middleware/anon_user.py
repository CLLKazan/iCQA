from django.http import HttpResponseRedirect
from forum.forms import get_next_url
from django.utils.translation import ugettext as _
from forum.user_messages import create_message, get_and_delete_messages
from forum import settings
from django.core.urlresolvers import reverse
import logging

class AnonymousMessageManager(object):
    def __init__(self,request):
        self.request = request
    def create(self,message=''):
        create_message(self.request,message)  
    def get_and_delete(self):
        messages = get_and_delete_messages(self.request)
        return messages

def dummy_deepcopy(*arg):
    """this is necessary to prevent deepcopy() on anonymous user object
    that now contains reference to request, which cannot be deepcopied
    """
    return None

class ConnectToSessionMessagesMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
            request.user.__deepcopy__ = dummy_deepcopy #plug on deepcopy which may be called by django db "driver"
            request.user.message_set = AnonymousMessageManager(request) #here request is linked to anon user
            request.user.get_and_delete_messages = request.user.message_set.get_and_delete

            #also set the first greeting one time per session only
            if 'greeting_set' not in request.session:
                request.session['greeting_set'] = True
                msg = _('First time here? Check out the <a href="%s">FAQ</a>!') % reverse('faq')
                request.user.message_set.create(message=msg)
