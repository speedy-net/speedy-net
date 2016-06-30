from django.test import TestCase
from friendship.models import Friend

from speedy.net.accounts.test_factories import UserFactory


class CanFriendRequestTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()

    def test_user_can_send_request_to_other_user(self):
        self.assertTrue(self.user.has_perm('friends.request', self.other_user))

    def test_user_cannot_send_request_to_himself(self):
        self.assertFalse(self.user.has_perm('friends.request', self.user))

    def test_user_cannot_send_second_request(self):
        Friend.objects.add_friend(self.user, self.other_user)
        self.assertFalse(self.user.has_perm('friends.request', self.other_user))


class ViewRequestsTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()

    def test_user_cannot_view_incoming_requests_for_other_user(self):
        self.assertFalse(self.user.has_perm('friends.view_requests', self.other_user))

    def test_user_can_view_incoming_requests(self):
        self.assertTrue(self.user.has_perm('friends.view_requests', self.user))


class RemoveTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        Friend.objects.add_friend(self.user, self.other_user).accept()

    def test_user_can_remove_other_user(self):
        self.assertTrue(self.user.has_perm('friends.remove', self.other_user))

    def test_other_user_can_remove_user(self):
        self.assertTrue(self.other_user.has_perm('friends.remove', self.user))

    def test_user_cannot_remove_himself(self):
        self.assertFalse(self.user.has_perm('friends.remove', self.user))

    def test_user_cannot_remove_other_user_if_not_friends(self):
        Friend.objects.remove_friend(self.user, self.other_user)
        self.assertFalse(self.user.has_perm('friends.remove', self.other_user))
