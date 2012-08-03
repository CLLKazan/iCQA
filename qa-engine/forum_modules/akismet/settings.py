from forum.settings.base import Setting
from forum.settings.extkeys import EXT_KEYS_SET
from forum.settings.minrep import MIN_REP_SET
from django.utils.translation import ugettext_lazy as _

WORDPRESS_API_KEY = Setting('WORDPRESS_API_KEY', '', EXT_KEYS_SET, dict(
label = _("WordPress API key"),
help_text = _("Your WordPress API key. You can get one at <a href='http://wordpress.com/'>http://wordpress.com/</a>"),
required=False))

REP_FOR_NO_SPAM_CHECK = Setting('REP_FOR_NO_SPAM_CHECK', 750, MIN_REP_SET, dict(
label = _("Minimum reputation to not have your posts checked"),
help_text = _("The minimum reputation a user must have so that when they post a question, answer or comment it is not checked for spam.")))
