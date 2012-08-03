import re
import sys, traceback
from django.core.management.base import NoArgsCommand

OK_MESSAGE = "  Found %(what)s version %(version)s - OK"

OLD_VERSION_ERROR = """  ERROR: Found %(what)s version %(version)s - you should upgrade it to at least %(minimum)s.
                Package installers like apt-get or yum usually maintain old versions of libraries in the repositories."""

NOT_FOUND_ERROR = "ERROR: %(what)s was not found on your system."

HOW_TO_INSTALL = """  Try easy_install %(what)s or download it from %(where)s"""

IMPORT_ERROR_MESSAGE = """Importing %(what)s is throwing an exception. Here's the full stack trace:"""

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        print "Checking dependencies:"

        try:
            import html5lib
            print "  Found html5lib - OK"
        except ImportError:
            print NOT_FOUND_ERROR % dict(what='html5lib')
            print HOW_TO_INSTALL % dict(what='html5lib', where='http://code.google.com/p/html5lib/')
        except Exception, e:
            print IMPORT_ERROR_MESSAGE % dict(what='html5lib')
            traceback.print_exc(file=sys.stdout)

        try:
            import markdown
            version = int(re.findall('^\d+', markdown.version)[0])
            if version < 2:
                print OLD_VERSION_ERROR % dict(what='markdown', version=markdown.version, minimum='2.0')
                print HOW_TO_INSTALL % dict(what='markdown', where='http://www.freewisdom.org/projects/python-markdown/')
            else:
                print OK_MESSAGE % dict(what='markdown', version=markdown.version)
        except ImportError:
            print NOT_FOUND_ERROR % dict(what='markdown')
            print HOW_TO_INSTALL % dict(what='markdown', where='http://www.freewisdom.org/projects/python-markdown/')
        except Exception, e:
            print IMPORT_ERROR_MESSAGE % dict(what='markdown')
            traceback.print_exc(file=sys.stdout)

        try:
            import south
            version = re.findall('\d+', south.__version__)

            if int(version[1]) < 6 and int(version[0]) == 0:
                print OLD_VERSION_ERROR % dict(what='south', version=south.__version__, minimum='0.6')
                print HOW_TO_INSTALL % dict(what='south', where='http://south.aeracode.org/')
            else:
                print OK_MESSAGE % dict(what='south', version=south.__version__)


        except ImportError:
            print NOT_FOUND_ERROR % dict(what='south')
            print HOW_TO_INSTALL % dict(what='south', where='http://south.aeracode.org/')
        except Exception, e:
            print IMPORT_ERROR_MESSAGE % dict(what='south')
            traceback.print_exc(file=sys.stdout)


        print "\n\nChecking database connection:"

        try:
            from forum.models import User
            User.objects.all().count()
            print "  Connection OK"
        except Exception, e:
            print "There seems to be a problem with your database: %s" % str(e)



        from django.conf import settings

        print "\n\nChecking important settings:"

        if not re.match('^https?:\/\/\w+', settings.APP_URL):
            print " Your APP_URL does not seem to be a valid url. Please fill this setting with the URL of your OSQA installation"
        else:
            print " APP_URL - %s" % settings.APP_URL
            print " APP_BASE_URL - %s" % settings.APP_BASE_URL

        
