from django import template
from django.conf import settings
from forum.modules import ui
import logging

register = template.Library()


class LoadRegistryNode(template.Node):
    def __init__(self, registry, separator):
        self.registry = registry
        self.separator = separator

    def render(self, context):
        separator = self.separator.render(context)
        result = ''

        for ui_object in self.registry:
            try:
                if ui_object.can_render(context):
                        if result:
                            result += separator
                        result += ui_object.render(context)
            except (KeyError, Exception), e:
                if settings.DEBUG:
                    import traceback
                    logging.error("Exception %s rendering ui objects %s: \n%s" % (
                        e, ui_object, traceback.format_exc()
                    ))

        return result


@register.tag
def loadregistry(parser, token):
    try:
        tag_name, registry = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly one argument" % token.contents.split()[0]

    registry = ui.get_registry_by_name(registry)
    separator = parser.parse(('endloadregistry',))
    parser.delete_first_token()
    return LoadRegistryNode(registry, separator)


class LoopRegistryNode(template.Node):
    def __init__(self, registry, nodelist):
        self.registry = registry
        self.nodelist = nodelist

    def render(self, context):
        result = ''

        for ui_object in self.registry:
            if ui_object.can_render(context):
                try:
                    ui_object.update_context(context)
                    result += self.nodelist.render(context)
                except Exception, e:
                    import traceback
                    logging.error("Exception %s updating ui loop context %s: \n%s" % (
                        e, ui_object, traceback.format_exc()
                    ))


        return result

@register.tag
def loopregistry(parser, token):
    try:
        tag_name, registry = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly one argument" % token.contents.split()[0]

    registry = ui.get_registry_by_name(registry)
    nodelist = parser.parse(('endloopregistry',))
    parser.delete_first_token()

    return LoopRegistryNode(registry, nodelist)