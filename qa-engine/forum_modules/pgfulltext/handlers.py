import re
from django.db import connection, transaction
from django.db.models import Q
from forum.models.question import Question, QuestionManager
from forum.models.node import Node
from forum.modules import decorate

word_re = re.compile(r'\w+', re.UNICODE)

@decorate(QuestionManager.search, needs_origin=False)
def question_search(self, keywords):
    tsquery = " | ".join(word_re.findall(keywords))
    ilike = keywords + u"%%"

    return True, self.extra(
            tables = ['forum_rootnode_doc'],
            select={
            'ranking': """
                                rank_exact_matches(ts_rank_cd('{0.1, 0.2, 0.8, 1.0}'::float4[], "forum_rootnode_doc"."document", to_tsquery('english', %s), 32))
                                """,
            },
            where=["""
                           "forum_rootnode_doc"."node_id" = "forum_node"."id" AND ("forum_rootnode_doc"."document" @@ to_tsquery('english', %s) OR
                           "forum_node"."title" ILIKE %s)
                           """],
            params=[tsquery, ilike],
            select_params=[tsquery],
            )


@decorate(Node.delete)
def delete(origin, self, *args, **kwargs):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM forum_rootnode_doc WHERE node_id = %s" % (self.id))
    transaction.commit_unless_managed()
    return origin(self, *args, **kwargs)


