"""
Test cases for the permission rules of the Speedy Match accounts app (viewing profiles).
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import unittest

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.core.accounts.tests.test_rules import ViewProfileRulesTestCaseMixin


        @only_on_speedy_match
        class ViewProfileRulesOnlyEnglishTestCase(ViewProfileRulesTestCaseMixin, SiteTestCase):
            """
            Tests the "view_profile" permission rule on Speedy Match, run only once (in English) since it is language-independent.

            Methods:
                test_doron_and_jennifer_have_access(self): Skipped on Speedy Match, since this scenario grants no access here.
                test_doron_and_jennifer_have_no_access(self): Asserts neither Doron nor Jennifer have profile view access to each other.
            """

            @unittest.skip(reason="This test is irrelevant in Speedy Match.")
            def test_doron_and_jennifer_have_access(self):
                """
                Not implemented on Speedy Match - this scenario is irrelevant here and the test is skipped.

                :raises NotImplementedError: Always, since this test is not implemented in this class.
                """
                raise NotImplementedError("This test is not implemented in this class.")

            def test_doron_and_jennifer_have_no_access(self):
                """
                Asserts that neither Doron nor Jennifer have profile view access to each other by default on Speedy Match.
                """
                self.assertIs(expr1=self.doron.has_perm(perm='accounts.view_profile', obj=self.jennifer), expr2=False)
                self.assertIs(expr1=self.jennifer.has_perm(perm='accounts.view_profile', obj=self.doron), expr2=False)


