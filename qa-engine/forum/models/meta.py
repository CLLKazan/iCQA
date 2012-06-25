from django.utils.translation import ugettext as _
from base import *

class Vote(models.Model):
    user = models.ForeignKey(User, related_name="votes")
    node = models.ForeignKey(Node, related_name="votes")
    value = models.SmallIntegerField()
    action = models.OneToOneField(Action, related_name="vote")
    voted_at = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        app_label = 'forum'
        unique_together = ('user', 'node')


class Flag(models.Model):
    user = models.ForeignKey(User, related_name="flags")
    node = models.ForeignKey(Node, related_name="flags")
    reason = models.CharField(max_length=300)
    action = models.OneToOneField(Action, related_name="flag")
    flagged_at = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        app_label = 'forum'
        unique_together = ('user', 'node')

class BadgesQuerySet(models.query.QuerySet):
    def get(self, *args, **kwargs):
        try:
            pk = [v for (k,v) in kwargs.items() if k in ('pk', 'pk__exact', 'id', 'id__exact')][0]
        except:
            return super(BadgesQuerySet, self).get(*args, **kwargs)

        from forum.badges.base import BadgesMeta
        badge = BadgesMeta.by_id.get(int(pk), None)
        if not badge:
            return super(BadgesQuerySet, self).get(*args, **kwargs)
        return badge.ondb


class BadgeManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return BadgesQuerySet(self.model)

class Badge(models.Model):
    GOLD = 1
    SILVER = 2
    BRONZE = 3

    type        = models.SmallIntegerField()
    cls         = models.CharField(max_length=50, null=True)
    awarded_count = models.PositiveIntegerField(default=0)
    
    awarded_to    = models.ManyToManyField(User, through='Award', related_name='badges')

    objects = BadgeManager()

    @property
    def name(self):
        cls = self.__dict__.get('_class', None)
        return cls and cls.name or _("Unknown")

    @property
    def description(self):
        cls = self.__dict__.get('_class', None)
        return cls and cls.description or _("No description available")

    @models.permalink
    def get_absolute_url(self):
        return ('badge', [], {'id': self.id, 'slug': slugify(self.name)})

    def save(self, *args, **kwargs):
        if isinstance(self.awarded_count, models.expressions.ExpressionNode):
            super(Badge, self).save(*args, **kwargs)
            self.awarded_count = self.__class__.objects.filter(id=self.id).values_list('awarded_count', flat=True)[0]
        else:
            super(Badge, self).save(*args, **kwargs)


    class Meta:
        app_label = 'forum'


class Award(models.Model):
    user = models.ForeignKey(User)
    badge = models.ForeignKey('Badge', related_name="awards")
    node = models.ForeignKey(Node, null=True)

    awarded_at = models.DateTimeField(default=datetime.datetime.now)

    trigger = models.ForeignKey(Action, related_name="awards", null=True)
    action = models.OneToOneField(Action, related_name="award")


    class Meta:
        unique_together = ('user', 'badge', 'node')
        app_label = 'forum'