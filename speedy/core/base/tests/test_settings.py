from django.conf import settings as django_settings

from speedy.core.base.test.models import SiteTestCase


class SettingsTestCase(SiteTestCase):
    def test_sites_with_login(self):
        self.assertListEqual(list1=django_settings.SITES_WITH_LOGIN, list2=[django_settings.SPEEDY_NET_SITE_ID, django_settings.SPEEDY_MATCH_SITE_ID])

    def test_xd_auth_sites(self):
        self.assertListEqual(list1=django_settings.XD_AUTH_SITES, list2=django_settings.SITES_WITH_LOGIN)

    def test_login_enabled(self):
        self.assertEqual(first=django_settings.LOGIN_ENABLED, second=(django_settings.SITE_ID in django_settings.SITES_WITH_LOGIN))

    def test_zzzyyyxxx(self): #### TODO
        raise Exception


