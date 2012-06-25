from base import Setting, SettingSet
from django.utils.translation import ugettext_lazy as _

""" view settings """
VIEW_SET = SettingSet('view', _('View settings'), _("Set up how certain parts of the site are displayed."), 20)

SUMMARY_LENGTH = Setting('SUMMARY_LENGTH', 300, VIEW_SET, dict(
label = _("Summary Length"),
help_text = _("The number of characters that are going to be displayed in order to get the content summary.")))

RECENT_TAGS_SIZE = Setting('RECENT_TAGS_SIZE', 25, VIEW_SET, dict(
label = _("Recent tags block size"),
help_text = _("The number of tags to display in the recent tags block in the front page.")))

RECENT_AWARD_SIZE = Setting('RECENT_AWARD_SIZE', 15, VIEW_SET, dict(
label = _("Recent awards block size"),
help_text = _("The number of awards to display in the recent awards block in the front page.")))

LIMIT_RELATED_TAGS = Setting('LIMIT_RELATED_TAGS', 0, VIEW_SET, dict(
label = _("Limit related tags block"),
help_text = _("Limit related tags block size in questions list pages. Set to 0 to display all all tags.")))