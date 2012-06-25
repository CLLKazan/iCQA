from consumer import OpenIdAbstractAuthConsumer
from forum.authentication.base import ConsumerTemplateContext

class GoogleAuthConsumer(OpenIdAbstractAuthConsumer):
    def get_user_url(self, request):
        return 'https://www.google.com/accounts/o8/id'

class GoogleAuthContext(ConsumerTemplateContext):
    mode = 'BIGICON'
    type = 'DIRECT'
    weight = 200
    human_name = 'Google'
    icon = '/media/images/openid/google.gif'



class YahooAuthConsumer(OpenIdAbstractAuthConsumer):
    def get_user_url(self, request):
        return 'http://yahoo.com/'

class YahooAuthContext(ConsumerTemplateContext):
    mode = 'BIGICON'
    type = 'DIRECT'
    weight = 300
    human_name = 'Yahoo'
    icon = '/media/images/openid/yahoo.gif'



class AolAuthConsumer(OpenIdAbstractAuthConsumer):
    def get_user_url(self, request):
        uname = request.POST['input_field']
        return 'http://openid.aol.com/' + uname

class AolAuthContext(ConsumerTemplateContext):
    mode = 'SMALLICON'
    type = 'SIMPLE_FORM'
    simple_form_context = {
        'your_what': 'AOL screen name'
    }
    weight = 200
    human_name = 'AOL'
    icon = '/media/images/openid/aol.png'


class MyOpenIdAuthConsumer(OpenIdAbstractAuthConsumer):
    dataype2ax_schema = {
        #'username': ('http://schema.openid.net/namePerson/friendly', 'friendly'),
        'email': 'http://schema.openid.net/contact/email',
        #'web': 'http://schema.openid.net/contact/web/default',
        #'birthdate': ('http://schema.openid.net/birthDate', 'birthDate'),
    }

    def get_user_url(self, request):
        blog_name = request.POST['input_field']
        return "http://%s.myopenid.com/" % blog_name

class MyOpenIdAuthContext(ConsumerTemplateContext):
    mode = 'BIGICON'
    type = 'SIMPLE_FORM'
    simple_form_context = {
        'your_what': 'MyOpenID user name'
    }
    weight = 400
    human_name = 'MyOpenID'
    icon = '/media/images/openid/myopenid_big.png'


class FlickrAuthConsumer(OpenIdAbstractAuthConsumer):
    def get_user_url(self, request):
        blog_name = request.POST['input_field']
        return "http://flickr.com/%s/" % blog_name

class FlickrAuthContext(ConsumerTemplateContext):
    mode = 'SMALLICON'
    type = 'SIMPLE_FORM'
    simple_form_context = {
        'your_what': 'Flickr user name'
    }
    weight = 250
    human_name = 'Flickr'
    icon = '/media/images/openid/flickr.png'


class TechnoratiAuthConsumer(OpenIdAbstractAuthConsumer):
    def get_user_url(self, request):
        blog_name = request.POST['input_field']
        return "http://technorati.com/people/technorati/%s/" % blog_name

class TechnoratiAuthContext(ConsumerTemplateContext):
    mode = 'SMALLICON'
    type = 'SIMPLE_FORM'
    simple_form_context = {
        'your_what': 'Technorati user name'
    }
    weight = 260
    human_name = 'Technorati'
    icon = '/media/images/openid/technorati.png'


class WordpressAuthConsumer(OpenIdAbstractAuthConsumer):
    def get_user_url(self, request):
        blog_name = request.POST['input_field']
        return "http://%s.wordpress.com/" % blog_name

class WordpressAuthContext(ConsumerTemplateContext):
    mode = 'SMALLICON'
    type = 'SIMPLE_FORM'
    simple_form_context = {
        'your_what': 'Wordpress blog name'
    }
    weight = 270
    human_name = 'Wordpress'
    icon = '/media/images/openid/wordpress.png'


class BloggerAuthConsumer(OpenIdAbstractAuthConsumer):
    def get_user_url(self, request):
        blog_name = request.POST['input_field']
        return "http://%s.blogspot.com/" % blog_name

class BloggerAuthContext(ConsumerTemplateContext):
    mode = 'SMALLICON'
    type = 'SIMPLE_FORM'
    simple_form_context = {
        'your_what': 'Blogger blog name'
    }
    weight = 300
    human_name = 'Blogger'
    icon = '/media/images/openid/blogger.png'


class LiveJournalAuthConsumer(OpenIdAbstractAuthConsumer):
    def get_user_url(self, request):
        blog_name = request.POST['input_field']
        return "http://%s.livejournal.com/" % blog_name

class LiveJournalAuthContext(ConsumerTemplateContext):
    mode = 'SMALLICON'
    type = 'SIMPLE_FORM'
    simple_form_context = {
        'your_what': 'LiveJournal blog name'
    }
    weight = 310
    human_name = 'LiveJournal'
    icon = '/media/images/openid/livejournal.png'


class ClaimIdAuthConsumer(OpenIdAbstractAuthConsumer):
    def get_user_url(self, request):
        blog_name = request.POST['input_field']
        return "http://claimid.com/%s" % blog_name

class ClaimIdAuthContext(ConsumerTemplateContext):
    mode = 'SMALLICON'
    type = 'SIMPLE_FORM'
    simple_form_context = {
        'your_what': 'ClaimID user name'
    }
    weight = 320
    human_name = 'ClaimID'
    icon = '/media/images/openid/claimid.png'

class VerisignAuthConsumer(OpenIdAbstractAuthConsumer):
    def get_user_url(self, request):
        blog_name = request.POST['input_field']
        return "http://%s.pip.verisignlabs.com/" % blog_name

class VerisignAuthContext(ConsumerTemplateContext):
    mode = 'SMALLICON'
    type = 'SIMPLE_FORM'
    simple_form_context = {
        'your_what': 'Verisign user name'
    }
    weight = 340
    human_name = 'Verisign'
    icon = '/media/images/openid/verisign.png'

    
class OpenIdUrlAuthConsumer(OpenIdAbstractAuthConsumer):
    pass

class OpenIdUrlAuthContext(ConsumerTemplateContext):
    mode = 'STACK_ITEM'
    weight = 300
    human_name = 'OpenId url'
    stack_item_template = 'modules/openidauth/openidurl.html'
    icon = '/media/images/openid/openid-inputicon.gif'
