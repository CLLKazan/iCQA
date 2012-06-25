from base import Setting, SettingSet
from django.utils.translation import ugettext_lazy as _

VOTE_RULES_SET = SettingSet('voting', _('Voting rules'), _("Configure the voting rules on your site."), 400)

USER_REPUTATION_TO_MAX_VOTES = Setting('USER_REPUTATION_TO_MAX_VOTES', True, VOTE_RULES_SET, dict(
label = _("Add reputation to max votes per day"), required=False,
help_text = _("The user reputation is added to the static MAX_VOTES_PER_DAY option. Users with higher reputation can vote more.")))

MAX_VOTES_PER_DAY = Setting('MAX_VOTES_PER_DAY', 30, VOTE_RULES_SET, dict(
label = _("Maximum votes per day"),
help_text = _("The maximum number of votes an user can cast per day.")))

START_WARN_VOTES_LEFT = Setting('START_WARN_VOTES_LEFT', 10, VOTE_RULES_SET, dict(
label = _("Start warning about votes left"),
help_text = _("From how many votes left should an user start to be warned about it.")))

MAX_FLAGS_PER_DAY = Setting('MAX_FLAGS_PER_DAY', 5, VOTE_RULES_SET, dict(
label = _("Maximum flags per day"),
help_text = _("The maximum number of times an can flag a post per day.")))

FLAG_COUNT_TO_HIDE_POST = Setting('FLAG_COUNT_TO_HIDE_POST', 3, VOTE_RULES_SET, dict(
label = _("Flag count to hide post"),
help_text = _("How many times a post needs to be flagged to be hidden from the main page.")))

FLAG_COUNT_TO_DELETE_POST = Setting('FLAG_COUNT_TO_DELETE_POST', 5, VOTE_RULES_SET, dict(
label = _("Flag count to delete post"),
help_text = _("How many times a post needs to be flagged to be deleted.")))

DENY_UNVOTE_DAYS = Setting('DENY_UNVOTE_DAYS', 1, VOTE_RULES_SET, dict(
label = _("Days to cancel a vote"),
help_text = _("How many days an user can cancel a vote after he originaly casted it.")))