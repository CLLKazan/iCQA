from os import linesep
from csv import reader, QUOTE_NONE
import markdown
from markdown import Extension
from markdown.preprocessors import Preprocessor
import re

from forum import settings

class SettingsExtension(markdown.Extension):
    def __init__(self, configs):
        self.configs = {} # settings.REP_TO_VOTE_UP}
        for key, value in configs:
            self.config[key] = value

        # self.extendMarkdown(markdown.Markdown()., config)

    def reset(self):
        pass

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        self.parser = md.parser
        md.preprocessors.add('MinRep', SettingsPre(self), '_begin')

SETTING_RE = re.compile(r'\|[A-Z_]+\|')

def setting_rep_callback(m):
    setting_name = m.group(0).strip('|')
    if hasattr(settings, setting_name):
        return unicode(getattr(settings, setting_name))
    else:
        return ''


class SettingsPre(Preprocessor):
    def run(self, lines):
        new_lines = []
        for line in lines:
            new_lines.append(SETTING_RE.sub(setting_rep_callback, line))

        return new_lines


def makeExtension(configs=None) :
    return SettingsExtension(configs=configs)