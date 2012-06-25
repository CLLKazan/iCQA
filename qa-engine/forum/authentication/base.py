
class AuthenticationConsumer(object):

    def prepare_authentication_request(self, request, redirect_to):
        raise NotImplementedError()

    def process_authentication_request(self, response):
        raise NotImplementedError()

    def get_user_data(self, key):
        raise NotImplementedError()


class ConsumerTemplateContext(object):
    """
        Class that provides information about a certain authentication provider context in the signin page.

        class attributes:

        mode - one of BIGICON, SMALLICON, FORM

        human_name - the human readable name of the provider

        extra_js - some providers require us to load extra javascript on the signin page for them to work,
        this is the place to add those files in the form of a list

        extra_css - same as extra_js but for css files
    """
    mode = ''
    weight = 500
    human_name = ''
    extra_js = []
    extra_css = []
    show_to_logged_in_user = True

    @classmethod
    def readable_key(cls, key):
        return key.key

class InvalidAuthentication(Exception):
    def __init__(self, message):
        self.message = message
        
    