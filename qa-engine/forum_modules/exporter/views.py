import os, tarfile, ConfigParser, datetime

from StringIO import StringIO
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.core.cache import cache
from django.core.urlresolvers import reverse
from forum.views.admin import admin_tools_page, admin_page
from forum.models import User
from forms import ExporterForm
from threading import Thread
import settings as selsettings
from forum import settings

from exporter import export, CACHE_KEY, EXPORT_STEPS, DATE_AND_AUTHOR_INF_SECTION, DATETIME_FORMAT
from importer import start_import


@admin_tools_page(_('exporter'), _('XML data export'))
def exporter(request):
    state = cache.get(CACHE_KEY)

    if state and state['running']:
        return HttpResponseRedirect(reverse('exporter_running', kwargs=dict(mode='exporter')))

    if request.method == 'POST':
        form = ExporterForm(request.POST)

        if form.is_valid():
            thread = Thread(target=export, args=[form.cleaned_data, request.user])
            thread.setDaemon(True)
            thread.start()

            return HttpResponseRedirect(reverse('exporter_running', kwargs=dict(mode='exporter')))
    else:
        form = ExporterForm()

    available = []

    folder = unicode(selsettings.EXPORTER_BACKUP_STORAGE)

    for f in os.listdir(folder):
        if (not os.path.isdir(os.path.join(folder, f))) and f.endswith('.backup.inf'):
            try:
                with open(os.path.join(folder, f), 'r') as inffile:
                    inf = ConfigParser.SafeConfigParser()
                    inf.readfp(inffile)

                    if inf.get(DATE_AND_AUTHOR_INF_SECTION, 'site') == settings.APP_URL and os.path.exists(
                                    os.path.join(folder, inf.get(DATE_AND_AUTHOR_INF_SECTION, 'file-name'))):
                        available.append({
                            'author': User.objects.get(id=inf.get(DATE_AND_AUTHOR_INF_SECTION, 'author')),
                            'date': datetime.datetime.strptime(inf.get(DATE_AND_AUTHOR_INF_SECTION, 'finished'), DATETIME_FORMAT)
                        })
            except Exception, e:
                pass

    return ('modules/exporter/exporter.html', {
        'form': form,
        'available': available,
    })

@admin_page
def running(request, mode):
    state = cache.get(CACHE_KEY)
    if state is None:
        return HttpResponseRedirect(reverse('admin_tools', args=[_('exporter')]))

    return ('modules/exporter/running.html', {
        'mode': mode,
        'steps': EXPORT_STEPS
    })

def state(request):
    return HttpResponse(simplejson.dumps(cache.get(CACHE_KEY)), mimetype="application/json")

@admin_page
def download(request):
    if request.GET and request.GET.get('file', None):
        fname = os.path.join(selsettings.EXPORTER_BACKUP_STORAGE, request.GET.get('file'))
    else:
        raise Http404

    if not os.path.exists(fname):
        raise Http404

    if fname.endswith('.gz'):
        content_type='application/x-gzip'
        filename = 'backup.tar.gz'
    else:
        content_type='application/zip'
        filename = 'backup.zip'

    response = HttpResponse(open(fname, 'rb').read(), content_type=content_type)
    response['Content-Length'] = os.path.getsize(fname)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response



