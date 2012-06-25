from django.shortcuts import render_to_response
from django.template import RequestContext
from forum.http_responses import HttpResponseUnauthorized
from forum.models import User
import importer
from zipfile import ZipFile
import os

def sximporter(request):
    if (not User.objects.exists()) or (request.user.is_authenticated() and request.user.is_superuser):
        list = []
        if request.method == "POST" and "dump" in request.FILES:
            dump = ZipFile(request.FILES['dump'])
            members = [f for f in dump.namelist() if f.endswith('.xml')]
            extract_to = os.path.join(os.path.dirname(__file__), 'tmp')

            if not os.path.exists(extract_to):
                os.makedirs(extract_to)

            for m in members:
                f = open(os.path.join(extract_to, m), 'w')
                f.write(dump.read(m))
                f.close()

            #dump.extractall(extract_to, members)
            dump.close()

            options = dict([(k, v) for k, v in request.POST.items()])
            options['authenticated_user'] = (request.user.is_authenticated() and (request.user,) or (None,))[0]

            importer.sximport(extract_to, options)

        return render_to_response('modules/sximporter/page.html', {
        'names': list
        }, context_instance=RequestContext(request))
    else:
        return HttpResponseUnauthorized(request)

