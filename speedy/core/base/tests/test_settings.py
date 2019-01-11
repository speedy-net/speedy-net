from django.conf import settings as django_settings

from speedy.core.settings import tests as tests_settings
from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.utils import normalize_slug, normalize_username


class SettingsTestCase(SiteTestCase):
    def test_sites_with_login(self):
        self.assertListEqual(list1=django_settings.SITES_WITH_LOGIN, list2=[django_settings.SPEEDY_NET_SITE_ID, django_settings.SPEEDY_MATCH_SITE_ID])

    def test_xd_auth_sites(self):
        self.assertListEqual(list1=django_settings.XD_AUTH_SITES, list2=django_settings.SITES_WITH_LOGIN)

    def test_login_enabled(self):
        self.assertEqual(first=django_settings.LOGIN_ENABLED, second=(django_settings.SITE_ID in django_settings.SITES_WITH_LOGIN))

    # def test_raise(self): #### TODO
    #     raise Exception
    #

class TestsSettingsTestCase(SiteTestCase):
    def test_slugs_to_test_list(self):
        self.assertEqual(first=len(tests_settings.SLUGS_TO_TEST_LIST), second=8)
        username_set, slug_set, username_length_set, slug_length_set = set(), set(), set(), set()
        for slug_dict in tests_settings.SLUGS_TO_TEST_LIST:
            username = normalize_username(slug=slug_dict["slug"])
            slug = normalize_slug(slug=slug_dict["slug"])
            username_set.add(username)
            slug_set.add(slug)
            username_length_set.add(len(username))
            slug_length_set.add(len(slug))
            self.assertEqual(first=slug_dict["slug_length"], second=len(slug))
            self.assertIn(member=len(username), container={29, 30, 31, 32})
            self.assertIn(member=len(slug), container={57, 59, 61, 63})
            self.assertIn(member=len(slug), container={len(username) * 2, (len(username) * 2) - 1})
        self.assertEqual(first=len(username_set), second=8)
        self.assertEqual(first=len(slug_set), second=8)
        self.assertEqual(first=len(username_length_set), second=4)
        self.assertEqual(first=len(slug_length_set), second=4)
        self.assertSetEqual(set1=username_length_set, set2={29, 30, 31, 32})
        self.assertSetEqual(set1=slug_length_set, set2={57, 59, 61, 63})

    # def test_raise(self): #### TODO
    #     raise Exception
    #

