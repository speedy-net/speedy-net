"""
Test cases for the view profile and delete account rules of Speedy Net.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import unittest

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_net

        from speedy.core.accounts.test.user_factories import InactiveUserFactory, SpeedyNetInactiveUserFactory, ActiveUserFactory

        from speedy.core.accounts.tests.test_rules import ViewProfileRulesTestCaseMixin


        @only_on_speedy_net
        class ViewProfileRulesOnlyEnglishTestCase(ViewProfileRulesTestCaseMixin, SiteTestCase):
            """
            Test the view profile permission rule on Speedy Net (English only, the rule logic doesn't depend on the language).

            Methods:
                test_doron_and_jennifer_have_access(self): Verify both users can view each other's profile on Speedy Net.
                test_doron_and_jennifer_have_no_access(self): Skipped; irrelevant on Speedy Net since profiles are always visible.
            """
            def test_doron_and_jennifer_have_access(self):
                """
                Verify both users can view each other's profile on Speedy Net.
                """
                self.assertIs(expr1=self.doron.has_perm(perm='accounts.view_profile', obj=self.jennifer), expr2=True)
                self.assertIs(expr1=self.jennifer.has_perm(perm='accounts.view_profile', obj=self.doron), expr2=True)

            @unittest.skip(reason="This test is irrelevant in Speedy Net.")
            def test_doron_and_jennifer_have_no_access(self):
                """
                Skipped; irrelevant on Speedy Net since profiles are always visible.
                """
                raise NotImplementedError("This test is not implemented in this class.")


        @only_on_speedy_net
        class DeleteAccountRulesOnlyEnglishTestCase(SiteTestCase):
            """
            Test the delete account permission rule on Speedy Net (English only, the rule logic doesn't depend on the language).

            Attributes:
                user (speedy.core.accounts.models.User): An active test user created in set_up.

            Methods:
                set_up(self): Creates an active test user.
                test_inactive_user_can_delete_his_account_1(self): Verify a user can delete their account only after deactivating their Speedy Net profile.
                test_inactive_user_can_delete_his_account_2(self): Verify a user created inactive (InactiveUserFactory) can delete their own account.
                test_inactive_user_can_delete_his_account_3(self): Verify a user created inactive on Speedy Net (SpeedyNetInactiveUserFactory) can delete their own account.
                test_active_user_cannot_delete_his_account(self): Verify an active user cannot delete their account even after deactivating only their Speedy Match profile.
                test_user_cannot_delete_other_user_account(self): Verify a user cannot delete another user's account regardless of either user's active/inactive state.
            """
            def set_up(self):
                """
                Creates an active test user.
                """
                super().set_up()
                self.user = ActiveUserFactory()

            def test_inactive_user_can_delete_his_account_1(self):
                """
                Verify a user can delete their account only after deactivating their Speedy Net profile.
                """
                self.assertIs(expr1=self.user.has_perm(perm='accounts.delete_account', obj=self.user), expr2=False)
                self.user.speedy_net_profile.deactivate()
                self.assertIs(expr1=self.user.has_perm(perm='accounts.delete_account', obj=self.user), expr2=True)

            def test_inactive_user_can_delete_his_account_2(self):
                """
                Verify a user created inactive (InactiveUserFactory) can delete their own account.
                """
                user_2 = InactiveUserFactory()
                self.assertIs(expr1=user_2.has_perm(perm='accounts.delete_account', obj=user_2), expr2=True)

            def test_inactive_user_can_delete_his_account_3(self):
                """
                Verify a user created inactive on Speedy Net (SpeedyNetInactiveUserFactory) can delete their own account.
                """
                user_2 = SpeedyNetInactiveUserFactory()
                self.assertIs(expr1=user_2.has_perm(perm='accounts.delete_account', obj=user_2), expr2=True)

            def test_active_user_cannot_delete_his_account(self):
                """
                Verify an active user cannot delete their account even after deactivating only their Speedy Match profile.
                """
                self.assertIs(expr1=self.user.has_perm(perm='accounts.delete_account', obj=self.user), expr2=False)
                # Deactivate the user's profile on Speedy Match, but not on Speedy Net.
                self.user.speedy_match_profile.deactivate()
                self.assertIs(expr1=self.user.has_perm(perm='accounts.delete_account', obj=self.user), expr2=False)

            def test_user_cannot_delete_other_user_account(self):
                """
                Verify a user cannot delete another user's account regardless of either user's active or inactive state.
                """
                user_2 = ActiveUserFactory()
                self.assertIs(expr1=self.user.has_perm(perm='accounts.delete_account', obj=user_2), expr2=False)
                user_2.speedy_net_profile.deactivate()
                self.assertIs(expr1=self.user.has_perm(perm='accounts.delete_account', obj=user_2), expr2=False)
                self.user.speedy_net_profile.deactivate()
                self.assertIs(expr1=self.user.has_perm(perm='accounts.delete_account', obj=user_2), expr2=False)
                user_2.speedy_net_profile.activate()
                self.assertIs(expr1=self.user.has_perm(perm='accounts.delete_account', obj=user_2), expr2=False)
                self.user.speedy_net_profile.activate()
                self.assertIs(expr1=self.user.has_perm(perm='accounts.delete_account', obj=user_2), expr2=False)


