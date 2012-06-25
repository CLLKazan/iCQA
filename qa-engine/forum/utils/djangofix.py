import re
import urllib
from forum.modules import decorate

from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.http import urlquote_plus

slug_re = re.compile(r'\w+', re.UNICODE)

@decorate(slugify)
def imp_slugify(origin, value):
    if settings.ALLOW_UNICODE_IN_SLUGS:
        try:
            bits = slug_re.findall(value.lower())
            return mark_safe("-".join(bits))
        except:
            pass
    return origin(value)

from forum import settings