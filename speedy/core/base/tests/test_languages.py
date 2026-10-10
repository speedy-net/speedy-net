"""
Test cases for the language names of Speedy Core in English and in all the other languages.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.models import SiteTestCase

    if (django_settings.LOGIN_ENABLED):
        from django.test import override_settings
        from django.utils.translation import get_language_info

        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.decorators import only_on_sites_with_login


    class LanguageNamesInEnglishOnlyEnglishTestCase(SiteTestCase):
        """
        Tests that the English names of all languages enabled on a site match Django's LANGUAGES setting, in English.
        """

        def test_language_names_in_english(self):
            """
            Tests that the English names of the languages in django_settings.LANGUAGES match the expected list of language names for the current site.
            """
            language_names_in_english = [str(language_name) for language_code, language_name in django_settings.LANGUAGES]
            all_46_languages_in_english = ['English', 'French', 'German', 'Spanish', 'Portuguese', 'Italian', 'Dutch', 'Japanese', 'Russian', 'Chinese', 'Polish', 'Persian', 'Hebrew', 'Korean', 'Arabic', 'Indonesian', 'Ukrainian', 'Turkish', 'Vietnamese', 'Czech', 'Swedish', 'Finnish', 'Hungarian', 'Thai', 'Greek', 'Malay', 'Serbian', 'Romanian', 'Bengali', 'Catalan', 'Norwegian (Bokmål)', 'Bulgarian', 'Danish', 'Slovak', 'Hindi', 'Estonian', 'Croatian', 'Azerbaijani', 'Cantonese', 'Lithuanian', 'Slovenian', 'Basque', 'Armenian', 'Uzbek', 'Tamil', 'Latvian']
            self.assertListEqual(list1=language_names_in_english, list2={django_settings.SPEEDY_NET_SITE_ID: all_46_languages_in_english, django_settings.SPEEDY_MATCH_SITE_ID: all_46_languages_in_english, django_settings.SPEEDY_COMPOSER_SITE_ID: ['English', 'Hebrew'], django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: ['English', 'Hebrew']}[self.site.id])


    if (django_settings.LOGIN_ENABLED):
        class LanguageNameTestCaseMixin(TestCaseMixin):
            """
            Mixin providing a shared assertion that the active language's translated name equals its local name.
            """

            def test_language_name_translated_equals_name_local(self):
                """
                Tests that the translated name of the active language equals its local name, as returned by get_language_info().
                """
                language_name = dict(django_settings.LANGUAGES)[self.language_code]
                language_name_translated = str(language_name)
                language_name_local = get_language_info(lang_code=self.language_code)['name_local']
                self.assertEqual(first=language_name_translated, second=language_name_local)


        @only_on_sites_with_login
        class LanguageNameAllLanguagesEnglishTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class LanguageNameAllLanguagesFrenchTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class LanguageNameAllLanguagesGermanTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class LanguageNameAllLanguagesSpanishTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class LanguageNameAllLanguagesPortugueseTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class LanguageNameAllLanguagesItalianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class LanguageNameAllLanguagesDutchTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class LanguageNameAllLanguagesJapaneseTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Japanese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class LanguageNameAllLanguagesRussianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Russian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class LanguageNameAllLanguagesChineseTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Chinese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class LanguageNameAllLanguagesPolishTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Polish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class LanguageNameAllLanguagesPersianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Persian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class LanguageNameAllLanguagesHebrewTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class LanguageNameAllLanguagesKoreanTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Korean).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class LanguageNameAllLanguagesArabicTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Arabic).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class LanguageNameAllLanguagesIndonesianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Indonesian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class LanguageNameAllLanguagesUkrainianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Ukrainian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class LanguageNameAllLanguagesTurkishTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Turkish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class LanguageNameAllLanguagesVietnameseTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Vietnamese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class LanguageNameAllLanguagesCzechTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Czech).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class LanguageNameAllLanguagesSwedishTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Swedish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class LanguageNameAllLanguagesFinnishTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Finnish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class LanguageNameAllLanguagesHungarianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Hungarian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class LanguageNameAllLanguagesThaiTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Thai).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class LanguageNameAllLanguagesGreekTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Greek).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class LanguageNameAllLanguagesMalayTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Malay).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class LanguageNameAllLanguagesSerbianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Serbian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class LanguageNameAllLanguagesRomanianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Romanian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class LanguageNameAllLanguagesBengaliTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Bengali).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class LanguageNameAllLanguagesCatalanTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Catalan).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class LanguageNameAllLanguagesNorwegianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Norwegian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class LanguageNameAllLanguagesBulgarianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Bulgarian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class LanguageNameAllLanguagesDanishTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Danish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class LanguageNameAllLanguagesSlovakTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Slovak).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class LanguageNameAllLanguagesHindiTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Hindi).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class LanguageNameAllLanguagesEstonianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Estonian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class LanguageNameAllLanguagesCroatianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Croatian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class LanguageNameAllLanguagesAzerbaijaniTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Azerbaijani).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class LanguageNameAllLanguagesCantoneseTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Cantonese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class LanguageNameAllLanguagesLithuanianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Lithuanian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class LanguageNameAllLanguagesSlovenianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Slovenian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class LanguageNameAllLanguagesBasqueTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Basque).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class LanguageNameAllLanguagesArmenianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Armenian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class LanguageNameAllLanguagesUzbekTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Uzbek).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class LanguageNameAllLanguagesTamilTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Tamil).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class LanguageNameAllLanguagesLatvianTestCase(LanguageNameTestCaseMixin, SiteTestCase):
            """
            Tests that the local name of the active language matches Django's translated language name, for all languages (Latvian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


