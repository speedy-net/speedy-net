"""
Test cases for the views of the Speedy Core admin app: the main page, users list, users with details list and user detail views.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.test import override_settings
        from django.utils.html import escape

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.admin.test.mixins import SpeedyCoreAdminLanguageMixin

        from speedy.core.accounts.test.user_factories import ActiveUserFactory


        class AdminViewBaseMixin(SpeedyCoreAdminLanguageMixin, TestCaseMixin):
            """
            Base mixin for testing admin-only views: sets up three users (two regular, one admin/superuser) and asserts access is denied to visitors and regular users, but granted to the admin.
            """

            def get_page_url(self):
                """
                Not implemented in this mixin - must be overridden by subclasses to return the page URL under test.

                :raises NotImplementedError: Always, since this method must be overridden by subclasses.
                """
                raise NotImplementedError("get_page_url must be defined in classes inherited from AdminViewBaseMixin.")

            def assert_permission_denied(self, r):
                """
                Asserts the given response denies permission to the page (status code 403, containing the "Permission Denied" heading and the private-page alert).

                :param r: The HTTP response to check.
                :type r: django.http.HttpResponse
                """
                self.assertEqual(first=r.status_code, second=403)
                self.assertIn(member="<h1>{}</h1>".format(escape(text=self._permission_denied_h1)), container=r.content.decode())
                self.assertIn(member=self._speedy_is_sorry_but_this_page_is_private_alert, container=r.content.decode())

            def set_up(self):
                """
                Creates two regular active users and one admin (superuser/staff) active user, and sets the page URL under test.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.user_3 = ActiveUserFactory(is_superuser=True, is_staff=True)
                self.page_url = self.get_page_url()

            def test_visitor_has_no_access(self):
                """
                Asserts that a logged-out visitor is denied access to the page.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assert_permission_denied(r=r)

            def test_user_1_has_no_access(self):
                """
                Asserts that a regular (non-admin) user is denied access to the page.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assert_permission_denied(r=r)

            def test_user_2_has_no_access(self):
                """
                Asserts that another regular (non-admin) user is denied access to the page.
                """
                self.client.login(username=self.user_2.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assert_permission_denied(r=r)

            def test_admin_has_access(self):
                """
                Asserts that the admin (superuser/staff) user can access the page, without the permission-denied heading or alert, and returns the response.

                :return: The HTTP response of the page.
                :rtype: django.http.HttpResponse
                """
                self.client.login(username=self.user_3.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertNotIn(member="<h1>{}</h1>".format(escape(text=self._permission_denied_h1)), container=r.content.decode())
                self.assertNotIn(member=self._speedy_is_sorry_but_this_page_is_private_alert, container=r.content.decode())
                return r


        class AdminMainPageViewTestCaseMixin(AdminViewBaseMixin, TestCaseMixin):
            """
            Tests the admin main page view, asserting it links to both the Speedy Net and Speedy Match profile lists.
            """

            def get_page_url(self):
                """
                Returns the admin main page URL.

                :return: The page URL.
                :rtype: str
                """
                return '/admin/'

            def assert_permission_denied(self, r):
                """
                Asserts the given response redirects to the admin login page, without the Speedy Net or Speedy Match profile-list links.

                :param r: The HTTP response to check.
                :type r: django.http.HttpResponse
                """
                self.assertRedirects(response=r, expected_url='/admin/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
                self.assertNotIn(member=escape(text=self._speedy_net_profiles), container=r.content.decode())
                self.assertNotIn(member=escape(text=self._speedy_match_profiles), container=r.content.decode())

            def test_admin_has_access(self):
                """
                Asserts the admin can access the page and it contains both the Speedy Net and Speedy Match profile-list links.
                """
                r = super().test_admin_has_access()
                self.assertIn(member=escape(text=self._speedy_net_profiles), container=r.content.decode())
                self.assertIn(member=escape(text=self._speedy_match_profiles), container=r.content.decode())


        @only_on_sites_with_login
        class AdminMainPageViewAllMainLanguagesEnglishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminMainPageViewAllMainLanguagesFrenchTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminMainPageViewAllMainLanguagesGermanTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminMainPageViewAllMainLanguagesSpanishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminMainPageViewAllMainLanguagesPortugueseTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminMainPageViewAllMainLanguagesItalianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminMainPageViewAllMainLanguagesDutchTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class AdminMainPageViewAllMainLanguagesJapaneseTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class AdminMainPageViewAllMainLanguagesRussianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class AdminMainPageViewAllMainLanguagesChineseTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class AdminMainPageViewAllMainLanguagesPolishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class AdminMainPageViewAllMainLanguagesPersianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminMainPageViewAllMainLanguagesHebrewTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AdminMainPageViewAllMainLanguagesKoreanTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class AdminMainPageViewAllMainLanguagesArabicTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class AdminMainPageViewAllMainLanguagesIndonesianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class AdminMainPageViewAllMainLanguagesUkrainianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class AdminMainPageViewAllMainLanguagesTurkishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class AdminMainPageViewAllMainLanguagesVietnameseTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class AdminMainPageViewAllMainLanguagesCzechTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AdminMainPageViewAllMainLanguagesSwedishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AdminMainPageViewAllMainLanguagesFinnishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class AdminMainPageViewAllMainLanguagesHungarianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class AdminMainPageViewAllMainLanguagesThaiTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class AdminMainPageViewAllMainLanguagesGreekTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class AdminMainPageViewAllMainLanguagesMalayTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class AdminMainPageViewAllMainLanguagesSerbianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class AdminMainPageViewAllMainLanguagesRomanianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class AdminMainPageViewAllMainLanguagesBengaliTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class AdminMainPageViewAllMainLanguagesCatalanTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class AdminMainPageViewAllMainLanguagesNorwegianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class AdminMainPageViewAllMainLanguagesBulgarianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class AdminMainPageViewAllMainLanguagesDanishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class AdminMainPageViewAllMainLanguagesSlovakTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class AdminMainPageViewAllMainLanguagesHindiTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class AdminMainPageViewAllMainLanguagesEstonianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class AdminMainPageViewAllMainLanguagesCroatianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class AdminMainPageViewAllMainLanguagesAzerbaijaniTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class AdminMainPageViewAllMainLanguagesCantoneseTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class AdminMainPageViewAllMainLanguagesLithuanianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class AdminMainPageViewAllMainLanguagesSlovenianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class AdminMainPageViewAllMainLanguagesBasqueTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class AdminMainPageViewAllMainLanguagesArmenianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class AdminMainPageViewAllMainLanguagesUzbekTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class AdminMainPageViewAllMainLanguagesTamilTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class AdminMainPageViewAllMainLanguagesLatvianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin main page view for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class AdminUsersListViewTestCaseMixin(AdminViewBaseMixin, TestCaseMixin):
            """
            Tests the admin users list view, asserting the three users appear (or not) by first name, name, full name and id depending on the site, and that no "other"-language users are mislabeled.
            """

            def get_page_url(self):
                """
                Returns the admin users list page URL.

                :return: The page URL.
                :rtype: str
                """
                return '/admin/users/'

            def test_admin_has_access(self):
                """
                Asserts the admin can access the page and all three users appear by first name and name; on Speedy Net the full name also appears, while on Speedy Match it does not; ids never appear, and no "other"-language markers appear in the response.
                """
                r = super().test_admin_has_access()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertIn(member=escape(text=user.first_name), container=r.content.decode())
                    self.assertIn(member=escape(text=user.name), container=r.content.decode())
                    if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                        self.assertIn(member=escape(text=user.full_name), container=r.content.decode())
                    elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                        self.assertNotIn(member=escape(text=user.full_name), container=r.content.decode())
                    else:
                        raise NotImplementedError("Unsupported SITE_ID.")
                    self.assertNotIn(member=escape(text=user.id), container=r.content.decode())
                self.assertEqual(first=r.content.decode().count(escape(text="['{}']".format(self.language_code))), second=0)


        @only_on_sites_with_login
        class AdminUsersListViewAllMainLanguagesEnglishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminUsersListViewAllMainLanguagesFrenchTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminUsersListViewAllMainLanguagesGermanTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminUsersListViewAllMainLanguagesSpanishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminUsersListViewAllMainLanguagesPortugueseTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminUsersListViewAllMainLanguagesItalianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminUsersListViewAllMainLanguagesDutchTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class AdminUsersListViewAllMainLanguagesJapaneseTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class AdminUsersListViewAllMainLanguagesRussianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class AdminUsersListViewAllMainLanguagesChineseTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class AdminUsersListViewAllMainLanguagesPolishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class AdminUsersListViewAllMainLanguagesPersianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminUsersListViewAllMainLanguagesHebrewTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AdminUsersListViewAllMainLanguagesKoreanTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class AdminUsersListViewAllMainLanguagesArabicTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class AdminUsersListViewAllMainLanguagesIndonesianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class AdminUsersListViewAllMainLanguagesUkrainianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class AdminUsersListViewAllMainLanguagesTurkishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class AdminUsersListViewAllMainLanguagesVietnameseTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class AdminUsersListViewAllMainLanguagesCzechTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AdminUsersListViewAllMainLanguagesSwedishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AdminUsersListViewAllMainLanguagesFinnishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class AdminUsersListViewAllMainLanguagesHungarianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class AdminUsersListViewAllMainLanguagesThaiTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class AdminUsersListViewAllMainLanguagesGreekTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class AdminUsersListViewAllMainLanguagesMalayTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class AdminUsersListViewAllMainLanguagesSerbianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class AdminUsersListViewAllMainLanguagesRomanianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class AdminUsersListViewAllMainLanguagesBengaliTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class AdminUsersListViewAllMainLanguagesCatalanTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class AdminUsersListViewAllMainLanguagesNorwegianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class AdminUsersListViewAllMainLanguagesBulgarianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class AdminUsersListViewAllMainLanguagesDanishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class AdminUsersListViewAllMainLanguagesSlovakTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class AdminUsersListViewAllMainLanguagesHindiTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class AdminUsersListViewAllMainLanguagesEstonianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class AdminUsersListViewAllMainLanguagesCroatianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class AdminUsersListViewAllMainLanguagesAzerbaijaniTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class AdminUsersListViewAllMainLanguagesCantoneseTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class AdminUsersListViewAllMainLanguagesLithuanianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class AdminUsersListViewAllMainLanguagesSlovenianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class AdminUsersListViewAllMainLanguagesBasqueTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class AdminUsersListViewAllMainLanguagesArmenianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class AdminUsersListViewAllMainLanguagesUzbekTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class AdminUsersListViewAllMainLanguagesTamilTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class AdminUsersListViewAllMainLanguagesLatvianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users list view for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class AdminUsersWithDetailsListViewTestCaseMixin(AdminViewBaseMixin, TestCaseMixin):
            """
            Tests the admin users list view with details, asserting the three users appear by first name, name, full name (Speedy Net only) and id, with language markers present only on Speedy Match.
            """

            def get_page_url(self):
                """
                Returns the admin users with-details list page URL.

                :return: The page URL.
                :rtype: str
                """
                return '/admin/users/with-details/'

            def test_admin_has_access(self):
                """
                Asserts the admin can access the page and all three users appear by first name, name and id; on Speedy Net the full name also appears (and no language markers appear), while on Speedy Match the full name does not appear (and a language marker appears once per user, i.e. three times).
                """
                r = super().test_admin_has_access()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertIn(member=escape(text=user.first_name), container=r.content.decode())
                    self.assertIn(member=escape(text=user.name), container=r.content.decode())
                    if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                        self.assertIn(member=escape(text=user.full_name), container=r.content.decode())
                    elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                        self.assertNotIn(member=escape(text=user.full_name), container=r.content.decode())
                    else:
                        raise NotImplementedError("Unsupported SITE_ID.")
                    self.assertIn(member=escape(text=user.id), container=r.content.decode())
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=r.content.decode().count(escape(text="['{}']".format(self.language_code))), second=0)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=r.content.decode().count(escape(text="['{}']".format(self.language_code))), second=3)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")


        @only_on_sites_with_login
        class AdminUsersWithDetailsListViewAllMainLanguagesEnglishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminUsersWithDetailsListViewAllMainLanguagesFrenchTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminUsersWithDetailsListViewAllMainLanguagesGermanTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminUsersWithDetailsListViewAllMainLanguagesSpanishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminUsersWithDetailsListViewAllMainLanguagesPortugueseTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminUsersWithDetailsListViewAllMainLanguagesItalianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminUsersWithDetailsListViewAllMainLanguagesDutchTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class AdminUsersWithDetailsListViewAllMainLanguagesJapaneseTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class AdminUsersWithDetailsListViewAllMainLanguagesRussianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class AdminUsersWithDetailsListViewAllMainLanguagesChineseTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class AdminUsersWithDetailsListViewAllMainLanguagesPolishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class AdminUsersWithDetailsListViewAllMainLanguagesPersianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminUsersWithDetailsListViewAllMainLanguagesHebrewTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AdminUsersWithDetailsListViewAllMainLanguagesKoreanTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class AdminUsersWithDetailsListViewAllMainLanguagesArabicTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class AdminUsersWithDetailsListViewAllMainLanguagesIndonesianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class AdminUsersWithDetailsListViewAllMainLanguagesUkrainianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class AdminUsersWithDetailsListViewAllMainLanguagesTurkishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class AdminUsersWithDetailsListViewAllMainLanguagesVietnameseTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class AdminUsersWithDetailsListViewAllMainLanguagesCzechTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AdminUsersWithDetailsListViewAllMainLanguagesSwedishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AdminUsersWithDetailsListViewAllMainLanguagesFinnishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class AdminUsersWithDetailsListViewAllMainLanguagesHungarianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class AdminUsersWithDetailsListViewAllMainLanguagesThaiTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class AdminUsersWithDetailsListViewAllMainLanguagesGreekTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class AdminUsersWithDetailsListViewAllMainLanguagesMalayTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class AdminUsersWithDetailsListViewAllMainLanguagesSerbianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class AdminUsersWithDetailsListViewAllMainLanguagesRomanianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class AdminUsersWithDetailsListViewAllMainLanguagesBengaliTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class AdminUsersWithDetailsListViewAllMainLanguagesCatalanTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class AdminUsersWithDetailsListViewAllMainLanguagesNorwegianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class AdminUsersWithDetailsListViewAllMainLanguagesBulgarianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class AdminUsersWithDetailsListViewAllMainLanguagesDanishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class AdminUsersWithDetailsListViewAllMainLanguagesSlovakTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class AdminUsersWithDetailsListViewAllMainLanguagesHindiTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class AdminUsersWithDetailsListViewAllMainLanguagesEstonianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class AdminUsersWithDetailsListViewAllMainLanguagesCroatianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class AdminUsersWithDetailsListViewAllMainLanguagesAzerbaijaniTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class AdminUsersWithDetailsListViewAllMainLanguagesCantoneseTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class AdminUsersWithDetailsListViewAllMainLanguagesLithuanianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class AdminUsersWithDetailsListViewAllMainLanguagesSlovenianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class AdminUsersWithDetailsListViewAllMainLanguagesBasqueTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class AdminUsersWithDetailsListViewAllMainLanguagesArmenianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class AdminUsersWithDetailsListViewAllMainLanguagesUzbekTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class AdminUsersWithDetailsListViewAllMainLanguagesTamilTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class AdminUsersWithDetailsListViewAllMainLanguagesLatvianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin users with details list view for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class AdminUserDetailViewTestCaseMixin(AdminViewBaseMixin, TestCaseMixin):
            """
            Tests the admin user detail view, asserting user_1's details appear (full name only on Speedy Net), with exactly one language marker on Speedy Match.
            """

            def get_page_url(self):
                """
                Returns the admin user detail page URL for user_1.

                :return: The page URL.
                :rtype: str
                """
                return '/admin/user/{}/'.format(self.user_1.slug)

            def test_admin_has_access(self):
                """
                Asserts the admin can access the page and user_1's first name, name and id appear; on Speedy Net the full name also appears (and no language markers appear), while on Speedy Match the full name does not appear (and exactly one language marker appears).
                """
                r = super().test_admin_has_access()
                user = self.user_1
                self.assertIn(member=escape(text=user.first_name), container=r.content.decode())
                self.assertIn(member=escape(text=user.name), container=r.content.decode())
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertIn(member=escape(text=user.full_name), container=r.content.decode())
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertNotIn(member=escape(text=user.full_name), container=r.content.decode())
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                self.assertIn(member=escape(text=user.id), container=r.content.decode())
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=r.content.decode().count(escape(text="['{}']".format(self.language_code))), second=0)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=r.content.decode().count(escape(text="['{}']".format(self.language_code))), second=1)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")


        @only_on_sites_with_login
        class AdminUserDetailViewAllMainLanguagesEnglishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminUserDetailViewAllMainLanguagesFrenchTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminUserDetailViewAllMainLanguagesGermanTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminUserDetailViewAllMainLanguagesSpanishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminUserDetailViewAllMainLanguagesPortugueseTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminUserDetailViewAllMainLanguagesItalianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminUserDetailViewAllMainLanguagesDutchTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class AdminUserDetailViewAllMainLanguagesJapaneseTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class AdminUserDetailViewAllMainLanguagesRussianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class AdminUserDetailViewAllMainLanguagesChineseTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class AdminUserDetailViewAllMainLanguagesPolishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class AdminUserDetailViewAllMainLanguagesPersianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminUserDetailViewAllMainLanguagesHebrewTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AdminUserDetailViewAllMainLanguagesKoreanTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class AdminUserDetailViewAllMainLanguagesArabicTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class AdminUserDetailViewAllMainLanguagesIndonesianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class AdminUserDetailViewAllMainLanguagesUkrainianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class AdminUserDetailViewAllMainLanguagesTurkishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class AdminUserDetailViewAllMainLanguagesVietnameseTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class AdminUserDetailViewAllMainLanguagesCzechTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AdminUserDetailViewAllMainLanguagesSwedishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AdminUserDetailViewAllMainLanguagesFinnishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class AdminUserDetailViewAllMainLanguagesHungarianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class AdminUserDetailViewAllMainLanguagesThaiTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class AdminUserDetailViewAllMainLanguagesGreekTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class AdminUserDetailViewAllMainLanguagesMalayTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class AdminUserDetailViewAllMainLanguagesSerbianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class AdminUserDetailViewAllMainLanguagesRomanianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class AdminUserDetailViewAllMainLanguagesBengaliTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class AdminUserDetailViewAllMainLanguagesCatalanTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class AdminUserDetailViewAllMainLanguagesNorwegianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class AdminUserDetailViewAllMainLanguagesBulgarianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class AdminUserDetailViewAllMainLanguagesDanishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class AdminUserDetailViewAllMainLanguagesSlovakTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class AdminUserDetailViewAllMainLanguagesHindiTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class AdminUserDetailViewAllMainLanguagesEstonianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class AdminUserDetailViewAllMainLanguagesCroatianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class AdminUserDetailViewAllMainLanguagesAzerbaijaniTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class AdminUserDetailViewAllMainLanguagesCantoneseTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class AdminUserDetailViewAllMainLanguagesLithuanianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class AdminUserDetailViewAllMainLanguagesSlovenianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class AdminUserDetailViewAllMainLanguagesBasqueTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class AdminUserDetailViewAllMainLanguagesArmenianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class AdminUserDetailViewAllMainLanguagesUzbekTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class AdminUserDetailViewAllMainLanguagesTamilTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class AdminUserDetailViewAllMainLanguagesLatvianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the admin user detail view for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


