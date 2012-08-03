from django.conf import settings
from django.template.loaders import filesystem
from django.template import TemplateDoesNotExist, Template as DJTemplate
from django.conf import settings as djsettings
import os.path
import logging

UNEXISTENT_TEMPLATE = object()

SKINS_FOLDER = os.path.dirname(__file__)
SKIN_TEMPLATES_FOLDER = 'templates'
DEFAULT_SKIN_NAME = 'default'
FORCE_DEFAULT_PREFIX = "%s/" % DEFAULT_SKIN_NAME


class Template(object):

    def __init__(self, file_name):
        self._file_name = file_name
        self._loaded = False

    def _get_mtime(self):
        return os.path.getmtime(self._file_name)

    def _check_mtime(self):
        if self._last_mtime is None:
            return False

        return self._last_mtime == self._get_mtime()

    def _load(self):
        try:
            f = open(self._file_name, 'r')
            self._source = f.read()
            f.close()
            self._loaded = True

            self._last_mtime = self._get_mtime()
        except:
            self._loaded = False
            self._last_mtime = None

            raise

    def return_tuple(self):
        if not (self._loaded and self._check_mtime()):
            try:
                self._load()
            except:
                raise TemplateDoesNotExist, self._file_name

        return self._source, self._file_name

class BaseTemplateLoader(object):
    is_usable = True

    def __init__(self):
        self.cache = {}

    def __call__(self, name=None, dirs=None):
        if name is None:
            return self

        return self.load_template(name, dirs)

    def load_template(self, name, dirs=None):
        if not djsettings.TEMPLATE_DEBUG:
            if name in self.cache:
                if self.cache[name] is UNEXISTENT_TEMPLATE:
                    raise TemplateDoesNotExist, name

                try:
                    return self.cache[name].return_tuple()
                except:
                    del self.cache[name]

        template = self.load_template_source(name, dirs)

        if template is not None:
            if not djsettings.DEBUG:
                self.cache[name] = template

            return template.return_tuple()
        else:
            if not djsettings.DEBUG:
                self.cache[name] = UNEXISTENT_TEMPLATE

            raise TemplateDoesNotExist, name

    def load_template_source(self, name, dirs=None):
        raise NotImplementedError


class SkinsTemplateLoader(BaseTemplateLoader):

    def load_template_source(self, name, dirs=None):

        if name.startswith(FORCE_DEFAULT_PREFIX):

            file_name = os.path.join(SKINS_FOLDER, DEFAULT_SKIN_NAME, SKIN_TEMPLATES_FOLDER, name[len(FORCE_DEFAULT_PREFIX):])

            if os.path.exists(file_name):
                return Template(file_name)
            else:
                return None

        for skin in (settings.OSQA_DEFAULT_SKIN, DEFAULT_SKIN_NAME):
            file_name = os.path.join(SKINS_FOLDER, skin, SKIN_TEMPLATES_FOLDER, name)

            if os.path.exists(file_name):
                return Template(file_name)

        return None

load_template_source = SkinsTemplateLoader()


def find_media_source(url):
    """returns url prefixed with the skin name
    of the first skin that contains the file 
    directories are searched in this order:
    settings.OSQA_DEFAULT_SKIN, then 'default', then 'commmon'
    if file is not found - returns None
    and logs an error message
    """
    while url[0] == '/': url = url[1:]
    d = os.path.dirname
    n = os.path.normpath
    j = os.path.join
    f = os.path.isfile
    skins = n(j(d(d(__file__)),'skins'))
    try:
        media = os.path.join(skins, settings.OSQA_DEFAULT_SKIN, url)
        assert(f(media))
        use_skin = settings.OSQA_DEFAULT_SKIN
    except:
        try:
            media = j(skins, 'default', url)
            assert(f(media))
            use_skin = 'default'
        except:
            media = j(skins, 'common', url)
            try:
                assert(f(media))
                use_skin = 'common'
            except:
                logging.error('could not find media for %s' % url)
                use_skin = ''
                return None
    return use_skin + '/' + url

