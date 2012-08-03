from base import Setting, SettingSet
from django.forms.widgets import Textarea

PAGES_SET = SettingSet('about', 'About page', "Define the text in the about page. You can use markdown and some basic html tags.", 2000, True)

ABOUT_PAGE_TEXT = Setting('ABOUT_PAGE_TEXT',
u"""
**Please customize this text in the administration area**

Here you can **ask** and **answer** questions, **comment**
and **vote** for the questions of others and their answers. Both questions and answers
**can be revised** and improved. Questions can be **tagged** with
the relevant keywords to simplify future access and organize the accumulated material.

This <span class="orange">Q&amp;A</span> site is moderated by its members, hopefully - including yourself!
Moderation rights are gradually assigned to the site users based on the accumulated "**karma**"
points. These points are added to the users account when others vote for his/her questions or answers.
These points (very) roughly reflect the level of trust of the community.

No points are necessary to ask or answer the questions - so please - join us!

If you would like to find out more about this site - please see the **frequently asked questions** page.
""", PAGES_SET, dict(
label = "About page text",
help_text = """
The about page.
""",
widget=Textarea(attrs={'rows': '20'})))