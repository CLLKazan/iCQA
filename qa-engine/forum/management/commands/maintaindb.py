from django.core.management.base import BaseCommand, CommandError
from forum.models import Node, NodeRevision

import logging

# Used to activate the latest revision connected to some node
def activate_latest_revision(node):
    # We're adding a new try-except block just in case that function has been called incorrectly.
    try:
        # The latest revision is the one that was added the last.
        rev = node.revisions.all().order_by('-pk')[0]
        node.active_revision_id = rev.id
        node.save()

        return rev
    except:
        logging.error("Incorrect attempt to activate the latest revision of a node \
                       that has no revisions at all has been made.")
        return None

# Used to create a new NodeRevision object according to the node content
def create_revision(node):
    rev = NodeRevision(
            author_id = node.author_id,
            body = node.body,
            node_id = node.id,
            revised_at = node.added_at,
            revision = 1,
            summary = 'Initial revision',
            tagnames = node.tagnames,
            title = node.title,
            )

    node.save()

    return node

class Command(BaseCommand):

    def handle(self,*args, **options):
        print 'Running MaintainDb'

        nodes = Node.objects.all()

        for node in nodes:
            if node.active_revision is None:
                print "Node #%(node_id)d: NodeRevision doesn't exist" % dict(node_id=node.id)

                # We currently don't have any active revision for this Node. Let's check if there are any revisions
                # at all for it. If there are any we activate the last.
                if node.revisions.all().count() > 0:
                    print "  We have revisions for Node #%(node_id)d." % dict(node_id=node.id)

                    # If there are already some revisions connected to the current node, we activate the latest
                    activate_latest_revision(node)
                else:
                    print "  We don't have revisions for Node #%(node_id)d. We're "\
                          "going to create a new one from the current node content."% dict(node_id=node.id)

                    # First of all we're going to create a new revision according to the current node data...
                    create_revision(node)

                    # ...and after that we're going to activate it
                    activate_latest_revision(node)

                    #print rev.node
