from django import template
from forum.models import Tag, Award
from forum import settings

from extra_filters import static_content

register = template.Library()

@register.inclusion_tag('sidebar/markdown_help.html')
def markdown_help():
    return {}

@register.inclusion_tag('sidebar/recent_awards.html')
def recent_awards():
    return {'awards': Award.objects.order_by('-awarded_at')[:settings.RECENT_AWARD_SIZE]}

@register.inclusion_tag('sidebar/user_blocks.html')
def sidebar_upper():
    return {
        'show': settings.SIDEBAR_UPPER_SHOW,
        'content': static_content(settings.SIDEBAR_UPPER_TEXT, settings.SIDEBAR_UPPER_RENDER_MODE),
        'wrap': not settings.SIDEBAR_UPPER_DONT_WRAP,
        'blockid': 'sidebar-upper'
    }

@register.inclusion_tag('sidebar/user_blocks.html')
def sidebar_lower():
    return {
        'show': settings.SIDEBAR_LOWER_SHOW,
        'content': static_content(settings.SIDEBAR_LOWER_TEXT, settings.SIDEBAR_LOWER_RENDER_MODE),
        'wrap': not settings.SIDEBAR_LOWER_DONT_WRAP,
        'blockid': 'sidebar-lower'
    }

@register.inclusion_tag('sidebar/recent_tags.html')
def recent_tags():
    return {'tags': Tag.active.order_by('-id')[:settings.RECENT_TAGS_SIZE]}

    