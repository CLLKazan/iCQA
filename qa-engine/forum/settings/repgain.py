from base import Setting, SettingSet
from django.utils.translation import ugettext_lazy as _

REP_GAIN_SET = SettingSet('repgain', _('Reputation gains and losses config'), _("Configure the reputation points a user may gain or lose upon certain actions."), 200)

INITIAL_REP = Setting('INITIAL_REP', 1, REP_GAIN_SET, dict(
label = _("Initial reputation"),
help_text = _("The initial reputation an user gets when he first signs in.")))

MAX_REP_BY_UPVOTE_DAY = Setting('MAX_REP_BY_UPVOTE_DAY', 200, REP_GAIN_SET, dict(
label = "Max rep by up votes / day",
help_text = _("Maximum reputation a user can gain in one day for being upvoted.")))

REP_GAIN_BY_EMAIL_VALIDATION = Setting('REP_GAIN_BY_EMAIL_VALIDATION', 10, REP_GAIN_SET, dict(
label = _("Rep gain by e-mail validation"),
help_text = _("Reputation a user gains for validating his e-mail.")))

REP_GAIN_BY_UPVOTED = Setting('REP_GAIN_BY_UPVOTED', 10, REP_GAIN_SET, dict(
label = _("Rep gain by upvoted"),
help_text = _("Reputation a user gains for having one of his posts up voted.")))

REP_LOST_BY_DOWNVOTED = Setting('REP_LOST_BY_DOWNVOTED', 2, REP_GAIN_SET, dict(
label = _("Rep lost by downvoted"),
help_text = _("Reputation a user loses for having one of his posts down voted.")))

REP_LOST_BY_DOWNVOTING = Setting('REP_LOST_BY_DOWNVOTING', 1, REP_GAIN_SET, dict(
label = _("Rep lost by downvoting"),
help_text = _("Reputation a user loses for down voting a post.")))


REP_GAIN_BY_ACCEPTED = Setting('REP_GAIN_BY_ACCEPTED', 15, REP_GAIN_SET, dict(
label = _("Rep gain by accepted answer"),
help_text = _("Reputation a user gains for having one of his answers accepted.")))

REP_GAIN_BY_ACCEPTING = Setting('REP_GAIN_BY_ACCEPTING', 2, REP_GAIN_SET, dict(
label = _("Rep gain by accepting answer"),
help_text = _("Reputation a user gains for accepting an answer to one of his questions.")))

REP_LOST_BY_FLAGGED = Setting('REP_LOST_BY_FLAGGED', 2, REP_GAIN_SET, dict(
label = _("Rep lost by post flagged"),
help_text = _("Reputation a user loses by having one of his posts flagged.")))

REP_LOST_BY_FLAGGED_3_TIMES = Setting('REP_LOST_BY_FLAGGED_3_TIMES', 30, REP_GAIN_SET, dict(
label = _("Rep lost by post flagged and hidden"),
help_text = _("Reputation a user loses by having the last revision of one of his posts flagged the enough number of times to hide the post.")))

REP_LOST_BY_FLAGGED_5_TIMES = Setting('REP_LOST_BY_FLAGGED_5_TIMES', 100, REP_GAIN_SET, dict(
label = _("Rep lost by post flagged and deleted"),
help_text = _("Reputation a user loses by having the last revision of one of his posts flagged the enough number of times to delete the post.")))