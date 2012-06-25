from base import Setting, SettingSet
from django.forms.widgets import Textarea, Select
from django.utils.translation import ugettext_lazy as _

from static import RENDER_CHOICES

SIDEBAR_SET = SettingSet('sidebar', 'Sidebar content', "Enter contents to display in the sidebar. You can use markdown and some basic html tags.", 10, True)

SHOW_WELCOME_BOX = Setting('SHOW_WELCOME_BOX', True, SIDEBAR_SET, dict(
label = _("Show the Welcome box"),
help_text = _("Do you want to show the welcome box when a user first visits your site."),
required=False))

APP_INTRO = Setting('APP_INTRO', u'<p>Ask and answer questions, make the world better!</p>', SIDEBAR_SET, dict(
label = _("Application intro"),
help_text = _("The introductory page that is visible in the sidebar for anonymous users."),
widget=Textarea))

QUESTION_TITLE_TIPS = Setting('QUESTION_TITLE_TIPS',
u"""
 - **ask a question relevant to the |APP_TITLE| community**
 - the title must be in the form of a question
 - provide enough details
 - be clear and concise
"""
, SIDEBAR_SET, dict(
label = "Question title tips",
help_text = "Tips visible on the ask or edit questions page about the question title.",
required=False))

QUESTION_TAG_TIPS = Setting('QUESTION_TAG_TIPS',
u"""
 - Tags are words that will tell others what this question is about.
 - They will help other find your question.
 - A question can have up to |FORM_MAX_NUMBER_OF_TAGS| tags, but it must have at least |FORM_MIN_NUMBER_OF_TAGS|.
"""
, SIDEBAR_SET, dict(
label = "Tagging tips",
help_text = "Tips visible on the ask or edit questions page about good tagging.",
required=False))


SIDEBAR_UPPER_SHOW = Setting('SIDEBAR_UPPER_SHOW', True, SIDEBAR_SET, dict(
label = "Show Upper Block",
help_text = "Check if your pages should display the upper sidebar block.",
required=False))

SIDEBAR_UPPER_DONT_WRAP = Setting('SIDEBAR_UPPER_DONT_WRAP', False, SIDEBAR_SET, dict(
label = "Don't Wrap Upper Block",
help_text = "Don't wrap upper block with the standard style.",
required=False))

SIDEBAR_UPPER_TEXT = Setting('SIDEBAR_UPPER_TEXT',
u"""
[![WebFaction logo][2]][1]
## [Reliable OSQA Hosting][1]

We recommend [**WebFaction**][1] for OSQA hosting. For \
under $10/month their reliable servers get the job done. See our \
[**step-by-step setup guide**](http://wiki.osqa.net/display/docs/Installing+OSQA+on+WebFaction).

[1]: http://www.webfaction.com?affiliate=osqa
[2]: /m/default/media/images/webfaction.png""", SIDEBAR_SET, dict(
label = "Upper Block Content",
help_text = " The upper sidebar block. ",
widget=Textarea(attrs={'rows': '10'})))

SIDEBAR_UPPER_RENDER_MODE = Setting('SIDEBAR_UPPER_RENDER_MODE', 'markdown', SIDEBAR_SET, dict(
label = _("Upper block rendering mode"),
help_text = _("How to render your upper block code."),
widget=Select(choices=RENDER_CHOICES),
required=False))


SIDEBAR_LOWER_SHOW = Setting('SIDEBAR_LOWER_SHOW', True, SIDEBAR_SET, dict(
label = "Show Lower Block",
help_text = "Check if your pages should display the lower sidebar block.",
required=False))

SIDEBAR_LOWER_DONT_WRAP = Setting('SIDEBAR_LOWER_DONT_WRAP', False, SIDEBAR_SET, dict(
label = "Don't Wrap Lower Block",
help_text = "Don't wrap lower block with the standard style.",
required=False))

SIDEBAR_LOWER_TEXT = Setting('SIDEBAR_LOWER_TEXT',
u"""
## Learn more about OSQA

The [**OSQA website**](http://www.osqa.net/) and [**OSQA wiki**](http://wiki.osqa.net/) \
are great resources to help you learn more about the OSQA open source Q&A system. \
[**Join the OSQA chat!**](http://meta.osqa.net/question/79/is-there-an-online-chat-room-or-irc-channel-for-osqa#302)
""", SIDEBAR_SET, dict(
label = "Lower Block Content",
help_text = " The lower sidebar block. ",
widget=Textarea(attrs={'rows': '10'})))

SIDEBAR_LOWER_RENDER_MODE = Setting('SIDEBAR_LOWER_RENDER_MODE', 'markdown', SIDEBAR_SET, dict(
label = _("Lower block rendering mode"),
help_text = _("How to render your lower block code."),
widget=Select(choices=RENDER_CHOICES),
required=False))