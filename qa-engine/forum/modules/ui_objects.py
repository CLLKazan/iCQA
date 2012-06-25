from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django import template
from forum.utils import html
from forum.models.user import AnonymousUser
from ui import Registry
from copy import copy

class Visibility(object):
    def __init__(self, level='public'):
        if level not in ['public', 'authenticated', 'staff', 'superuser', 'owner']:
            try:
                int(level)
                self.by_reputation = True
            except:
                raise "Invalid visibility level for ui object: %s" % level
        else:
            self.by_reputation = False

        self.level = level
        self.negated = False

    def show_to(self, user):
        if self.by_reputation:
            res = user.is_authenticated() and (user.reputation >= int(self.level) or user.is_staff or user.is_superuser)
        else:
            res = self.level == 'public' or (user.is_authenticated() and (
                self.level == 'authenticated' or (
                self.level == 'superuser' and user.is_superuser) or (
                self.level == 'staff' and (user.is_staff or user.is_superuser)) or (
                self.level == 'owner' and user.is_siteowner)))

        if self.negated:
            return not res
        else:
            return res

    def __invert__(self):
        inverted = copy(self)
        inverted.negated = True
        

Visibility.PUBLIC = Visibility('public')
Visibility.AUTHENTICATED = Visibility('authenticated')
Visibility.STAFF = Visibility('staff')
Visibility.SUPERUSER = Visibility('superuser')
Visibility.OWNER = Visibility('owner')
Visibility.REPUTED = lambda r: Visibility(r)


class Url(object):
    def __init__(self, url_pattern):
        self.url_pattern = url_pattern

    def __call__(self, u, c):
        return reverse(self.url_pattern)


class ObjectBase(object):
    class Argument(object):
        def __init__(self, argument):
            self.argument = argument

        def __call__(self, context):
            if callable(self.argument):
                user = context.get('request', None) and context['request'].user or AnonymousUser()
                return self.argument(user, context)
            else:
                return self.argument

    def __init__(self, visibility=None, weight=500):
        self.visibility = visibility
        self.weight = weight

    def _visible_to(self, user):
        return (not self.visibility) or (self.visibility and self.visibility.show_to(user))

    def can_render(self, context):
        try:
            return self._visible_to(context['request'].user)
        except KeyError:
            try:
                return self._visible_to(context['viewer'])
            except KeyError:
                return self._visible_to(AnonymousUser())

    def render(self, context):
        return ''

class LoopBase(ObjectBase):
    def update_context(self, context):
        pass



class Link(ObjectBase):
    def __init__(self, text, url, attrs=None, pre_code='', post_code='', visibility=None, weight=500):
        super(Link, self).__init__(visibility, weight)
        self.text = self.Argument(text)
        self.url = self.Argument(url)
        self.attrs = self.Argument(attrs or {})
        self.pre_code = self.Argument(pre_code)
        self.post_code = self.Argument(post_code)

    def render(self, context):
        return "%s %s %s" % (self.pre_code(context),
            html.hyperlink(self.url(context), self.text(context), **self.attrs(context)),
            self.post_code(context))

class Include(ObjectBase):
    def __init__(self, tpl, visibility=None, weight=500):
        super(Include, self).__init__(visibility, weight)
        self.template = template.loader.get_template(tpl)

    def render(self, context):
        if not isinstance(context, template.Context):
            context = template.Context(context)
        return self.template.render(context)
        

class LoopContext(LoopBase):
    def __init__(self, loop_context, visibility=None, weight=500):
        super(LoopContext, self).__init__(visibility, weight)
        self.loop_context = self.Argument(loop_context)

    def update_context(self, context):
        context.update(self.loop_context(context))


class PageTab(LoopBase):
    def __init__(self, tab_name, tab_title, url_getter, weight):
        super(PageTab, self).__init__(weight=weight)
        self.tab_name = tab_name
        self.tab_title = tab_title
        self.url_getter = url_getter

    def update_context(self, context):
        context.update(dict(
            tab_name=self.tab_name,
            tab_title=self.tab_title,
            tab_url=self.url_getter()
        ))


class ProfileTab(LoopBase):
    def __init__(self, name, title, description, url_getter, private=False, render_to=None, weight=500):
        super(ProfileTab, self).__init__(weight=weight)
        self.name = name
        self.title = title
        self.description = description
        self.url_getter = url_getter
        self.private = private
        self.render_to = render_to

    def can_render(self, context):
        return (not self.render_to or (self.render_to(context['view_user']))) and (
            not self.private or (
            context['view_user'] == context['request'].user or context['request'].user.is_superuser))

    def update_context(self, context):        
        context.update(dict(
            tab_name=self.name,
            tab_title=self.title,
            tab_description = self.description,
            tab_url=self.url_getter(context['view_user'])
        ))


class AjaxMenuItem(ObjectBase):
    def __init__(self, label, url, a_attrs=None, span_label='', span_attrs=None, visibility=None, weight=500):
        super(AjaxMenuItem, self).__init__(visibility, weight)
        self.label = self.Argument(label)
        self.url = self.Argument(url)
        self.a_attrs = self.Argument(a_attrs or {})
        self.span_label = self.Argument(span_label)
        self.span_attrs = self.Argument(span_attrs or {})

    def render(self, context):
        return html.buildtag('li',
            html.buildtag('span', self.span_label(context), **self.span_attrs(context)) + \
            html.hyperlink(self.url(context), self.label(context), **self.a_attrs(context)),
            **{'class': 'item'})

class AjaxMenuGroup(ObjectBase, Registry):
    def __init__(self, label, items, visibility=None, weight=500):
        super(AjaxMenuGroup, self).__init__(visibility, weight)
        self.label = label

        for item in items:
            self.add(item)

    def can_render(self, context):
        if super(AjaxMenuGroup, self).can_render(context):
            for item in self:
                if item.can_render(context): return True

        return False

    def render(self, context):
        return html.buildtag('li', self.label, **{'class': 'separator'}) + "".join([
            item.render(context) for item in self if item.can_render(context)
        ])

class UserMenuItem(AjaxMenuItem):
    def __init__(self, render_to=None, *args, **kwargs):
        super(UserMenuItem, self).__init__(*args, **kwargs)
        self.render_to = render_to

    def can_render(self, context):
        return (not self.render_to or (self.render_to(context['user']))) and super(UserMenuItem, self)._visible_to(context['viewer'])
