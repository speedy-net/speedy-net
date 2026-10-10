from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.test import override_settings
        from django.utils.translation import gettext_lazy as _, pgettext_lazy

        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.accounts.test.mixins import SpeedyCoreAccountsLanguageMixin
        from speedy.net.accounts.test.mixins import SpeedyNetAccountsLanguageMixin

        from speedy.core.accounts.models import User


        class PrivacyPolicyViewTestCaseMixin(SpeedyCoreAccountsLanguageMixin, SpeedyNetAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the translated text of the privacy policy page, for all genders, in the current test's language.

            Methods:
                test_translations(self): Asserts the "Delete Account" and "Edit Profile" translations, and that the "delete your account" paragraph contains them (quoted, except in the Hebrew "other" gender case), and that non-English text differs from the English text.
            """
            def test_translations(self):
                """
                Asserts, for each gender, that the "Delete Account" and "Edit Profile" translations match the expected text, that non-English translations differ from the English originals (and English translations equal them), and that the "delete your account" paragraph contains the "Edit Profile" text (quoted) and the "Delete Account" text (quoted, except in the Hebrew "other" gender case, where it is not quoted/contained).
                """
                for gender in User.ALL_GENDERS:
                    _if_you_want_you_can_delete_your_account_on_speedy_net_english_text = "If you want, you can delete your account on Speedy Net. Deleting your Speedy Net account will automatically delete your Speedy Match account as well. To delete your Speedy Net account, log in to Speedy Net, deactivate your account, and then click “Delete Account” (in the “Edit Profile” menu). Fill out the details in the form and confirm. Please note that a deleted account cannot be recovered. Account deletion is permanent and irreversible."
                    _delete_account_english_text = "Delete Account"
                    _edit_profile_english_text = "Edit Profile"
                    _if_you_want_you_can_delete_your_account_on_speedy_net_text = str(_(_if_you_want_you_can_delete_your_account_on_speedy_net_english_text))
                    _delete_account_text = str(pgettext_lazy(context=gender, message=_delete_account_english_text))
                    _edit_profile_text = str(_(_edit_profile_english_text))
                    self.assertEqual(first=_delete_account_text, second=self._delete_account_text_dict_by_gender[gender])
                    self.assertEqual(first=_edit_profile_text, second=self._edit_profile_text)
                    if (self.language_code == 'en'):
                        self.assertEqual(first=_if_you_want_you_can_delete_your_account_on_speedy_net_text, second=_if_you_want_you_can_delete_your_account_on_speedy_net_english_text)
                        self.assertEqual(first=_delete_account_text, second=_delete_account_english_text)
                        self.assertEqual(first=_edit_profile_text, second=_edit_profile_english_text)
                    else:
                        self.assertNotEqual(first=_if_you_want_you_can_delete_your_account_on_speedy_net_text, second=_if_you_want_you_can_delete_your_account_on_speedy_net_english_text)
                        self.assertNotEqual(first=_delete_account_text, second=_delete_account_english_text)
                        self.assertNotEqual(first=_edit_profile_text, second=_edit_profile_english_text)
                    if ((self.language_code == 'he') and (gender == User.GENDER_OTHER_STRING)):
                        self.assertIs(expr1=_delete_account_text in _if_you_want_you_can_delete_your_account_on_speedy_net_text, expr2=False)
                    else:
                        self.assertIs(expr1=_delete_account_text in _if_you_want_you_can_delete_your_account_on_speedy_net_text, expr2=True)
                    _delete_account_text_with_quotes_1_is_contained_in_string = '"{}"'.format(_delete_account_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    _delete_account_text_with_quotes_2_is_contained_in_string = '”{}”'.format(_delete_account_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    _delete_account_text_with_quotes_3_is_contained_in_string = '„{}”'.format(_delete_account_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    _delete_account_text_with_quotes_4_is_contained_in_string = '„{}“'.format(_delete_account_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    _delete_account_text_with_quotes_5_is_contained_in_string = '“{}”'.format(_delete_account_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    _delete_account_text_with_quotes_6_is_contained_in_string = '«{}»'.format(_delete_account_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    _delete_account_text_with_quotes_7_is_contained_in_string = '「{}」'.format(_delete_account_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    _delete_account_text_with_quotes_8_is_contained_in_string = '« {} »'.format(_delete_account_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    if ((self.language_code == 'he') and (gender == User.GENDER_OTHER_STRING)):
                        self.assertIs(expr1=_delete_account_text_with_quotes_1_is_contained_in_string or _delete_account_text_with_quotes_2_is_contained_in_string or _delete_account_text_with_quotes_3_is_contained_in_string or _delete_account_text_with_quotes_4_is_contained_in_string or _delete_account_text_with_quotes_5_is_contained_in_string or _delete_account_text_with_quotes_6_is_contained_in_string or _delete_account_text_with_quotes_7_is_contained_in_string or _delete_account_text_with_quotes_8_is_contained_in_string, expr2=False)
                    else:
                        self.assertIs(expr1=_delete_account_text_with_quotes_1_is_contained_in_string or _delete_account_text_with_quotes_2_is_contained_in_string or _delete_account_text_with_quotes_3_is_contained_in_string or _delete_account_text_with_quotes_4_is_contained_in_string or _delete_account_text_with_quotes_5_is_contained_in_string or _delete_account_text_with_quotes_6_is_contained_in_string or _delete_account_text_with_quotes_7_is_contained_in_string or _delete_account_text_with_quotes_8_is_contained_in_string, expr2=True)
                    self.assertIs(expr1=_edit_profile_text in _if_you_want_you_can_delete_your_account_on_speedy_net_text, expr2=True)
                    _edit_profile_text_with_quotes_1_is_contained_in_string = '"{}"'.format(_edit_profile_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    _edit_profile_text_with_quotes_2_is_contained_in_string = '”{}”'.format(_edit_profile_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    _edit_profile_text_with_quotes_3_is_contained_in_string = '„{}”'.format(_edit_profile_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    _edit_profile_text_with_quotes_4_is_contained_in_string = '„{}“'.format(_edit_profile_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    _edit_profile_text_with_quotes_5_is_contained_in_string = '“{}”'.format(_edit_profile_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    _edit_profile_text_with_quotes_6_is_contained_in_string = '«{}»'.format(_edit_profile_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    _edit_profile_text_with_quotes_7_is_contained_in_string = '「{}」'.format(_edit_profile_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    _edit_profile_text_with_quotes_8_is_contained_in_string = '« {} »'.format(_edit_profile_text) in _if_you_want_you_can_delete_your_account_on_speedy_net_text
                    self.assertIs(expr1=_edit_profile_text_with_quotes_1_is_contained_in_string or _edit_profile_text_with_quotes_2_is_contained_in_string or _edit_profile_text_with_quotes_3_is_contained_in_string or _edit_profile_text_with_quotes_4_is_contained_in_string or _edit_profile_text_with_quotes_5_is_contained_in_string or _edit_profile_text_with_quotes_6_is_contained_in_string or _edit_profile_text_with_quotes_7_is_contained_in_string or _edit_profile_text_with_quotes_8_is_contained_in_string, expr2=True)


        @only_on_sites_with_login
        class PrivacyPolicyViewAllLanguagesEnglishTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class PrivacyPolicyViewAllLanguagesFrenchTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class PrivacyPolicyViewAllLanguagesGermanTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class PrivacyPolicyViewAllLanguagesSpanishTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class PrivacyPolicyViewAllLanguagesPortugueseTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class PrivacyPolicyViewAllLanguagesItalianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class PrivacyPolicyViewAllLanguagesDutchTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class PrivacyPolicyViewAllLanguagesJapaneseTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Japanese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class PrivacyPolicyViewAllLanguagesRussianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Russian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class PrivacyPolicyViewAllLanguagesChineseTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Chinese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class PrivacyPolicyViewAllLanguagesPolishTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Polish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class PrivacyPolicyViewAllLanguagesPersianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Persian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class PrivacyPolicyViewAllLanguagesHebrewTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class PrivacyPolicyViewAllLanguagesKoreanTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Korean).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class PrivacyPolicyViewAllLanguagesArabicTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Arabic).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class PrivacyPolicyViewAllLanguagesIndonesianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Indonesian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class PrivacyPolicyViewAllLanguagesUkrainianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Ukrainian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class PrivacyPolicyViewAllLanguagesTurkishTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Turkish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class PrivacyPolicyViewAllLanguagesVietnameseTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Vietnamese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class PrivacyPolicyViewAllLanguagesCzechTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Czech).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class PrivacyPolicyViewAllLanguagesSwedishTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Swedish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class PrivacyPolicyViewAllLanguagesFinnishTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Finnish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class PrivacyPolicyViewAllLanguagesHungarianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Hungarian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class PrivacyPolicyViewAllLanguagesThaiTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Thai).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class PrivacyPolicyViewAllLanguagesGreekTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Greek).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class PrivacyPolicyViewAllLanguagesMalayTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Malay).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class PrivacyPolicyViewAllLanguagesSerbianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Serbian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class PrivacyPolicyViewAllLanguagesRomanianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Romanian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class PrivacyPolicyViewAllLanguagesBengaliTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Bengali).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class PrivacyPolicyViewAllLanguagesCatalanTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Catalan).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class PrivacyPolicyViewAllLanguagesNorwegianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Norwegian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class PrivacyPolicyViewAllLanguagesBulgarianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Bulgarian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class PrivacyPolicyViewAllLanguagesDanishTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Danish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class PrivacyPolicyViewAllLanguagesSlovakTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Slovak).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class PrivacyPolicyViewAllLanguagesHindiTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Hindi).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class PrivacyPolicyViewAllLanguagesEstonianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Estonian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class PrivacyPolicyViewAllLanguagesCroatianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Croatian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')

        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class PrivacyPolicyViewAllLanguagesAzerbaijaniTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Azerbaijani).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class PrivacyPolicyViewAllLanguagesCantoneseTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Cantonese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class PrivacyPolicyViewAllLanguagesLithuanianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Lithuanian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class PrivacyPolicyViewAllLanguagesSlovenianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Slovenian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class PrivacyPolicyViewAllLanguagesBasqueTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Basque).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class PrivacyPolicyViewAllLanguagesArmenianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Armenian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class PrivacyPolicyViewAllLanguagesUzbekTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Uzbek).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class PrivacyPolicyViewAllLanguagesTamilTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Tamil).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class PrivacyPolicyViewAllLanguagesLatvianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            """
            Tests the privacy policy page translations for all main languages (Latvian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


