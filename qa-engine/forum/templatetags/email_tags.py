from django import template
from forum import settings
from forum.utils.mail import create_and_send_mail_messages
from django.template.defaulttags import url as default_url
import logging

register = template.Library()

class MultiUserMailMessage(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        recipients = context['recipients']
        messages = list()

        for recipient in recipients:
            context['embeddedmedia'] = {}
            context['recipient'] = recipient
            self.nodelist.render(context)
            messages.append((recipient, context['subject'], context['htmlcontent'], context['textcontent'], context['embeddedmedia']))

        create_and_send_mail_messages(messages)

@register.tag
def email(parser, token):
    nodelist = parser.parse(('endemail',))
    parser.delete_first_token()
    return MultiUserMailMessage(nodelist)



class EmailPartNode(template.Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        context[self.varname] = self.nodelist.render(context).strip()

@register.tag
def subject(parser, token):
    nodelist = parser.parse(('endsubject',))
    parser.delete_first_token()
    return EmailPartNode(nodelist, 'subject')

def content(parser, token):
    try:
        tag_name, base = token.split_contents()
    except ValueError:
        try:
            tag_name = token.split_contents()[0]
            base = None
        except:
            raise template.TemplateSyntaxError, "%r tag requires at least two arguments" % token.contents.split()[0]

    nodelist = parser.parse(('end%s' % tag_name,))

    if base:
        base = template.loader.get_template(base)

        basenodes = base.nodelist
        content = [i for i,n in enumerate(basenodes) if isinstance(n, template.loader_tags.BlockNode) and n.name == "content"]
        if len(content):
            index = content[0]
            nodelist = template.NodeList(basenodes[0:index] + nodelist + basenodes[index:])
        

    parser.delete_first_token()
    return EmailPartNode(nodelist, tag_name)


register.tag('htmlcontent', content)
register.tag('textcontent', content)


class EmbedMediaNode(template.Node):
    def __init__(self, location, alias):
        self.location = template.Variable(location)
        self.alias = alias

    def render(self, context):
        context['embeddedmedia'][self.alias] = self.location.resolve(context)
        pass


@register.tag
def embedmedia(parser, token):
    try:
        tag_name, location, _, alias = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly four arguments" % token.contents.split()[0]

    return EmbedMediaNode(location, alias)


class FullUrlNode(template.Node):
    def __init__(self, default_node):
        self.default_node = default_node

    def render(self, context):
        domain = settings.APP_BASE_URL
        path = self.default_node.render(context)
        return "%s%s" % (domain, path)

@register.tag(name='fullurl')
def fullurl(parser, token):
    default_node = default_url(parser, token)
    return FullUrlNode(default_node)





    
    


