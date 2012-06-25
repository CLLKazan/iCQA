from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from views import user_is_registered

urlpatterns = patterns('',
    url(r'^xd_receiver.htm$',  direct_to_template,  {'template': 'modules/facebookauth/xd_receiver.html'}, name='xd_receiver'),
    url(r'^facebook/user_is_registered/', user_is_registered, name="facebook_user_is_registered"),
)