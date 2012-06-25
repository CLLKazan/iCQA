import os.path
from base import Setting, SettingSet
from django.utils.translation import ugettext_lazy as _

FORUM_SET = SettingSet('form', _('Form settings'), _("General settings for the OSQA forms."), 10)

WIKI_ON = Setting('WIKI_ON', True, FORUM_SET, dict(
label = _("Enable community wiki"),
help_text = _("Can questions or answers be marked as community wiki."),
required=False))

LIMIT_TAG_CREATION = Setting('LIMIT_TAG_CREATION', False, FORUM_SET, dict(
label = _("Limit tag creation"),
help_text = _("Limit tag creation to super users, staff or users with a minimum reputation."),
required=False))


""" settings for questions """
FORM_MIN_QUESTION_TITLE = Setting('FORM_MIN_QUESTION_TITLE', 10, FORUM_SET, dict(
label = _("Minimum number of characters for a question's title"),
help_text = _("The minimum number of characters a user must enter into the title field of a question.")))

# FORM_MAX_QUESTION_TITLE = Setting('FORM_MAX_QUESTION_TITLE', 100, FORUM_SET, dict(
# label = _("Maximum number of characters for a question."),
# help_text = _("The maximum number of characters a user can enter into the description field to submit a question.")))

FORM_MIN_QUESTION_BODY = Setting('FORM_MIN_QUESTION_BODY', 10, FORUM_SET, dict(
label = _("Minimum number of characters for a question's content"),
help_text = _("The minimum number of characters a user must enter into the content field of a question.")))

# FORM_MAX_QUESTION_DESCRIPTION = Setting('FORM_MAX_QUESTION_DESCRIPTION', 600, FORUM_SET, dict(
# label = _("Maximum number of characters for a question."),
# help_text = _("The maximum number of characters a user can enter into the description field to submit a question.")))

FORM_EMPTY_QUESTION_BODY = Setting('FORM_EMPTY_QUESTION_BODY', False, FORUM_SET, dict(
label = _("Empty question content"),
help_text = _("If a question's content can be empty."),
required=False))




""" settings for tags """
FORM_MIN_NUMBER_OF_TAGS = Setting('FORM_MIN_NUMBER_OF_TAGS', 1, FORUM_SET, dict(
label = _("Required number of tags per question"),
help_text = _("How many tags are required in questions."),
))

FORM_MAX_NUMBER_OF_TAGS = Setting('FORM_MAX_NUMBER_OF_TAGS', 5, FORUM_SET, dict(
label = _("Maximum number of tags per question"),
help_text = _("How many tags are allowed in questions."),
))

FORM_MIN_LENGTH_OF_TAG = Setting('FORM_MIN_LENGTH_OF_TAG', 1, FORUM_SET, dict(
label = _("Minimum length of a tag"),
help_text = _("How short a tag can be."),
))

FORM_MAX_LENGTH_OF_TAG = Setting('FORM_MAX_LENGTH_OF_TAG', 20, FORUM_SET, dict(
label = _("Maximum length of a tag"),
help_text = _("How long a tag can be."),
))




""" settings for comments """
FORM_MIN_COMMENT_BODY = Setting('FORM_MIN_COMMENT_BODY', 10, FORUM_SET, dict(
label = _("Minimum number of characters for a comment"),
help_text = _("The minimum number of characters a user must enter into the body of a comment.")))

FORM_MAX_COMMENT_BODY = Setting('FORM_MAX_COMMENT_BODY', 600, FORUM_SET, dict(
label = _("Maximum length of comment"),
help_text = _("The maximum number of characters a user can enter into the body of a comment.")))

FORM_ALLOW_MARKDOWN_IN_COMMENTS = Setting('FORM_ALLOW_MARKDOWN_IN_COMMENTS', True, FORUM_SET, dict(
label = _("Allow markdown in comments"),
help_text = _("Allow users to use markdown in comments."),
required=False))

FORM_GRAVATAR_IN_COMMENTS = Setting('FORM_GRAVATAR_IN_COMMENTS', False, FORUM_SET, dict(
label = _("Show author gravatar in comments"),
help_text = _("Show the gravatar image of a comment author."),
required=False))



