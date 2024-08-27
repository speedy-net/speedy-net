from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import unittest

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_net

        from speedy.core.friends.tests.test_views import UserFriendListViewTestCaseMixin


        @only_on_speedy_net
        class UserFriendListViewOnlyEnglishTestCase(UserFriendListViewTestCaseMixin, SiteTestCase):
            def test_visitor_can_open_the_page(self):
                self.client.logout()
                r = self.client.get(path=self.first_user_friends_list_url)
                self.assertEqual(first=r.status_code, second=200)

            @unittest.skip(reason="This test is irrelevant in Speedy Net.")
            def test_visitor_cannot_open_the_page(self):
                raise NotImplementedError()

            def test_user_can_open_other_users_friends_page(self):
                r = self.client.get(path=self.second_user_friends_list_url)
                self.assertEqual(first=r.status_code, second=200)

            @unittest.skip(reason="This test is irrelevant in Speedy Net.")
            def test_user_cannot_open_other_users_friends_page(self):
                raise NotImplementedError()


