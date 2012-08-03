import markdown
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags
from forum.utils.html import sanitize_html

class LimitedSyntaxExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        del md.inlinePatterns["image_reference"]

def makeExtension(configs=None) :
    return LimitedSyntaxExtension(configs=configs)
