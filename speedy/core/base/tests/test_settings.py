from django.conf import settings

from speedy.core.base.test.models import SiteTestCase


class SettingsTestCase(SiteTestCase):
    def test_sites_with_login(self):
        self.assertListEqual(list1=settings.SITES_WITH_LOGIN, list2=[settings.SPEEDY_NET_SITE_ID, settings.SPEEDY_MATCH_SITE_ID])

    def test_xd_auth_sites(self):
        self.assertListEqual(list1=settings.XD_AUTH_SITES, list2=settings.SITES_WITH_LOGIN)

    def test_login_enabled(self):
        self.assertEqual(first=settings.LOGIN_ENABLED, second=(settings.SITE_ID in settings.SITES_WITH_LOGIN))

    def test_zzzyyyxxx(self): #### TODO
        raise Exception


