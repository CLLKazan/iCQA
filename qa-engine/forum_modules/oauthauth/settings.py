from forum.settings import EXT_KEYS_SET
from forum.settings.base import Setting

TWITTER_CONSUMER_KEY = Setting('TWITTER_CONSUMER_KEY', '', EXT_KEYS_SET, dict(
label = "Twitter consumer key",
help_text = """
Get this key at the <a href="http://twitter.com/apps/">Twitter apps</a> to enable
authentication in your site through Twitter.
""",
required=False))

TWITTER_CONSUMER_SECRET = Setting('TWITTER_CONSUMER_SECRET', '', EXT_KEYS_SET, dict(
label = "Twitter consumer secret",
help_text = """
This your Twitter consumer secret that you'll get in the same place as the consumer key.
""",
required=False))


