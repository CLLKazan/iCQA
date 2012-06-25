from forum.forms import NextUrlField, UserNameField, UserEmailField, SetPasswordForm
from forum.models import Question
from forum.modules import call_all_handlers
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate
from django import forms
import logging

class ClassicRegisterForm(SetPasswordForm):
    """ legacy registration form """

    next = NextUrlField()
    username = UserNameField()
    email = UserEmailField()

    def __init__(self, *args, **kwargs):
        super(ClassicRegisterForm, self).__init__(*args, **kwargs)

        spam_fields = call_all_handlers('create_anti_spam_field')
        if spam_fields:
            spam_fields = dict(spam_fields)
            for name, field in spam_fields.items():
                self.fields[name] = field

            self._anti_spam_fields = spam_fields.keys()
        else:
            self._anti_spam_fields = []

    def anti_spam_fields(self):
        return [self[name] for name in self._anti_spam_fields]

class ClassicLoginForm(forms.Form):
    """ legacy account signin form """
    next = NextUrlField()
    username = UserNameField(required=False, skip_clean=True)
    password = forms.CharField(max_length=128,
                               widget=forms.widgets.PasswordInput(attrs={'class':'required login'}),
                               required=False)

    def __init__(self, data=None, files=None, auto_id='id_%s',
                 prefix=None, initial=None):
        super(ClassicLoginForm, self).__init__(data, files, auto_id,
                                               prefix, initial)
        self.user_cache = None

    def _clean_nonempty_field(self, field):
        value = None
        if field in self.cleaned_data:
            value = self.cleaned_data[field].strip()
            if value == '':
                value = None
        self.cleaned_data[field] = value
        return value

    def clean_username(self):
        return self._clean_nonempty_field('username')

    def clean_password(self):
        return self._clean_nonempty_field('password')

    def clean(self):
        error_list = []
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        self.user_cache = None
        if username and password:
            user_ = authenticate(username=username, password=password)

            if user_ is None:
                del self.cleaned_data['username']
                del self.cleaned_data['password']

                error_list.insert(0, (_("Please enter valid username and password "
                "(both are case-sensitive).")))

            if len(error_list) > 0:
                error_list.insert(0, _('Login failed.'))
            try:
                self.user_cache = user_.user
            except:
                error_list.append(_('This user is not a valid user'))

        elif password == None and username == None:
            error_list.append(_('Please enter username and password'))
        elif password == None:
            error_list.append(_('Please enter your password'))
        elif username == None:
            error_list.append(_('Please enter user name'))
        if len(error_list) > 0:
            self._errors['__all__'] = forms.util.ErrorList(error_list)

        return self.cleaned_data

    def get_user(self):
        """ get authenticated user """
        return self.user_cache