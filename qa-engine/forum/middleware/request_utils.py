from forum.settings import MAINTAINANCE_MODE, APP_LOGO, APP_TITLE

from forum.http_responses import HttpResponseServiceUnavailable

class RequestUtils(object):
    def process_request(self, request):
        if MAINTAINANCE_MODE.value is not None and isinstance(MAINTAINANCE_MODE.value.get('allow_ips', None), list):
            ip = request.META['REMOTE_ADDR']

            if not ip in MAINTAINANCE_MODE.value['allow_ips']:
                return HttpResponseServiceUnavailable(MAINTAINANCE_MODE.value.get('message', ''))

        if request.session.get('redirect_POST_data', None):
            request.POST = request.session.pop('redirect_POST_data')
            request.META['REQUEST_METHOD'] = "POST"

        self.request = request
        return None