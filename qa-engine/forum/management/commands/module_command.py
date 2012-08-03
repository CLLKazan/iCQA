from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    def handle(self, *args, **options):

        for path in args:
            m = __import__('forum_modules.%s' % path, globals(), locals(), ['forum_modules'])

            if hasattr(m, 'run'):
                run = getattr(m, 'run')
                if callable(run):
                    run()
