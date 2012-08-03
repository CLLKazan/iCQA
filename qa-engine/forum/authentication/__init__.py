import re
import django.dispatch
from forum.modules import get_modules_script_classes
from forum.authentication.base import AuthenticationConsumer, ConsumerTemplateContext

class ConsumerAndContext:
    def __init__(self, id, consumer, context):
        self.id = id
        self._consumer = consumer

        if context:
            context.id = id
        self.context = context

    @property
    def consumer(self):
        return self._consumer()

consumers = dict([
            (re.sub('AuthConsumer$', '', name).lower(), cls) for name, cls
            in get_modules_script_classes('authentication', AuthenticationConsumer).items()
            if not re.search('AbstractAuthConsumer$', name)
        ])

contexts = dict([
            (re.sub('AuthContext$', '', name).lower(), cls) for name, cls
            in get_modules_script_classes('authentication', ConsumerTemplateContext).items()
        ])

AUTH_PROVIDERS = dict([
            (name, ConsumerAndContext(name, consumers[name], contexts.get(name, None))) for name in consumers.keys()
        ])


