import urllib
import urllib2
import httplib
import time

from forum.authentication.base import AuthenticationConsumer, InvalidAuthentication
from django.utils.translation import ugettext as _

from lib import oauth

class OAuthAbstractAuthConsumer(AuthenticationConsumer):

    def __init__(self, consumer_key, consumer_secret, server_url, request_token_url, access_token_url, authorization_url):
        self.consumer_secret = consumer_secret
        self.consumer_key = consumer_key

        self.consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

        self.server_url = server_url
        self.request_token_url = request_token_url
        self.access_token_url = access_token_url
        self.authorization_url = authorization_url

    def prepare_authentication_request(self, request, redirect_to):
        request_token = self.fetch_request_token()
        request.session['unauthed_token'] = request_token.to_string()
        return self.authorize_token_url(request_token)

    def process_authentication_request(self, request):
        unauthed_token = request.session.get('unauthed_token', None)
        if not unauthed_token:
             raise InvalidAuthentication(_('Error, the oauth token is not on the server'))

        token = oauth.OAuthToken.from_string(unauthed_token)

        if token.key != request.GET.get('oauth_token', 'no-token'):
            raise InvalidAuthentication(_("Something went wrong! Auth tokens do not match"))

        access_token = self.fetch_access_token(token)

        return access_token.to_string()

    def get_user_data(self, key):
        #token = oauth.OAuthToken.from_string(access_token)
        return {}
        
    def fetch_request_token(self):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, http_url=self.request_token_url)
        oauth_request.sign_request(self.signature_method, self.consumer, None)
        params = oauth_request.parameters
        data = urllib.urlencode(params)
        full_url='%s?%s'%(self.request_token_url, data)
        response = urllib2.urlopen(full_url)
        return oauth.OAuthToken.from_string(response.read())

    def authorize_token_url(self, token, callback_url=None):
        oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token,\
                        callback=callback_url, http_url=self.authorization_url)
        params = oauth_request.parameters
        data = urllib.urlencode(params)
        full_url='%s?%s'%(self.authorization_url, data)
        return full_url

    def fetch_access_token(self, token):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=token, http_url=self.access_token_url)
        oauth_request.sign_request(self.signature_method, self.consumer, token)
        params = oauth_request.parameters
        data = urllib.urlencode(params)
        full_url='%s?%s'%(self.access_token_url, data)
        response = urllib2.urlopen(full_url)
        return oauth.OAuthToken.from_string(response.read())

    def fetch_data(self, token, http_url, parameters=None):
        access_token = oauth.OAuthToken.from_string(token)
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, token=access_token, http_method="GET",
            http_url=http_url, parameters=parameters,
        )
        oauth_request.sign_request(self.signature_method, self.consumer, access_token)

        url = oauth_request.to_url()
        connection = httplib.HTTPSConnection(self.server_url)
        connection.request(oauth_request.http_method, url)

        return connection.getresponse().read()

