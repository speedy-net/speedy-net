from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import random

        from django.test import override_settings

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_net
        from speedy.core.accounts.test.mixins import SpeedyCoreAccountsLanguageMixin
        from speedy.net.accounts.test.mixins import SpeedyNetAccountsLanguageMixin

        from speedy.core.accounts.tests.test_forms import ProfileNotificationsFormTestCaseMixin

        from speedy.core.accounts.models import User
        from speedy.core.accounts.forms import ProfileNotificationsForm
        from speedy.net.accounts.forms import DeleteAccountForm

        from speedy.core.accounts.test.user_factories import InactiveUserFactory, SpeedyNetInactiveUserFactory


        @only_on_speedy_net
        class ProfileNotificationsFormOnlyEnglishTestCase(ProfileNotificationsFormTestCaseMixin, SiteTestCase):
            def test_has_correct_fields(self):
                form = ProfileNotificationsForm(instance=self.user)
                self.assertListEqual(list1=list(form.fields.keys()), list2=[
                    'notify_on_message',
                ])


        class DeleteAccountFormTestCaseMixin(SpeedyCoreAccountsLanguageMixin, SpeedyNetAccountsLanguageMixin, TestCaseMixin):
            def set_up(self):
                super().set_up()
                self.random_choice = random.choice([1, 2])
                if (self.random_choice == 1):
                    self.user = InactiveUserFactory()
                elif (self.random_choice == 2):
                    self.user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")

            def test_correct_password_and_delete_my_account_text(self):
                data = {
                    'password': tests_settings.USER_PASSWORD,
                    'delete_my_account_text': self._yes_delete_my_account_text,
                }
                form = DeleteAccountForm(user=self.user, data=data)
                self.assertIs(expr1=form.is_valid(), expr2=True)
                self.assertDictEqual(d1=form.errors, d2={})

            def test_incorrect_password(self):
                data = {
                    'password': 'wrong password!!',
                    'delete_my_account_text': self._yes_delete_my_account_text,
                }
                form = DeleteAccountForm(user=self.user, data=data)
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._invalid_password_errors_dict())

            def test_incorrect_delete_my_account_text(self):
                data = {
                    'password': tests_settings.USER_PASSWORD,
                    'delete_my_account_text': 'wrong text!!',
                }
                form = DeleteAccountForm(user=self.user, data=data)
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._invalid_delete_my_account_text_errors_dict_by_gender(gender=self.user.get_gender()))

            def test_no_password(self):
                data = {
                    'delete_my_account_text': self._yes_delete_my_account_text,
                }
                form = DeleteAccountForm(user=self.user, data=data)
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._password_is_required_errors_dict())

            def test_no_delete_my_account_text(self):
                data = {
                    'password': tests_settings.USER_PASSWORD,
                }
                form = DeleteAccountForm(user=self.user, data=data)
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._delete_my_account_text_is_required_errors_dict())

            def test_no_password_and_delete_my_account_text(self):
                data = {}
                form = DeleteAccountForm(user=self.user, data=data)
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._delete_account_form_all_the_required_fields_are_required_errors_dict())

            def test_yes_delete_my_account_text_is_contained_in_are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender_for_all_genders_with_and_without_quotes(self):
                for gender in User.ALL_GENDERS:
                    self.assertIs(expr1=self._yes_delete_my_account_text in self._are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender[gender], expr2=True)
                    _yes_delete_my_account_text_with_quotes_1_is_contained_in_string = '"{}"'.format(self._yes_delete_my_account_text) in self._are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender[gender]
                    _yes_delete_my_account_text_with_quotes_2_is_contained_in_string = '”{}”'.format(self._yes_delete_my_account_text) in self._are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender[gender]
                    _yes_delete_my_account_text_with_quotes_3_is_contained_in_string = '„{}”'.format(self._yes_delete_my_account_text) in self._are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender[gender]
                    _yes_delete_my_account_text_with_quotes_4_is_contained_in_string = '„{}“'.format(self._yes_delete_my_account_text) in self._are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender[gender]
                    _yes_delete_my_account_text_with_quotes_5_is_contained_in_string = '“{}”'.format(self._yes_delete_my_account_text) in self._are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender[gender]
                    _yes_delete_my_account_text_with_quotes_6_is_contained_in_string = '«{}»'.format(self._yes_delete_my_account_text) in self._are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender[gender]
                    _yes_delete_my_account_text_with_quotes_7_is_contained_in_string = '「{}」'.format(self._yes_delete_my_account_text) in self._are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender[gender]
                    _yes_delete_my_account_text_with_quotes_8_is_contained_in_string = '« {} »'.format(self._yes_delete_my_account_text) in self._are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender[gender]
                    self.assertIs(expr1=_yes_delete_my_account_text_with_quotes_1_is_contained_in_string or _yes_delete_my_account_text_with_quotes_2_is_contained_in_string or _yes_delete_my_account_text_with_quotes_3_is_contained_in_string or _yes_delete_my_account_text_with_quotes_4_is_contained_in_string or _yes_delete_my_account_text_with_quotes_5_is_contained_in_string or _yes_delete_my_account_text_with_quotes_6_is_contained_in_string or _yes_delete_my_account_text_with_quotes_7_is_contained_in_string or _yes_delete_my_account_text_with_quotes_8_is_contained_in_string, expr2=True)


        @only_on_speedy_net
        class DeleteAccountFormAllLanguagesEnglishTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='fr')
        class DeleteAccountFormAllLanguagesFrenchTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='de')
        class DeleteAccountFormAllLanguagesGermanTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='es')
        class DeleteAccountFormAllLanguagesSpanishTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='pt')
        class DeleteAccountFormAllLanguagesPortugueseTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='it')
        class DeleteAccountFormAllLanguagesItalianTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='nl')
        class DeleteAccountFormAllLanguagesDutchTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='ja')
        class DeleteAccountFormAllLanguagesJapaneseTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='ru')
        class DeleteAccountFormAllLanguagesRussianTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='zh')
        class DeleteAccountFormAllLanguagesChineseTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='pl')
        class DeleteAccountFormAllLanguagesPolishTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='fa')
        class DeleteAccountFormAllLanguagesPersianTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='he')
        class DeleteAccountFormAllLanguagesHebrewTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='ko')
        class DeleteAccountFormAllLanguagesKoreanTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='ar')
        class DeleteAccountFormAllLanguagesArabicTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='id')
        class DeleteAccountFormAllLanguagesIndonesianTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='uk')
        class DeleteAccountFormAllLanguagesUkrainianTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='tr')
        class DeleteAccountFormAllLanguagesTurkishTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='vi')
        class DeleteAccountFormAllLanguagesVietnameseTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='cs')
        class DeleteAccountFormAllLanguagesCzechTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='sv')
        class DeleteAccountFormAllLanguagesSwedishTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='fi')
        class DeleteAccountFormAllLanguagesFinnishTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='hu')
        class DeleteAccountFormAllLanguagesHungarianTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='th')
        class DeleteAccountFormAllLanguagesThaiTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='el')
        class DeleteAccountFormAllLanguagesGreekTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='ms')
        class DeleteAccountFormAllLanguagesMalayTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='sr')
        class DeleteAccountFormAllLanguagesSerbianTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='ro')
        class DeleteAccountFormAllLanguagesRomanianTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='bn')
        class DeleteAccountFormAllLanguagesBengaliTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='ca')
        class DeleteAccountFormAllLanguagesCatalanTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='no')
        class DeleteAccountFormAllLanguagesNorwegianTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='bg')
        class DeleteAccountFormAllLanguagesBulgarianTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='da')
        class DeleteAccountFormAllLanguagesDanishTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='sk')
        class DeleteAccountFormAllLanguagesSlovakTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='hi')
        class DeleteAccountFormAllLanguagesHindiTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='et')
        class DeleteAccountFormAllLanguagesEstonianTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='hr')
        class DeleteAccountFormAllLanguagesCroatianTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


