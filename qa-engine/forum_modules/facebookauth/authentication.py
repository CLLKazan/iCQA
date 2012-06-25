import hashlib
from time import time
from datetime import datetime
from urllib import urlopen,  urlencode
from forum.authentication.base import AuthenticationConsumer, ConsumerTemplateContext, InvalidAuthentication
from django.utils.translation import ugettext as _

import settings

try:
    from json import load as load_json
except:
    from django.utils.simplejson import JSONDecoder

    def load_json(json):
        decoder = JSONDecoder()
        return decoder.decode(json.read())

REST_SERVER = 'http://api.facebook.com/restserver.php'

class FacebookAuthConsumer(AuthenticationConsumer):
    
    def process_authentication_request(self, request):
        API_KEY = str(settings.FB_API_KEY)

        if API_KEY in request.COOKIES:
            if self.check_cookies_signature(request.COOKIES):
                if self.check_session_expiry(request.COOKIES):
                    return request.COOKIES[API_KEY + '_user']
                else:
                    raise InvalidAuthentication(_('Sorry, your Facebook session has expired, please try again'))
            else:
                raise InvalidAuthentication(_('The authentication with Facebook connect failed due to an invalid signature'))
        else:
            raise InvalidAuthentication(_('The authentication with Facebook connect failed, cannot find authentication tokens'))

    def generate_signature(self, values):
        keys = []

        for key in sorted(values.keys()):
            keys.append(key)

        signature = ''.join(['%s=%s' % (key,  values[key]) for key in keys]) + str(settings.FB_APP_SECRET)
        return hashlib.md5(signature).hexdigest()

    def check_session_expiry(self, cookies):
        return datetime.fromtimestamp(float(cookies[settings.FB_API_KEY+'_expires'])) > datetime.now()

    def check_cookies_signature(self, cookies):
        API_KEY = str(settings.FB_API_KEY)

        values = {}

        for key in cookies.keys():
            if (key.startswith(API_KEY + '_')):
                values[key.replace(API_KEY + '_',  '')] = cookies[key]

        return self.generate_signature(values) == cookies[API_KEY]

    def get_user_data(self, key):
        request_data = {
            'method': 'Users.getInfo',
            'api_key': settings.FB_API_KEY,
            'call_id': time(),
            'v': '1.0',
            'uids': key,
            'fields': 'name,first_name,last_name,email',
            'format': 'json',
        }

        request_data['sig'] = self.generate_signature(request_data)
        fb_response = load_json(urlopen(REST_SERVER, urlencode(request_data)))[0]

        return {
            'username': fb_response['first_name'] + ' ' + fb_response['last_name'],
            'email': fb_response['email']
        }

class FacebookAuthContext(ConsumerTemplateContext):
    mode = 'BIGICON'
    type = 'CUSTOM'
    weight = 100
    human_name = 'Facebook'
    code_template = 'modules/facebookauth/button.html'
    extra_css = ["http://www.facebook.com/css/connect/connect_button.css"]

    API_KEY = settings.FB_API_KEY