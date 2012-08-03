from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext as _

from views import state, running, download

urlpatterns = patterns('',
    url(r'^%s%s%s$' % (_('admin/'), _('exporter/'), _('state/')),  state, name='exporter_state'),
    url(r'^%s(?P<mode>\w+)/%s$' % (_('admin/'), _('running/')),  running, name='exporter_running'),
    url(r'^%s%s%s$' % (_('admin/'), _('exporter/'), _('download/')),  download, name='exporter_download'),
)
