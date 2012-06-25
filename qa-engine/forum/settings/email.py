from base import Setting, SettingSet
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import PasswordInput
from django.forms.widgets import RadioSelect
from forms import TestEmailSettingsWidget

EMAIL_SET = SettingSet('email', _('Email settings'), _("Email server and other email related settings."), 50)

TEST_EMAIL_SETTINGS = Setting('TEST_EMAIL_SETTINGS', '', EMAIL_SET, dict(
label = _("E-Mail settings test"),
help_text = _("Test the current E-Mail configuration."),
required=False,
widget=TestEmailSettingsWidget))

EMAIL_HOST = Setting('EMAIL_HOST', '', EMAIL_SET, dict(
label = _("Email Server"),
help_text = _("The SMTP server through which your application will be sending emails."),
required=False))

EMAIL_PORT = Setting('EMAIL_PORT', 25, EMAIL_SET, dict(
label = _("Email Port"),
help_text = _("The port on which your SMTP server is listening to. Usually this is 25, but can be something else."),
required=False))

EMAIL_HOST_USER = Setting('EMAIL_HOST_USER', '', EMAIL_SET, dict(
label = _("Email User"),
help_text = _("The username for your SMTP connection."),
required=False))

EMAIL_HOST_PASSWORD = Setting('EMAIL_HOST_PASSWORD', '', EMAIL_SET, dict(
label = _("Email Password"),
help_text = _("The password for your SMTP connection."),
required=False,
widget=PasswordInput))

EMAIL_USE_TLS = Setting('EMAIL_USE_TLS', False, EMAIL_SET, dict(
label = _("Use TLS"),
help_text = _("Whether to use TLS for authentication with your SMTP server."),
required=False))

DEFAULT_FROM_EMAIL = Setting('DEFAULT_FROM_EMAIL', '', EMAIL_SET, dict(
label = _("Site 'from' Email Address"),
help_text = _("The address that will show up on the 'from' field on emails sent by your website."),
required=False))

EMAIL_SUBJECT_PREFIX = Setting('EMAIL_SUBJECT_PREFIX', '', EMAIL_SET, dict(
label = _("Email Subject Prefix"),
help_text = _("Every email sent through your website will have the subject prefixed by this string. It's usually a good idea to have such a prefix so your users can easily set up a filter on theyr email clients."),
required=False))

EMAIL_FOOTER_TEXT = Setting(u'EMAIL_FOOTER_TEXT', '', EMAIL_SET, dict(
label = _("Email Footer Text"),
help_text = _("Email footer text, usually \"CAN SPAM\" compliance, or the physical address of the organization running the website. See <a href=\"http://en.wikipedia.org/wiki/CAN-SPAM_Act_of_2003\">this Wikipedia article</a> for more info."),
required=False))

EMAIL_BORDER_COLOR = Setting('EMAIL_BORDER_COLOR', '#e5ebf8', EMAIL_SET, dict(
label = _("Email Border Color"),
help_text = _("The outter border color of the email base template"),
required=False))

EMAIL_PARAGRAPH_STYLE = Setting('EMAIL_PARAGRAPH_STYLE', "color:#333333;font-family:'helvetica neue', arial, Helvetica, sans-serif;line-height:18px;font-size:14px;margin-top:10px;", EMAIL_SET, dict(
label = _("Email Paragraph Style"),
help_text = _("A valid css string to be used to style email paragraphs (the P tag)."),
required=False))

EMAIL_ANCHOR_STYLE = Setting('EMAIL_ANCHOR_STYLE', "text-decoration:none;color:#3060a8;font-weight:bold;", EMAIL_SET, dict(
label = _("Email Link Style"),
help_text = _("A valid css string to be used to style email links (the A tag)."),
required=False))



EMAIL_DIGEST_FLAG = Setting('EMAIL_DIGEST_FLAG', None)
