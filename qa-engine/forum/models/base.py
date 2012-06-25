import datetime
import re
from urllib import quote_plus, urlencode
from django.db import models, IntegrityError, connection, transaction
from django.utils.http import urlquote  as django_urlquote
from django.utils.html import strip_tags
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.template.defaultfilters import slugify
from django.db.models.signals import post_delete, post_save, pre_save, pre_delete
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.contrib.sitemaps import ping_google
import django.dispatch
from forum import settings
import logging


class LazyQueryList(object):
    def __init__(self, model, items):
        self.items = items
        self.model = model

    def __getitem__(self, k):
        return self.model.objects.get(id=self.items[k][0])

    def __iter__(self):
        for id in self.items:
            yield self.model.objects.get(id=id[0])

    def __len__(self):
        return len(self.items)

class CachedQuerySet(models.query.QuerySet):

    def lazy(self):
        if not len(self.query.aggregates):
            values_list = ['id']

            if len(self.query.extra):
                extra_keys = self.query.extra.keys()
                values_list += extra_keys

            return LazyQueryList(self.model, list(self.values_list(*values_list)))
        else:
            if len(self.query.extra):
                print self.query.extra
            return self

    def obj_from_datadict(self, datadict):
        obj = self.model()
        obj.__dict__.update(datadict)
        return obj

    def get(self, *args, **kwargs):
        key = self.model.infer_cache_key(kwargs)

        if key is not None:
            obj = cache.get(key)

            if obj is None:
                obj = super(CachedQuerySet, self).get(*args, **kwargs)
                obj.cache()
            else:
                obj = self.obj_from_datadict(obj)
                obj.reset_original_state()

            return obj

        return super(CachedQuerySet, self).get(*args, **kwargs)

class CachedManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return CachedQuerySet(self.model)

    def get_or_create(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except:
            return super(CachedManager, self).get_or_create(*args, **kwargs)


class DenormalizedField(object):
    def __init__(self, manager, *args, **kwargs):
        self.manager = manager
        self.filter = (args, kwargs)

    def setup_class(self, cls, name):
        dict_name = '_%s_dencache_' % name

        def getter(inst):
            val = inst.__dict__.get(dict_name, None)

            if val is None:
                val = getattr(inst, self.manager).filter(*self.filter[0], **self.filter[1]).count()
                inst.__dict__[dict_name] = val
                inst.cache()

            return val

        def reset_cache(inst):
            inst.__dict__.pop(dict_name, None)
            inst.uncache()

        cls.add_to_class(name, property(getter))
        cls.add_to_class("reset_%s_cache" % name, reset_cache)


class BaseMetaClass(models.Model.__metaclass__):
    to_denormalize = []

    def __new__(cls, *args, **kwargs):
        new_cls = super(BaseMetaClass, cls).__new__(cls, *args, **kwargs)

        BaseMetaClass.to_denormalize.extend(
            [(new_cls, name, field) for name, field in new_cls.__dict__.items() if isinstance(field, DenormalizedField)]
        )

        return new_cls

    @classmethod
    def setup_denormalizes(cls):
        for new_cls, name, field in BaseMetaClass.to_denormalize:
            field.setup_class(new_cls, name)


class BaseModel(models.Model):
    __metaclass__ = BaseMetaClass

    objects = CachedManager()

    class Meta:
        abstract = True
        app_label = 'forum'

    def __init__(self, *args, **kwargs):
        super(BaseModel, self).__init__(*args, **kwargs)
        self.reset_original_state(kwargs.keys())

    def reset_original_state(self, reset_fields=None):
        self._original_state = self._as_dict()
        
        if reset_fields:
            self._original_state.update(dict([(f, None) for f in reset_fields]))

    def get_dirty_fields(self):
        return [f.name for f in self._meta.fields if self._original_state[f.attname] != self.__dict__[f.attname]]

    def _as_dict(self):
        return dict([(name, getattr(self, name)) for name in
                     ([f.attname for f in self._meta.fields] + [k for k in self.__dict__.keys() if k.endswith('_dencache_')])
        ])

    def _get_update_kwargs(self):
        return dict([
            (f.name, getattr(self, f.name)) for f in self._meta.fields if self._original_state[f.attname] != self.__dict__[f.attname]
        ])

    def save(self, full_save=False, *args, **kwargs):
        put_back = [k for k, v in self.__dict__.items() if isinstance(v, models.expressions.ExpressionNode)]

        if self.id and not full_save:
            self.__class__.objects.filter(id=self.id).update(**self._get_update_kwargs())
        else:
            super(BaseModel, self).save()

        if put_back:
            try:
                self.__dict__.update(
                    self.__class__.objects.filter(id=self.id).values(*put_back)[0]
                )
            except:
                logging.error("Unable to read %s from %s" % (", ".join(put_back), self.__class__.__name__))
                self.uncache()

        self.reset_original_state()
        self.cache()

    @classmethod
    def _generate_cache_key(cls, key, group=None):
        if group is None:
            group = cls.__name__

        return '%s:%s:%s' % (settings.APP_URL, group, key)

    def cache_key(self):
        return self._generate_cache_key(self.id)

    @classmethod
    def infer_cache_key(cls, querydict):
        try:
            pk = [v for (k,v) in querydict.items() if k in ('pk', 'pk__exact', 'id', 'id__exact'
                            ) or k.endswith('_ptr__pk') or k.endswith('_ptr__id')][0]

            return cls._generate_cache_key(pk)
        except:
            return None

    def cache(self):
        cache.set(self.cache_key(), self._as_dict(), 60 * 60)

    def uncache(self):
        cache.delete(self.cache_key())

    def delete(self):
        self.uncache()
        super(BaseModel, self).delete()


from user import User
from node import Node, NodeRevision, NodeManager
from action import Action





