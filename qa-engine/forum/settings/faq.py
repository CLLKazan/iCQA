from base import Setting, SettingSet
from django.forms.widgets import Textarea

FAQ_SET = SettingSet('faq', 'FAQ page', "Define the text in the about page. You can use markdown and some basic html tags.", 2000, True)

FAQ_PAGE_TEXT = Setting('FAQ_PAGE_TEXT',
u"""
**Please customize this text in the administration area**

**Frequently Asked Questions (FAQ)**

**How is a Question/Answer community different from a typical forum?**

A Question/Answer community is different from a typical forum because it focuses on finding answers to the questions of its members.  A typical forum, by contrast, operates more like a discussion group, where people are free to give their opinions and topics tend to be more subjective.

By keeping a laser focus on questions and answers, this community ensures that finding answers to existing questions - and getting answers to new questions - can be done without any distractions.

**What kinds of questions can I ask here?**

Most importantly - questions should be relevant to this community. Before you ask, please make sure to search for a similar question. You can search for questions by their title, content, or tags.

**What kinds of questions should be avoided?**

Please avoid asking questions that are not relevant to this community, are too subjective or argumentative.

**What should I avoid in my answers?**

OSQA: Open Source Q&A Forum is a question and answer site - it is not a discussion group. Please avoid holding debates in your answers as they tend to dilute the essense of questions and answers. For brief discussions please use commenting facility.

** Why are email notifications so important? **

Email notifications are the bedrock of a successful question and answer community. These notifications allow community members to be notified of important events, such as:

* When their questions have been answered
* When one of their posts is commented on by another member
* When other members post new questions, answers, or comments in their area of interest

The success of the community relies upon community member involvement, and members are much more likely to become involved, active participants on the site when they're notified of interesting developments.  That is why this community considers a valid email address as a requirement for participating in the community and using this site.

If you're already a member of this community and haven't validated your email address, you can do so [here](/account/send-validation/ "Validate Email Address").  If you aren't yet a member of this community, join up by [creating a new account](/account/local/register/ "Create a new account").

 **Who moderates this community?**

The short answer is: you. This website is moderated by the users. The community features a karma system that allows users to earn rights to perform a variety of moderation tasks.

**How does the karma system work?**

When a question or answer is upvoted, the user who posted them will gain some points, which are called "karma points". These points serve as a rough measure of the community trust in him/her. Various moderation tasks are gradually assigned to the users based on those points.

For example, if you ask an interesting question or give a helpful answer, your input will be upvoted. On the other hand if the answer is misleading, it will be downvoted. Each vote in favor will generate |REP_GAIN_BY_UPVOTED| points, each vote against will subtract |REP_LOST_BY_DOWNVOTED| points. There is a limit of 200 points that can be accumulated per question or answer. The table below explains karma requirements for each type of moderation task.

* add comments ->  |REP_TO_COMMENT|
* delete comments -> |REP_TO_DELETE_COMMENTS|
* close own questions -> |REP_TO_CLOSE_OWN|
* reopen own questions -> |REP_TO_REOPEN_OWN|
* retag questions -> |REP_TO_RETAG|
* edit any answer -> |REP_TO_EDIT_OTHERS|
* open any closed question -> |REP_TO_CLOSE_OTHERS|
* delete any comment -> |REP_TO_DELETE_COMMENTS|

**What is a gravatar?**

Gravatar means globally recognized avatar - your unique avatar image associated with your email address. It's simply a picture that shows next to your posts on the websites that support gravatar protocol. The default gravatar appears as a square filled with a snowflake-like figure. You can set your image at gravatar.com

**To participate in this community, do I need to create new account?**

No, you don't have to. You can login through any service that supports OpenID, e.g. Google, Yahoo, AOL, etc. [Login now!](/account/signin/ "Login")

**Why can other people can edit my questions/answers?**

Allowing experienced members of this community to curate the questions and answers improves the overall quality of the knowledge base content. If this approach is not for you, we respect your choice.

**Still have questions?**

Please ask your question, help make our community better!
""", FAQ_SET, dict(
label = "FAQ page text",
help_text = " The faq page. ",
widget=Textarea(attrs={'rows': '25'})))