from forum.models import User, SubscriptionSettings, QuestionSubscription
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        users = User.objects.all()
        for u in users:
            s = SubscriptionSettings(user=u)
            s.save()

            user_questions = u.questions.all()

            for q in user_questions:
                sub = QuestionSubscription(user=u, question=q)
                sub.save()