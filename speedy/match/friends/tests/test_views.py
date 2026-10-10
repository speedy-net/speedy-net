from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import unittest

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.core.friends.tests.test_views import UserFriendListViewTestCaseMixin


        @only_on_speedy_match
        class UserFriendListViewOnlyEnglishTestCase(UserFriendListViewTestCaseMixin, SiteTestCase):
            """
            Tests access to the user friend-list page in Speedy Match, run only once (in English) since it is language-independent.

            Methods:
                test_visitor_can_open_the_page(self): Skipped - not implemented in this class.
                test_visitor_cannot_open_the_page(self): Asserts a logged-out visitor is redirected to the login page.
                test_user_can_open_other_users_friends_page(self): Skipped - not implemented in this class.
                test_user_cannot_open_other_users_friends_page(self): Asserts a logged-in user gets a 403 when trying to view another user's friends page.
            """
            @unittest.skip(reason="This test is irrelevant in Speedy Match.")
            def test_visitor_can_open_the_page(self):
                """
                Skipped. This test is irrelevant in Speedy Match.
                """
                raise NotImplementedError("This test is not implemented in this class.")

            def test_visitor_cannot_open_the_page(self):
                """
                Asserts a logged-out visitor is redirected to the login page when trying to view the friends list page.
                """
                self.client.logout()
                r = self.client.get(path=self.first_user_friends_list_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.first_user_friends_list_url), status_code=302, target_status_code=200)

            @unittest.skip(reason="This test is irrelevant in Speedy Match.")
            def test_user_can_open_other_users_friends_page(self):
                """
                Skipped. This test is irrelevant in Speedy Match.
                """
                raise NotImplementedError("This test is not implemented in this class.")

            def test_user_cannot_open_other_users_friends_page(self):
                """
                Asserts a logged-in user gets a 403 Forbidden response when trying to view another user's friends page, since friend lists are irrelevant in Speedy Match.
                """
                r = self.client.get(path=self.second_user_friends_list_url)
                self.assertEqual(first=r.status_code, second=403)


