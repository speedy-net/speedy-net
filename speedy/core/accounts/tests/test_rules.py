"""
Test cases for the permission rules of the Speedy Core accounts app.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.accounts.models import User
        from speedy.core.blocks.models import Block


        class ViewProfileRulesTestCaseMixin(TestCaseMixin):
            """
            Mixin testing the 'accounts.view_profile' permission rule, including the effect of blocking and of Speedy Match gender-matching preferences.

            Methods:
                get_active_user_doron(self): Creates and returns an active female user named Doron who only wants to match with males.
                get_active_user_jennifer(self): Creates and returns an active female user named Jennifer with default matching preferences.
                set_up(self): Creates self.user, self.other_user, self.doron and self.jennifer for use by the test methods.
                test_user_and_other_user_have_access(self): Asserts that two mutually-matching users can both view each other's profile.
                test_user_and_other_user_have_no_access_if_blocked(self): Asserts that blocking removes both users' permission to view each other's profile.
                test_doron_and_jennifer_have_access(self): Not implemented in this mixin; must be overridden by subclasses.
                test_doron_and_jennifer_have_no_access(self): Not implemented in this mixin; must be overridden by subclasses.
            """
            def get_active_user_doron(self):
                """
                Creates and returns an active female user named Doron who only wants to match with male users on Speedy Match.

                :return: The created user.
                :rtype: User
                """
                user = ActiveUserFactory(first_name_en="Doron", last_name_en="Matalon", slug="doron-matalon", gender=User.GENDER_FEMALE)
                user.speedy_match_profile.gender_to_match = [User.GENDER_MALE]
                user.save_user_and_profile()
                return user

            def get_active_user_jennifer(self):
                """
                Creates and returns an active female user named Jennifer with the default Speedy Match matching preferences.

                :return: The created user.
                :rtype: User
                """
                user = ActiveUserFactory(first_name_en="Jennifer", last_name_en="Connelly", slug="jennifer-connelly", gender=User.GENDER_FEMALE)
                user.save_user_and_profile()
                return user

            def set_up(self):
                """
                Creates self.user and self.other_user (who match each other by default), and self.doron and self.jennifer (who don't match on Speedy Match).
                """
                super().set_up()
                # The default for ActiveUserFactory() on Speedy Match is to match everybody with 5 stars.
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()
                # Doron wants to meet only male and Jennifer is a female, therefore they don't match on Speedy Match.
                self.doron = self.get_active_user_doron()
                self.jennifer = self.get_active_user_jennifer()

            def test_user_and_other_user_have_access(self):
                """
                Asserts that self.user and self.other_user both have permission to view each other's profile.
                """
                self.assertIs(expr1=self.user.has_perm(perm='accounts.view_profile', obj=self.other_user), expr2=True)
                self.assertIs(expr1=self.other_user.has_perm(perm='accounts.view_profile', obj=self.user), expr2=True)

            def test_user_and_other_user_have_no_access_if_blocked(self):
                """
                Asserts that after self.other_user blocks self.user, neither of them has permission to view the other's profile.
                """
                Block.objects.block(blocker=self.other_user, blocked=self.user)
                self.assertIs(expr1=self.user.has_perm(perm='accounts.view_profile', obj=self.other_user), expr2=False)
                self.assertIs(expr1=self.other_user.has_perm(perm='accounts.view_profile', obj=self.user), expr2=False)

            def test_doron_and_jennifer_have_access(self):
                """
                Not implemented in this mixin; subclasses must override this test for the specific site under test.
                """
                raise NotImplementedError("This test is not implemented in this mixin.")

            def test_doron_and_jennifer_have_no_access(self):
                """
                Not implemented in this mixin; subclasses must override this test for the specific site under test.
                """
                raise NotImplementedError("This test is not implemented in this mixin.")


