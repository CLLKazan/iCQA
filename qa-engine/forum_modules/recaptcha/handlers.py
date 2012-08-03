from formfield import ReCaptchaField

def create_anti_spam_field():
    return ('recaptcha', ReCaptchaField())