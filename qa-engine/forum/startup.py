import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'markdownext'))

from forum.modules import get_modules_script

get_modules_script('settings')
get_modules_script('startup')


import forum.badges
import forum.subscriptions
import forum.registry



