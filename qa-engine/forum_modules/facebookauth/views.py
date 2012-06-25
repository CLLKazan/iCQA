from forum.models import AuthKeyUserAssociation
from django.http import HttpResponse

def user_is_registered(request):
    try:
        fb_uid = request.POST['fb_uid']
        #print fb_uid
        AuthKeyUserAssociation.objects.get(key=fb_uid)
        return HttpResponse('yes')
    except:
        return HttpResponse('no')