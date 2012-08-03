from base import Setting, SettingSet
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _

ACCEPT_SET = SettingSet('accept', _('Accepting answers'), _("Settings to tweak the behaviour of accepting answers."), 500)

DISABLE_ACCEPTING_FEATURE = Setting('DISABLE_ACCEPTING_FEATURE', False, ACCEPT_SET, dict(
label = _("Disallow answers to be accepted"),
help_text = _("Disable accepting answers feature. If you re-enable it in the future, currently accepted answers will still be marked as accepted."),
required=False))

MAXIMUM_ACCEPTED_ANSWERS = Setting('MAXIMUM_ACCEPTED_ANSWERS', 1, ACCEPT_SET, dict(
label = _("Maximum accepted answers per question"),
help_text = _("How many accepted answers are allowed per question. Use 0 for no limit.")))

MAXIMUM_ACCEPTED_PER_USER = Setting('MAXIMUM_ACCEPTED_PER_USER', 1, ACCEPT_SET, dict(
label = _("Maximum accepted answers per user/question"),
help_text = _("If more than one accpeted answer is allowed, how many can be accepted per single user per question.")))

USERS_CAN_ACCEPT_OWN = Setting('USERS_CAN_ACCEPT_OWN', False, ACCEPT_SET, dict(
label = _("Users an accept own answer"),
help_text = _("Are normal users allowed to accept their own answers.."),
required=False))


