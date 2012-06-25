from django import forms
from lib import captcha
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode, smart_unicode
from django.utils.translation import ugettext_lazy as _
import settings

class ReCaptchaField(forms.Field):
    def __init__(self, *args, **kwargs):
        super(ReCaptchaField, self).__init__(widget=ReCaptchaWidget)

    def clean(self, values):
        super(ReCaptchaField, self).clean(values[1])
        recaptcha_challenge_value = smart_unicode(values[0])
        recaptcha_response_value = smart_unicode(values[1])
        check_captcha = captcha.submit(recaptcha_challenge_value,
            recaptcha_response_value, settings.RECAPTCHA_PRIV_KEY, {})

        if not check_captcha.is_valid:
            raise forms.util.ValidationError(_('Invalid captcha'))
            
        return values[0]


class ReCaptchaWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        return mark_safe(force_unicode(captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)))

    def value_from_datadict(self, data, files, name):
        return (data.get('recaptcha_challenge_field', None), data.get('recaptcha_response_field', None))
        

