from django.test import TestCase
from friendship.models import Friend

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
        self.assertEqual(self.other_user.friendship_requests_received.count(), 1)
        self.assertEqual(self.user.friendship_requests_sent.count(), 1)
        frequest = self.other_user.friendship_requests_received.all()[0]
        self.assertEqual(frequest.from_user, self.user)
        self.assertEqual(frequest.to_user, self.other_user)


class AcceptFriendRequestViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        frequest = Friend.objects.add_friend(self.user, self.other_user)
        self.page_url = '/{}/friends/request/accept/{}/'.format(self.other_user.slug, frequest.id)

    def test_visitor_cannot_accept_friend_request(self):
        self.client.logout()
        r = self.client.post(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_cannot_accept_friend_request_he_sent_another_user(self):
        self.client.login(username=self.user.slug, password='111')
        r = self.client.post(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_that_has_received_request_can_accept_it(self):
        self.client.login(username=self.other_user.slug, password='111')
        self.assertFalse(Friend.objects.are_friends(self.user, self.other_user))
        r = self.client.post(self.page_url)
        self.assertRedirects(r, '/{}/friends/'.format(self.other_user.slug))
        self.assertTrue(Friend.objects.are_friends(self.user, self.other_user))


class RejectFriendRequestViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        frequest = Friend.objects.add_friend(self.user, self.other_user)
        self.page_url = '/{}/friends/request/reject/{}/'.format(self.other_user.slug, frequest.id)

    def test_visitor_cannot_reject_friend_request(self):
        self.client.logout()
        r = self.client.post(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_cannot_reject_friend_request_he_sent_another_user(self):
        self.client.login(username=self.user.slug, password='111')
        r = self.client.post(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_that_has_received_request_can_reject_it(self):
        self.client.login(username=self.other_user.slug, password='111')
        self.assertFalse(Friend.objects.are_friends(self.user, self.other_user))
        r = self.client.post(self.page_url)
        self.assertRedirects(r, '/{}/friends/'.format(self.other_user.slug))
        self.assertFalse(Friend.objects.are_friends(self.user, self.other_user))
        self.assertIsNotNone(self.other_user.friendship_requests_received.all()[0].rejected)
