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
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ja')
        class AdminMatchesListViewAllMainLanguagesJapaneseTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ru')
        class AdminMatchesListViewAllMainLanguagesRussianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='zh')
        class AdminMatchesListViewAllMainLanguagesChineseTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='pl')
        class AdminMatchesListViewAllMainLanguagesPolishTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fa')
        class AdminMatchesListViewAllMainLanguagesPersianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='he')
        class AdminMatchesListViewAllMainLanguagesHebrewTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            """
            Tests the language-scoped admin matches list view for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ko')
        class AdminMatchesListViewAllMainLanguagesKoreanTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ar')
        class AdminMatchesListViewAllMainLanguagesArabicTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='id')
        class AdminMatchesListViewAllMainLanguagesIndonesianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='uk')
        class AdminMatchesListViewAllMainLanguagesUkrainianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='tr')
        class AdminMatchesListViewAllMainLanguagesTurkishTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='vi')
        class AdminMatchesListViewAllMainLanguagesVietnameseTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='cs')
        class AdminMatchesListViewAllMainLanguagesCzechTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sv')
        class AdminMatchesListViewAllMainLanguagesSwedishTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fi')
        class AdminMatchesListViewAllMainLanguagesFinnishTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='hu')
        class AdminMatchesListViewAllMainLanguagesHungarianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='th')
        class AdminMatchesListViewAllMainLanguagesThaiTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='el')
        class AdminMatchesListViewAllMainLanguagesGreekTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ms')
        class AdminMatchesListViewAllMainLanguagesMalayTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sr')
        class AdminMatchesListViewAllMainLanguagesSerbianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ro')
        class AdminMatchesListViewAllMainLanguagesRomanianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='bn')
        class AdminMatchesListViewAllMainLanguagesBengaliTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ca')
        class AdminMatchesListViewAllMainLanguagesCatalanTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='no')
        class AdminMatchesListViewAllMainLanguagesNorwegianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='bg')
        class AdminMatchesListViewAllMainLanguagesBulgarianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='da')
        class AdminMatchesListViewAllMainLanguagesDanishTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sk')
        class AdminMatchesListViewAllMainLanguagesSlovakTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='hi')
        class AdminMatchesListViewAllMainLanguagesHindiTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='et')
        class AdminMatchesListViewAllMainLanguagesEstonianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='hr')
        class AdminMatchesListViewAllMainLanguagesCroatianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='az')
        class AdminMatchesListViewAllMainLanguagesAzerbaijaniTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='zh-yue')
        class AdminMatchesListViewAllMainLanguagesCantoneseTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='lt')
        class AdminMatchesListViewAllMainLanguagesLithuanianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sl')
        class AdminMatchesListViewAllMainLanguagesSlovenianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='eu')
        class AdminMatchesListViewAllMainLanguagesBasqueTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='hy')
        class AdminMatchesListViewAllMainLanguagesArmenianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='uz')
        class AdminMatchesListViewAllMainLanguagesUzbekTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ta')
        class AdminMatchesListViewAllMainLanguagesTamilTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='lv')
        class AdminMatchesListViewAllMainLanguagesLatvianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the language-scoped admin matches list view for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class AdminMatchesAnyLanguageListViewTestCaseMixin(AdminViewBaseMixin, AdminMatchesListViewBaseMixin, TestCaseMixin):
            """
            Tests the admin matches list view for any language, asserting all users (regardless of language) are listed.
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
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ja')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesJapaneseTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ru')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesRussianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='zh')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesChineseTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='pl')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesPolishTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fa')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesPersianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='he')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesHebrewTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):
            """
            Tests the any-language admin matches list view for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ko')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesKoreanTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ar')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesArabicTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='id')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesIndonesianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='uk')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesUkrainianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='tr')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesTurkishTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='vi')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesVietnameseTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='cs')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesCzechTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sv')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesSwedishTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fi')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesFinnishTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='hu')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesHungarianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='th')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesThaiTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='el')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesGreekTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ms')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesMalayTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sr')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesSerbianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ro')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesRomanianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='bn')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesBengaliTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ca')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesCatalanTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='no')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesNorwegianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='bg')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesBulgarianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='da')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesDanishTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sk')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesSlovakTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='hi')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesHindiTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='et')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesEstonianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='hr')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesCroatianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='az')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesAzerbaijaniTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='zh-yue')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesCantoneseTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='lt')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesLithuanianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sl')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesSlovenianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='eu')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesBasqueTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='hy')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesArmenianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='uz')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesUzbekTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ta')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesTamilTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='lv')
        class AdminMatchesAnyLanguageListViewAllMainLanguagesLatvianTestCase(AdminMatchesAnyLanguageListViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the any-language admin matches list view for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


