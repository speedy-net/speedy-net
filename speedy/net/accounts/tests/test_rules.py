from speedy.core.test import TestCase
from friendship.models import Friend

from speedy.core.test import exclude_on_speedy_match
from speedy.net.accounts.models import ACCESS_FRIENDS, ACCESS_ME
from speedy.net.blocks.models import Block
from .test_factories import UserFactory


class ViewProfileTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()

    @exclude_on_speedy_match
    def test_has_access(self):
        self.assertTrue(self.user.has_perm('accounts.view_profile', self.other_user))
        self.assertTrue(self.other_user.has_perm('accounts.view_profile', self.user))

    @exclude_on_speedy_match
    def test_has_no_access_if_friends_only(self):
        self.other_user.profile.access_account = ACCESS_FRIENDS
        self.other_user.profile.save()
        self.assertFalse(self.user.has_perm('accounts.view_profile', self.other_user))
        self.assertTrue(self.other_user.has_perm('accounts.view_profile', self.user))

    def test_has_access_if_friends_only(self):
        self.other_user.profile.access_account = ACCESS_FRIENDS
        self.other_user.profile.save()
        Friend.objects.add_friend(self.user, self.other_user).accept()
        self.assertTrue(self.user.has_perm('accounts.view_profile', self.other_user))
        self.assertTrue(self.other_user.has_perm('accounts.view_profile', self.user))

    def test_has_no_access_if_private(self):
        self.other_user.profile.access_account = ACCESS_ME
        self.other_user.profile.save()
        Friend.objects.add_friend(self.user, self.other_user).accept()
        self.assertFalse(self.user.has_perm('accounts.view_profile', self.other_user))
        self.assertTrue(self.other_user.has_perm('accounts.view_profile', self.user))

    @exclude_on_speedy_match
    def test_has_no_access_if_blocked(self):
        Block.objects.block(blocker=self.other_user, blockee=self.user)
        self.assertFalse(self.user.has_perm('accounts.view_profile', self.other_user))
        self.assertTrue(self.other_user.has_perm('accounts.view_profile', self.user))
