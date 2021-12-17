from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import unittest

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match
        from speedy.core.friends.tests.test_rules import ViewFriendListRulesTestCaseMixin


        @only_on_speedy_match
        class ViewFriendListRulesTestCase(ViewFriendListRulesTestCaseMixin, SiteTestCase):
            @unittest.skip(reason="This test is irrelevant in Speedy Match.")
            def test_user_can_view_another_user_friend_list(self):
                raise NotImplementedError()

            def test_user_cannot_view_another_user_friend_list(self):
                self.assertFalse(expr=self.user.has_perm(perm='friends.view_friend_list', obj=self.other_user))


