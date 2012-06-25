from forum.settings import BADGES_SET
from forum.settings.base import Setting

BUG_BUSTER_VOTES_UP = Setting('BUG_BUSTER_VOTES_UP', 3, BADGES_SET, dict(
label = "Bug Buster Votes Up",
help_text = """
Number of votes up required for the author of a question tagged as bug to be awarded the Bug Buster badge.
"""))