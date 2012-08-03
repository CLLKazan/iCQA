

class Registry(list):
    def add(self, item):
        for i, r in enumerate(self):
            if r.weight > item.weight:
                self.insert(i, item)
                return

        self.append(item)


HEAD_CONTENT = 'HEAD_CONTENT'
HEADER_LINKS = 'HEADER_LINKS'
PAGE_TOP_TABS = 'PAGE_TOP_TABS'
FOOTER_LINKS = 'FOOTER_LINKS'
PROFILE_TABS = 'PROFILE_TABS'

USER_MENU = 'USER_MENU'


__CONTAINER = {
    HEAD_CONTENT: Registry(),
    HEADER_LINKS: Registry(),
    PAGE_TOP_TABS: Registry(),
    FOOTER_LINKS: Registry(),
    PROFILE_TABS: Registry(),

    USER_MENU: Registry(),
}


def register(registry, *ui_objects):
    if not registry in __CONTAINER:
        raise('unknown registry')

    for ui_object in ui_objects:
        __CONTAINER[registry].add(ui_object)

def get_registry_by_name(name):
    name = name.upper()

    if not name in __CONTAINER:
        raise('unknown registry')

    return __CONTAINER[name]



from ui_objects import *

