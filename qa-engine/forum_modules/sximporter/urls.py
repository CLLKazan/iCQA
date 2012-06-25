from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext as _

from views import sximporter

urlpatterns = patterns('',
    url(r'^%s%s$' % (_('admin/'), _('sximporter/')),  sximporter, name='sximporter'),
)