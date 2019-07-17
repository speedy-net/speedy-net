import unittest
from django.conf import settings as django_settings

from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_speedy_net

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.tests.test_rules import ViewProfileRulesTestCaseMixin


    @only_on_speedy_net
    class ViewProfileRulesTestCase(ViewProfileRulesTestCaseMixin, SiteTestCase):
        def test_doron_and_jennifer_have_access(self):
            self.assertTrue(expr=self.doron.has_perm(perm='accounts.view_profile', obj=self.jennifer))
            self.assertTrue(expr=self.jennifer.has_perm(perm='accounts.view_profile', obj=self.doron))

        @unittest.skip
        def test_doron_and_jennifer_have_no_access(self):
            raise NotImplementedError()


