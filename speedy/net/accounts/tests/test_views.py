from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.test import override_settings
        from django.utils.translation import gettext_lazy as _, pgettext_lazy

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_net
        from speedy.core.accounts.test.mixins import SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin
        from speedy.net.accounts.test.mixins import SpeedyNetAccountsLanguageMixin

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.accounts.tests.test_views import IndexViewTestCaseMixin, EditProfileNotificationsViewTestCaseMixin, ActivateSiteProfileViewTestCaseMixin1, ActivateSiteProfileViewTestCaseMixin2

        from speedy.core.accounts.models import User


        @only_on_speedy_net
        class IndexViewTestCase(IndexViewTestCaseMixin, SiteTestCase):
            def test_user_gets_redirected_to_his_profile(self):
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path='/')
                if (self.random_choice == 1):
                    self.assertEqual(first=self.user.is_active, second=True)
                    self.assertEqual(first=self.user.profile.is_active, second=True)
                    self.assertEqual(first=self.user.speedy_net_profile.is_active, second=True)
                    self.assertEqual(first=self.user.speedy_match_profile.is_active, second=False)
                    self.assertRedirects(response=r, expected_url='/{}/'.format(self.user.slug), status_code=302, target_status_code=200)
                elif (self.random_choice == 2):
                    self.assertEqual(first=self.user.is_active, second=False)
                    self.assertEqual(first=self.user.profile.is_active, second=False)
                    self.assertEqual(first=self.user.speedy_net_profile.is_active, second=False)
                    self.assertEqual(first=self.user.speedy_match_profile.is_active, second=False)
                    self.assertRedirects(response=r, expected_url='/welcome/', status_code=302, target_status_code=200)
                elif (self.random_choice == 3):
                    self.assertEqual(first=self.user.is_active, second=False)
                    self.assertEqual(first=self.user.profile.is_active, second=False)
                    self.assertEqual(first=self.user.speedy_net_profile.is_active, second=False)
                    self.assertEqual(first=self.user.speedy_match_profile.is_active, second=False)
                    self.assertRedirects(response=r, expected_url='/welcome/', status_code=302, target_status_code=200)
                else:
                    raise NotImplementedError()


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


        class DeleteAccountViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, SpeedyNetAccountsLanguageMixin):
            page_url = '/edit-profile/delete-account/'

            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=1,
                    unconfirmed_email_address_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )

            def assert_user_is_not_deleted(self, user, user_is_active):
                # Test that the user is not deleted.
                self.assertIs(expr1=user.is_deleted, expr2=False)
                self.assertIs(expr1=user.is_deleted_time is None, expr2=True)
                if (user_is_active):
                    self.assertEqual(first=user.is_active, second=True)
                    self.assertEqual(first=user.profile.is_active, second=True)
                    self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                else:
                    self.assertEqual(first=user.is_active, second=False)
                    self.assertEqual(first=user.profile.is_active, second=False)
                    self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertNotEqual(first=user.name, second=self._speedy_net_deleted_user_name)
                self.assertNotEqual(first=user.name, second=self._speedy_match_deleted_user_name)
                self.assertEqual(first=len(user.email_addresses.all()), second=1)
                self.assertIs(expr1=user.email is None, expr2=False)
                self.assertIs(expr1='@' in user.email, expr2=True)
                self.assertEqual(first=user.has_confirmed_email, second=True)
                self.assertNotEqual(first=user.username, second=user.id)
                self.assertNotEqual(first=user.slug, second=user.id)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=1,
                    unconfirmed_email_address_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )

            def assert_user_is_deleted(self, user):
                # Test that the user is deleted.
                self.assertIs(expr1=user.is_deleted, expr2=True)
                self.assertIs(expr1=user.is_deleted_time is None, expr2=False)
                self.assertEqual(first=user.is_active, second=False)
                self.assertEqual(first=user.profile.is_active, second=False)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertEqual(first=user.name, second=self._speedy_net_deleted_user_name)
                self.assertNotEqual(first=user.name, second=self._speedy_match_deleted_user_name)
                self.assertEqual(first=len(user.email_addresses.all()), second=0)
                self.assertIs(expr1=user.email is None, expr2=True)
                self.assertEqual(first=user.has_confirmed_email, second=False)
                self.assertNotEqual(first=user.username, second=user.id)
                self.assertNotEqual(first=user.slug, second=user.id)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=0,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )

            def assert_user_is_logged_out(self):
                # Test that the user is logged out.
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)
                r = self.client.get(path='/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='main/main_page.html')

            def assert_user_is_logged_in(self, user, user_is_active):
                # Test that the user is logged in.
                r = self.client.get(path=self.page_url)
                if (user_is_active):
                    self.assertEqual(first=r.status_code, second=403)
                else:
                    self.assertEqual(first=r.status_code, second=200)
                    self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/delete_account.html')
                r = self.client.get(path='/')
                if (user_is_active):
                    self.assertRedirects(response=r, expected_url='/{}/'.format(user.slug), status_code=302, target_status_code=200, fetch_redirect_response=False)
                else:
                    self.assertRedirects(response=r, expected_url='/welcome/', status_code=302, target_status_code=200, fetch_redirect_response=False)

            def test_translations(self):
                self.assertEqual(first=_("Yes. Delete my account."), second=self._yes_delete_my_account_text)
                self.assertEqual(first=pgettext_lazy(context=self.user.get_gender(), message='Delete Account'), second=self._delete_account_text_dict_by_gender[self.user.get_gender()])
                self.assertEqual(first=pgettext_lazy(context=self.user.get_gender(), message='Are you sure you want to delete your Speedy Net account? This is permanent and irreversible. Deleting your Speedy Net account will also delete your Speedy Match account. If you are sure, type "Yes. Delete my account." in this field, exactly and case sensitive.'), second=self._are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender[self.user.get_gender()])
                self.assertEqual(first=pgettext_lazy(context=self.user.get_gender(), message='Permanently delete your {site_name} account').format(site_name=self.site_name), second=self._permanently_delete_your_speedy_net_account_text_dict_by_gender[self.user.get_gender()])
                self.assertEqual(first=pgettext_lazy(context=self.user.get_gender(), message='Your Speedy Net and Speedy Match accounts have been deleted. Thank you for using {site_name}.').format(site_name=self.site_name), second=self._your_speedy_net_and_speedy_match_accounts_have_been_deleted_message_dict_by_gender[self.user.get_gender()])

            def test_visitor_has_no_access(self):
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_inactive_user_can_open_the_page(self):
                self.user.speedy_net_profile.deactivate()
                self.assertIs(expr1=self.user.is_deleted, expr2=False)
                self.assertIs(expr1=self.user.is_deleted_time is None, expr2=True)
                self.assertEqual(first=self.user.is_active, second=False)
                self.assertEqual(first=self.user.profile.is_active, second=False)
                self.assertEqual(first=self.user.speedy_net_profile.is_active, second=False)
                self.assertEqual(first=self.user.speedy_match_profile.is_active, second=False)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/delete_account.html')

            def test_active_user_cannot_open_the_page(self):
                self.assertIs(expr1=self.user.is_deleted, expr2=False)
                self.assertIs(expr1=self.user.is_deleted_time is None, expr2=True)
                self.assertEqual(first=self.user.is_active, second=True)
                self.assertEqual(first=self.user.profile.is_active, second=True)
                self.assertEqual(first=self.user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=self.user.speedy_match_profile.is_active, second=False)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=403)

            def test_staff_and_superuser_gets_redirected(self):
                self.client.logout()
                user_2 = ActiveUserFactory(is_superuser=True, is_staff=True)
                self.client.login(username=user_2.slug, password=tests_settings.USER_PASSWORD)
                self.assertIs(expr1=user_2.is_deleted, expr2=False)
                self.assertIs(expr1=user_2.is_deleted_time is None, expr2=True)
                self.assertEqual(first=user_2.is_active, second=True)
                self.assertEqual(first=user_2.profile.is_active, second=True)
                self.assertEqual(first=user_2.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user_2.speedy_match_profile.is_active, second=False)
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/admin/', status_code=302, target_status_code=200)
                user_2.speedy_net_profile.deactivate()
                self.assertIs(expr1=user_2.is_deleted, expr2=False)
                self.assertIs(expr1=user_2.is_deleted_time is None, expr2=True)
                self.assertEqual(first=user_2.is_active, second=True)
                self.assertEqual(first=user_2.profile.is_active, second=False)
                self.assertEqual(first=user_2.speedy_net_profile.is_active, second=False)
                self.assertEqual(first=user_2.speedy_match_profile.is_active, second=False)
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/admin/', status_code=302, target_status_code=200)
                user_2.is_active = False
                user_2.save_user_and_profile()
                self.assertIs(expr1=user_2.is_deleted, expr2=False)
                self.assertIs(expr1=user_2.is_deleted_time is None, expr2=True)
                self.assertEqual(first=user_2.is_active, second=False)
                self.assertEqual(first=user_2.profile.is_active, second=False)
                self.assertEqual(first=user_2.speedy_net_profile.is_active, second=False)
                self.assertEqual(first=user_2.speedy_match_profile.is_active, second=False)
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/admin/', status_code=302, target_status_code=302)
                r = self.client.get(path='/admin/')
                self.assertRedirects(response=r, expected_url='/admin/login/?next=/admin/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                user_2.is_superuser, user_2.is_staff = False, False
                user_2.save_user_and_profile()
                self.assertIs(expr1=user_2.is_deleted, expr2=False)
                self.assertIs(expr1=user_2.is_deleted_time is None, expr2=True)
                self.assertEqual(first=user_2.is_active, second=False)
                self.assertEqual(first=user_2.profile.is_active, second=False)
                self.assertEqual(first=user_2.speedy_net_profile.is_active, second=False)
                self.assertEqual(first=user_2.speedy_match_profile.is_active, second=False)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/delete_account.html')

            def test_inactive_user_can_delete_his_account(self):
                self.user.speedy_net_profile.deactivate()
                self.assert_user_is_not_deleted(user=self.user, user_is_active=False)
                data = {
                    'password': tests_settings.USER_PASSWORD,
                    'delete_my_account_text': self._yes_delete_my_account_text,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=200)
                self.user = User.objects.get(pk=self.user.pk)
                self.assert_user_is_deleted(user=self.user)
                self.assert_user_is_logged_out()

            def test_active_user_cannot_delete_his_account(self):
                self.assert_user_is_not_deleted(user=self.user, user_is_active=True)
                data = {
                    'password': tests_settings.USER_PASSWORD,
                    'delete_my_account_text': self._yes_delete_my_account_text,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=403)
                self.user = User.objects.get(pk=self.user.pk)
                self.assert_user_is_not_deleted(user=self.user, user_is_active=True)
                self.assert_user_is_logged_in(user=self.user, user_is_active=True)

            def test_inactive_user_cannot_delete_his_account_using_incorrect_password(self):
                self.user.speedy_net_profile.deactivate()
                self.assert_user_is_not_deleted(user=self.user, user_is_active=False)
                data = {
                    'password': 'wrong password!!',
                    'delete_my_account_text': self._yes_delete_my_account_text,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._invalid_password_errors_dict())
                self.user = User.objects.get(pk=self.user.pk)
                self.assert_user_is_not_deleted(user=self.user, user_is_active=False)
                self.assert_user_is_logged_in(user=self.user, user_is_active=False)

            def test_inactive_user_cannot_delete_his_account_using_incorrect_delete_my_account_text(self):
                self.user.speedy_net_profile.deactivate()
                self.assert_user_is_not_deleted(user=self.user, user_is_active=False)
                data = {
                    'password': tests_settings.USER_PASSWORD,
                    'delete_my_account_text': 'wrong text!!',
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._invalid_delete_my_account_text_errors_dict_by_gender(gender=self.user.get_gender()))
                self.user = User.objects.get(pk=self.user.pk)
                self.assert_user_is_not_deleted(user=self.user, user_is_active=False)
                self.assert_user_is_logged_in(user=self.user, user_is_active=False)

            def test_inactive_user_cannot_delete_his_account_without_password(self):
                self.user.speedy_net_profile.deactivate()
                self.assert_user_is_not_deleted(user=self.user, user_is_active=False)
                data = {
                    'delete_my_account_text': self._yes_delete_my_account_text,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_is_required_errors_dict())
                self.user = User.objects.get(pk=self.user.pk)
                self.assert_user_is_not_deleted(user=self.user, user_is_active=False)
                self.assert_user_is_logged_in(user=self.user, user_is_active=False)

            def test_inactive_user_cannot_delete_his_account_without_delete_my_account_text(self):
                self.user.speedy_net_profile.deactivate()
                self.assert_user_is_not_deleted(user=self.user, user_is_active=False)
                data = {
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._delete_my_account_text_is_required_errors_dict())
                self.user = User.objects.get(pk=self.user.pk)
                self.assert_user_is_not_deleted(user=self.user, user_is_active=False)
                self.assert_user_is_logged_in(user=self.user, user_is_active=False)

            def test_inactive_user_cannot_delete_his_account_without_password_and_delete_my_account_text(self):
                self.user.speedy_net_profile.deactivate()
                self.assert_user_is_not_deleted(user=self.user, user_is_active=False)
                data = {}
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._delete_account_form_all_the_required_fields_are_required_errors_dict())
                self.user = User.objects.get(pk=self.user.pk)
                self.assert_user_is_not_deleted(user=self.user, user_is_active=False)
                self.assert_user_is_logged_in(user=self.user, user_is_active=False)


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


