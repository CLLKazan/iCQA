from forum.authentication.base import AuthenticationConsumer, ConsumerTemplateContext, InvalidAuthentication
from forms import ClassicLoginForm

class LocalAuthConsumer(AuthenticationConsumer):
    def process_authentication_request(self, request):
        form_auth = ClassicLoginForm(request.POST)

        if form_auth.is_valid():
            return form_auth.get_user()
        else:
            raise InvalidAuthentication(" ".join(form_auth.errors.values()[0]))

class LocalAuthContext(ConsumerTemplateContext):
    mode = 'STACK_ITEM'                      
    weight = 1000
    human_name = 'Local authentication'
    stack_item_template = 'modules/localauth/loginform.html'
    show_to_logged_in_user = False

