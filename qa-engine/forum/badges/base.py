import re
from string import lower

from django.core.exceptions import MultipleObjectsReturned
from django.db.models.signals import post_save

from forum.models import Badge, Node, Action
from forum.actions import AwardAction

import logging

installed = dict([(b.cls, b) for b in Badge.objects.all()])

class BadgesMeta(type):
    by_class = {}
    by_id = {}

    def __new__(mcs, name, bases, dic):
        badge = type.__new__(mcs, name, bases, dic)

        if not dic.get('abstract', False):
            if not name in installed:
                badge.ondb = Badge(cls=name, type=dic.get('type', Badge.BRONZE))
                badge.ondb.save()
            else:
                badge.ondb = installed[name]

            inst = badge()

            def hook(action, new):
                user = inst.award_to(action)

                if user:
                    badge.award(user, action, badge.award_once)

            for action in badge.listen_to:
                action.hook(hook)

            BadgesMeta.by_class[name] = badge
            badge.ondb.__dict__['_class'] = inst
            BadgesMeta.by_id[badge.ondb.id] = badge

        return badge

class AbstractBadge(object):
    __metaclass__ = BadgesMeta

    abstract = True
    award_once = False

    @property
    def name(self):
        raise NotImplementedError

    @property
    def description(self):
        raise NotImplementedError

    @classmethod
    def award(cls, user, action, once=False):
        try:
            if once:
                node = None
                awarded = AwardAction.get_for(user, cls.ondb)
            else:
                node = action.node
                awarded = AwardAction.get_for(user, cls.ondb, node)

            trigger = isinstance(action, Action) and action or None

            if not awarded:
                AwardAction(user=user, node=node).save(data=dict(badge=cls.ondb, trigger=trigger))
        except MultipleObjectsReturned:
            if node:
                logging.error('Found multiple %s badges awarded for user %s (%s)' % (self.name, user.username, user.id))
            else:
                logging.error('Found multiple %s badges awarded for user %s (%s) and node %s' % (self.name, user.username, user.id, node.id))