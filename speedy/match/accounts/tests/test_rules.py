from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import unittest

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.core.accounts.tests.test_rules import ViewProfileRulesTestCaseMixin


        @only_on_speedy_match
        class ViewProfileRulesOnlyEnglishTestCase(ViewProfileRulesTestCaseMixin, SiteTestCase):
            @unittest.skip(reason="This test is irrelevant in Speedy Match.")
            def test_doron_and_jennifer_have_access(self):
                raise NotImplementedError("This test is not implemented.")

            def test_doron_and_jennifer_have_no_access(self):
                self.assertIs(expr1=self.doron.has_perm(perm='accounts.view_profile', obj=self.jennifer), expr2=False)
                self.assertIs(expr1=self.jennifer.has_perm(perm='accounts.view_profile', obj=self.doron), expr2=False)


