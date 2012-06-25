from general import NextUrlField,  UserNameField,  UserEmailField, SetPasswordForm
from forum.models import Question, User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django import forms
import logging

class SimpleRegistrationForm(forms.Form):
    next = NextUrlField()
    username = UserNameField()
    email = UserEmailField()

class TemporaryLoginRequestForm(forms.Form):
    def __init__(self, data=None):
        super(TemporaryLoginRequestForm, self).__init__(data)
        self.user_cache = None

    email = forms.EmailField(
            required=True,
            label=_("Your account email"),
            error_messages={
                'required': _("You cannot leave this field blank"),
                'invalid': _('please enter a valid email address'),
            }
    )

    def clean_email(self):
        users = list(User.objects.filter(email=self.cleaned_data['email']))

        if not len(users):
            raise forms.ValidationError(_("Sorry, but this email is not on our database."))

        self.user_cache = users
        return self.cleaned_data['email']

class ChangePasswordForm(SetPasswordForm):
    """ change password form """
    oldpw = forms.CharField(widget=forms.PasswordInput(attrs={'class':'required'}),
                label=mark_safe(_('Current password')))

    def __init__(self, data=None, user=None, *args, **kwargs):
        if user is None:
            raise TypeError("Keyword argument 'user' must be supplied")
        super(ChangePasswordForm, self).__init__(data, *args, **kwargs)
        self.user = user

    def clean_oldpw(self):
        """ test old password """
        if not self.user.check_password(self.cleaned_data['oldpw']):
            raise forms.ValidationError(_("Old password is incorrect. \
                    Please enter the correct password."))
        return self.cleaned_data['oldpw']
