import os, re

from forum.skins import load_template_source as skins_template_loader, Template, BaseTemplateLoader
from django.conf import settings

MODULES_TEMPLATE_PREFIX = 'modules/'
NO_OVERRIDE_TEMPLATE_PREFIX = 'no_override/'
MODULES_TEMPLATE_FOLDER = 'templates'
MODULES_TEMPLATE_OVERRIDES_FOLDER = 'template_overrides'

TEMPLATE_OVERRIDE_LOOKUP_PATHS = [f for f in [
        os.path.join(os.path.dirname(m.__file__), MODULES_TEMPLATE_OVERRIDES_FOLDER) for m in settings.MODULE_LIST
    ] if os.path.exists(f)
]

class ModulesTemplateLoader(BaseTemplateLoader):

    modules_re = re.compile('^%s(\w+)\/(.*)$' % MODULES_TEMPLATE_PREFIX)

    def load_template_source(self, name, dirs=None):
        template = None

        if name.startswith(MODULES_TEMPLATE_PREFIX):
            match = self.modules_re.search(name)
            file_name = os.path.join(settings.MODULES_FOLDER, match.group(1), MODULES_TEMPLATE_FOLDER, match.group(2))

            if os.path.exists(file_name):
                template = Template(file_name)

        elif name.startswith(NO_OVERRIDE_TEMPLATE_PREFIX):
            return skins_template_loader.load_template_source(name[len(NO_OVERRIDE_TEMPLATE_PREFIX):], dirs)

        else:
            for override_path in TEMPLATE_OVERRIDE_LOOKUP_PATHS:
                file_name = os.path.join(override_path, name)

                if os.path.exists(file_name):
                    template = Template(file_name)
                    break


        return template

module_templates_loader = ModulesTemplateLoader()
