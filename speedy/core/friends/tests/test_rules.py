from friendship.models import Friend

from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software
from speedy.core.blocks.models import Block


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class RequestTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()

    def test_user_can_send_request_to_other_user(self):
        self.assertTrue(expr=self.user.has_perm('friends.request', self.other_user))

    def test_user_cannot_send_request_to_other_user_if_blocked(self):
        Block.objects.block(blocker=self.other_user, blocked=self.user)
        self.assertFalse(expr=self.user.has_perm('friends.request', self.other_user))
        self.assertFalse(expr=self.other_user.has_perm('friends.request', self.user))

    def test_user_cannot_send_request_to_himself(self):
        self.assertFalse(expr=self.user.has_perm('friends.request', self.user))

    def test_user_cannot_send_second_request(self):
        Friend.objects.add_friend(self.user, self.other_user)
        self.assertFalse(expr=self.user.has_perm('friends.request', self.other_user))


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class ViewRequestsTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()

    def test_user_cannot_view_incoming_requests_for_other_user(self):
        self.assertFalse(expr=self.user.has_perm('friends.view_requests', self.other_user))

    def test_user_can_view_incoming_requests(self):
        self.assertTrue(expr=self.user.has_perm('friends.view_requests', self.user))


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class RemoveTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        Friend.objects.add_friend(self.user, self.other_user).accept()

    def test_user_can_remove_other_user(self):
        self.assertTrue(expr=self.user.has_perm('friends.remove', self.other_user))

    def test_other_user_can_remove_user(self):
        self.assertTrue(expr=self.other_user.has_perm('friends.remove', self.user))

    def test_user_cannot_remove_himself(self):
        self.assertFalse(expr=self.user.has_perm('friends.remove', self.user))

    def test_user_cannot_remove_other_user_if_not_friends(self):
        Friend.objects.remove_friend(self.user, self.other_user)
        self.assertFalse(expr=self.user.has_perm('friends.remove', self.other_user))
