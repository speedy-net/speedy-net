from django.test import TestCase

from speedy.net.accounts.test_factories import UserFactory


class UserFriendListViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_can_open_the_page(self):
        self.client.logout()
        r = self.client.get('/{}/friends/'.format(self.user.slug))
        self.assertEqual(r.status_code, 200)

    def test_user_can_open_his_friends_page(self):
        r = self.client.get('/{}/friends/'.format(self.user.slug))
        self.assertEqual(r.status_code, 200)

    def test_user_can_open_other_users_friends_page(self):
        r = self.client.get('/{}/friends/'.format(self.other_user.slug))
        self.assertEqual(r.status_code, 200)


class UserFriendRequestViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.page_url = '/{}/friends/request/'.format(self.other_user.slug)
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_cannot_send_friend_request(self):
        self.client.logout()
        r = self.client.post(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_can_send_friend_request(self):
        r = self.client.post(self.page_url)
        self.assertRedirects(r, self.other_user.get_absolute_url())
