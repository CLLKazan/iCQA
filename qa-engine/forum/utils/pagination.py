import math
from django.utils.datastructures import SortedDict
from django import template
from django.core.paginator import Paginator, EmptyPage
from django.utils.translation import ugettext as _
from django.http import Http404
from django.utils.http import urlquote
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags, escape
from forum.utils.html import sanitize_html
import logging

def generate_uri(querydict, exclude=None):
    all = []

    for k, l in querydict.iterlists():
        if (not exclude) or (not k in exclude):
            all += ["%s=%s" % (k, urlquote(strip_tags(v))) for v in l]
        
    return "&".join(all)

class SortBase(object):
    def __init__(self, label, description=''):
        self.label = label
        self.description = description

class SimpleSort(SortBase):
    def __init__(self, label, order_by, description=''):
        super(SimpleSort, self) .__init__(label, description)
        self.order_by = order_by

    def _get_order_by(self):
        return isinstance(self.order_by, (list, tuple)) and self.order_by or [self.order_by]

    def apply(self, objects):
        return objects.order_by(*self._get_order_by())

class PaginatorContext(object):
    visible_page_range = 5
    outside_page_range = 1

    base_path = None

    def __init__(self, id, sort_methods=None, default_sort=None, force_sort = None,
                 pagesizes=None, default_pagesize=None, prefix=''):
        self.id = id
        if sort_methods:
            self.has_sort = True
            self.sort_methods = SortedDict(data=sort_methods)

            if not default_sort:
                default_sort = sort_methods[0][0]

            self.default_sort = default_sort
        else:
            self.has_sort = False


        if pagesizes:
            self.has_pagesize = True
            self.pagesizes = pagesizes

            if not default_pagesize:
                self.default_pagesize = pagesizes[int(math.ceil(float(len(pagesizes)) / 2)) - 1]
            else:
                self.default_pagesize = default_pagesize
        else:
            self.has_pagesize = False

        self.force_sort = force_sort
        self.prefix = prefix

    def preferences(self, request):
        if request.user.is_authenticated():
            if request.user.prop.pagination:
                preferences = request.user.prop.pagination.get(self.id, {})
            else:
                preferences = {}
        else:
            preferences = request.session.get('paginator_%s%s' % (self.prefix, self.id), {})

        return preferences

    def set_preferences(self, request, preferences):
        if request.user.is_authenticated():
            all_preferences = request.user.prop.pagination or {}
            all_preferences[self.id] = preferences
            request.user.prop.pagination = all_preferences
        else:
            request.session['paginator_%s%s' % (self.prefix, self.id)] = preferences

    def pagesize(self, request, session_prefs=None):
        if not session_prefs:
            session_prefs = self.preferences(request)


        if self.has_pagesize:
            if request.GET.get(self.PAGESIZE, None):
                try:
                    pagesize = int(request.GET[self.PAGESIZE])
                except ValueError:
                    logging.error('Found invalid page size "%s", loading %s, refered by %s' % (
                        request.GET.get(self.PAGESIZE, ''), request.path, request.META.get('HTTP_REFERER', 'UNKNOWN')
                    ))
                    raise Http404()

                session_prefs[self.PAGESIZE] = pagesize
            else:
                pagesize = session_prefs.get(self.PAGESIZE, self.default_pagesize)

            if not pagesize in self.pagesizes:
                pagesize = self.default_pagesize
        else:
            pagesize = 30

        return pagesize

    def page(self, request):
        try:
            return int(request.GET.get(self.PAGE, "1").strip())
        except ValueError:
            logging.error('Found invalid page number "%s", loading %s, refered by %s' % (
                request.GET.get(self.PAGE, ''), request.path, request.META.get('HTTP_REFERER', 'UNKNOWN')
            ))
            raise Http404()

    def sort(self, request, session_prefs=None):
        if not session_prefs:
            session_prefs = self.preferences(request)

        sort = None
        sticky = request.user.is_authenticated() and request.user.prop.preferences and request.user.prop.preferences.get('sticky_sorts', False)

        if self.has_sort:
            if request.GET.get(self.SORT, None):
                sort = request.GET[self.SORT]

                if sticky:
                    session_prefs[self.SORT] = sort
            else:
                sort = self.force_sort or (sticky and session_prefs.get(self.SORT, None)) or self.default_sort

            if not sort in self.sort_methods:
                sort = self.default_sort

        return sort

    def sorted(self, objects, request, session_prefs=None):
        sort = self.sort(request, session_prefs)

        if sort:
            objects = self.sort_methods[sort].apply(objects)

        return sort, objects

    @property
    def PAGESIZE(self):
        return self.prefix and "%s_%s" % (self.prefix, _('pagesize')) or _('pagesize')

    @property
    def PAGE(self):
        return self.prefix and "%s_%s" % (self.prefix, _('page')) or _('page')

    @property
    def SORT(self):
        return self.prefix and "%s_%s" % (self.prefix, _('sort')) or _('sort')

page_numbers_template = template.loader.get_template('paginator/page_numbers.html')
page_sizes_template = template.loader.get_template('paginator/page_sizes.html')
sort_tabs_template = template.loader.get_template('paginator/sort_tabs.html')

def paginated(request, paginators, tpl_context):
    if len(paginators) == 2 and isinstance(paginators[0], basestring):
        paginators = (paginators,)

    for list_name, context in paginators:
        tpl_context[list_name] = _paginated(request, tpl_context[list_name], context)

    return tpl_context

def _paginated(request, objects, context):
    session_prefs = context.preferences(request)

    pagesize = context.pagesize(request, session_prefs)
    page = context.page(request)
    sort, objects = context.sorted(objects, request, session_prefs)

    paginator = Paginator(objects, pagesize)

    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        logging.error('Found invalid page number "%s", loading %s, refered by %s' % (
            request.GET.get(context.PAGE, ''), request.path, request.META.get('HTTP_REFERER', 'UNKNOWN')
        ))
        raise Http404()

    if context.base_path:
        base_path = context.base_path
    else:
        base_path = request.path
        get_params = generate_uri(request.GET, (context.PAGE, context.PAGESIZE, context.SORT))

        if get_params:
            base_path += "?" + get_params

    url_joiner = "?" in base_path and "&" or "?"


    def get_page():
        object_list = page_obj.object_list

        if hasattr(object_list, 'lazy'):
            return object_list.lazy()
        return object_list
    paginator.page = get_page()

    total_pages = paginator.num_pages

    if total_pages > 1:
        def page_nums():
            total_pages = paginator.num_pages

            has_previous = page > 1
            has_next = page < total_pages

            range_start = page - context.visible_page_range / 2
            range_end = page + context.visible_page_range / 2

            if range_start < 1:
                range_end = context.visible_page_range
                range_start = 1

            if range_end > total_pages:
                range_start = total_pages - context.visible_page_range + 1
                range_end = total_pages
                if range_start < 1:
                    range_start = 1

            page_numbers = []

            if sort:
                url_builder = lambda n: mark_safe("%s%s%s=%s&%s=%s" % (base_path, url_joiner, context.SORT, sort, context.PAGE, n))
            else:
                url_builder = lambda n: mark_safe("%s%s%s=%s" % (base_path, url_joiner, context.PAGE, n))

            if range_start > (context.outside_page_range + 1):
                page_numbers.append([(n, url_builder(n)) for n in range(1, context.outside_page_range + 1)])
                page_numbers.append(None)
            elif range_start > 1:
                page_numbers.append([(n, url_builder(n)) for n in range(1, range_start)])

            page_numbers.append([(n, url_builder(n)) for n in range(range_start, range_end + 1)])

            if range_end < (total_pages - context.outside_page_range):
                page_numbers.append(None)
                page_numbers.append([(n, url_builder(n)) for n in range(total_pages - context.outside_page_range + 1, total_pages + 1)])
            elif range_end < total_pages:
                page_numbers.append([(n, url_builder(n)) for n in range(range_end + 1, total_pages + 1)])

            return page_numbers_template.render(template.Context({
                'has_previous': has_previous,
                'previous_url': has_previous and url_builder(page - 1) or None,
                'has_next': has_next,
                'next_url': has_next and url_builder(page + 1) or None,
                'current': page,
                'page_numbers': page_numbers
            }))
        paginator.page_numbers = page_nums
    else:
        paginator.page_numbers = ''

    if pagesize:
        def page_sizes():
            if sort:
                url_builder = lambda s: mark_safe("%s%s%s=%s&%s=%s" % (escape(base_path), url_joiner, context.SORT, sort, context.PAGESIZE, s))
            else:
                url_builder = lambda s: mark_safe("%s%s%s=%s" % (escape(base_path), url_joiner, context.PAGESIZE, s))

            sizes = [(s, url_builder(s)) for s in context.pagesizes]

            return page_sizes_template.render(template.Context({
                'current': pagesize,
                'sizes': sizes
            }))

        paginator.page_sizes = page_sizes
    else:
        paginator.page_sizes = ''

    if sort:
        def sort_tabs():
            url_builder = lambda s: mark_safe("%s%s%s=%s" % (escape(base_path), url_joiner, context.SORT, s))
            sorts = [(n, s.label, url_builder(n), strip_tags(s.description)) for n, s in context.sort_methods.items()]

            for name, label, url, descr in sorts:
                paginator.__dict__['%s_sort_link' % name] = url

            return sort_tabs_template.render(template.Context({
                'current': sort,
                'sorts': sorts,
                'sticky': session_prefs.get('sticky_sort', False)
            }))
        paginator.sort_tabs = sort_tabs()
        paginator.sort_description = mark_safe(context.sort_methods[sort].description)
        paginator.current_sort = sort
    else:
        paginator.sort_tabs = paginator.sort_description = ''
        paginator.current_sort = ''

    context.set_preferences(request, session_prefs)
    objects.paginator = paginator
    return objects
