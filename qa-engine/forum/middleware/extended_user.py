from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth import logout
from forum.models.user import AnonymousUser
from forum.views.auth import forward_suspended_user
import logging

class ExtendedUser(AuthenticationMiddleware):
    def process_request(self, request):
        super(ExtendedUser, self).process_request(request)
        if request.user.is_authenticated():
            try:
                request.user = request.user.user

                if request.user.is_suspended():
                    user = request.user
                    logout(request)
                    return forward_suspended_user(request, user)

                return None
            except Exception, e:
                import traceback
                logging.error("Unable to convert auth_user %s to forum_user: \n%s" % (
                    request.user.id, traceback.format_exc()
                ))

        request.user = AnonymousUser()
        return None