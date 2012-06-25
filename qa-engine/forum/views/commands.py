import datetime
from forum import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ungettext, ugettext as _
from django.template import RequestContext
from forum.models import *
from forum.models.node import NodeMetaClass
from forum.actions import *
from django.core.urlresolvers import reverse
from forum.utils.decorators import ajax_method, ajax_login_required
from decorators import command, CommandException, RefreshPageCommand
from forum.modules import decorate
from forum import settings
import logging

class NotEnoughRepPointsException(CommandException):
    def __init__(self, action):
        super(NotEnoughRepPointsException, self).__init__(
                _(
                        """Sorry, but you don't have enough reputation points to %(action)s.<br />Please check the <a href='%(faq_url)s'>faq</a>"""
                        ) % {'action': action, 'faq_url': reverse('faq')}
                )

class CannotDoOnOwnException(CommandException):
    def __init__(self, action):
        super(CannotDoOnOwnException, self).__init__(
                _(
                        """Sorry but you cannot %(action)s your own post.<br />Please check the <a href='%(faq_url)s'>faq</a>"""
                        ) % {'action': action, 'faq_url': reverse('faq')}
                )

class AnonymousNotAllowedException(CommandException):
    def __init__(self, action):
        super(AnonymousNotAllowedException, self).__init__(
                _(
                        """Sorry but anonymous users cannot %(action)s.<br />Please login or create an account <a href='%(signin_url)s'>here</a>."""
                        ) % {'action': action, 'signin_url': reverse('auth_signin')}
                )

class NotEnoughLeftException(CommandException):
    def __init__(self, action, limit):
        super(NotEnoughLeftException, self).__init__(
                _(
                        """Sorry, but you don't have enough %(action)s left for today..<br />The limit is %(limit)s per day..<br />Please check the <a href='%(faq_url)s'>faq</a>"""
                        ) % {'action': action, 'limit': limit, 'faq_url': reverse('faq')}
                )

class CannotDoubleActionException(CommandException):
    def __init__(self, action):
        super(CannotDoubleActionException, self).__init__(
                _(
                        """Sorry, but you cannot %(action)s twice the same post.<br />Please check the <a href='%(faq_url)s'>faq</a>"""
                        ) % {'action': action, 'faq_url': reverse('faq')}
                )


@decorate.withfn(command)
def vote_post(request, id, vote_type):
    post = get_object_or_404(Node, id=id).leaf
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('vote'))

    if user == post.author:
        raise CannotDoOnOwnException(_('vote'))

    if not (vote_type == 'up' and user.can_vote_up() or user.can_vote_down()):
        raise NotEnoughRepPointsException(vote_type == 'up' and _('upvote') or _('downvote'))

    user_vote_count_today = user.get_vote_count_today()

    if user_vote_count_today >= user.can_vote_count_today():
        raise NotEnoughLeftException(_('votes'), str(settings.MAX_VOTES_PER_DAY))

    new_vote_cls = (vote_type == 'up') and VoteUpAction or VoteDownAction
    score_inc = 0

    old_vote = VoteAction.get_action_for(node=post, user=user)

    if old_vote:
        if old_vote.action_date < datetime.datetime.now() - datetime.timedelta(days=int(settings.DENY_UNVOTE_DAYS)):
            raise CommandException(
                    _("Sorry but you cannot cancel a vote after %(ndays)d %(tdays)s from the original vote") %
                    {'ndays': int(settings.DENY_UNVOTE_DAYS),
                     'tdays': ungettext('day', 'days', int(settings.DENY_UNVOTE_DAYS))}
                    )

        old_vote.cancel(ip=request.META['REMOTE_ADDR'])
        score_inc += (old_vote.__class__ == VoteDownAction) and 1 or -1

    if old_vote.__class__ != new_vote_cls:
        new_vote_cls(user=user, node=post, ip=request.META['REMOTE_ADDR']).save()
        score_inc += (new_vote_cls == VoteUpAction) and 1 or -1
    else:
        vote_type = "none"

    response = {
    'commands': {
    'update_post_score': [id, score_inc],
    'update_user_post_vote': [id, vote_type]
    }
    }

    votes_left = (int(settings.MAX_VOTES_PER_DAY) - user_vote_count_today) + (vote_type == 'none' and -1 or 1)

    if int(settings.START_WARN_VOTES_LEFT) >= votes_left:
        response['message'] = _("You have %(nvotes)s %(tvotes)s left today.") % \
                    {'nvotes': votes_left, 'tvotes': ungettext('vote', 'votes', votes_left)}

    return response

@decorate.withfn(command)
def flag_post(request, id):
    if not request.POST:
        return render_to_response('node/report.html', {'types': settings.FLAG_TYPES})

    post = get_object_or_404(Node, id=id)
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('flag posts'))

    if user == post.author:
        raise CannotDoOnOwnException(_('flag'))

    if not (user.can_flag_offensive(post)):
        raise NotEnoughRepPointsException(_('flag posts'))

    user_flag_count_today = user.get_flagged_items_count_today()

    if user_flag_count_today >= int(settings.MAX_FLAGS_PER_DAY):
        raise NotEnoughLeftException(_('flags'), str(settings.MAX_FLAGS_PER_DAY))

    try:
        current = FlagAction.objects.get(canceled=False, user=user, node=post)
        raise CommandException(
                _("You already flagged this post with the following reason: %(reason)s") % {'reason': current.extra})
    except ObjectDoesNotExist:
        reason = request.POST.get('prompt', '').strip()

        if not len(reason):
            raise CommandException(_("Reason is empty"))

        FlagAction(user=user, node=post, extra=reason, ip=request.META['REMOTE_ADDR']).save()

    return {'message': _("Thank you for your report. A moderator will review your submission shortly.")}

@decorate.withfn(command)
def like_comment(request, id):
    comment = get_object_or_404(Comment, id=id)
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('like comments'))

    if user == comment.user:
        raise CannotDoOnOwnException(_('like'))

    if not user.can_like_comment(comment):
        raise NotEnoughRepPointsException( _('like comments'))

    like = VoteAction.get_action_for(node=comment, user=user)

    if like:
        like.cancel(ip=request.META['REMOTE_ADDR'])
        likes = False
    else:
        VoteUpCommentAction(node=comment, user=user, ip=request.META['REMOTE_ADDR']).save()
        likes = True

    return {
    'commands': {
    'update_post_score': [comment.id, likes and 1 or -1],
    'update_user_post_vote': [comment.id, likes and 'up' or 'none']
    }
    }

@decorate.withfn(command)
def delete_comment(request, id):
    comment = get_object_or_404(Comment, id=id)
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('delete comments'))

    if not user.can_delete_comment(comment):
        raise NotEnoughRepPointsException( _('delete comments'))

    if not comment.nis.deleted:
        DeleteAction(node=comment, user=user, ip=request.META['REMOTE_ADDR']).save()

    return {
    'commands': {
    'remove_comment': [comment.id],
    }
    }

@decorate.withfn(command)
def mark_favorite(request, id):
    question = get_object_or_404(Question, id=id)

    if not request.user.is_authenticated():
        raise AnonymousNotAllowedException(_('mark a question as favorite'))

    try:
        favorite = FavoriteAction.objects.get(canceled=False, node=question, user=request.user)
        favorite.cancel(ip=request.META['REMOTE_ADDR'])
        added = False
    except ObjectDoesNotExist:
        FavoriteAction(node=question, user=request.user, ip=request.META['REMOTE_ADDR']).save()
        added = True

    return {
    'commands': {
    'update_favorite_count': [added and 1 or -1],
    'update_favorite_mark': [added and 'on' or 'off']
    }
    }

@decorate.withfn(command)
def comment(request, id):
    post = get_object_or_404(Node, id=id)
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('comment'))

    if not request.method == 'POST':
        raise CommandException(_("Invalid request"))

    comment_text = request.POST.get('comment', '').strip()

    if not len(comment_text):
        raise CommandException(_("Comment is empty"))

    if len(comment_text) < settings.FORM_MIN_COMMENT_BODY:
        raise CommandException(_("At least %d characters required on comment body.") % settings.FORM_MIN_COMMENT_BODY)

    if len(comment_text) > settings.FORM_MAX_COMMENT_BODY:
        raise CommandException(_("No more than %d characters on comment body.") % settings.FORM_MAX_COMMENT_BODY)

    if 'id' in request.POST:
        comment = get_object_or_404(Comment, id=request.POST['id'])

        if not user.can_edit_comment(comment):
            raise NotEnoughRepPointsException( _('edit comments'))

        comment = ReviseAction(user=user, node=comment, ip=request.META['REMOTE_ADDR']).save(
                data=dict(text=comment_text)).node
    else:
        if not user.can_comment(post):
            raise NotEnoughRepPointsException( _('comment'))

        comment = CommentAction(user=user, ip=request.META['REMOTE_ADDR']).save(
                data=dict(text=comment_text, parent=post)).node

    if comment.active_revision.revision == 1:
        return {
        'commands': {
        'insert_comment': [
                id, comment.id, comment.comment, user.decorated_name, user.get_profile_url(),
                reverse('delete_comment', kwargs={'id': comment.id}),
                reverse('node_markdown', kwargs={'id': comment.id}),
                reverse('convert_comment', kwargs={'id': comment.id}),            
                ]
        }
        }
    else:
        return {
        'commands': {
        'update_comment': [comment.id, comment.comment]
        }
        }

@decorate.withfn(command)
def node_markdown(request, id):
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('accept answers'))

    node = get_object_or_404(Node, id=id)
    return HttpResponse(node.active_revision.body, mimetype="text/plain")


@decorate.withfn(command)
def accept_answer(request, id):
    if settings.DISABLE_ACCEPTING_FEATURE:
        raise Http404()

    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('accept answers'))

    answer = get_object_or_404(Answer, id=id)
    question = answer.question

    if not user.can_accept_answer(answer):
        raise CommandException(_("Sorry but you cannot accept the answer"))

    commands = {}

    if answer.nis.accepted:
        answer.nstate.accepted.cancel(user, ip=request.META['REMOTE_ADDR'])
        commands['unmark_accepted'] = [answer.id]
    else:
        if settings.MAXIMUM_ACCEPTED_ANSWERS and (question.accepted_count >= settings.MAXIMUM_ACCEPTED_ANSWERS):
            raise CommandException(ungettext("This question already has an accepted answer.",
                "Sorry but this question has reached the limit of accepted answers.", int(settings.MAXIMUM_ACCEPTED_ANSWERS)))

        if settings.MAXIMUM_ACCEPTED_PER_USER and question.accepted_count:
            accepted_from_author = question.accepted_answers.filter(author=answer.author).count()

            if accepted_from_author >= settings.MAXIMUM_ACCEPTED_PER_USER:
                raise CommandException(ungettext("The author of this answer already has an accepted answer in this question.",
                "Sorry but the author of this answer has reached the limit of accepted answers per question.", int(settings.MAXIMUM_ACCEPTED_PER_USER)))             


        AcceptAnswerAction(node=answer, user=user, ip=request.META['REMOTE_ADDR']).save()
        commands['mark_accepted'] = [answer.id]

    return {'commands': commands}

@decorate.withfn(command)
def delete_post(request, id):
    post = get_object_or_404(Node, id=id)
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('delete posts'))

    if not (user.can_delete_post(post)):
        raise NotEnoughRepPointsException(_('delete posts'))

    ret = {'commands': {}}

    if post.nis.deleted:
        post.nstate.deleted.cancel(user, ip=request.META['REMOTE_ADDR'])
        ret['commands']['unmark_deleted'] = [post.node_type, id]
    else:
        DeleteAction(node=post, user=user, ip=request.META['REMOTE_ADDR']).save()

        ret['commands']['mark_deleted'] = [post.node_type, id]

    return ret

@decorate.withfn(command)
def close(request, id, close):
    if close and not request.POST:
        return render_to_response('node/report.html', {'types': settings.CLOSE_TYPES})

    question = get_object_or_404(Question, id=id)
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('close questions'))

    if question.nis.closed:
        if not user.can_reopen_question(question):
            raise NotEnoughRepPointsException(_('reopen questions'))

        question.nstate.closed.cancel(user, ip=request.META['REMOTE_ADDR'])
    else:
        if not request.user.can_close_question(question):
            raise NotEnoughRepPointsException(_('close questions'))

        reason = request.POST.get('prompt', '').strip()

        if not len(reason):
            raise CommandException(_("Reason is empty"))

        CloseAction(node=question, user=user, extra=reason, ip=request.META['REMOTE_ADDR']).save()

    return RefreshPageCommand()

@decorate.withfn(command)
def wikify(request, id):
    node = get_object_or_404(Node, id=id)
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('mark posts as community wiki'))

    if node.nis.wiki:
        if not user.can_cancel_wiki(node):
            raise NotEnoughRepPointsException(_('cancel a community wiki post'))

        if node.nstate.wiki.action_type == "wikify":
            node.nstate.wiki.cancel()
        else:
            node.nstate.wiki = None
    else:
        if not user.can_wikify(node):
            raise NotEnoughRepPointsException(_('mark posts as community wiki'))

        WikifyAction(node=node, user=user, ip=request.META['REMOTE_ADDR']).save()

    return RefreshPageCommand()

@decorate.withfn(command)
def convert_to_comment(request, id):
    user = request.user
    answer = get_object_or_404(Answer, id=id)
    question = answer.question

    if not request.POST:
        description = lambda a: _("Answer by %(uname)s: %(snippet)s...") % {'uname': a.author.username,
                                                                            'snippet': a.summary[:10]}
        nodes = [(question.id, _("Question"))]
        [nodes.append((a.id, description(a))) for a in
         question.answers.filter_state(deleted=False).exclude(id=answer.id)]

        return render_to_response('node/convert_to_comment.html', {'answer': answer, 'nodes': nodes})

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_("convert answers to comments"))

    if not user.can_convert_to_comment(answer):
        raise NotEnoughRepPointsException(_("convert answers to comments"))

    try:
        new_parent = Node.objects.get(id=request.POST.get('under', None))
    except:
        raise CommandException(_("That is an invalid post to put the comment under"))

    if not (new_parent == question or (new_parent.node_type == 'answer' and new_parent.parent == question)):
        raise CommandException(_("That is an invalid post to put the comment under"))

    AnswerToCommentAction(user=user, node=answer, ip=request.META['REMOTE_ADDR']).save(data=dict(new_parent=new_parent))

    return RefreshPageCommand()

@decorate.withfn(command)
def convert_comment_to_answer(request, id):
    user = request.user
    comment = get_object_or_404(Comment, id=id)
    parent = comment.parent

    if not parent.question:
        question = parent
    else:
        question = parent.question
    
    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_("convert comments to answers"))

    if not user.can_convert_comment_to_answer(comment):
        raise NotEnoughRepPointsException(_("convert comments to answers"))
    
    CommentToAnswerAction(user=user, node=comment, ip=request.META['REMOTE_ADDR']).save(data=dict(question=question))

    return RefreshPageCommand()

@decorate.withfn(command)
def subscribe(request, id, user=None):
    if user:
        try:
            user = User.objects.get(id=user)
        except User.DoesNotExist:
            raise Http404()

        if not (request.user.is_a_super_user_or_staff() or user.is_authenticated()):
            raise CommandException(_("You do not have the correct credentials to preform this action."))
    else:
        user = request.user

    question = get_object_or_404(Question, id=id)

    try:
        subscription = QuestionSubscription.objects.get(question=question, user=user)
        subscription.delete()
        subscribed = False
    except:
        subscription = QuestionSubscription(question=question, user=user, auto_subscription=False)
        subscription.save()
        subscribed = True

    return {
        'commands': {
            'set_subscription_button': [subscribed and _('unsubscribe me') or _('subscribe me')],
            'set_subscription_status': ['']
        }
    }

#internally grouped views - used by the tagging system
@ajax_login_required
def mark_tag(request, tag=None, **kwargs):#tagging system
    action = kwargs['action']
    ts = MarkedTag.objects.filter(user=request.user, tag__name=tag)
    if action == 'remove':
        logging.debug('deleting tag %s' % tag)
        ts.delete()
    else:
        reason = kwargs['reason']
        if len(ts) == 0:
            try:
                t = Tag.objects.get(name=tag)
                mt = MarkedTag(user=request.user, reason=reason, tag=t)
                mt.save()
            except:
                pass
        else:
            ts.update(reason=reason)
    return HttpResponse(simplejson.dumps(''), mimetype="application/json")

def matching_tags(request):
    if len(request.GET['q']) == 0:
        raise CommandException(_("Invalid request"))

    possible_tags = Tag.active.filter(name__icontains = request.GET['q'])
    tag_output = ''
    for tag in possible_tags:
        tag_output += "%s|%s|%s\n" % (tag.id, tag.name, tag.used_count)

    return HttpResponse(tag_output, mimetype="text/plain")

def matching_users(request):
    if len(request.GET['q']) == 0:
        raise CommandException(_("Invalid request"))

    possible_users = User.objects.filter(username__icontains = request.GET['q'])
    output = ''

    for user in possible_users:
        output += ("%s|%s|%s\n" % (user.id, user.decorated_name, user.reputation))

    return HttpResponse(output, mimetype="text/plain")

def related_questions(request):
    if request.POST and request.POST.get('title', None):
        can_rank, questions = Question.objects.search(request.POST['title'])
        return HttpResponse(simplejson.dumps(
                [dict(title=q.title, url=q.get_absolute_url(), score=q.score, summary=q.summary)
                 for q in questions.filter_state(deleted=False)[0:10]]), mimetype="application/json")
    else:
        raise Http404()

@decorate.withfn(command)
def answer_permanent_link(request, id):
    # Getting the current answer object
    answer = get_object_or_404(Answer, id=id)

    # Getting the current object URL -- the Application URL + the object relative URL
    url = '%s%s' % (settings.APP_BASE_URL, answer.get_absolute_url())

    # Display the template
    return render_to_response('node/permanent_link.html', { 'url' : url, })

@decorate.withfn(command)
def award_points(request, user_id, answer_id):
    user = request.user
    awarded_user = get_object_or_404(User, id=user_id)
    answer = get_object_or_404(Answer, id=answer_id)

    # Users shouldn't be able to award themselves
    if awarded_user.id == user.id:
        raise CannotDoOnOwnException(_("award"))

    # Anonymous users cannot award  points, they just don't have such
    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('award'))

    if not request.POST:
        return render_to_response("node/award_points.html", { 'user' : user, 'awarded_user' : awarded_user, })
    else:
        points = int(request.POST['points'])

        # We should check if the user has enough reputation points, otherwise we raise an exception.
        if user.reputation < points:
            raise NotEnoughRepPointsException(_("award"))

        extra = dict(message=request.POST.get('message', ''), awarding_user=request.user.id, value=points)

        # We take points from the awarding user
        BonusRepAction(user=request.user, extra=extra).save(data=dict(value=-points, affected=user))

        # And give them to the awarded one
        BonusRepAction(user=request.user, extra=extra).save(data=dict(value=points, affected=awarded_user))

        return { 'message' : _("You have awarded %s with %d points") % (awarded_user, points) }
