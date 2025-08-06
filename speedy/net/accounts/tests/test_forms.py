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
        @override_settings(LANGUAGE_CODE='sv')
        class DeleteAccountFormAllLanguagesSwedishTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='ko')
        class DeleteAccountFormAllLanguagesKoreanTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='fi')
        class DeleteAccountFormAllLanguagesFinnishTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='he')
        class DeleteAccountFormAllLanguagesHebrewTestCase(DeleteAccountFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


