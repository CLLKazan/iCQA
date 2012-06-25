from datetime import datetime, timedelta
import os, time, csv, random

from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from forum.http_responses import HttpResponseUnauthorized
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.db import models
from forum.settings.base import Setting
from forum.forms import MaintenanceModeForm, PageForm, CreateUserForm
from forum.settings.forms import SettingsSetForm
from forum.utils import pagination, html
from forum.utils.mail import send_template_email

from forum.models import Question, Answer, User, Node, Action, Page, NodeState, Tag
from forum.models.node import NodeMetaClass
from forum.actions import NewPageAction, EditPageAction, PublishAction, DeleteAction, UserJoinsAction, CloseAction
from forum import settings

TOOLS = {}

def super_user_required(fn):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.is_superuser:
            return fn(request, *args, **kwargs)
        else:
            return HttpResponseUnauthorized(request)

    return wrapper

def admin_page(fn):
    @super_user_required
    def wrapper(request, *args, **kwargs):
        res = fn(request, *args, **kwargs)
        if isinstance(res, HttpResponse):
            return res

        template, context = res
        context['basetemplate'] = settings.DJSTYLE_ADMIN_INTERFACE and "osqaadmin/djstyle_base.html" or "osqaadmin/base.html"
        context['allsets'] = Setting.sets
        context['othersets'] = sorted(
                [s for s in Setting.sets.values() if not s.name in
                ('basic', 'users', 'email', 'paths', 'extkeys', 'repgain', 'minrep', 'voting', 'accept', 'badges', 'about', 'faq', 'sidebar',
                'form', 'moderation', 'css', 'headandfoot', 'head', 'view', 'urls')]
                , lambda s1, s2: s1.weight - s2.weight)

        context['tools'] = TOOLS

        unsaved = request.session.get('previewing_settings', {})
        context['unsaved'] = set([getattr(settings, s).set.name for s in unsaved.keys() if hasattr(settings, s)])

        return render_to_response(template, context, context_instance=RequestContext(request))

    return wrapper

def admin_tools_page(name, label):    
    def decorator(fn):
        fn = admin_page(fn)
        fn.label = label
        TOOLS[name] = fn

        return fn
    return decorator

class ActivityPaginatorContext(pagination.PaginatorContext):
    def __init__(self):
        super (ActivityPaginatorContext, self).__init__('ADMIN_RECENT_ACTIVITY', pagesizes=(20, 40, 80), default_pagesize=40)

@admin_page
def dashboard(request):
    return ('osqaadmin/dashboard.html', pagination.paginated(request, ("recent_activity", ActivityPaginatorContext()), {
    'settings_pack': unicode(settings.SETTINGS_PACK),
    'statistics': get_statistics(),
    'recent_activity': get_recent_activity(),
    'flagged_posts': get_flagged_posts(),
    }))

@super_user_required
def interface_switch(request):
    if request.GET and request.GET.get('to', None) and request.GET['to'] in ('default', 'djstyle'):
        settings.DJSTYLE_ADMIN_INTERFACE.set_value(request.GET['to'] == 'djstyle')

    return HttpResponseRedirect(reverse('admin_index'))

@admin_page
def statistics(request):
    today = datetime.now()
    last_month = today - timedelta(days=30)

    last_month_questions = Question.objects.filter_state(deleted=False).filter(added_at__gt=last_month
                                                                               ).order_by('added_at').values_list(
            'added_at', flat=True)

    last_month_n_questions = Question.objects.filter_state(deleted=False).filter(added_at__lt=last_month).count()
    qgraph_data = simplejson.dumps([
    (time.mktime(d.timetuple()) * 1000, i + last_month_n_questions)
    for i, d in enumerate(last_month_questions)
    ])

    last_month_users = User.objects.filter(date_joined__gt=last_month
                                           ).order_by('date_joined').values_list('date_joined', flat=True)

    last_month_n_users = User.objects.filter(date_joined__lt=last_month).count()

    ugraph_data = simplejson.dumps([
    (time.mktime(d.timetuple()) * 1000, i + last_month_n_users)
    for i, d in enumerate(last_month_users)
    ])

    return 'osqaadmin/statistics.html', {
    'graphs': [
            {
            'id': 'questions_graph',
            'caption': _("Questions Graph"),
            'data': qgraph_data
            }, {
            'id': 'userss_graph',
            'caption': _("Users Graph"),
            'data': ugraph_data
            }
            ]
    }

@admin_page
def tools_page(request, name):
    if not name in TOOLS:
        raise Http404

    return TOOLS[name](request)


@admin_page
def settings_set(request, set_name):
    set = Setting.sets.get(set_name, {})
    current_preview = request.session.get('previewing_settings', {})

    if set is None:
        raise Http404

    if request.POST:
        form = SettingsSetForm(set, data=request.POST, files=request.FILES)

        if form.is_valid():
            if 'preview' in request.POST:
                current_preview.update(form.cleaned_data)
                request.session['previewing_settings'] = current_preview

                return HttpResponseRedirect(reverse('index'))
            else:
                for s in set:
                    current_preview.pop(s.name, None)

                request.session['previewing_settings'] = current_preview

                if not 'reset' in request.POST:
                    form.save()
                    request.user.message_set.create(message=_("'%s' settings saved succesfully") % set_name)

                    if set_name in ('minrep', 'badges', 'repgain'):
                        settings.SETTINGS_PACK.set_value("custom")

                return HttpResponseRedirect(reverse('admin_set', args=[set_name]))
    else:
        form = SettingsSetForm(set, unsaved=current_preview)

    return 'osqaadmin/set.html', {
    'form': form,
    'markdown': set.markdown,
    }

@super_user_required
def get_default(request, set_name, var_name):
    set = Setting.sets.get(set_name, None)
    if set is None: raise Http404

    setting = dict([(s.name, s) for s in set]).get(var_name, None)
    if setting is None: raise Http404

    setting.to_default()

    if request.is_ajax():
        return HttpResponse(setting.default)
    else:
        return HttpResponseRedirect(reverse('admin_set', kwargs={'set_name': set_name}))


def get_recent_activity():
    return Action.objects.order_by('-action_date')

def get_flagged_posts():
    return Action.objects.filter(canceled=False, action_type="flag").order_by('-action_date')[0:30]

def get_statistics():
    return {
    'total_users': User.objects.all().count(),
    'users_last_24': User.objects.filter(date_joined__gt=(datetime.now() - timedelta(days=1))).count(),
    'total_questions': Question.objects.filter_state(deleted=False).count(),
    'questions_last_24': Question.objects.filter_state(deleted=False).filter(
            added_at__gt=(datetime.now() - timedelta(days=1))).count(),
    'total_answers': Answer.objects.filter_state(deleted=False).count(),
    'answers_last_24': Answer.objects.filter_state(deleted=False).filter(
            added_at__gt=(datetime.now() - timedelta(days=1))).count(),
    }

@super_user_required
def go_bootstrap(request):
#todo: this is the quick and dirty way of implementing a bootstrap mode
    try:
        from forum_modules.default_badges import settings as dbsets
        dbsets.POPULAR_QUESTION_VIEWS.set_value(100)
        dbsets.NOTABLE_QUESTION_VIEWS.set_value(200)
        dbsets.FAMOUS_QUESTION_VIEWS.set_value(300)
        dbsets.NICE_ANSWER_VOTES_UP.set_value(2)
        dbsets.NICE_QUESTION_VOTES_UP.set_value(2)
        dbsets.GOOD_ANSWER_VOTES_UP.set_value(4)
        dbsets.GOOD_QUESTION_VOTES_UP.set_value(4)
        dbsets.GREAT_ANSWER_VOTES_UP.set_value(8)
        dbsets.GREAT_QUESTION_VOTES_UP.set_value(8)
        dbsets.FAVORITE_QUESTION_FAVS.set_value(1)
        dbsets.STELLAR_QUESTION_FAVS.set_value(3)
        dbsets.DISCIPLINED_MIN_SCORE.set_value(3)
        dbsets.PEER_PRESSURE_MAX_SCORE.set_value(-3)
        dbsets.CIVIC_DUTY_VOTES.set_value(15)
        dbsets.PUNDIT_COMMENT_COUNT.set_value(10)
        dbsets.SELF_LEARNER_UP_VOTES.set_value(2)
        dbsets.STRUNK_AND_WHITE_EDITS.set_value(10)
        dbsets.ENLIGHTENED_UP_VOTES.set_value(2)
        dbsets.GURU_UP_VOTES.set_value(4)
        dbsets.NECROMANCER_UP_VOTES.set_value(2)
        dbsets.NECROMANCER_DIF_DAYS.set_value(30)
        dbsets.TAXONOMIST_USE_COUNT.set_value(5)
    except:
        pass

    settings.REP_TO_VOTE_UP.set_value(0)
    settings.REP_TO_VOTE_DOWN.set_value(15)
    settings.REP_TO_FLAG.set_value(15)
    settings.REP_TO_COMMENT.set_value(0)
    settings.REP_TO_LIKE_COMMENT.set_value(0)
    settings.REP_TO_UPLOAD.set_value(0)
    settings.REP_TO_CREATE_TAGS.set_value(0)
    settings.REP_TO_CLOSE_OWN.set_value(60)
    settings.REP_TO_REOPEN_OWN.set_value(120)
    settings.REP_TO_RETAG.set_value(150)
    settings.REP_TO_EDIT_WIKI.set_value(200)
    settings.REP_TO_EDIT_OTHERS.set_value(400)
    settings.REP_TO_CLOSE_OTHERS.set_value(600)
    settings.REP_TO_DELETE_COMMENTS.set_value(400)
    settings.REP_TO_VIEW_FLAGS.set_value(30)

    settings.INITIAL_REP.set_value(1)
    settings.MAX_REP_BY_UPVOTE_DAY.set_value(300)
    settings.REP_GAIN_BY_UPVOTED.set_value(15)
    settings.REP_LOST_BY_DOWNVOTED.set_value(1)
    settings.REP_LOST_BY_DOWNVOTING.set_value(0)
    settings.REP_GAIN_BY_ACCEPTED.set_value(25)
    settings.REP_GAIN_BY_ACCEPTING.set_value(5)
    settings.REP_LOST_BY_FLAGGED.set_value(2)
    settings.REP_LOST_BY_FLAGGED_3_TIMES.set_value(30)
    settings.REP_LOST_BY_FLAGGED_5_TIMES.set_value(100)

    settings.SETTINGS_PACK.set_value("bootstrap")

    request.user.message_set.create(message=_('Bootstrap mode enabled'))
    return HttpResponseRedirect(reverse('admin_index'))

@super_user_required
def go_defaults(request):
    for setting in Setting.sets['badges']:
        setting.to_default()
    for setting in Setting.sets['minrep']:
        setting.to_default()
    for setting in Setting.sets['repgain']:
        setting.to_default()

    settings.SETTINGS_PACK.set_value("default")

    request.user.message_set.create(message=_('All values reverted to defaults'))
    return HttpResponseRedirect(reverse('admin_index'))


@super_user_required
def recalculate_denormalized(request):
    for n in Node.objects.all():
        n = n.leaf
        n.score = n.votes.aggregate(score=models.Sum('value'))['score']
        if not n.score: n.score = 0
        n.save()

    for u in User.objects.all():
        u.reputation = u.reputes.aggregate(reputation=models.Sum('value'))['reputation']
        u.save()

    request.user.message_set.create(message=_('All values recalculated'))
    return HttpResponseRedirect(reverse('admin_index'))

@admin_page
def maintenance(request):
    if request.POST:
        if 'close' in request.POST or 'adjust' in request.POST:
            form = MaintenanceModeForm(request.POST)

            if form.is_valid():
                settings.MAINTAINANCE_MODE.set_value({
                'allow_ips': form.cleaned_data['ips'],
                'message': form.cleaned_data['message']})

                if 'close' in request.POST:
                    message = _('Maintenance mode enabled')
                else:
                    message = _('Settings adjusted')

                request.user.message_set.create(message=message)

                return HttpResponseRedirect(reverse('admin_maintenance'))
        elif 'open' in request.POST:
            settings.MAINTAINANCE_MODE.set_value(None)
            request.user.message_set.create(message=_("Your site is now running normally"))
            return HttpResponseRedirect(reverse('admin_maintenance'))
    else:
        form = MaintenanceModeForm(initial={'ips': request.META['REMOTE_ADDR'],
                                            'message': _('Currently down for maintenance. We\'ll be back soon')})

    return ('osqaadmin/maintenance.html', {'form': form, 'in_maintenance': settings.MAINTAINANCE_MODE.value is not None
                                           })


@admin_page
def flagged_posts(request):
    return ('osqaadmin/flagged_posts.html', {
    'flagged_posts': get_flagged_posts(),
    })

@admin_page
def static_pages(request):
    pages = Page.objects.all()

    return ('osqaadmin/static_pages.html', {
    'pages': pages,
    })

@admin_page
def edit_page(request, id=None):
    if id:
        page = get_object_or_404(Page, id=id)
    else:
        page = None

    if request.POST:
        form = PageForm(page, request.POST)

        if form.is_valid():
            if form.has_changed():
                if not page:
                    page = NewPageAction(user=request.user, ip=request.META['REMOTE_ADDR']).save(data=form.cleaned_data
                                                                                                 ).node
                else:
                    EditPageAction(user=request.user, node=page, ip=request.META['REMOTE_ADDR']).save(
                            data=form.cleaned_data)

            if ('publish' in request.POST) and (not page.published):
                PublishAction(user=request.user, node=page, ip=request.META['REMOTE_ADDR']).save()
            elif ('unpublish' in request.POST) and page.published:
                page.nstate.published.cancel(ip=request.META['REMOTE_ADDR'])

            return HttpResponseRedirect(reverse('admin_edit_page', kwargs={'id': page.id}))

    else:
        form = PageForm(page)

    if page:
        published = page.published
    else:
        published = False

    return ('osqaadmin/edit_page.html', {
    'page': page,
    'form': form,
    'published': published
    })

@admin_tools_page(_('createuser'), _("Create new user"))
def create_user(request):
    if request.POST:
        form = CreateUserForm(request.POST)

        if form.is_valid():
            user_ = User(username=form.cleaned_data['username'], email=form.cleaned_data['email'])
            user_.set_password(form.cleaned_data['password1'])

            if not form.cleaned_data.get('validate_email', False):
                user_.email_isvalid = True

            user_.save()
            UserJoinsAction(user=user_).save()

            request.user.message_set.create(message=_("New user created sucessfully. %s.") % html.hyperlink(
                    user_.get_profile_url(), _("See %s profile") % user_.username, target="_blank"))

            return HttpResponseRedirect(reverse("admin_tools", kwargs={'name': 'createuser'}))
    else:
        form = CreateUserForm()

    return ('osqaadmin/createuser.html', {
        'form': form,
    })

class NodeManagementPaginatorContext(pagination.PaginatorContext):
    def __init__(self, id='QUESTIONS_LIST', prefix='', default_pagesize=100):
        super (NodeManagementPaginatorContext, self).__init__(id, sort_methods=(
            (_('added_at'), pagination.SimpleSort(_('added_at'), '-added_at', "")),
            (_('added_at_asc'), pagination.SimpleSort(_('added_at_asc'), 'added_at', "")),
            (_('author'), pagination.SimpleSort(_('author'), '-author__username', "")),
            (_('author_asc'), pagination.SimpleSort(_('author_asc'), 'author__username', "")),
            (_('score'), pagination.SimpleSort(_('score'), '-score', "")),
            (_('score_asc'), pagination.SimpleSort(_('score_asc'), 'score', "")),
            (_('act_at'), pagination.SimpleSort(_('act_at'), '-last_activity_at', "")),
            (_('act_at_asc'), pagination.SimpleSort(_('act_at_asc'), 'last_activity_at', "")),
            (_('act_by'), pagination.SimpleSort(_('act_by'), '-last_activity_by__username', "")),
            (_('act_by_asc'), pagination.SimpleSort(_('act_by_asc'), 'last_activity_by__username', "")),
        ), pagesizes=(default_pagesize,), force_sort='added_at', default_pagesize=default_pagesize, prefix=prefix)

@admin_tools_page(_("nodeman"), _("Bulk management"))
def node_management(request):
    if request.POST:
        params = pagination.generate_uri(request.GET, ('page',))

        if "save_filter" in request.POST:
            filter_name = request.POST.get('filter_name', _('filter'))
            params = pagination.generate_uri(request.GET, ('page',))
            current_filters = settings.NODE_MAN_FILTERS.value
            current_filters.append((filter_name, params))
            settings.NODE_MAN_FILTERS.set_value(current_filters)

        elif r"execute" in request.POST:
            selected_nodes = request.POST.getlist('_selected_node')

            if selected_nodes and request.POST.get('action', None):
                action = request.POST['action']
                selected_nodes = Node.objects.filter(id__in=selected_nodes)

                message = _("No action performed")

                if action == 'delete_selected':
                    for node in selected_nodes:
                        if node.node_type in ('question', 'answer', 'comment') and (not node.nis.deleted):
                            DeleteAction(user=request.user, node=node, ip=request.META['REMOTE_ADDR']).save()

                    message = _("All selected nodes marked as deleted")

                if action == 'undelete_selected':
                    for node in selected_nodes:
                        if node.node_type in ('question', 'answer', 'comment') and (node.nis.deleted):
                            node.nstate.deleted.cancel(ip=request.META['REMOTE_ADDR'])

                    message = _("All selected nodes undeleted")

                if action == "close_selected":
                    for node in selected_nodes:
                        if node.node_type == "question" and (not node.nis.closed):
                            CloseAction(node=node.leaf, user=request.user, extra=_("bulk close"), ip=request.META['REMOTE_ADDR']).save()

                    message = _("Selected questions were closed")

                if action == "hard_delete_selected":
                    ids = [n.id for n in selected_nodes]

                    for id in ids:
                        try:
                            node = Node.objects.get(id=id)
                            node.delete()
                        except:
                            pass

                    message = _("All selected nodes deleted")

                request.user.message_set.create(message=message)

                params = pagination.generate_uri(request.GET, ('page',))
                
            return HttpResponseRedirect(reverse("admin_tools", kwargs={'name': 'nodeman'}) + "?" + params)


    nodes = Node.objects.all()

    text = request.GET.get('text', '')
    text_in = request.GET.get('text_in', 'body')

    authors = request.GET.getlist('authors')
    tags = request.GET.getlist('tags')

    type_filter = request.GET.getlist('node_type')
    state_filter = request.GET.getlist('state_type')
    state_filter_type = request.GET.get('state_filter_type', 'any')

    if type_filter:
        nodes = nodes.filter(node_type__in=type_filter)

    state_types = NodeState.objects.filter(node__in=nodes).values_list('state_type', flat=True).distinct('state_type')
    state_filter = [s for s in state_filter if s in state_types]

    if state_filter:
        if state_filter_type == 'all':
            nodes = nodes.all_states(*state_filter)
        else:
            nodes = nodes.any_state(*state_filter)

    if (authors):
        nodes = nodes.filter(author__id__in=authors)
        authors = User.objects.filter(id__in=authors)

    if (tags):
        nodes = nodes.filter(tags__id__in=tags)
        tags = Tag.objects.filter(id__in=tags)

    if text:
        text_in = request.GET.get('text_in', 'body')
        filter = None

        if text_in == 'title' or text_in == 'both':
            filter = models.Q(title__icontains=text)

        if text_in == 'body' or text_in == 'both':
            sec_filter = models.Q(body__icontains=text)
            if filter:
                filter = filter | sec_filter
            else:
                filter = sec_filter

        if filter:
            nodes = nodes.filter(filter)

    node_types = [(k, n.friendly_name) for k, n in NodeMetaClass.types.items()]

    return ('osqaadmin/nodeman.html', pagination.paginated(request, ("nodes", NodeManagementPaginatorContext()), {
    'nodes': nodes,
    'text': text,
    'text_in': text_in,
    'type_filter': type_filter,
    'state_filter': state_filter,
    'state_filter_type': state_filter_type,
    'node_types': node_types,
    'state_types': state_types,
    'authors': authors,
    'tags': tags,
    'hide_menu': True
    }))

@super_user_required
def test_email_settings(request):
    user = request.user

    send_template_email([user,], 'osqaadmin/mail_test.html', { 'user' : user })

    return render_to_response(
        'osqaadmin/test_email_settings.html',
        { 'user': user, },
        RequestContext(request)
    )