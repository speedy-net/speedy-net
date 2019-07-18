import unittest

from django.conf import settings as django_settings

from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_speedy_net

if (django_settings.LOGIN_ENABLED):
    from speedy.core.friends.tests.test_rules import ViewFriendListRulesTestCaseMixin


    @only_on_speedy_net
    class ViewFriendListRulesTestCase(ViewFriendListRulesTestCaseMixin, SiteTestCase):
        def test_user_can_view_another_user_friend_list(self):
            self.assertTrue(expr=self.user.has_perm(perm='friends.view_friend_list', obj=self.other_user))

        @unittest.skip
        def test_user_cannot_view_another_user_friend_list(self):
            raise NotImplementedError()


