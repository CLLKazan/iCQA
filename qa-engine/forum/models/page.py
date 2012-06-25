from base import *
from django.utils.translation import ugettext as _

class Page(Node):
    friendly_name = _("page")

    @property
    def published(self):
        return self.marked

    @property
    def html(self):
        return self._as_markdown(self.body)

    def save(self, *args, **kwargs):
        old_options = self._original_state.get('extra', None)

        super(Page, self).save(*args, **kwargs)

        registry = settings.STATIC_PAGE_REGISTRY

        if old_options:
            registry.pop(old_options.get('path', ''), None)

        registry[self.extra['path']] = self.id


        settings.STATIC_PAGE_REGISTRY.set_value(registry)

    @property
    def headline(self):
        if self.published:
            return self.title
        else:
            return _("[Unpublished] %s") % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('static_page', (), {'path': self.extra['path']})
        
    def activate_revision(self, user, revision, extensions=['urlize']):
        self.title = revision.title
        self.tagnames = revision.tagnames        
        self.body = revision.body

        self.active_revision = revision
        self.update_last_activity(user)

        self.save()

    class Meta(Node.Meta):
        proxy = True

    
