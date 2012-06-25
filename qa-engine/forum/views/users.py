from forum.models import User
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from forum.http_responses import HttpResponseUnauthorized
from django.utils.translation import ugettext as _
from django.utils.http import urlquote_plus
from django.utils.html import strip_tags
from django.utils import simplejson
from django.core.urlresolvers import reverse, NoReverseMatch
from forum.forms import *
from forum.utils.html import sanitize_html
from forum.modules import decorate, ReturnImediatelyException
from datetime import datetime, date
from forum.actions import EditProfileAction, FavoriteAction, BonusRepAction, SuspendAction
from forum.modules import ui
from forum.utils import pagination
from forum.views.readers import QuestionListPaginatorContext, AnswerPaginatorContext
from forum.settings import ONLINE_USERS
 
import bisect
import time
import datetime
import decorators
import unicodedata

class UserReputationSort(pagination.SimpleSort):
    def apply(self, objects):
        return objects.order_by('-is_active', self.order_by)

class UserListPaginatorContext(pagination.PaginatorContext):
    def __init__(self):
        super (UserListPaginatorContext, self).__init__('USERS_LIST', sort_methods=(
            (_('reputation'), UserReputationSort(_('reputation'), '-reputation', _("sorted by reputation"))),
            (_('newest'), pagination.SimpleSort(_('recent'), '-date_joined', _("newest members"))),
            (_('last'), pagination.SimpleSort(_('oldest'), 'date_joined', _("oldest members"))),
            (_('name'), pagination.SimpleSort(_('by username'), 'username', _("sorted by username"))),
        ), pagesizes=(20, 35, 60))

class SubscriptionListPaginatorContext(pagination.PaginatorContext):
    def __init__(self):
        super (SubscriptionListPaginatorContext, self).__init__('SUBSCRIPTION_LIST', pagesizes=(5, 10, 20), default_pagesize=20)

class UserAnswersPaginatorContext(pagination.PaginatorContext):
    def __init__(self):
        super (UserAnswersPaginatorContext, self).__init__('USER_ANSWER_LIST', sort_methods=(
            (_('oldest'), pagination.SimpleSort(_('oldest answers'), 'added_at', _("oldest answers will be shown first"))),
            (_('newest'), pagination.SimpleSort(_('newest answers'), '-added_at', _("newest answers will be shown first"))),
            (_('votes'), pagination.SimpleSort(_('popular answers'), '-score', _("most voted answers will be shown first"))),
        ), default_sort=_('votes'), pagesizes=(5, 10, 20), default_pagesize=20, prefix=_('answers'))

USERS_PAGE_SIZE = 35# refactor - move to some constants file

@decorators.render('users/users.html', 'users', _('users'), weight=200)
def users(request):
    suser = request.REQUEST.get('q', "")
    users = User.objects.all()

    if suser != "":
        users = users.filter(username__icontains=suser)

    return pagination.paginated(request, ('users', UserListPaginatorContext()), {
        "users" : users,
        "suser" : suser,
    })


@decorators.render('users/online_users.html', 'online_users', _('Online Users'), weight=200, tabbed=False)
def online_users(request):
    suser = request.REQUEST.get('q', "")

    sort = ""
    if request.GET.get("sort", None):
        try:
            sort = int(request.GET["sort"])
        except ValueError:
            logging.error('Found invalid sort "%s", loading %s, refered by %s' % (
                request.GET.get("sort", ''), request.path, request.META.get('HTTP_REFERER', 'UNKNOWN')
            ))
            raise Http404()

    page = 0
    if request.GET.get("page", None):
        try:
            page = int(request.GET["page"])
        except ValueError:
            logging.error('Found invalid page "%s", loading %s, refered by %s' % (
                request.GET.get("page", ''), request.path, request.META.get('HTTP_REFERER', 'UNKNOWN')
            ))
            raise Http404()

    pagesize = 10
    if request.GET.get("pagesize", None):
        try:
            pagesize = int(request.GET["pagesize"])
        except ValueError:
            logging.error('Found invalid pagesize "%s", loading %s, refered by %s' % (
                request.GET.get("pagesize", ''), request.path, request.META.get('HTTP_REFERER', 'UNKNOWN')
            ))
            raise Http404()


    users = None
    if sort == "reputation":
        users = sorted(ONLINE_USERS.sets.keys(), key=lambda user: user.reputation)
    elif sort == "newest" :
        users = sorted(ONLINE_USERS.sets.keys(), key=lambda user: user.newest)
    elif sort == "last":
        users = sorted(ONLINE_USERS.sets.keys(), key=lambda user: user.last)
    elif sort == "name":
        users = sorted(ONLINE_USERS.sets.keys(), key=lambda user: user.name)
    elif sort == "oldest":
        users = sorted(ONLINE_USERS.sets.keys(), key=lambda user: user.oldest)
    elif sort == "newest":
        users = sorted(ONLINE_USERS.sets.keys(), key=lambda user: user.newest)
    elif sort == "votes":
        users = sorted(ONLINE_USERS.sets.keys(), key=lambda user: user.votes)
    else:
        users = sorted(ONLINE_USERS.iteritems(), key=lambda x: x[1])

    return render_to_response('users/online_users.html', {
        "users" : users,
        "suser" : suser,
        "sort" : sort,
        "page" : page,
        "pageSize" : pagesize,
    })


def edit_user(request, id):
    user = get_object_or_404(User, id=id)
    if not (request.user.is_superuser or request.user == user):
        return HttpResponseUnauthorized(request)
    if request.method == "POST":
        form = EditUserForm(user, request.POST)
        if form.is_valid():
            new_email = sanitize_html(form.cleaned_data['email'])

            if new_email != user.email:
                user.email = new_email
                user.email_isvalid = False

                try:
                    hash = ValidationHash.objects.get(user=request.user, type='email')
                    hash.delete()
                except:
                    pass

            if settings.EDITABLE_SCREEN_NAME:
                user.username = sanitize_html(form.cleaned_data['username'])
            user.real_name = sanitize_html(form.cleaned_data['realname'])
            user.website = sanitize_html(form.cleaned_data['website'])
            user.location = sanitize_html(form.cleaned_data['city'])
            user.date_of_birth = form.cleaned_data['birthday']
            if user.date_of_birth == "None":
                user.date_of_birth = datetime(1900, 1, 1, 0, 0)
            user.about = sanitize_html(form.cleaned_data['about'])

            user.save()
            EditProfileAction(user=user, ip=request.META['REMOTE_ADDR']).save()

            request.user.message_set.create(message=_("Profile updated."))
            return HttpResponseRedirect(user.get_profile_url())
    else:
        form = EditUserForm(user)
    return render_to_response('users/edit.html', {
    'user': user,
    'form' : form,
    'gravatar_faq_url' : reverse('faq') + '#gravatar',
    }, context_instance=RequestContext(request))


@decorate.withfn(decorators.command)
def user_powers(request, id, action, status):
    if not request.user.is_superuser:
        raise decorators.CommandException(_("Only superusers are allowed to alter other users permissions."))

    if (action == 'remove' and 'status' == 'super') and not request.user.is_siteowner():
        raise decorators.CommandException(_("Only the site owner can remove the super user status from other user."))

    user = get_object_or_404(User, id=id)
    new_state = action == 'grant'

    if status == 'super':
        user.is_superuser = new_state
    elif status == 'staff':
        user.is_staff = new_state
    else:
        raise Http404()

    user.save()
    return decorators.RefreshPageCommand()


@decorate.withfn(decorators.command)
def award_points(request, id):
    if not request.POST:
        return render_to_response('users/karma_bonus.html')

    if not request.user.is_superuser:
        raise decorators.CommandException(_("Only superusers are allowed to award reputation points"))

    try:
        points = int(request.POST['points'])
    except:
        raise decorators.CommandException(_("Invalid number of points to award."))

    user = get_object_or_404(User, id=id)

    extra = dict(message=request.POST.get('message', ''), awarding_user=request.user.id, value=points)

    BonusRepAction(user=request.user, extra=extra).save(data=dict(value=points, affected=user))

    return {'commands': {
            'update_profile_karma': [user.reputation]
        }}
    

@decorate.withfn(decorators.command)
def suspend(request, id):
    user = get_object_or_404(User, id=id)

    if not request.user.is_superuser:
        raise decorators.CommandException(_("Only superusers can suspend other users"))

    if not request.POST.get('bantype', None):
        if user.is_suspended():
            suspension = user.suspension
            suspension.cancel(user=request.user, ip=request.META['REMOTE_ADDR'])
            return decorators.RefreshPageCommand()
        else:
            return render_to_response('users/suspend_user.html')

    data = {
        'bantype': request.POST.get('bantype', 'indefinetly').strip(),
        'publicmsg': request.POST.get('publicmsg', _('Bad behaviour')),
        'privatemsg': request.POST.get('privatemsg', None) or request.POST.get('publicmsg', ''),
        'suspended': user
    }

    if data['bantype'] == 'forxdays':
        try:
            data['forxdays'] = int(request.POST['forxdays'])
        except:
            raise decorators.CommandException(_('Invalid numeric argument for the number of days.'))

    SuspendAction(user=request.user, ip=request.META['REMOTE_ADDR']).save(data=data)

    return decorators.RefreshPageCommand()


def user_view(template, tab_name, tab_title, tab_description, private=False, tabbed=True, render_to=None, weight=500):
    def decorator(fn):
        def params(request, id, slug=None):
            user = get_object_or_404(User, id=id)
            if private and not (user == request.user or request.user.is_superuser):
                raise ReturnImediatelyException(HttpResponseUnauthorized(request))

            if render_to and (not render_to(user)):
                raise ReturnImediatelyException(HttpResponseRedirect(user.get_profile_url()))

            return [request, user], {}

        decorated = decorate.params.withfn(params)(fn)

        def result(context, request, user):
            rev_page_title = user.username + " - " + tab_description

            context.update({
                "tab": "users",
                "active_tab" : tab_name,
                "tab_description" : tab_description,
                "page_title" : rev_page_title,
                "can_view_private": (user == request.user) or request.user.is_superuser
            })
            return render_to_response(template, context, context_instance=RequestContext(request))

        decorated = decorate.result.withfn(result, needs_params=True)(decorated)

        if tabbed:
            def url_getter(vu):
                try:
                    return reverse(fn.__name__, kwargs={'id': vu.id, 'slug': slugify(vu.username)})
                except NoReverseMatch:
                    return reverse(fn.__name__, kwargs={'id': vu.id})

            ui.register(ui.PROFILE_TABS, ui.ProfileTab(
                tab_name, tab_title, tab_description,url_getter, private, render_to, weight
            ))

        return decorated
    return decorator


@user_view('users/stats.html', 'stats', _('overview'), _('user overview'))
def user_profile(request, user):
    questions = Question.objects.filter_state(deleted=False).filter(author=user).order_by('-added_at')
    answers = Answer.objects.filter_state(deleted=False).filter(author=user).order_by('-added_at')

    up_votes = user.vote_up_count
    down_votes = user.vote_down_count
    votes_today = user.get_vote_count_today()
    votes_total = int(settings.MAX_VOTES_PER_DAY)

    user_tags = Tag.objects.filter(Q(nodes__author=user) | Q(nodes__children__author=user)) \
        .annotate(user_tag_usage_count=Count('name')).order_by('-user_tag_usage_count')

    awards = [(Badge.objects.get(id=b['id']), b['count']) for b in
              Badge.objects.filter(awards__user=user).values('id').annotate(count=Count('cls')).order_by('-count')]

    return pagination.paginated(request, (
    ('questions', QuestionListPaginatorContext('USER_QUESTION_LIST', _('questions'), 15)),
    ('answers', UserAnswersPaginatorContext())), {
    "view_user" : user,
    "questions" : questions,
    "answers" : answers,
    "up_votes" : up_votes,
    "down_votes" : down_votes,
    "total_votes": up_votes + down_votes,
    "votes_today_left": votes_total-votes_today,
    "votes_total_per_day": votes_total,
    "user_tags" : user_tags[:50],
    "awards": awards,
    "total_awards" : len(awards),
    })
    
@user_view('users/recent.html', 'recent', _('recent activity'), _('recent user activity'))
def user_recent(request, user):
    activities = user.actions.exclude(
            action_type__in=("voteup", "votedown", "voteupcomment", "flag", "newpage", "editpage")).order_by(
            '-action_date')[:USERS_PAGE_SIZE]

    return {"view_user" : user, "activities" : activities}


@user_view('users/reputation.html', 'reputation', _('reputation history'), _('graph of user karma'))
def user_reputation(request, user):
    rep = list(user.reputes.order_by('date'))
    values = [r.value for r in rep]
    redux = lambda x, y: x+y

    graph_data = simplejson.dumps([
    (time.mktime(rep[i].date.timetuple()) * 1000, reduce(redux, values[:i], 0))
    for i in range(len(values))
    ])

    rep = user.reputes.filter(action__canceled=False).order_by('-date')[0:20]

    return {"view_user": user, "reputation": rep, "graph_data": graph_data}

@user_view('users/votes.html', 'votes', _('votes'), _('user vote record'), True)
def user_votes(request, user):
    votes = user.votes.exclude(node__state_string__contains="(deleted").filter(
            node__node_type__in=("question", "answer")).order_by('-voted_at')[:USERS_PAGE_SIZE]

    return {"view_user" : user, "votes" : votes}

@user_view('users/questions.html', 'favorites', _('favorites'), _('questions that user selected as his/her favorite'))
def user_favorites(request, user):
    favorites = FavoriteAction.objects.filter(canceled=False, user=user)

    return {"favorites" : favorites, "view_user" : user}

@user_view('users/subscriptions.html', 'subscriptions', _('subscription'), _('subscriptions'), True, tabbed=False)
def user_subscriptions(request, user):
    enabled = True

    tab = request.GET.get('tab', "settings")

    if tab == 'settings':
        manage_open = False
        if request.method == 'POST':
            manage_open = False
            form = SubscriptionSettingsForm(data=request.POST, instance=user.subscription_settings)

            if form.is_valid():
                form.save()
                message = _('New subscription settings are now saved')

                user.subscription_settings.enable_notifications = enabled
                user.subscription_settings.save()

                request.user.message_set.create(message=message)
        else:
            form = SubscriptionSettingsForm(instance=user.subscription_settings)

        return {
            'view_user':user,
            'notificatons_on': enabled,
            'form':form,
            'manage_open':manage_open,
        }

    elif tab == 'manage':
        manage_open = True

        auto = request.GET.get('auto', 'True')
        if auto == 'True':
            show_auto = True
            subscriptions = QuestionSubscription.objects.filter(user=user).order_by('-last_view')
        else:
            show_auto = False
            subscriptions = QuestionSubscription.objects.filter(user=user, auto_subscription=False).order_by('-last_view')

        return pagination.paginated(request, ('subscriptions', SubscriptionListPaginatorContext()), {
            'subscriptions':subscriptions,
            'view_user':user,
            "auto":show_auto,
            'manage_open':manage_open,
        })

    # else:
        # todo: probably want to throw an error
        # error = "error to throw"







@user_view('users/preferences.html', 'preferences', _('preferences'), _('preferences'), True, tabbed=False)
def user_preferences(request, user):
    if request.POST:
        form = UserPreferencesForm(request.POST)

        if form.is_valid():
            user.prop.preferences = form.cleaned_data
            request.user.message_set.create(message=_('New preferences saved'))

    else:
        preferences = user.prop.preferences

        if preferences:
            form = UserPreferencesForm(initial=preferences)
        else:
            form = UserPreferencesForm()
            
    return {'view_user': user, 'form': form}


