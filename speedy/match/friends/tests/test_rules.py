from django.conf import settings as django_settings

from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_speedy_match

if (django_settings.LOGIN_ENABLED):
    from speedy.core.friends.tests.test_rules import ViewFriendListRulesTestCaseMixin


    @only_on_speedy_match
    class ViewFriendListRulesTestCase(ViewFriendListRulesTestCaseMixin, SiteTestCase):
        def test_user_can_view_another_user_friend_list(self): # ~~~~ TODO: fails!
            self.assertTrue(expr=self.user.has_perm(perm='friends.view_friend_list', obj=self.other_user)) # ~~~~ TODO: fails!

        def test_user_cannot_view_another_user_friend_list(self):
            self.assertFalse(expr=self.user.has_perm(perm='friends.view_friend_list', obj=self.other_user))


