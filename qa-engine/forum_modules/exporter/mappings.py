from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponsePermanentRedirect
from django.template.defaultfilters import slugify

from forum.views import readers
from forum.modules import decorate
from forum.models import Question

import settings, logging

@decorate(readers.question, needs_origin=True)
def match_question_slug(origin, request, id, slug='', answer=None):
    try:
        id = int(id)
    except:
        raise Http404()

    if settings.MERGE_MAPPINGS and (int(id) in settings.MERGE_MAPPINGS.get('merged_nodes', {})):
        try:
            question = Question.objects.get(id=id)

            if slug != slugify(question.title):
                return origin(request, settings.MERGE_MAPPINGS['merged_nodes'][int(id)], slug, answer)

        except:
            pass

    return origin(request, id, slug, answer)