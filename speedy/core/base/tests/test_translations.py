"""
Test cases for the translations of Speedy Core in all languages.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.test import override_settings
        from django.utils.translation import gettext_lazy as _

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.decorators import only_on_sites_with_login


        class TranslationsTestCaseMixin(TestCaseMixin):
            """
            Mixin providing a shared assertion that translating an empty string returns an empty string.
            """

            def test_translating_empty_string_returns_empty_string(self):
                """
                Tests that translating an empty string with gettext_lazy returns an empty string.
                """
                self.assertEqual(first=str(_("")), second="")


        @only_on_sites_with_login
        class TranslationsAllLanguagesEnglishTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class TranslationsAllLanguagesFrenchTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class TranslationsAllLanguagesGermanTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class TranslationsAllLanguagesSpanishTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class TranslationsAllLanguagesPortugueseTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class TranslationsAllLanguagesItalianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class TranslationsAllLanguagesDutchTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class TranslationsAllLanguagesJapaneseTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class TranslationsAllLanguagesRussianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class TranslationsAllLanguagesChineseTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class TranslationsAllLanguagesPolishTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class TranslationsAllLanguagesPersianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class TranslationsAllLanguagesHebrewTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class TranslationsAllLanguagesKoreanTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class TranslationsAllLanguagesArabicTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class TranslationsAllLanguagesIndonesianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class TranslationsAllLanguagesUkrainianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class TranslationsAllLanguagesTurkishTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class TranslationsAllLanguagesVietnameseTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class TranslationsAllLanguagesCzechTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class TranslationsAllLanguagesSwedishTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class TranslationsAllLanguagesFinnishTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class TranslationsAllLanguagesHungarianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class TranslationsAllLanguagesThaiTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class TranslationsAllLanguagesGreekTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class TranslationsAllLanguagesMalayTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class TranslationsAllLanguagesSerbianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class TranslationsAllLanguagesRomanianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class TranslationsAllLanguagesBengaliTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class TranslationsAllLanguagesCatalanTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class TranslationsAllLanguagesNorwegianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class TranslationsAllLanguagesBulgarianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class TranslationsAllLanguagesDanishTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class TranslationsAllLanguagesSlovakTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class TranslationsAllLanguagesHindiTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class TranslationsAllLanguagesEstonianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class TranslationsAllLanguagesCroatianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class TranslationsAllLanguagesAzerbaijaniTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class TranslationsAllLanguagesCantoneseTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class TranslationsAllLanguagesLithuanianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class TranslationsAllLanguagesSlovenianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class TranslationsAllLanguagesBasqueTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class TranslationsAllLanguagesArmenianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class TranslationsAllLanguagesUzbekTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class TranslationsAllLanguagesTamilTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class TranslationsAllLanguagesLatvianTestCase(TranslationsTestCaseMixin, SiteTestCase):
            """
            Tests that translating an empty string returns an empty string, for all languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


