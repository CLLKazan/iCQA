import socket
from django import forms
from django.utils.translation import ugettext as _
from django.contrib.admin.widgets import FilteredSelectMultiple, AdminDateWidget
from qanda import TitleField, EditorField
from forum import settings
from forum.models.node import NodeMetaClass
from forum.models import User

class IPListField(forms.CharField):
    def clean(self, value):
        ips = [ip.strip() for ip in value.strip().strip(',').split(',')]
        iplist = []

        if len(ips) < 1:
            raise forms.ValidationError(_('Please input at least one ip address'))

        for ip in ips:
            try:
                socket.inet_aton(ip)
            except socket.error:
                raise forms.ValidationError(_('Invalid ip address: %s' % ip))

            if not len(ip.split('.')) == 4:
                raise forms.ValidationError(_('Please use the dotted quad notation for the ip addresses'))

            iplist.append(ip)

        return iplist

class MaintenanceModeForm(forms.Form):
    ips = IPListField(label=_('Allow ips'),
                      help_text=_('Comma separated list of ips allowed to access the site while in maintenance'),
                      required=True,
                      widget=forms.TextInput(attrs={'class': 'longstring'}))

    message = forms.CharField(label=_('Message'),
                              help_text=_('A message to display to your site visitors while in maintainance mode'),
                              widget=forms.Textarea)


TEMPLATE_CHOICES = (
('default', _('Default')),
('sidebar', _('Default with sidebar')),
('none', _('None')),
)

RENDER_CHOICES = (
('markdown', _('Markdown')),
('html', _('HTML')),
('escape', _('Escaped'))
)

class UrlFieldWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        if not value:
            value = ''

        return """
                <input class="url_field" type="text" name="%(name)s" value="%(value)s" />
                <a class="url_field_anchor" target="_blank" href="%(app_url)s"></a>
            """  % {'name': name, 'value': value, 'app_url': settings.APP_URL}


class PageForm(forms.Form):
    def __init__(self, page, *args, **kwargs):
        if page:
            initial = page.extra
            initial.update(dict(title=page.title, content=page.body))
            super(PageForm, self).__init__(initial=initial, *args, **kwargs)
        else:
            super(PageForm, self).__init__(*args, **kwargs)


    title  = forms.CharField(label=_('Title'), max_length=255, widget=forms.TextInput(attrs={'class': 'longstring'}),
                             initial='New page')
    path  = forms.CharField(label=_('Page URL'), widget=UrlFieldWidget, initial='pages/new/')

    content = forms.CharField(label=_('Page Content'), widget=forms.Textarea(attrs={'rows': 30}))
    mimetype = forms.CharField(label=_('Mime Type'), initial='text/html')

    render = forms.ChoiceField(widget=forms.RadioSelect, choices=RENDER_CHOICES, initial='markdown',
                               label=_('Render Mode'))

    template = forms.ChoiceField(widget=forms.RadioSelect, choices=TEMPLATE_CHOICES, initial='default',
                                 label=_('Template'))
    sidebar = forms.CharField(label=_('Sidebar Content'), widget=forms.Textarea(attrs={'rows': 20}), required=False)
    sidebar_wrap = forms.BooleanField(label=_("Wrap sidebar block"), initial=True, required=False)
    sidebar_render = forms.ChoiceField(widget=forms.RadioSelect, choices=RENDER_CHOICES, initial='markdown',
                                       label=_('Sidebar Render Mode'))

    comments = forms.BooleanField(label=_("Allow comments"), initial=False, required=False)

from forum.forms.auth import SimpleRegistrationForm
from forum.forms.general import SetPasswordForm


class CreateUserForm(SimpleRegistrationForm, SetPasswordForm):
    validate_email = forms.BooleanField(required=False, label=_('send validation email'))

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['username', 'email', 'validate_email', 'password1', 'password2']
        self.fields['email'].label = _('email address')


    
