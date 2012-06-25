import startup

import os.path
from forum import settings
from django.conf.urls.defaults import *
from django.conf import settings as djsettings
from django.contrib import admin
from forum import views as app
from forum.sitemap import OsqaSitemap
from django.utils.translation import ugettext as _
import logging

admin.autodiscover()

sitemaps = {
    'questions': OsqaSitemap
}

APP_PATH = os.path.dirname(__file__)

core_urls = (
    url(r'^$', app.readers.index, name='index'),
    url(r'^%s(.*)' % _('nimda/'), admin.site.root),
                        
    url(r'^sitemap.xml$', 'forum.sitemap.index', {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', 'forum.sitemap.sitemap', {'sitemaps': sitemaps}),
    
    url(r'^favicon\.ico$', app.meta.favicon),
    url(r'^cstyle\.css$', app.meta.custom_css, name='custom_css'),
    
    url(r'^m/(?P<skin>\w+)/media/(?P<path>.*)$', app.meta.media , name='osqa_media'),
    url(r'^%s(?P<path>.*)$' % _('upfiles/'), 'django.views.static.serve', {'document_root': os.path.join(APP_PATH, 'upfiles').replace('\\', '/')}, name='uploaded_file',),
    
    url(r'^%s$' % _('faq/'), app.meta.static, {'content': settings.FAQ_PAGE_TEXT, 'title': _('FAQ')}, name='faq'),
    url(r'^%s$' % _('about/'), app.meta.static, {'content': settings.ABOUT_PAGE_TEXT, 'title': _('About')}, name='about'),
    url(r'^%s$' % _('markdown_help/'), app.meta.markdown_help, name='markdown_help'), url(r'^opensearch\.xml$', app.meta.opensearch, name='opensearch'),
    url(r'^opensearch\.xml$', app.meta.opensearch, name='opensearch'),
    url(r'^%s$' % _('privacy/'), app.meta.privacy, name='privacy'),
    url(r'^%s$' % _('logout/'), app.meta.logout, name='logout'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('answers/'), _('edit/')), app.writers.edit_answer, name='edit_answer'),
    url(r'^%s(?P<id>\d+)/$' % _('revisions/'), app.readers.revisions, name='revisions'),
    url(r'^%s$' % _('questions/'), app.readers.questions, name='questions'),
    url(r'^%s%s$' % (_('questions/'), _('ask/')), app.writers.ask, name='ask'),
    url(r'^%s%s$' % (_('questions/'), _('related_questions/')), app.commands.related_questions, name='related_questions'),
    
    url(r'^%s%s$' % (_('questions/'), _('unanswered/')), app.readers.unanswered, name='unanswered'),
    url(r'^%s(?P<mode>[\w\-]+)/(?P<user>\d+)/(?P<slug>.*)/$' % _('questions/'), app.readers.user_questions, name='user_questions'),
    
    
    url(r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('edit/')), app.writers.edit_question, name='edit_question'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('close/')), app.commands.close, kwargs=dict(close=True), name='close'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('reopen/')), app.commands.close, kwargs=dict(close=False), name='reopen'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('answer/')), app.writers.answer, name='answer'),
    url(r'^%s(?P<action>\w+)/$' % _('pending-data/'), app.writers.manage_pending_data, name='manage_pending_data'),
    
    url(r'^%s(?P<id>\d+)/(?P<vote_type>[a-z]+)/' % _('vote/'), app.commands.vote_post, name='vote_post'),
    url(r'^%s(?P<id>\d+)/$' % _('like_comment/'), app.commands.like_comment, name='like_comment'),
    url(r'^%s(?P<id>\d+)/' % _('comment/'), app.commands.comment, name='comment'),
    url(r'^%s(?P<id>\d+)/$' % _('delete_comment/'), app.commands.delete_comment, name='delete_comment'),
    url(r'^%s(?P<id>\d+)/$' % _('convert_comment/'), app.commands.convert_comment_to_answer, name='convert_comment'),
    url(r'^%s(?P<id>\d+)/$' % _('accept_answer/'), app.commands.accept_answer, name='accept_answer'),
    url(r'^%s(?P<id>\d+)/$' % _('answer_link/'), app.commands.answer_permanent_link, name='answer_permanent_link'),
    url(r'^%s(?P<id>\d+)/$' % _('mark_favorite/'), app.commands.mark_favorite, name='mark_favorite'),
    url(r'^%s%s(?P<user_id>\d+)/%s(?P<answer_id>\d+)/$' % (_('award_points/'), _('user/'), _('answer/')), app.commands.award_points, name='award_points'),
    
    url(r'^%s(?P<id>\d+)/' % _('flag/'), app.commands.flag_post, name='flag_post'),
    url(r'^%s(?P<id>\d+)/' % _('delete/'), app.commands.delete_post, name='delete_post'),
    url(r'^%s(?P<id>\d+)/(?P<user>\d+)?$' % _('subscribe/'), app.commands.subscribe, name='subscribe'),
    url(r'^%s(?P<id>\d+)/$' % _('subscribe/'), app.commands.subscribe, name='subscribe_simple'),
    url(r'^%s' % _('matching_tags/'), app.commands.matching_tags, name='matching_tags'),
    url(r'^%s' % _('matching_users/'), app.commands.matching_users, name='matching_users'),
    url(r'^%s(?P<id>\d+)/' % _('node_markdown/'), app.commands.node_markdown, name='node_markdown'),
    url(r'^%s(?P<id>\d+)/' % _('convert/'), app.commands.convert_to_comment, name='convert_to_comment'),
    url(r'^%s(?P<id>\d+)/' % _('convert_to_question/'), app.writers.convert_to_question,name='convert_to_question'),
    url(r'^%s(?P<id>\d+)/' % _('wikify/'), app.commands.wikify, name='wikify'),
    
    url(r'^%s(?P<id>\d+)/(?P<slug>[\w-]*)$' % _('question/'), 'django.views.generic.simple.redirect_to', {'url': '/questions/%(id)s/%(slug)s'}),
    url(r'^%s(?P<id>\d+)/?$' % _('questions/'), app.readers.question, name='question'),
    url(r'^%s(?P<id>\d+)/(?P<slug>.*)/(?P<answer>\d+)$' % _('questions/'), app.readers.question),
    url(r'^%s(?P<id>\d+)/(?P<slug>.*)$' % _('questions/'), app.readers.question, name='question'),
    
    
    url(r'^%s$' % _('tags/'), app.readers.tags, name='tags'),
    url(r'^%s(?P<tag>.*)/$' % _('tags/'), app.readers.tag, name='tag_questions'),     
    url(r'^%s%s(?P<tag>[^/]+)/$' % (_('mark-tag/'),_('interesting/')), app.commands.mark_tag, kwargs={'reason':'good','action':'add'}, name='mark_interesting_tag'),     
    url(r'^%s%s(?P<tag>[^/]+)/$' % (_('mark-tag/'),_('ignored/')), app.commands.mark_tag, kwargs={'reason':'bad','action':'add'}, name='mark_ignored_tag'),     
    url(r'^%s(?P<tag>[^/]+)/$' % _('unmark-tag/'), app.commands.mark_tag, kwargs={'action':'remove'}, name='mark_ignored_tag'),     
    
    url(r'^%s$' % _('users/'), app.users.users, name='users'),
    # url(r'^%s$' % _('online_users/'), app.users.online_users, name='online_users'),    
    
    url(r'^%s(?P<id>\d+)/%s$' % (_('users/'), _('edit/')), app.users.edit_user, name='edit_user'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('users/'), _('award/')), app.users.award_points, name='user_award_points'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('users/'), _('suspend/')), app.users.suspend, name='user_suspend'),
    url(r'^%s(?P<id>\d+)/%s(?P<action>[a-z]+)/(?P<status>[a-z]+)/$' % (_('users/'), _('powers/')), app.users.user_powers, name='user_powers'),
    url(r'^%s(?P<id>\d+)/(?P<slug>.*)/%s$' % (_('users/'), _('subscriptions/')), app.users.user_subscriptions, name='user_subscriptions'),
    url(r'^%s(?P<id>\d+)/(?P<slug>.*)/%s$' % (_('users/'), _('preferences/')), app.users.user_preferences, name='user_preferences'),
    url(r'^%s(?P<id>\d+)/(?P<slug>.*)/%s$' % (_('users/'), _('favorites/')), app.users.user_favorites, name='user_favorites'),
    url(r'^%s(?P<id>\d+)/(?P<slug>.*)/%s$' % (_('users/'), _('reputation/')), app.users.user_reputation, name='user_reputation'),
    url(r'^%s(?P<id>\d+)/(?P<slug>.*)/%s$' % (_('users/'), _('votes/')), app.users.user_votes, name='user_votes'),
    url(r'^%s(?P<id>\d+)/(?P<slug>.*)/%s$' % (_('users/'), _('recent/')), app.users.user_recent, name='user_recent'),
    url(r'^%s(?P<id>\d+)/(?P<slug>.*)/$' % _('users/'), app.users.user_profile, name='user_profile'),
    url(r'^%s$' % _('badges/'), app.meta.badges, name='badges'),
    url(r'^%s(?P<id>\d+)/(?P<slug>[\w-]+)/?$' % _('badges/'), app.meta.badge, name='badge'),
    # (r'^admin/doc/' % _('admin/doc'), include('django.contrib.admindocs.urls')),
    
    url(r'^%s$' % _('upload/'), app.writers.upload, name='upload'),
    url(r'^%s$' % _('search/'), app.readers.search, name='search'),
    url(r'^%s$' % _('contact/'), app.meta.feedback, name='feedback'),
    
    (r'^i18n/', include('django.conf.urls.i18n')),
    
    url(r'^%s%s$' % (_('account/'), _('signin/')), app.auth.signin_page, name='auth_signin'),
    url(r'^%s%s$' % (_('account/'), _('signout/')), app.auth.signout, name='user_signout'),
    url(r'^%s(?P<provider>\w+)/%s$' % (_('account/'), _('signin/')), app.auth.prepare_provider_signin, name='auth_provider_signin'),
    url(r'^%s(?P<provider>\w+)/%s$' % (_('account/'), _('done/')), app.auth.process_provider_signin, name='auth_provider_done'),
    url(r'^%s%s$' % (_('account/'), _('register/')), app.auth.external_register, name='auth_external_register'),
    url(r'^%s%s(?P<user>\d+)/(?P<code>.+)/$' % (_('account/'), _('validate/')), app.auth.validate_email, name='auth_validate_email'),
    url(r'^%s%s$' % (_('account/'), _('tempsignin/')), app.auth.request_temp_login, name='auth_request_tempsignin'),
    url(r'^%s%s(?P<user>\d+)/(?P<code>.+)/$' % (_('account/'), _('tempsignin/')), app.auth.temp_signin, name='auth_tempsignin'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('account/'), _('authsettings/')), app.auth.auth_settings, name='user_authsettings'),
    url(r'^%s%s(?P<id>\d+)/%s$' % (_('account/'), _('providers/'), _('remove/')), app.auth.remove_external_provider, name='user_remove_external_provider'),
    url(r'^%s%s%s$' % (_('account/'), _('providers/'), _('add/')), app.auth.signin_page, name='user_add_external_provider'),
    url(r'^%s%s$' %(_('account/'), _('send-validation/')), app.auth.send_validation_email, name='send_validation_email'),
    
    
    url(r'^%s$' % _('admin/'), app.admin.dashboard, name='admin_index'),
    url(r'^%s%s$' % (_('admin/'), _('switch_interface/')), app.admin.interface_switch, name='admin_switch_interface'),
    url(r'^%s%s$' % (_('admin/'), _('statistics/')), app.admin.statistics, name='admin_statistics'),
    url(r'^%s%s$' % (_('admin/'), _('denormalize/')), app.admin.recalculate_denormalized, name='admin_denormalize'),
    url(r'^%s%s$' % (_('admin/'), _('go_bootstrap/')), app.admin.go_bootstrap, name='admin_go_bootstrap'),
    url(r'^%s%s$' % (_('admin/'), _('go_defaults/')), app.admin.go_defaults, name='admin_go_defaults'),
    url(r'^%s%s(?P<set_name>\w+)/(?P<var_name>\w+)/$' % (_('admin/'), _('settings/')), app.admin.get_default, name='admin_default'),
    url(r'^%s%s$' % (_('admin/'), _('maintenance/')), app.admin.maintenance, name='admin_maintenance'),
    url(r'^%s%s$' % (_('admin/'), _('flagged_posts/')), app.admin.flagged_posts, name='admin_flagged_posts'),
    url(r'^%s%s$' % (_('admin/'), _('static_pages/')), app.admin.static_pages, name='admin_static_pages'),
    
    url(r'^%s%s%s$' % (_('admin/'), _('static_pages/'), _('new/')), app.admin.edit_page, name='admin_new_page'),
    url(r'^%s%s%s(?P<id>\d+)/$' % (_('admin/'), _('static_pages/'), _('edit/')), app.admin.edit_page, name='admin_edit_page'),
    
    url(r'^%s%s(?P<name>\w+)/$' % (_('admin/'), _('tools/')), app.admin.tools_page, name='admin_tools'),
    
    url(r'^%s%s(?P<set_name>\w+)/$' % (_('admin/'), _('settings/')), app.admin.settings_set, name='admin_set'),
    
    url(r'%s%s' % (_('admin/'), _('test_email_settings/')), app.admin.test_email_settings, name='test_email_settings'),
    
    url(r'^feeds/rss[/]?$', app.readers.feed, name='latest_questions_feed'),
    
)

from forum.modules import get_modules_script

module_patterns = get_modules_script('urls')

urlpatterns = patterns('')

for pattern_file in module_patterns:
    pattern = getattr(pattern_file, 'urlpatterns', None)
    if pattern:
        urlpatterns += pattern

module_defined = {}

for t in urlpatterns:
    if hasattr(t, 'name') and t.name:
        module_defined[t.name] = True

core_defined = []

for u in core_urls:
    if not(hasattr(u, 'name') and u.name and (u.name in module_defined)):
        core_defined.append(u)

def urlname(name):
    if name in module_defined:
        return None
    return name

urlpatterns += patterns('', *core_defined)

