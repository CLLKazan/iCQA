from forum.settings import BADGES_SET
from forum.settings.base import Setting
from django.utils.translation import ugettext_lazy as _

POPULAR_QUESTION_VIEWS = Setting('POPULAR_QUESTION_VIEWS', 1000, BADGES_SET, dict(
label = _("Popular Question views"),
help_text = _("""
Number of question views required to award a Popular Question badge to the question author
""")))

NOTABLE_QUESTION_VIEWS = Setting('NOTABLE_QUESTION_VIEWS', 2500, BADGES_SET, dict(
label = _("Notable Question views"),
help_text = _("""
Number of question views required to award a Notable Question badge to the question author
""")))

FAMOUS_QUESTION_VIEWS = Setting('FAMOUS_QUESTION_VIEWS', 10000, BADGES_SET, dict(
label = _("Famous Question views"),
help_text = _("""
Number of question views required to award a Famous Question badge to the question author
""")))

NICE_ANSWER_VOTES_UP = Setting('NICE_ANSWER_VOTES_UP', 10, BADGES_SET, dict(
label = _("Nice Answer up votes"),
help_text = _("""
Number of up votes required to award a Nice Answer badge to the answer author
""")))

NICE_QUESTION_VOTES_UP = Setting('NICE_QUESTION_VOTES_UP', 10, BADGES_SET, dict(
label = _("Nice Question up votes"),
help_text = _("""
Number of up votes required to award a Nice Question badge to the question author
""")))

GOOD_ANSWER_VOTES_UP = Setting('GOOD_ANSWER_VOTES_UP', 25, BADGES_SET, dict(
label = _("Good Answer up votes"),
help_text = _("""
Number of up votes required to award a Good Answer badge to the answer author
""")))

GOOD_QUESTION_VOTES_UP = Setting('GOOD_QUESTION_VOTES_UP', 25, BADGES_SET, dict(
label = _("Good Question up votes"),
help_text = _("""
Number of up votes required to award a Good Question badge to the question author
""")))

GREAT_ANSWER_VOTES_UP = Setting('GREAT_ANSWER_VOTES_UP', 100, BADGES_SET, dict(
label = _("Great Answer up votes"),
help_text = _("""
Number of up votes required to award a Great Answer badge to the answer author
""")))

GREAT_QUESTION_VOTES_UP = Setting('GREAT_QUESTION_VOTES_UP', 100, BADGES_SET, dict(
label = _("Great Question up votes"),
help_text = _("""
Number of up votes required to award a Great Question badge to the question author
""")))

FAVORITE_QUESTION_FAVS = Setting('FAVORITE_QUESTION_FAVS', 25, BADGES_SET, dict(
label = _("Favorite Question favorite count"),
help_text = _("""
How many times a question needs to be favorited by other users to award a Favorite Question badge to the question author
""")))

STELLAR_QUESTION_FAVS = Setting('STELLAR_QUESTION_FAVS', 100, BADGES_SET, dict(
label = _("Stellar Question favorite count"),
help_text = _("""
How many times a question needs to be favorited by other users to award a Stellar Question badge to the question author
""")))

DISCIPLINED_MIN_SCORE = Setting('DISCIPLINED_MIN_SCORE', 3, BADGES_SET, dict(
label = _("Disciplined minimum score"),
help_text = _("""
Minimum score a question needs to have to award the Disciplined badge to an author of a question who deletes it.
""")))

PEER_PRESSURE_MAX_SCORE = Setting('PEER_PRESSURE_MAX_SCORE', -3, BADGES_SET, dict(
label = _("Peer Pressure maximum score"),
help_text = _("""
Maximum score a question needs to have to award the Peer Pressure badge to an author of a question who deletes it.
""")))

CIVIC_DUTY_VOTES = Setting('CIVIC_DUTY_VOTES', 300, BADGES_SET, dict(
label = _("Civic Duty votes"),
help_text = _("""
Number of votes an user needs to cast to be awarded the Civic Duty badge.
""")))

PUNDIT_COMMENT_COUNT = Setting('PUNDIT_COMMENT_COUNT', 10, BADGES_SET, dict(
label = _("Pundit number of comments"),
help_text = _("""
Number of comments an user needs to post to be awarded the Pundit badge.
""")))

SELF_LEARNER_UP_VOTES = Setting('SELF_LEARNER_UP_VOTES', 3, BADGES_SET, dict(
label = _("Self Learner up votes"),
help_text = _("""
Number of up votes an answer from the question author needs to have for the author to be awarded the Self Learner badge.
""")))

STRUNK_AND_WHITE_EDITS = Setting('STRUNK_AND_WHITE_EDITS', 100, BADGES_SET, dict(
label = _("Strunk and White updates"),
help_text = _("""
Number of question or answer updates an user needs to make to be awarded the Strunk & White badge.
""")))

ENLIGHTENED_UP_VOTES = Setting('ENLIGHTENED_UP_VOTES', 10, BADGES_SET, dict(
label = _("Enlightened up votes"),
help_text = _("""
Number of up votes an accepted answer needs to have for the author to be awarded the Enlightened badge.
""")))

GURU_UP_VOTES = Setting('GURU_UP_VOTES', 40, BADGES_SET, dict(
label = _("Guru up votes"),
help_text = _("""
Number of up votes an accepted answer needs to have for the author to be awarded the Guru badge.
""")))

NECROMANCER_UP_VOTES = Setting('NECROMANCER_UP_VOTES', 5, BADGES_SET, dict(
label = _("Necromancer up votes"),
help_text = _("""
Number of up votes an answer needs to have for the author to be awarded the Necromancer badge.
""")))

NECROMANCER_DIF_DAYS = Setting('NECROMANCER_DIF_DAYS', 60, BADGES_SET, dict(
label = _("Necromancer difference in days"),
help_text = _("""
Difference in days betwen the posted date of a question and an answer for the answer author to be awarded the Necromancer badge.
""")))

TAXONOMIST_USE_COUNT = Setting('TAXONOMIST_USE_COUNT', 50, BADGES_SET, dict(
label = _("Taxonomist usage count"),
help_text = _("""
How many usages a tag needs to have for the tag creator to be awarded the Taxonomist badge. 
""")))

