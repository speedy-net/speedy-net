from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.test import override_settings
        from django.utils.translation import gettext_lazy as _, pgettext_lazy

        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.net.accounts.test.mixins import SpeedyNetAccountsLanguageMixin

        from speedy.core.accounts.models import User


        class PrivacyPolicyViewTestCaseMixin(SpeedyNetAccountsLanguageMixin, TestCaseMixin):
            def test_translations(self):
                for gender in User.ALL_GENDERS:
                    _if_you_want_you_can_delete_your_account_on_speedy_net_english_text = "If you want, you can delete your account on Speedy Net. Deleting your Speedy Net account will automatically delete your Speedy Match account as well. To delete your Speedy Net account, log in to Speedy Net, deactivate your account, and then click “Delete Account” (in the “Edit Profile” menu). Fill out the details in the form and confirm. Please note that a deleted account cannot be recovered. Account deletion is permanent and irreversible."
                    _delete_account_english_text = "Delete Account"
                    _edit_profile_english_text = "Edit Profile"
                    _if_you_want_you_can_delete_your_account_on_speedy_net_text = str(_(_if_you_want_you_can_delete_your_account_on_speedy_net_english_text))
                    _delete_account_text = str(pgettext_lazy(context=gender, message=_delete_account_english_text))
                    _edit_profile_text = str(_(_edit_profile_english_text))
                    self.assertEqual(first=_delete_account_text, second=self._delete_account_text_dict_by_gender[gender])
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
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class PrivacyPolicyViewAllLanguagesFrenchTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class PrivacyPolicyViewAllLanguagesGermanTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class PrivacyPolicyViewAllLanguagesSpanishTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class PrivacyPolicyViewAllLanguagesPortugueseTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class PrivacyPolicyViewAllLanguagesItalianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class PrivacyPolicyViewAllLanguagesDutchTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class PrivacyPolicyViewAllLanguagesJapaneseTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class PrivacyPolicyViewAllLanguagesRussianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class PrivacyPolicyViewAllLanguagesChineseTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class PrivacyPolicyViewAllLanguagesPolishTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class PrivacyPolicyViewAllLanguagesPersianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class PrivacyPolicyViewAllLanguagesHebrewTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class PrivacyPolicyViewAllLanguagesKoreanTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class PrivacyPolicyViewAllLanguagesArabicTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class PrivacyPolicyViewAllLanguagesIndonesianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class PrivacyPolicyViewAllLanguagesUkrainianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class PrivacyPolicyViewAllLanguagesTurkishTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class PrivacyPolicyViewAllLanguagesVietnameseTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class PrivacyPolicyViewAllLanguagesCzechTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class PrivacyPolicyViewAllLanguagesSwedishTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class PrivacyPolicyViewAllLanguagesFinnishTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class PrivacyPolicyViewAllLanguagesHungarianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class PrivacyPolicyViewAllLanguagesThaiTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class PrivacyPolicyViewAllLanguagesGreekTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class PrivacyPolicyViewAllLanguagesMalayTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class PrivacyPolicyViewAllLanguagesSerbianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class PrivacyPolicyViewAllLanguagesRomanianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class PrivacyPolicyViewAllLanguagesBengaliTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class PrivacyPolicyViewAllLanguagesCatalanTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class PrivacyPolicyViewAllLanguagesNorwegianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class PrivacyPolicyViewAllLanguagesBulgarianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class PrivacyPolicyViewAllLanguagesDanishTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class PrivacyPolicyViewAllLanguagesSlovakTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class PrivacyPolicyViewAllLanguagesHindiTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class PrivacyPolicyViewAllLanguagesEstonianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class PrivacyPolicyViewAllLanguagesCroatianTestCase(PrivacyPolicyViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


