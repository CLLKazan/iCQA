from base import Setting, SettingSet
from django.utils.translation import ugettext_lazy as _

MIN_REP_SET = SettingSet('minrep', _('Minimum reputation config'), _("Configure the minimum reputation required to perform certain actions on your site."), 300)

CAPTCHA_IF_REP_LESS_THAN = Setting('CAPTCHA_IF_REP_LESS_THAN', 0, MIN_REP_SET, dict(
label = _("Show captcha if user with less reputation than"),
help_text = _("If the user has less reputation, captcha is used to when adding new content.")))

REP_TO_VOTE_UP = Setting('REP_TO_VOTE_UP', 15, MIN_REP_SET, dict(
label = _("Minimum reputation to vote up"),
help_text = _("The minimum reputation an user must have to be allowed to vote up.")))

REP_TO_VOTE_DOWN = Setting('REP_TO_VOTE_DOWN', 100, MIN_REP_SET, dict(
label = _("Minimum reputation to vote down"),
help_text = _("The minimum reputation an user must have to be allowed to vote down.")))

REP_TO_FLAG = Setting('REP_TO_FLAG', 15, MIN_REP_SET, dict(
label = _("Minimum reputation to flag a post"),
help_text = _("The minimum reputation an user must have to be allowed to flag a post.")))

REP_TO_COMMENT = Setting('REP_TO_COMMENT', 50, MIN_REP_SET, dict(
label = _("Minimum reputation to comment"),
help_text = _("The minimum reputation an user must have to be allowed to comment a post.")))

REP_TO_LIKE_COMMENT = Setting('REP_TO_LIKE_COMMENT', 15, MIN_REP_SET, dict(
label = _("Minimum reputation to like a comment"),
help_text = _("The minimum reputation an user must have to be allowed to \"like\" a comment.")))

REP_TO_UPLOAD = Setting('REP_TO_UPLOAD', 60, MIN_REP_SET, dict(
label = _("Minimum reputation to upload"),
help_text = _("The minimum reputation an user must have to be allowed to upload a file.")))

REP_TO_CREATE_TAGS = Setting('REP_TO_CREATE_TAGS', 250, MIN_REP_SET, dict(
label = _("Minimum reputation to create tags"),
help_text = _("The minimum reputation an user must have to be allowed to create new tags.")))

REP_TO_CLOSE_OWN = Setting('REP_TO_CLOSE_OWN', 250, MIN_REP_SET, dict(
label = _("Minimum reputation to close own question"),
help_text = _("The minimum reputation an user must have to be allowed to close his own question.")))

REP_TO_REOPEN_OWN = Setting('REP_TO_REOPEN_OWN', 500, MIN_REP_SET, dict(
label = _("Minimum reputation to reopen own question"),
help_text = _("The minimum reputation an user must have to be allowed to reopen his own question.")))

REP_TO_RETAG = Setting('REP_TO_RETAG', 500, MIN_REP_SET, dict(
label = _("Minimum reputation to retag others questions"),
help_text = _("The minimum reputation an user must have to be allowed to retag others questions.")))

REP_TO_EDIT_WIKI = Setting('REP_TO_EDIT_WIKI', 750, MIN_REP_SET, dict(
label = _("Minimum reputation to edit wiki posts"),
help_text = _("The minimum reputation an user must have to be allowed to edit community wiki posts.")))

REP_TO_WIKIFY = Setting('REP_TO_WIKIFY', 2000, MIN_REP_SET, dict(
label = _("Minimum reputation to mark post as community wiki"),
help_text = _("The minimum reputation an user must have to be allowed to mark a post as community wiki.")))

REP_TO_EDIT_OTHERS = Setting('REP_TO_EDIT_OTHERS', 2000, MIN_REP_SET, dict(
label = _("Minimum reputation to edit others posts"),
help_text = _("The minimum reputation an user must have to be allowed to edit others posts.")))

REP_TO_CLOSE_OTHERS = Setting('REP_TO_CLOSE_OTHERS', 3000, MIN_REP_SET, dict(
label = _("Minimum reputation to close others posts"),
help_text = _("The minimum reputation an user must have to be allowed to close others posts.")))

REP_TO_DELETE_COMMENTS = Setting('REP_TO_DELETE_COMMENTS', 2000, MIN_REP_SET, dict(
label = _("Minimum reputation to delete comments"),
help_text = _("The minimum reputation an user must have to be allowed to delete comments.")))

REP_TO_CONVERT_TO_COMMENT = Setting('REP_TO_CONVERT_TO_COMMENT', 2000, MIN_REP_SET, dict(
label = _("Minimum reputation to convert answers to comment"),
help_text = _("The minimum reputation an user must have to be allowed to convert an answer into a comment.")))

REP_TO_CONVERT_COMMENTS_TO_ANSWERS = Setting('REP_TO_CONVERT_COMMENTS_TO_ANSWERS', 2000, MIN_REP_SET, dict(
label = _("Minimum reputation to convert comments to answers"),
help_text = _("The minimum reputation an user must have to be allowed to convert comments into an answer.")))

REP_TO_CONVERT_TO_QUESTION = Setting('REP_TO_CONVERT_TO_QUESTION', 2000, MIN_REP_SET, dict(
label = _("Minimum reputation to convert answers to questions"),
help_text = _("The minimum reputation an user must have to be allowed to convert an answer into a question.")))

REP_TO_VIEW_FLAGS = Setting('REP_TO_VIEW_FLAGS', 2000, MIN_REP_SET, dict(
label = _("Minimum reputation to view offensive flags"),
help_text = _("The minimum reputation an user must have to view offensive flags.")))

#REP_TO_DISABLE_NOFOLLOW = Setting('REP_TO_DISABLE_NOFOLLOW', 2000, MIN_REP_SET, dict(
#label = _("Minimum reputation to disable nofollow"),
#help_text = _("""
#The minimum reputation an user must have to be allowed to disable the nofollow attribute of a post link.
#""")))
