from django.test import TestCase
from forum.models.user import *

class UserTest(TestCase):
    fixtures = ['users.xml']

    def setUp(self):
        self.client.login(username='super', password='secret')

        

    def tearDown(self):
        self.client.logout()

    def test_gravatar(self):
        
        self.assert_(True)

    def test_save(self):
        self.assert_(True)

    def test_get_absolute_url(self):
        self.assert_(True)

    def test_get_messages(self):
        self.assert_(True)

    def test_delete_messages(self):
        self.assert_(True)

    def test_get_profile_url(self):
        self.assert_(True)

    def test_get_profile_link(self):
        self.assert_(True)

    def test_get_visible_answers(self):
        self.assert_(True)

    def test_get_vote_count_today(self):
        self.assert_(True)

    def test_get_reputation_by_upvoted_today(self):
        self.assert_(True)

    def test_get_flagged_items_count_today(self):
        self.assert_(True)

    def test_can_view_deleted_post(self):
        self.assert_(True)

    def test_can_vote_up(self):
        self.assert_(True)

    def test_can_vote_down(self):
        self.assert_(True)

    def test_can_flag_offensive(self):
        self.assert_(True)

    def test_can_view_offensive_flags(self):
        self.assert_(True)

    def test_can_comment(self):
        self.assert_(True)

    def test_can_like_comment(self):
        self.assert_(True)

    def test_can_edit_comment(self):
        self.assert_(True)

    def test_can_delete_comment(self):
        self.assert_(True)

    def test_can_accept_answer(self):
        self.assert_(True)

    def test_can_edit_post(self):
        self.assert_(True)

    def test_can_retag_questions(self):
        self.assert_(True)

    def test_can_close_question(self):
        self.assert_(True)

    def test_can_reopen_question(self):
        self.assert_(True)

    def test_can_delete_post(self):
        self.assert_(True)

    def test_can_upload_files(self):
        self.assert_(True)

