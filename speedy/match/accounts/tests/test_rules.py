import unittest

from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_speedy_match
from speedy.core.accounts.tests.test_rules import ViewProfileTestCaseMixin


@only_on_speedy_match
class ViewProfileTestCase(ViewProfileTestCaseMixin, SiteTestCase):
    @unittest.skip
    def test_doron_and_jennifer_have_access(self):
        raise NotImplementedError()

    def test_doron_and_jennifer_have_no_access(self):
        self.assertFalse(expr=self.doron.has_perm(perm='accounts.view_profile', obj=self.jennifer))
        self.assertFalse(expr=self.jennifer.has_perm(perm='accounts.view_profile', obj=self.doron))


