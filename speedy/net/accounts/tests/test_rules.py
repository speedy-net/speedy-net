from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import unittest

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_net

        from speedy.core.accounts.tests.test_rules import ViewProfileRulesTestCaseMixin


        @only_on_speedy_net
        class ViewProfileRulesTestCase(ViewProfileRulesTestCaseMixin, SiteTestCase):
            def test_doron_and_jennifer_have_access(self):
                self.assertIs(expr1=self.doron.has_perm(perm='accounts.view_profile', obj=self.jennifer), expr2=True)
                self.assertIs(expr1=self.jennifer.has_perm(perm='accounts.view_profile', obj=self.doron), expr2=True)

            @unittest.skip(reason="This test is irrelevant in Speedy Net.")
            def test_doron_and_jennifer_have_no_access(self):
                raise NotImplementedError()


