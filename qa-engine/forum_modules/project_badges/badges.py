from django.utils.translation import ugettext as _
from forum.badges.base import AbstractBadge
from forum.models import Badge, Tag
from forum.actions import VoteUpAction
import settings

class BugBuster(AbstractBadge):
    type = Badge.SILVER
    name = _("Bug Buster")
    description = _('Got %s upvotes in a question tagged with "bug"') % settings.BUG_BUSTER_VOTES_UP
    listen_to = (VoteUpAction, )

    def award_to(self, action):
        if action.node.node_type == "question" and action.node.score == settings.BUG_BUSTER_VOTES_UP:
            try:
                bug = Tag.objects.get(name="bug")
                if bug in action.node.tags.all():
                    return action.node.author
            except:
                pass
