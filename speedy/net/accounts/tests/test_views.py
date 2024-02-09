from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.test import override_settings
        from django.utils.translation import gettext_lazy as _, pgettext_lazy

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_net
        from speedy.core.accounts.test.mixins import SpeedyCoreAccountsModelsMixin
        from speedy.net.accounts.test.mixins import SpeedyNetAccountsLanguageMixin

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.accounts.tests.test_views import IndexViewTestCaseMixin, EditProfileNotificationsViewTestCaseMixin, ActivateSiteProfileViewTestCaseMixin1, ActivateSiteProfileViewTestCaseMixin2

        from speedy.core.accounts.models import User


        @only_on_speedy_net
        class IndexViewTestCase(IndexViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()

            def test_user_gets_redirected_to_his_profile(self):
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path='/')
                self.assertRedirects(response=r, expected_url='/{}/'.format(self.user.slug), status_code=302, target_status_code=200)


        @only_on_speedy_net
        class EditProfileNotificationsViewTestCase(EditProfileNotificationsViewTestCaseMixin, SiteTestCase):
            def test_user_can_save_his_settings(self):
                self.assertEqual(first=self.user.notify_on_message, second=User.NOTIFICATIONS_ON)
                data = {
                    'notify_on_message': User.NOTIFICATIONS_OFF,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=200)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.notify_on_message, second=User.NOTIFICATIONS_OFF)


        @only_on_speedy_net
        class ActivateSiteProfileViewTestCase1(ActivateSiteProfileViewTestCaseMixin1, SiteTestCase):
            redirect_url = '/welcome/'

            def test_inactive_user_can_request_activation(self):
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=302)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.profile.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)


        @only_on_speedy_net
        class ActivateSiteProfileViewTestCase2(ActivateSiteProfileViewTestCaseMixin2, SiteTestCase):
            redirect_url = '/welcome/'

            def test_inactive_user_can_request_activation(self):
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=302)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.profile.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=True)


        class DeleteAccountViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyNetAccountsLanguageMixin):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=1,
                    unconfirmed_email_address_count=0,
                )

            def test_translations(self):
                print("self.user.get_gender()", self.user.get_gender())################ TODO
                self.assertEqual(first=_("Yes. Delete my account."), second=self._yes_delete_my_account_text)
                self.assertEqual(first=pgettext_lazy(context=self.user.get_gender(), message='Delete Account'), second=self._delete_account_text_dict_by_gender[self.user.get_gender()])
                self.assertEqual(first=pgettext_lazy(context=self.user.get_gender(), message='Are you sure you want to delete your Speedy Net account? This is permanent and irreversible. Deleting your Speedy Net account will also delete your Speedy Match account. If you are sure, type "Yes. Delete my account." in this field, exactly and case sensitive.'), second=self._are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender[self.user.get_gender()])
                self.assertEqual(first=pgettext_lazy(context=self.user.get_gender(), message='Permanently delete your {site_name} account').format(site_name=self.site_name), second=self._permanently_delete_your_speedy_net_account_text_dict_by_gender[self.user.get_gender()])
                self.assertEqual(first=pgettext_lazy(context=self.user.get_gender(), message='Your Speedy Net and Speedy Match accounts have been deleted. Thank you for using {site_name}.').format(site_name=self.site_name), second=self._your_speedy_net_and_speedy_match_accounts_have_been_deleted_message_dict_by_gender[self.user.get_gender()])


        @only_on_speedy_net
        class DeleteAccountViewEnglishTestCase(DeleteAccountViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='fr')
        class DeleteAccountViewFrenchTestCase(DeleteAccountViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='de')
        class DeleteAccountViewGermanTestCase(DeleteAccountViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='es')
        class DeleteAccountViewSpanishTestCase(DeleteAccountViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='pt')
        class DeleteAccountViewPortugueseTestCase(DeleteAccountViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='it')
        class DeleteAccountViewItalianTestCase(DeleteAccountViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='nl')
        class DeleteAccountViewDutchTestCase(DeleteAccountViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='sv')
        class DeleteAccountViewSwedishTestCase(DeleteAccountViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='ko')
        class DeleteAccountViewKoreanTestCase(DeleteAccountViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='fi')
        class DeleteAccountViewFinnishTestCase(DeleteAccountViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_speedy_net
        @override_settings(LANGUAGE_CODE='he')
        class DeleteAccountViewHebrewTestCase(DeleteAccountViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


