from base import *
from django.utils.translation import ugettext as _
import re

class Comment(Node):
    friendly_name = _("comment")

    class Meta(Node.Meta):
        ordering = ('-added_at',)
        proxy = True

    def _update_parent_comment_count(self, diff):
        parent = self.parent
        parent.comment_count = parent.comment_count + diff
        parent.save()

    @property
    def comment(self):
        if settings.FORM_ALLOW_MARKDOWN_IN_COMMENTS:
            return self.as_markdown('limitedsyntax')
        else:
            return self.body

    @property
    def headline(self):
        return self.absolute_parent.headline

    @property
    def content_object(self):
        return self.parent.leaf

    def save(self, *args, **kwargs):
        super(Comment,self).save(*args, **kwargs)

        if not self.id:
            self.parent.reset_comment_count_cache()

    def mark_deleted(self, user):
        if super(Comment, self).mark_deleted(user):
            self.parent.reset_comment_count_cache()

    def unmark_deleted(self):
        if super(Comment, self).unmark_deleted():
            self.parent.reset_comment_count_cache()

    def is_reply_to(self, user):
        inreply = re.search('@\w+', self.body)
        if inreply is not None:
            return user.username.startswith(inreply.group(0))

        return False

    def get_absolute_url(self):
        return self.abs_parent.get_absolute_url() + "#%d" % self.id

    def __unicode__(self):
        return self.body

