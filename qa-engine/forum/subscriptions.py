import os
import re
import datetime
import logging
from forum.models import User, Question, Comment, QuestionSubscription, SubscriptionSettings, Answer
from forum.utils.mail import send_template_email
from django.utils.translation import ugettext as _
from forum.actions import AskAction, AnswerAction, CommentAction, AcceptAnswerAction, UserJoinsAction, QuestionViewAction
from forum import settings
from django.db.models import Q, F

def create_subscription_if_not_exists(question, user):
    try:
        subscription = QuestionSubscription.objects.get(question=question, user=user)
    except:
        subscription = QuestionSubscription(question=question, user=user)
        subscription.save()

def filter_subscribers(subscribers):
    subscribers = subscribers.exclude(is_active=False)

    if settings.DONT_NOTIFY_UNVALIDATED:
        return subscribers.exclude(email_isvalid=False)
    else:
        return subscribers

def question_posted(action, new):
    question = action.node

    subscribers = User.objects.filter(
            Q(subscription_settings__enable_notifications=True, subscription_settings__new_question='i') |
            (Q(subscription_settings__new_question_watched_tags='i') &
              Q(marked_tags__name__in=question.tagnames.split(' ')) &
              Q(tag_selections__reason='good'))
    ).exclude(id=question.author.id).distinct()

    subscribers = filter_subscribers(subscribers)

    send_template_email(subscribers, "notifications/newquestion.html", {'question': question})

    subscription = QuestionSubscription(question=question, user=question.author)
    subscription.save()

    new_subscribers = User.objects.filter(
            Q(subscription_settings__all_questions=True) |
            Q(subscription_settings__all_questions_watched_tags=True,
                    marked_tags__name__in=question.tagnames.split(' '),
                    tag_selections__reason='good'))

    for user in new_subscribers:
        create_subscription_if_not_exists(question, user)

AskAction.hook(question_posted)


def answer_posted(action, new):
    answer = action.node
    question = answer.question

    subscribers = question.subscribers.filter(
            subscription_settings__enable_notifications=True,
            subscription_settings__notify_answers=True,
            subscription_settings__subscribed_questions='i'
    ).exclude(id=answer.author.id).distinct()

    subscribers = filter_subscribers(subscribers)

    send_template_email(subscribers, "notifications/newanswer.html", {'answer': answer})

    create_subscription_if_not_exists(question, answer.author)

AnswerAction.hook(answer_posted)


def comment_posted(action, new):
    comment = action.node
    post = comment.parent

    if post.__class__ == Question:
        question = post
    else:
        question = post.question

    q_filter = Q(subscription_settings__notify_comments=True) | Q(subscription_settings__notify_comments_own_post=True, id=post.author.id)

    inreply = re.search('@\w+', comment.comment)
    if inreply is not None:
        q_filter = q_filter | Q(subscription_settings__notify_reply_to_comments=True,
                                username__istartswith=inreply.group(0)[1:],
                                nodes__parent=post, nodes__node_type="comment")

    subscribers = question.subscribers.filter(
            q_filter, subscription_settings__subscribed_questions='i', subscription_settings__enable_notifications=True
    ).exclude(id=comment.user.id).distinct()

    subscribers = filter_subscribers(subscribers)


    send_template_email(subscribers, "notifications/newcomment.html", {'comment': comment})

    create_subscription_if_not_exists(question, comment.user)

CommentAction.hook(comment_posted)


def answer_accepted(action, new):
    question = action.node.question

    subscribers = question.subscribers.filter(
            subscription_settings__enable_notifications=True,
            subscription_settings__subscribed_questions='i'
    ).exclude(id=action.node.nstate.accepted.by.id).distinct()
    
    subscribers = filter_subscribers(subscribers)

    send_template_email(subscribers, "notifications/answeraccepted.html", {'answer': action.node})

AcceptAnswerAction.hook(answer_accepted)


def member_joined(action, new):
    subscribers = User.objects.filter(
            subscription_settings__enable_notifications=True,
            subscription_settings__member_joins='i'
    ).exclude(id=action.user.id).distinct()

    subscribers = filter_subscribers(subscribers)

    send_template_email(subscribers, "notifications/newmember.html", {'newmember': action.user})

UserJoinsAction.hook(member_joined)

def question_viewed(action, new):
    if not action.viewuser.is_authenticated():
        return

    try:
        subscription = QuestionSubscription.objects.get(question=action.node, user=action.viewuser)
        subscription.last_view = datetime.datetime.now()
        subscription.save()
    except:
        if action.viewuser.subscription_settings.questions_viewed:
            subscription = QuestionSubscription(question=action.node, user=action.viewuser)
            subscription.save()

QuestionViewAction.hook(question_viewed)


#todo: translate this
#record_answer_event_re = re.compile("You have received (a|\d+) .*new response.*")
#def record_answer_event(instance, created, **kwargs):
#    if created:
#        q_author = instance.question.author
#        found_match = False
#        #print 'going through %d messages' % q_author.message_set.all().count()
#        for m in q_author.message_set.all():
##            #print m.message
# #           match = record_answer_event_re.search(m.message)
#            if match:
#                found_match = True
#                try:
#                    cnt = int(match.group(1))
#                except:
#                    cnt = 1
##                m.message = u"You have received %d <a href=\"%s?sort=responses\">new responses</a>."\
# #                           % (cnt+1, q_author.get_profile_url())
#
#                m.save()
#                break
#        if not found_match:
#            msg = u"You have received a <a href=\"%s?sort=responses\">new response</a>."\
#                    % q_author.get_profile_url()
#
#            q_author.message_set.create(message=msg)
#
#post_save.connect(record_answer_event, sender=Answer)
