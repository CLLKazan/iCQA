from forum.models import Question
from django.conf import settings
from djangosphinx.manager import SphinxSearch

from djangosphinx.models import SphinxSearch

Question.add_to_class('search', SphinxSearch(
                                   index=' '.join(settings.SPHINX_SEARCH_INDICES),
                                   mode='SPH_MATCH_ALL',
                                )
                      )
