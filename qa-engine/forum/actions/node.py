from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from forum.models.action import ActionProxy
from forum.models import Comment, Question, Answer, NodeRevision
import logging

class NodeEditAction(ActionProxy):
    def create_revision_data(self, initial=False, **data):
        revision_data = dict(summary=data.get('summary', (initial and _('Initial revision') or '')), body=data['text'])

        if data.get('title', None):
            revision_data['title'] = strip_tags(data['title'].strip())

        if data.get('tags', None):
            revision_data['tagnames'] = data['tags'].strip()

        return revision_data

class AskAction(NodeEditAction):
    verb = _("asked")

    def process_data(self, **data):
        processed_data = self.create_revision_data(True, **data)
        if 'added_at' in data:
            processed_data['added_at'] = data['added_at']

        question = Question(author=self.user, **processed_data)
        question.save()
        self.node = question

    def describe(self, viewer=None):
        return _("%(user)s asked %(question)s") % {
            'user': self.hyperlink(self.user.get_profile_url(), self.friendly_username(viewer, self.user)),
            'question': self.hyperlink(self.node.get_absolute_url(), self.node.title)
        }

class AnswerAction(NodeEditAction):
    verb = _("answered")

    def process_data(self, **data):
        answer = Answer(author=self.user, parent=data['question'], **self.create_revision_data(True, **data))
        answer.save()
        self.node = answer

    def process_action(self):
        self.node.question.reset_answer_count_cache()

    def describe(self, viewer=None):
        question = self.node.parent
        return _("%(user)s answered %(asker)s on %(question)s") % {
            'user': self.hyperlink(self.user.get_profile_url(), self.friendly_username(viewer, self.user)),
            'asker': self.hyperlink(question.author.get_profile_url(), self.friendly_username(viewer, question.author)),
            'question': self.hyperlink(self.node.get_absolute_url(), question.title)
        }

class CommentAction(ActionProxy):
    verb = _("commented")

    def process_data(self, text='', parent=None):
        comment = Comment(author=self.user, parent=parent, body=text)
        comment.save()
        self.node = comment

    def describe(self, viewer=None):
        return _("%(user)s commented on %(post_desc)s") % {
            'user': self.hyperlink(self.node.author.get_profile_url(), self.friendly_username(viewer, self.node.author)),
            'post_desc': self.describe_node(viewer, self.node.parent)
        }

class ReviseAction(NodeEditAction):
    verb = _("edited")

    def process_data(self, **data):
        revision_data = self.create_revision_data(**data)
        revision = self.node.create_revision(self.user, **revision_data)
        self.extra = revision.revision

    def process_action(self):
        self.node.last_edited = self
        self.node.save()

    def describe(self, viewer=None):
        return _("%(user)s edited %(post_desc)s") % {
            'user': self.hyperlink(self.user.get_profile_url(), self.friendly_username(viewer, self.user)),
            'post_desc': self.describe_node(viewer, self.node)
        }

    def get_absolute_url(self):
        return self.node.get_revisions_url()

class RetagAction(ActionProxy):
    verb = _("retagged")

    def process_data(self, tagnames=''):
        active = self.node.active_revision
        revision_data = dict(summary=_('Retag'), title=active.title, tagnames=strip_tags(tagnames.strip()), body=active.body)
        revision = self.node.create_revision(self.user, **revision_data)
        self.extra = revision.revision

    def process_action(self):
        self.node.last_edited = self
        self.node.save()

    def describe(self, viewer=None):
        return _("%(user)s retagged %(post_desc)s") % {
            'user': self.hyperlink(self.user.get_profile_url(), self.friendly_username(viewer, self.user)),
            'post_desc': self.describe_node(viewer, self.node)
        }

    def get_absolute_url(self):
        return self.node.get_revisions_url()

class RollbackAction(ActionProxy):
    verb = _("reverted")

    def process_data(self, activate=None):
        previous = self.node.active_revision
        self.node.activate_revision(self.user, activate)
        self.extra = "%d:%d" % (previous.revision, activate.revision)

    def process_action(self):
        self.node.last_edited = self
        self.node.save()

    def describe(self, viewer=None):
        revisions = [NodeRevision.objects.get(node=self.node, revision=int(n)) for n in self.extra.split(':')]

        return _("%(user)s reverted %(post_desc)s from revision %(initial)d (%(initial_sum)s) to revision %(final)d (%(final_sum)s)") % {
            'user': self.hyperlink(self.user.get_profile_url(), self.friendly_username(viewer, self.user)),
            'post_desc': self.describe_node(viewer, self.node),
            'initial': revisions[0].revision, 'initial_sum': revisions[0].summary,
            'final': revisions[1].revision, 'final_sum': revisions[1].summary,
        }

    def get_absolute_url(self):
        return self.node.get_revisions_url()

class CloseAction(ActionProxy):
    verb = _("closed")

    def process_action(self):
        self.node.marked = True
        self.node.nstate.closed = self
        self.node.last_edited = self
        self.node.update_last_activity(self.user, save=True)

    def cancel_action(self):
        self.node.marked = False
        self.node.nstate.closed = None
        self.node.update_last_activity(self.user, save=True)

    def describe(self, viewer=None):
        return _("%(user)s closed %(post_desc)s: %(reason)s") % {
            'user': self.hyperlink(self.user.get_profile_url(), self.friendly_username(viewer, self.user)),
            'post_desc': self.describe_node(viewer, self.node),
            'reason': self.extra
        }

class AnswerToCommentAction(ActionProxy):
    verb = _("converted")

    def process_data(self, new_parent=None):
        self.node.parent = new_parent
        self.node.node_type = "comment"

        for comment in self.node.comments.all():
            comment.parent = new_parent
            comment.save()

        self.node.last_edited = self
        self.node.update_last_activity(self.user, save=True)
        try:
            self.node.abs_parent.reset_answer_count_cache()
        except AttributeError:
            pass

    def describe(self, viewer=None):
        return _("%(user)s converted an answer to %(question)s into a comment") % {
            'user': self.hyperlink(self.user.get_profile_url(), self.friendly_username(viewer, self.user)),
            'question': self.describe_node(viewer, self.node.abs_parent),
        }

class CommentToAnswerAction(ActionProxy):
    verb = _("converted")

    def process_data(self, question):
        self.node.parent = question
        self.node.node_type = "answer"
        self.node.last_edited = self
        self.node.update_last_activity(self.user, save=True)


    def describe(self, viewer=None):
        return _("%(user)s converted comment on %(question)s into an answer") % {
            'user': self.hyperlink(self.user.get_profile_url(), self.friendly_username(viewer, self.user)),
            'question': self.describe_node(viewer, self.node.abs_parent),
        }

class AnswerToQuestionAction(NodeEditAction):
    verb = _("converted to question")

    def process_data(self,  **data):
        revision_data = self.create_revision_data(**data)
        revision = self.node.create_revision(self.user, **revision_data)

        original_question = self.node.question

        self.extra = {
            'covert_revision': revision.revision,
            'original_question': original_question
        }

        self.node.node_type = "question"
        self.node.parent = None
        self.node.abs_parent = None

        original_question.reset_answer_count_cache()

    def process_action(self):
        self.node.last_edited = self
        self.node.save()


    def describe(self, viewer=None):
        return _("%(user)s converted an answer to %(question)s into a separate question") % {
            'user': self.hyperlink(self.user.get_profile_url(), self.friendly_username(viewer, self.user)),
            'question': self.describe_node(viewer, self.node.abs_parent),
        }

class WikifyAction(ActionProxy):
    verb = _("wikified")

    def process_action(self):
        self.node.nstate.wiki = self
        self.node.last_edited = self
        self.node.update_last_activity(self.user, save=True)

    def cancel_action(self):
        self.node.nstate.wiki = None
        self.node.update_last_activity(self.user, save=True)

    def describe(self, viewer=None):
        return _("%(user)s marked %(node)s as community wiki.") % {
            'user': self.hyperlink(self.user.get_profile_url(), self.friendly_username(viewer, self.user)),
            'node': self.describe_node(viewer, self.node),
        }

