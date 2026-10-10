"""
Test cases for the friends list view rules of Speedy Match.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import unittest

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.core.friends.tests.test_rules import ViewFriendListRulesTestCaseMixin


        @only_on_speedy_match
        class ViewFriendListRulesOnlyEnglishTestCase(ViewFriendListRulesTestCaseMixin, SiteTestCase):
            """
            Tests the view-friend-list permission rule in Speedy Match, run only once (in English) since it is language-independent.

            Methods:
                test_user_can_view_another_user_friend_list(self): Skipped - not implemented in this class.
                test_user_cannot_view_another_user_friend_list(self): Asserts a user has no permission to view another user's friend list, since friend lists are irrelevant in Speedy Match.
            """
            @unittest.skip(reason="This test is irrelevant in Speedy Match.")
            def test_user_can_view_another_user_friend_list(self):
                """
                Skipped. This test is irrelevant in Speedy Match.
                """
                raise NotImplementedError("This test is not implemented in this class.")

            def test_user_cannot_view_another_user_friend_list(self):
                """
                Asserts the user has no permission to view another user's friend list, since friend lists are irrelevant in Speedy Match.
                """
                self.assertIs(expr1=self.user.has_perm(perm='friends.view_friend_list', obj=self.other_user), expr2=False)


