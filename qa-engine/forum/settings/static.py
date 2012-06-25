from base import Setting, SettingSet
from django.forms.widgets import Textarea, RadioSelect, Select
from django.utils.translation import ugettext_lazy as _

RENDER_CHOICES = (
('markdown', _('Markdown')),
('html', _('HTML')),
('escape', _('Escaped'))
)

STATIC_PAGE_REGISTRY = Setting('STATIC_PAGE_REGISTRY', {})

CSS_SET = SettingSet('css', 'Custom CSS', "Define some custom css you can use to override the default css.", 2000,
                     can_preview=True)

USE_CUSTOM_CSS = Setting('USE_CUSTOM_CSS', False, CSS_SET, dict(
        label = _("Use custom CSS"),
        help_text = _("Do you want to use custom CSS."),
        required=False))

CUSTOM_CSS = Setting('CUSTOM_CSS', '', CSS_SET, dict(
        label = _("Custom CSS"),
        help_text = _("Your custom CSS."),
        widget=Textarea(attrs={'rows': '25'}),
        required=False))

HEAD_AND_FOOT_SET = SettingSet('headandfoot', 'Header and Footer', "Adds a custom header and/or footer to your page",
                               2000, can_preview=True)

USE_CUSTOM_HEADER = Setting('USE_CUSTOM_HEADER', False, HEAD_AND_FOOT_SET, dict(
        label = _("Use custom header"),
        help_text = _("Do you want to use a custom header."),
        required=False))

CUSTOM_HEADER = Setting('CUSTOM_HEADER', '', HEAD_AND_FOOT_SET, dict(
        label = _("Custom Header"),
        help_text = _("Your custom header."),
        widget=Textarea(attrs={'rows': '25'}),
        required=False))

CUSTOM_HEADER_RENDER_MODE = Setting('CUSTOM_HEADER_RENDER_MODE', 'markdown', HEAD_AND_FOOT_SET, dict(
        label = _("Custom Header rendering mode"),
        help_text = _("How to render your custom header code."),
        widget=Select(choices=RENDER_CHOICES),
        required=False))

USE_ANNOUNCEMENT_BAR = Setting('USE_ANNOUNCEMENT_BAR', False, HEAD_AND_FOOT_SET, dict(
        label = _("Show announcement bar"),
        help_text = _("Some piece of content that goes under the search bar and can be used for announcements, etc."),
        required=False))

ANNOUNCEMENT_BAR = Setting('ANNOUNCEMENT_BAR', '', HEAD_AND_FOOT_SET, dict(
        label = _("Announcement bar"),
        help_text = _("The announcement bar content."),
        widget=Textarea(attrs={'rows': '25'}),
        required=False))

ANNOUNCEMENT_BAR_RENDER_MODE = Setting('ANNOUNCEMENT_BAR_RENDER_MODE', 'markdown', HEAD_AND_FOOT_SET, dict(
        label = _("Announcement bar rendering mode"),
        help_text = _("How to render your announcement bar code."),
        widget=Select(choices=RENDER_CHOICES),
        required=False))

USE_CUSTOM_FOOTER = Setting('USE_CUSTOM_FOOTER', False, HEAD_AND_FOOT_SET, dict(
        label = _("Use custom footer"),
        help_text = _("Do you want to use a custom footer."),
        required=False))

CUSTOM_FOOTER = Setting('CUSTOM_FOOTER', '', HEAD_AND_FOOT_SET, dict(
        label = _("Custom Footer"),
        help_text = _("Your custom footer."),
        widget=Textarea(attrs={'rows': '25'}),
        required=False))

CUSTOM_FOOTER_RENDER_MODE = Setting('CUSTOM_FOOTER_RENDER_MODE', 'markdown', HEAD_AND_FOOT_SET, dict(
        label = _("Custom footer rendering mode"),
        help_text = _("How to render your custom footer code."),
        widget=Select(choices=RENDER_CHOICES),
        required=False))

CUSTOM_FOOTER_MODE_CHOICES = (
('replace', _('Replace default footer')),
('above', _('Above default footer')),
('below', _('Below default footer')),
)

CUSTOM_FOOTER_MODE = Setting('CUSTOM_FOOTER_MODE', 'replace', HEAD_AND_FOOT_SET, dict(
        label = _("Custom Footer Mode"),
        help_text = _("How your custom footer will appear."),
        widget=RadioSelect,
        choices=CUSTOM_FOOTER_MODE_CHOICES,
        required=False))

HEAD_SET = SettingSet('head', '<head>', "Define some custom elements to include in the head section of every page.",
                      2000, can_preview=True)

USE_CUSTOM_HEAD = Setting('USE_CUSTOM_HEAD', False, HEAD_SET, dict(
        label = _("Use custom Head elements"),
        help_text = _("Do you want to use custom head elements."),
        required=False))

CUSTOM_HEAD = Setting('CUSTOM_HEAD', '', HEAD_SET, dict(
        label = _("Custom Head"),
        help_text = _("Your custom Head elements."),
        widget=Textarea(attrs={'rows': '25'}),
        required=False))