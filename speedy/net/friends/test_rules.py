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
