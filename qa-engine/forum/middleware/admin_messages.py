from forum.user_messages import create_message
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

from forum.settings import EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, \
        APP_URL

class AdminMessagesMiddleware(object):
    def process_request(self, request):
        # Check if the email settings are configured
        self.check_email_settings(request)

        # Check if the APP_URL setting is configured
        self.check_app_url(request)

    def check_email_settings(self, request):
        # We want to warn only the administrators that the email settings are not configured.
        # So, first of all we check if we're dealing with the administrators and after that if
        # the SMTP settings are configured at all. We suppose that the SMTP settings are not configured
        # if the EMAIL_HOST, the EMAIL_HOST_USER and the EMAIL_HOST_PASSWORD are not set at all.
        if request.user.is_authenticated and request.user.is_staff and request.user.is_superuser and \
            EMAIL_HOST == '' and EMAIL_HOST_USER == '' and EMAIL_HOST_PASSWORD == '':

            msg = _("""
                    The e-mail settings of this community are not configured yet. We strongly recommend you to
                    do that from the <a href="%(email_settings_url)s">e-mail settings page</a> as soon as possible.
                    """ % dict(email_settings_url=reverse('admin_set', kwargs={'set_name':'email'})))

            # We do not want to repeat ourselves. If the message already exists in the message list, we're not going to
            # add it. That's why first of all we're going the check if it is there.
            try:
                # If the message doesn't exist in the RelatedManager ObjectsDoesNotExist is going to be raised.
                request.user.message_set.all().get(message=msg)
            except ObjectDoesNotExist:
                # Let's create the message.
                request.user.message_set.create(message=msg)
            except:
                pass

    def check_app_url(self, request):
        # We consider the APP_URL setting not configured if it contains only the protocol
        # name or if it's shorter than 7 characters.
        if request.user.is_authenticated and request.user.is_staff and request.user.is_superuser and \
            APP_URL == 'http://' or APP_URL == 'https://' or len(APP_URL) < 7:

            msg = _("""
                       Please, configure your APP_URL setting from the local settings file.
                    """)

            # We do not want to repeat ourselves. If the message already exists in the message list, we're not going to
            # add it. That's why first of all we're going the check if it is there.
            try:
                # If the message doesn't exist in the RelatedManager ObjectsDoesNotExist is going to be raised.
                request.user.message_set.all().get(message=msg)
            except ObjectDoesNotExist:
                # Let's create the message.
                request.user.message_set.create(message=msg)
            except:
                pass
