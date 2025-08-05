from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test import tests_settings
    from speedy.core.base.test.models import SiteTestCase

    from speedy.core.base.utils import normalize_slug, normalize_username


    class SettingsOnlyEnglishTestCase(SiteTestCase):
        def test_sites_with_login(self):
            self.assertListEqual(list1=django_settings.SITES_WITH_LOGIN, list2=[django_settings.SPEEDY_NET_SITE_ID, django_settings.SPEEDY_MATCH_SITE_ID])

        def test_xd_auth_sites(self):
            self.assertListEqual(list1=django_settings.XD_AUTH_SITES, list2=django_settings.SITES_WITH_LOGIN)

        def test_templates_top_sites(self):
            self.assertListEqual(list1=django_settings.TEMPLATES_TOP_SITES, list2=django_settings.SITES_WITH_LOGIN)

        def test_login_enabled(self):
            self.assertEqual(first=django_settings.LOGIN_ENABLED, second=(django_settings.SITE_ID in django_settings.SITES_WITH_LOGIN))
            self.assertEqual(first=django_settings.LOGIN_ENABLED, second={django_settings.SPEEDY_NET_SITE_ID: True, django_settings.SPEEDY_MATCH_SITE_ID: True, django_settings.SPEEDY_COMPOSER_SITE_ID: False, django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: False}[self.site.id])

        def test_languages(self):
            self.assertListEqual(list1=[language_code for language_code, language_name in django_settings.LANGUAGES], list2={django_settings.SPEEDY_NET_SITE_ID: ['en', 'fr', 'de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', 'he'], django_settings.SPEEDY_MATCH_SITE_ID: ['en', 'fr', 'de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', 'he'], django_settings.SPEEDY_COMPOSER_SITE_ID: ['en', 'he'], django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: ['en', 'he']}[self.site.id])
            self.assertListEqual(list1=self.all_language_codes, list2=[language_code for language_code, language_name in django_settings.LANGUAGES])
            self.assertEqual(first=len([language_code for language_code, language_name in django_settings.LANGUAGES]), second={django_settings.SPEEDY_NET_SITE_ID: 11, django_settings.SPEEDY_MATCH_SITE_ID: 11, django_settings.SPEEDY_COMPOSER_SITE_ID: 2, django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: 2}[self.site.id])
            self.assertEqual(first=len(django_settings.LANGUAGES), second={django_settings.SPEEDY_NET_SITE_ID: 11, django_settings.SPEEDY_MATCH_SITE_ID: 11, django_settings.SPEEDY_COMPOSER_SITE_ID: 2, django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: 2}[self.site.id])
            self.assertEqual(first=len(self.all_language_codes), second={django_settings.SPEEDY_NET_SITE_ID: 11, django_settings.SPEEDY_MATCH_SITE_ID: 11, django_settings.SPEEDY_COMPOSER_SITE_ID: 2, django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: 2}[self.site.id])

        def test_languages_with_ads(self):
            self.assertSetEqual(set1=django_settings.LANGUAGES_WITH_ADS, set2={django_settings.SPEEDY_NET_SITE_ID: {'en', 'fr', 'de', 'es', 'pt'}, django_settings.SPEEDY_MATCH_SITE_ID: {'en', 'fr', 'de', 'es', 'pt'}, django_settings.SPEEDY_COMPOSER_SITE_ID: set(), django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: set()}[self.site.id])


    class TestsSettingsOnlyEnglishTestCase(SiteTestCase):
        def test_slugs_to_test_list(self):
            self.assertEqual(first=len(tests_settings.SLUGS_TO_TEST_LIST), second=8)
            username_set, slug_set, username_length_set, slug_length_set = set(), set(), set(), set()
            for slug_dict in tests_settings.SLUGS_TO_TEST_LIST:
                username = normalize_username(username=slug_dict["slug"])
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


