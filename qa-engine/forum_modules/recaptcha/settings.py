from forum.settings import EXT_KEYS_SET
from forum.settings.base import Setting

RECAPTCHA_PUB_KEY = Setting('RECAPTCHA_PUB_KEY', '', EXT_KEYS_SET, dict(
label = "Recaptch public key",
help_text = """
Get this key at <a href="http://recaptcha.net">reCaptcha</a> to enable
recaptcha anti spam through.
""",
required=False))

RECAPTCHA_PRIV_KEY = Setting('RECAPTCHA_PRIV_KEY', '', EXT_KEYS_SET, dict(
label = "Recaptch private key",
help_text = """
This is the private key you'll get in the same place as the recaptcha public key.
""",
required=False))
