from base import *
from tag import Tag
from django.utils.translation import ugettext as _

class QuestionManager(NodeManager):
    def search(self, keywords):
        return False, self.filter(models.Q(title__icontains=keywords) | models.Q(body__icontains=keywords))

class Question(Node):
    class Meta(Node.Meta):
        proxy = True

    answer_count = DenormalizedField("children", ~models.Q(state_string__contains="(deleted)"), node_type="answer")
    accepted_count = DenormalizedField("children", ~models.Q(state_string__contains="(deleted)"), node_type="answer", marked=True)
    favorite_count = DenormalizedField("actions", action_type="favorite", canceled=False)

    friendly_name = _("question")
    objects = QuestionManager()

    @property
    def closed(self):
        return self.nis.closed

    @property    
    def view_count(self):
        return self.extra_count

    @property
    def headline(self):
        if self.nis.deleted:
            return _('[deleted] ') + self.title

        if self.nis.closed:
            return _('[closed] ') + self.title

        return self.title

    @property
    def accepted_answers(self):
        return self.answers.filter(~models.Q(state_string__contains="(deleted)"), marked=True)

    @models.permalink    
    def get_absolute_url(self):
        return ('question', (), {'id': self.id, 'slug': django_urlquote(slugify(self.title))})
        
    def meta_description(self):
        return self.summary

    def get_revision_url(self):
        return reverse('question_revisions', args=[self.id])

    def get_related_questions(self, count=10):
        cache_key = '%s.related_questions:%d:%d' % (settings.APP_URL, count, self.id)
        related_list = cache.get(cache_key)

        if related_list is None:
            related_list = Question.objects.filter_state(deleted=False).values('id').filter(tags__id__in=[t.id for t in self.tags.all()]
            ).exclude(id=self.id).annotate(frequency=models.Count('id')).order_by('-frequency')[:count]
            cache.set(cache_key, related_list, 60 * 60)

        return [Question.objects.get(id=r['id']) for r in related_list]
    
    def get_active_users(self):
        active_users = set()
        
        active_users.add(self.author)
        
        for answer in self.answers:
            active_users.add(answer.author)
            
            for comment in answer.comments:
                active_users.add(comment.author)
                        
        for comment in self.comments:
            active_users.add(comment.author)
        
        return active_users


class QuestionSubscription(models.Model):
    user = models.ForeignKey(User)
    question = models.ForeignKey(Node)
    auto_subscription = models.BooleanField(default=True)
    last_view = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        app_label = 'forum'


class QuestionRevision(NodeRevision):
    class Meta:
        proxy = True
        
