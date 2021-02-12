import unittest

from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_speedy_match
    from speedy.core.friends.tests.test_views import UserFriendListViewTestCaseMixin


    @only_on_speedy_match
    class UserFriendListViewTestCase(UserFriendListViewTestCaseMixin, SiteTestCase):
        @unittest.skip(reason="This test is irrelevant in Speedy Match.")
        def test_visitor_can_open_the_page(self):
            raise NotImplementedError()

        def test_visitor_cannot_open_the_page(self):
            self.client.logout()
            r = self.client.get(path=self.first_user_friends_list_url)
            self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.first_user_friends_list_url), status_code=302, target_status_code=200)

        @unittest.skip(reason="This test is irrelevant in Speedy Match.")
        def test_user_can_open_other_users_friends_page(self):
            raise NotImplementedError()

        def test_user_cannot_open_other_users_friends_page(self):
            r = self.client.get(path=self.second_user_friends_list_url)
            self.assertEqual(first=r.status_code, second=403)


