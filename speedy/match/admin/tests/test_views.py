"""
Test cases for the admin matches list views of Speedy Match, in all main languages and in any language.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.test import override_settings
        from django.utils.html import escape
        from django.utils.translation import get_language

        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.admin.tests.test_views import AdminViewBaseMixin


        class AdminMatchesListViewBaseMixin(TestCaseMixin):
            """
            Creates two extra users (user_4, user_5) each registered under a different language code than the current test's language, to verify language-scoped admin matches list filtering.

            Methods:
                set_up(self): Creates user_4 and user_5 under language codes different from the current test's language code.
            """
            def set_up(self):
                """
                Creates user_4 and user_5, each registered while a different language (not the current test's language_code) is active, asserting their active_languages reflect the language used during registration.
                """
                super().set_up()
                if (self.language_code == 'de'):
                    language_code = 'en'
                else:
                    language_code = 'de'
                with override_settings(LANGUAGE_CODE=language_code):
                    self.assertEqual(first=get_language(), second=language_code)
                    self.user_4 = ActiveUserFactory(first_name_en="___Michael")  # User's first name must be different than all other user names.
                if (self.language_code == 'de'):
                    self.assertListEqual(list1=self.user_4.speedy_match_profile.active_languages, list2=['en'])
                else:
                    self.assertListEqual(list1=self.user_4.speedy_match_profile.active_languages, list2=['de'])
                self.assertListEqual(list1=self.user_4.speedy_match_profile.active_languages, list2=[language_code])
                if (self.language_code == 'fr'):
                    language_code = 'en'
                else:
                    language_code = 'fr'
                with override_settings(LANGUAGE_CODE=language_code):
                    self.assertEqual(first=get_language(), second=language_code)
                    self.user_5 = ActiveUserFactory(first_name_en="___Jenny")  # User's first name must be different than all other user names.
                if (self.language_code == 'fr'):
                    self.assertListEqual(list1=self.user_5.speedy_match_profile.active_languages, list2=['en'])
                else:
                    self.assertListEqual(list1=self.user_5.speedy_match_profile.active_languages, list2=['fr'])
                self.assertListEqual(list1=self.user_5.speedy_match_profile.active_languages, list2=[language_code])
                language_code = None
                self.assertEqual(first=get_language(), second=self.language_code)


        class AdminMatchesListViewTestCaseMixin(AdminViewBaseMixin, AdminMatchesListViewBaseMixin, TestCaseMixin):
            """
            Tests the admin matches list view (scoped to the current language), asserting only same-language users are listed.

            Methods:
                get_page_url(self): Returns the admin matches list page URL.
                test_admin_has_access(self): Asserts the admin can access the page and only same-language users (user_1, user_2, user_3) appear in it, while other-language users (user_4, user_5) do not.
            """
            def get_page_url(self):
                """
                Returns the admin matches list page URL.

                :return: The page URL.
                :rtype: str
                """
                return '/admin/matches/'

            def test_admin_has_access(self):
                """
                Asserts the admin can access the page and only same-language users (user_1, user_2, user_3) appear by first name and name (but not full name or id), while other-language users (user_4, user_5) do not appear at all.

                :return: The HTTP response from the base class's access check.
                :rtype: django.http.HttpResponse
                """
                r = super().test_admin_has_access()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertIn(member=escape(text=user.first_name), container=r.content.decode())
                    self.assertIn(member=escape(text=user.name), container=r.content.decode())
                    self.assertNotIn(member=escape(text=user.full_name), container=r.content.decode())
                    self.assertNotIn(member=escape(text=user.id), container=r.content.decode())
                for user in [self.user_4, self.user_5]:
                    self.assertNotIn(member=escape(text=user.first_name), container=r.content.decode())
                    self.assertNotIn(member=escape(text=user.name), container=r.content.decode())
                    self.assertNotIn(member=escape(text=user.full_name), container=r.content.decode())
                    self.assertNotIn(member=escape(text=user.id), container=r.content.decode())
                self.assertEqual(first=r.content.decode().count(escape(text="['{}']".format(self.language_code))), second=0)


        @only_on_speedy_match
        class AdminMatchesListViewAllMainLanguagesEnglishTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            """
            Tests the language-scoped admin matches list view for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fr')
        class AdminMatchesListViewAllMainLanguagesFrenchTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            """
            Tests the language-scoped admin matches list view for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='de')
        class AdminMatchesListViewAllMainLanguagesGermanTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            """
            Tests the language-scoped admin matches list view for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='es')
        class AdminMatchesListViewAllMainLanguagesSpanishTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            """
            Tests the language-scoped admin matches list view for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='pt')
        class AdminMatchesListViewAllMainLanguagesPortugueseTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            """
            Tests the language-scoped admin matches list view for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='it')
        class AdminMatchesListViewAllMainLanguagesItalianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            """
            Tests the language-scoped admin matches list view for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='nl')
        class AdminMatchesListViewAllMainLanguagesDutchTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            """
            Tests the language-scoped admin matches list view for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='he')
        class AdminMatchesListViewAllMainLanguagesHebrewTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            """
            Tests the language-scoped admin matches list view for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class AdminMatchesAnyLanguageListViewTestCaseMixin(AdminViewBaseMixin, AdminMatchesListViewBaseMixin, TestCaseMixin):
            """
            Tests the admin matches list view for any language, asserting all users (regardless of language) are listed.

            Methods:
                get_page_url(self): Returns the admin any-language matches list page URL.
                test_admin_has_access(self): Asserts the admin can access the page and all users (user_1 through user_5), regardless of language, appear in it.
            """
            def get_page_url(self):
                """
                Returns the admin any-language matches list page URL.

                :return: The page URL.
                :rtype: str
                """
                return '/admin/matches/any/'

            def test_admin_has_access(self):
                """
                Asserts the admin can access the page and all users (user_1 through user_5), regardless of language, appear in it by first name and name (but not full name or id).

                :return: The HTTP response from the base class's access check.
                :rtype: django.http.HttpResponse
                """
                r = super().test_admin_has_access()
                for user in [self.user_1, self.user_2, self.user_3, self.user_4, self.user_5]:
                    self.assertIn(member=escape(text=user.first_name), container=r.content.decode())
                    self.assertIn(member=escape(text=user.name), container=r.content.decode())
                    self.assertNotIn(member=escape(text=user.full_name), container=r.content.decode())
                    self.assertNotIn(member=escape(text=user.id), container=r.content.decode())
                self.assertEqual(first=r.content.decode().count(escape(text="['{}']".format(self.language_code))), second=0)


        @only_on_speedy_match
        class AdminMatchesAnyLanguageListViewAllMainLanguagesEnglishTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):
            """
            Tests the any-language admin matches list view for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fr')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesFrenchTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):
            """
            Tests the any-language admin matches list view for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='de')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesGermanTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):
            """
            Tests the any-language admin matches list view for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='es')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesSpanishTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):
            """
            Tests the any-language admin matches list view for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='pt')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesPortugueseTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):
            """
            Tests the any-language admin matches list view for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='it')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesItalianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):
            """
            Tests the any-language admin matches list view for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='nl')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesDutchTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):
            """
            Tests the any-language admin matches list view for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='he')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesHebrewTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):
            """
            Tests the any-language admin matches list view for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


