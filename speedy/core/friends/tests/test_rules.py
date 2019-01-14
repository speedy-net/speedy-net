from django.conf import settings as django_settings
from friendship.models import Friend

from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_sites_with_login
from speedy.core.blocks.models import Block

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.test.user_factories import ActiveUserFactory


@only_on_sites_with_login
class RequestTestCase(SiteTestCase):
    def set_up(self):
        super().set_up()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()

    def test_user_can_send_request_to_other_user(self):
        self.assertTrue(expr=self.user.has_perm(perm='friends.request', obj=self.other_user))

    def test_user_cannot_send_request_to_other_user_if_blocked(self):
        Block.objects.block(blocker=self.other_user, blocked=self.user)
        self.assertFalse(expr=self.user.has_perm(perm='friends.request', obj=self.other_user))
        self.assertFalse(expr=self.other_user.has_perm(perm='friends.request', obj=self.user))

    def test_user_cannot_send_request_to_himself(self):
        self.assertFalse(expr=self.user.has_perm(perm='friends.request', obj=self.user))

    def test_user_cannot_send_second_request(self):
        Friend.objects.add_friend(from_user=self.user, to_user=self.other_user)
        self.assertFalse(expr=self.user.has_perm(perm='friends.request', obj=self.other_user))


@only_on_sites_with_login
class ViewRequestsTestCase(SiteTestCase):
    def set_up(self):
        super().set_up()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()

    def test_user_cannot_view_incoming_requests_for_other_user(self):
        self.assertFalse(expr=self.user.has_perm(perm='friends.view_requests', obj=self.other_user))

    def test_user_can_view_incoming_requests(self):
        self.assertTrue(expr=self.user.has_perm(perm='friends.view_requests', obj=self.user))


@only_on_sites_with_login
class RemoveTestCase(SiteTestCase):
    def set_up(self):
        super().set_up()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        Friend.objects.add_friend(from_user=self.user, to_user=self.other_user).accept()

    def test_user_can_remove_other_user(self):
        self.assertTrue(expr=self.user.has_perm(perm='friends.remove', obj=self.other_user))

    def test_other_user_can_remove_user(self):
        self.assertTrue(expr=self.other_user.has_perm(perm='friends.remove', obj=self.user))

    def test_user_cannot_remove_himself(self):
        self.assertFalse(expr=self.user.has_perm(perm='friends.remove', obj=self.user))

    def test_user_cannot_remove_other_user_if_not_friends(self):
        Friend.objects.remove_friend(from_user=self.user, to_user=self.other_user)
        self.assertFalse(expr=self.user.has_perm(perm='friends.remove', obj=self.other_user))


