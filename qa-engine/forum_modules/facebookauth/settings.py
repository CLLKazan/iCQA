from forum.settings import EXT_KEYS_SET
from forum.settings.base import Setting

FB_API_KEY = Setting('FB_API_KEY', '', EXT_KEYS_SET, dict(
label = "Facebook API key",
help_text = """
Get this key at the <a href="http://www.facebook.com/developers/">Facebook developers network</a> to enable
authentication in your site through facebook.
""",
required=False))

FB_APP_SECRET = Setting('FB_APP_SECRET', '', EXT_KEYS_SET, dict(
label = "Facebook APP secret",
help_text = """
This your facebook app secret that you'll get in the same place as the API key.
""",
required=False))
