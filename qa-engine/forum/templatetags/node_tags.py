from datetime import datetime, timedelta
import re

from forum.models import Question, Action
from django.utils.translation import ungettext, ugettext as _
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django import template
from forum.actions import *
from forum import settings

register = template.Library()

@register.inclusion_tag('node/vote_buttons.html')
def vote_buttons(post, user):
    context = dict(post=post, user_vote='none')

    if user.is_authenticated():
        context['user_vote'] = {1: 'up', -1: 'down', None: 'none'}[VoteAction.get_for(user, post)]

    return context

@register.inclusion_tag('node/accept_button.html')
def accept_button(answer, user):
    if not settings.DISABLE_ACCEPTING_FEATURE:
        return {
            'can_accept': user.is_authenticated() and user.can_accept_answer(answer),
            'answer': answer,
            'user': user
        }
    else:
        return ''

@register.inclusion_tag('node/wiki_symbol.html')
def wiki_symbol(user, post):
    context = {
        'is_wiki': post.nis.wiki,
        'post_type': post.friendly_name
    }

    if post.nis.wiki:
        if user.can_edit_post(post):
            context['can_edit'] = True
            context['edit_url'] = reverse('edit_' + post.node_type, kwargs={'id': post.id})
        context['by'] = post.nstate.wiki.by.username
        context['at'] = post.nstate.wiki.at

    return context

@register.inclusion_tag('node/favorite_mark.html')
def favorite_mark(question, user):
    try:
        FavoriteAction.objects.get(canceled=False, node=question, user=user)
        favorited = True
    except:
        favorited = False

    return {'favorited': favorited, 'favorite_count': question.favorite_count, 'question': question}

@register.simple_tag
def post_classes(post):
    classes = []

    if post.nis.deleted:
        classes.append('deleted')

    if post.node_type == "answer":
        if (not settings.DISABLE_ACCEPTING_FEATURE) and post.nis.accepted:
            classes.append('accepted-answer')

        if post.author == post.question.author:
            classes.append('answered-by-owner')

    return " ".join(classes)

def post_control(text, url, command=False, withprompt=False, confirm=False, title=""):
    classes = (command and "ajax-command" or " ") + (withprompt and " withprompt" or " ") + (confirm and " confirm" or " ")
    return {'text': text, 'url': url, 'classes': classes, 'title': title}

@register.inclusion_tag('node/post_controls.html')
def post_controls(post, user):
    controls = []
    menu = []
    post_type = post.node_type

    # We show the link tool if the post is an Answer. It is visible to Guests too.
    if post_type == "answer":
        # Answer permanent link tool
        controls.append(post_control(_('permanent link'), reverse('answer_permanent_link', kwargs={'id' : post.id}),
                                     title=_("answer permanent link"), command=True, withprompt=True))

        # Users should be able to award points for an answer. Users cannot award their own answers
        if user != post.author and user.is_authenticated():
            controls.append(post_control(_("award points"), reverse('award_points', kwargs={'user_id' : post.author.id,
                                         'answer_id' : post.id}), title=_("award points to %s") % post.author,
                                         command=True, withprompt=True))

    # The other controls are visible only to authenticated users.
    if user.is_authenticated():
        try:
            edit_url = reverse('edit_' + post_type, kwargs={'id': post.id})
            if user.can_edit_post(post):
                controls.append(post_control(_('edit'), edit_url))
            elif post_type == 'question' and user.can_retag_questions():
                controls.append(post_control(_('retag'), edit_url))
        except:
            pass

        if post_type == 'question':
            if post.nis.closed and user.can_reopen_question(post):
                controls.append(post_control(_('reopen'), reverse('reopen', kwargs={'id': post.id}), command=True))
            elif not post.nis.closed and user.can_close_question(post):
                controls.append(post_control(_('close'), reverse('close', kwargs={'id': post.id}), command=True, withprompt=True))

        if user.can_flag_offensive(post):
            label = _('report')
            
            if user.can_view_offensive_flags(post):
                label =  "%s (%d)" % (label, post.flag_count)

            controls.append(post_control(label, reverse('flag_post', kwargs={'id': post.id}),
                    command=True, withprompt=True, title=_("report as offensive (i.e containing spam, advertising, malicious text, etc.)")))

        if user.can_delete_post(post):
            if post.nis.deleted:
                controls.append(post_control(_('undelete'), reverse('delete_post', kwargs={'id': post.id}),
                        command=True, confirm=True))
            else:
                controls.append(post_control(_('delete'), reverse('delete_post', kwargs={'id': post.id}),
                        command=True, confirm=True))

        if user.can_delete_post(post):
            menu.append(post_control(_('see revisions'),
                        reverse('revisions',
                        kwargs={'id': post.id}),
                        command=False, confirm=False))

        if settings.WIKI_ON:
            if (not post.nis.wiki) and user.can_wikify(post):
                menu.append(post_control(_('mark as community wiki'), reverse('wikify', kwargs={'id': post.id}),
                            command=True, confirm=True))

            elif post.nis.wiki and user.can_cancel_wiki(post):
                menu.append(post_control(_('cancel community wiki'), reverse('wikify', kwargs={'id': post.id}),
                            command=True, confirm=True))

        if post.node_type == "answer" and user.can_convert_to_comment(post):
            menu.append(post_control(_('convert to comment'), reverse('convert_to_comment', kwargs={'id': post.id}),
                        command=True, withprompt=True))
        
        if post.node_type == "answer" and user.can_convert_to_question(post):
            menu.append(post_control(_('convert to question'), reverse('convert_to_question', kwargs={'id': post.id}),
                        command=False, confirm=True))

        if user.is_superuser or user.is_staff:
            plain_text = strip_tags(post.html)

            char_count = len(plain_text)
            fullStr = plain_text + " "
            left_trimmedStr = re.sub(re.compile(r"^[^\w]+", re.IGNORECASE), "", fullStr)
            cleanedStr = re.sub(re.compile(r"[^\w]+", re.IGNORECASE), " ", left_trimmedStr)
            splitString = cleanedStr.split(" ")
            word_count = len(splitString) - 1

            metrics = mark_safe("<b>%s %s / %s %s</b>" % (char_count, ungettext('character', 'characters', char_count),
                                        word_count, ungettext('word', 'words', word_count)))

            menu.append(post_control(metrics, "#", command=False, withprompt=False))

    return {'controls': controls, 'menu': menu, 'post': post, 'user': user}

@register.inclusion_tag('node/comments.html')
def comments(post, user):
    all_comments = post.comments.filter_state(deleted=False).order_by('added_at')

    if len(all_comments) <= 5:
        top_scorers = all_comments
    else:
        top_scorers = sorted(all_comments, lambda c1, c2: cmp(c2.score, c1.score))[0:5]

    comments = []
    showing = 0
    for c in all_comments:
        context = {
            'can_delete': user.can_delete_comment(c),
            'can_like': user.can_like_comment(c),
            'can_edit': user.can_edit_comment(c),
            'can_convert': user.can_convert_comment_to_answer(c)
        }

        if c in top_scorers or c.is_reply_to(user):
            context['top_scorer'] = True
            showing += 1
        
        if context['can_like']:
            context['likes'] = VoteAction.get_for(user, c) == 1

        context['user'] = c.user
        context['comment'] = c.comment
        context.update(dict(c.__dict__))
        comments.append(context)

    return {
        'comments': comments,
        'post': post,
        'can_comment': user.can_comment(post),
        'max_length': settings.FORM_MAX_COMMENT_BODY,
        'min_length': settings.FORM_MIN_COMMENT_BODY,
        'show_gravatar': settings.FORM_GRAVATAR_IN_COMMENTS,
        'showing': showing,
        'total': len(all_comments),
        'user': user,
    }


@register.inclusion_tag("node/contributors_info.html")
def contributors_info(node, verb=None):
    return {
        'node_verb': verb and verb or ((node.node_type == "question") and _("asked") or (
                    (node.node_type == "answer") and _("answered") or _("posted"))),
        'node': node,
    }

@register.inclusion_tag("node/reviser_info.html")
def reviser_info(revision):
    return {'revision': revision}
