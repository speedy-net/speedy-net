from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import logging
        import random
        from unittest import mock
        from datetime import date, datetime, timedelta

        from django.test import override_settings
        from django.core import mail

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.base.test.utils import get_random_user_password
        from speedy.core.accounts.test.mixins import SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin

        from speedy.core.accounts.test.user_factories import ActiveUserFactory, InactiveUserFactory, SpeedyNetInactiveUserFactory
        from speedy.core.accounts.test.user_email_address_factories import UserEmailAddressFactory

        from speedy.core.base.utils import normalize_slug, normalize_username, to_attribute
        from speedy.core.accounts.models import Entity, User, UserEmailAddress


        class RedirectMeMixin(TestCaseMixin):
            def assert_me_url_redirects(self, expected_url):
                r = self.client.get(path='/me/')
                self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200)

            def assert_me_url_redirects_to_login_url(self):
                expected_url = '/login/?next=/me/'
                self.assert_me_url_redirects(expected_url=expected_url)

            def assert_me_url_redirects_to_user_profile_url(self, user):
                expected_url = '/{}/'.format(user.slug)
                self.assert_me_url_redirects(expected_url=expected_url)

            def assert_me_url_redirects_to_welcome_url(self):
                expected_url = '/welcome/'
                self.assert_me_url_redirects(expected_url=expected_url)

            def assert_me_url_redirects_to_registration_step_2_url(self):
                expected_url = '/registration-step-2/'
                self.assert_me_url_redirects(expected_url=expected_url)

            def assert_me_url_redirects_after_login_by_site_user_and_random_choice(self, user, random_choice):
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    if (random_choice == 1):
                        self.assertEqual(first=user.is_active, second=True)
                        self.assertEqual(first=user.profile.is_active, second=True)
                        self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                        self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                        self.assert_me_url_redirects_to_user_profile_url(user=user)
                    elif (random_choice == 2):
                        self.assertEqual(first=user.is_active, second=False)
                        self.assertEqual(first=user.profile.is_active, second=False)
                        self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
                        self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                        self.assert_me_url_redirects_to_welcome_url()
                    elif (random_choice == 3):
                        self.assertEqual(first=user.is_active, second=False)
                        self.assertEqual(first=user.profile.is_active, second=False)
                        self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
                        self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                        self.assert_me_url_redirects_to_welcome_url()
                    else:
                        raise NotImplementedError("Invalid random choice.")
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    if (random_choice == 1):
                        self.assertEqual(first=user.is_active, second=True)
                        self.assertEqual(first=user.profile.is_active, second=True)
                        self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                        self.assertEqual(first=user.speedy_match_profile.is_active, second=True)
                        self.assert_me_url_redirects_to_user_profile_url(user=user)
                    elif (random_choice == 2):
                        self.assertEqual(first=user.is_active, second=True)
                        self.assertEqual(first=user.profile.is_active, second=False)
                        self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                        self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                        self.assert_me_url_redirects_to_registration_step_2_url()
                    elif (random_choice == 3):
                        self.assertEqual(first=user.is_active, second=False)
                        self.assertEqual(first=user.profile.is_active, second=False)
                        self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
                        self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                        self.assert_me_url_redirects_to_welcome_url()
                    else:
                        raise NotImplementedError("Invalid random choice.")
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")


        class IndexViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, TestCaseMixin):
            def set_up(self):
                super().set_up()
                self.random_choice = random.choice([1, 2, 3])
                if (self.random_choice == 1):
                    self.user = ActiveUserFactory()
                elif (self.random_choice == 2):
                    self.user = InactiveUserFactory()
                elif (self.random_choice == 3):
                    self.user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count={"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count={"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=0,
                )

            def test_visitor_gets_registration_page(self):
                r = self.client.get(path='/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='main/main_page.html')

            def test_visitor_gets_redirected_to_canonical_url_1(self):
                r = self.client.get(path='/?a=1')
                self.assertRedirects(response=r, expected_url='/', status_code=301, target_status_code=200)

            def test_visitor_gets_redirected_to_canonical_url_2(self):
                r = self.client.get(path='/?b=2')
                self.assertRedirects(response=r, expected_url='/', status_code=301, target_status_code=200)


        @only_on_sites_with_login
        class MeViewOnlyEnglishTestCase(RedirectMeMixin, SpeedyCoreAccountsModelsMixin, SiteTestCase):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory(slug='markmark')
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=1,
                    unconfirmed_email_address_count=0,
                )

            def test_visitor_has_no_access(self):
                self.assert_me_url_redirects_to_login_url()

            def test_user_gets_redirected_to_his_profile(self):
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_to_user_profile_url(user=self.user)
                # Assert expected_url directly once to confirm.
                self.assert_me_url_redirects(expected_url='/markmark/')


        @only_on_sites_with_login
        class LoginOnlyEnglishTestCase(RedirectMeMixin, SpeedyCoreAccountsModelsMixin, SiteTestCase):
            def set_up(self):
                super().set_up()
                self.random_choice = random.choice([1, 2, 3])
                if (self.random_choice == 1):
                    self.user = ActiveUserFactory()
                elif (self.random_choice == 2):
                    self.user = InactiveUserFactory()
                elif (self.random_choice == 3):
                    self.user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
                self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=1,
                )

            def assert_me_url_redirects_after_login(self, user):
                if (user == self.user):
                    random_choice = self.random_choice
                else:
                    raise NotImplementedError("Invalid user.")
                self.assert_me_url_redirects_after_login_by_site_user_and_random_choice(user=user, random_choice=random_choice)

            def test_user_can_login_with_slug(self):
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_user_can_login_with_username(self):
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_user_can_login_with_confirmed_email_address(self):
                self.client.login(username=self.confirmed_email_address.email, password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_user_can_login_with_unconfirmed_email_address(self):
                self.client.login(username=self.unconfirmed_email_address.email, password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_user_cannot_login_with_wrong_slug(self):
                self.client.login(username='a{}'.format(self.user.slug), password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_to_login_url()

            def test_user_cannot_login_with_wrong_username(self):
                self.client.login(username='a{}'.format(self.user.username), password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_to_login_url()

            def test_user_cannot_login_with_wrong_email(self):
                self.client.login(username='a{}'.format(self.confirmed_email_address.email), password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_to_login_url()

            def test_user_cannot_login_with_incorrect_password(self):
                self.client.login(username=self.user.slug, password='{}-'.format(tests_settings.USER_PASSWORD))
                self.assert_me_url_redirects_to_login_url()


        class RegistrationViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            def set_up(self):
                super().set_up()
                self.password = get_random_user_password()
                self.data = {
                    'email': 'email@example.com',
                    'slug': 'user-1234',
                    'new_password1': self.password,
                    'gender': 1,
                    'date_of_birth': '1980-08-20',
                }
                self.username = normalize_username(username=self.data['slug'])
                self.slug = normalize_slug(slug=self.data['slug'])
                self.assertNotEqual(first=self.password, second=tests_settings.USER_PASSWORD)
                self.assertEqual(first=self.username, second='user1234')
                self.assertEqual(first=self.slug, second='user-1234')
                self.assertNotEqual(first=self.username, second=self.slug)
                self.assert_models_count(
                    entity_count=0,
                    user_count=0,
                    user_email_address_count=0,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=0,
                )

            def set_up_required_fields(self):
                self.required_fields = self.data.keys() - {to_attribute(name="last_name", language_code=self.language_code)}
                self.assert_registration_form_required_fields(required_fields=self.required_fields)

            def test_visitor_can_see_registration_page(self):
                r = self.client.get(path='/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='main/main_page.html')

            def test_visitor_can_register(self):
                r = self.client.post(path='/', data=self.data)
                self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=302)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=1,
                )
                self.assertEqual(first=Entity.objects.filter(username=self.username).count(), second=1)
                self.assertEqual(first=User.objects.filter(username=self.username).count(), second=1)
                entity = Entity.objects.get(username=self.username)
                user = User.objects.get(username=self.username)
                self.assertEqual(first=user, second=entity.user)
                self.assertEqual(first=entity.id, second=user.id)
                self.assertEqual(first=entity.username, second=user.username)
                self.assertEqual(first=entity.slug, second=user.slug)
                self.assertEqual(first=len(entity.id), second=15)
                self.assertIs(expr1=user.check_password(raw_password=self.password), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=False)
                self.assertEqual(first=user.first_name, second=self.first_name)
                self.assertEqual(first=user.last_name, second=self.last_name)
                self.assert_user_first_and_last_name_in_all_languages(user=user)
                self.assertEqual(first=user.username, second=self.username)
                self.assertEqual(first=user.username, second='user1234')
                self.assertEqual(first=user.slug, second=self.slug)
                self.assertEqual(first=user.slug, second='user-1234')
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                self.assertEqual(first=user.email_addresses.first().email, second='email@example.com')
                self.assertIs(expr1=user.email_addresses.first().is_confirmed, expr2=False)
                self.assertIs(expr1=user.email_addresses.first().is_primary, expr2=True)
                for (key, value) in self.data.items():
                    if (not (key in ['new_password1', 'date_of_birth'])):
                        self.assertEqual(first=getattr(user, key), second=value)
                self.assertEqual(first=user.date_of_birth, second=date(year=1980, month=8, day=20))

            def run_test_visitor_register_logs_n_records(self, number_of_records_logged):
                log_records = []
                console_handler = next(h for h in logging.root.handlers if h.name == 'console')
                with mock.patch.object(target=console_handler, attribute='emit') as mocked_emit:
                    r = self.client.post(path='/', data=self.data)
                    for call in mocked_emit.call_args_list:
                        log_record = call.args[-1]
                        if (log_record.msg.startswith('New user')):
                            log_records.append(log_record)
                self.assertEqual(first=len(log_records), second=number_of_records_logged)

            @override_settings(DEBUG=True)
            def test_visitor_register_logs_one_record(self):
                self.run_test_visitor_register_logs_n_records(number_of_records_logged=1)

            @override_settings(LOGGING=tests_settings.OVERRIDE_LOGGING_SETTINGS.LOGGING, DEBUG=True)
            def test_visitor_register_logs_two_records_with_override_settings(self):
                self.run_test_visitor_register_logs_n_records(number_of_records_logged=2)

            def run_test_required_fields(self, data):
                r = self.client.post(path='/', data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._registration_form_all_the_required_fields_are_required_errors_dict())
                self.assert_models_count(
                    entity_count=0,
                    user_count=0,
                    user_email_address_count=0,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=0,
                )

            def test_required_fields_1(self):
                data = {}
                self.run_test_required_fields(data=data)

            def test_required_fields_2(self):
                data = {field_name: '' for field_name in self.required_fields}
                self.run_test_required_fields(data=data)

            def test_non_unique_confirmed_email_address(self):
                existing_user_email = UserEmailAddressFactory(email=self.data['email'], is_confirmed=True)
                existing_user = existing_user_email.user
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=1,
                    unconfirmed_email_address_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                r = self.client.post(path='/', data=self.data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._this_email_is_already_in_use_errors_dict())
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=1,
                    unconfirmed_email_address_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )

            def test_unique_confirmed_email_address(self):
                existing_user_email = UserEmailAddressFactory(email='a{}'.format(self.data['email']), is_confirmed=True)
                existing_user = existing_user_email.user
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=1,
                    unconfirmed_email_address_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                r = self.client.post(path='/', data=self.data)
                self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=302)
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=2,
                    confirmed_email_address_count=1,
                    unconfirmed_email_address_count=1,
                )
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )

            def test_non_unique_unconfirmed_email_address(self):
                # Unconfirmed email address is deleted if another user adds it again.
                existing_user_email = UserEmailAddressFactory(email=self.data['email'], is_confirmed=False)
                existing_user = existing_user_email.user
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=1,
                )
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                r = self.client.post(path='/', data=self.data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._this_email_is_already_in_use_errors_dict())
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=1,
                )
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )

            def test_non_unique_unconfirmed_email_address_registered_6_minutes_ago(self):
                # Unconfirmed email address is deleted if another user adds it again.
                existing_user_email = UserEmailAddressFactory(email=self.data['email'], is_confirmed=False)
                existing_user_email.date_created -= timedelta(minutes=6)
                existing_user_email.save()
                existing_user = existing_user_email.user
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=1,
                )
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                r = self.client.post(path='/', data=self.data)
                self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=302)
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=1,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=1,
                )
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )

            def test_unique_unconfirmed_email_address(self):
                existing_user_email = UserEmailAddressFactory(email='a{}'.format(self.data['email']), is_confirmed=False)
                existing_user = existing_user_email.user
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=1,
                )
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                r = self.client.post(path='/', data=self.data)
                self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=302)
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=2,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=2,
                )
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )

            def test_password_too_short(self):
                data = self.data.copy()
                data['new_password1'] = 'abcdef'
                self.assertEqual(first=len(data['new_password1']), second=6)
                r = self.client.post(path='/', data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_too_short_errors_dict(field_names=self._first_password_field_names))
                self.assert_models_count(
                    entity_count=0,
                    user_count=0,
                    user_email_address_count=0,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=0,
                )

            def test_password_too_long(self):
                data = self.data.copy()
                data['new_password1'] = 'abcdef' + ('8' * 115)
                self.assertEqual(first=len(data['new_password1']), second=121)
                r = self.client.post(path='/', data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_too_long_errors_dict(field_names=self._first_password_field_names))
                self.assert_models_count(
                    entity_count=0,
                    user_count=0,
                    user_email_address_count=0,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=0,
                )

            def test_password_not_enough_unique_characters(self):
                data = self.data.copy()
                data['new_password1'] = '1234' * 2
                self.assertEqual(first=len(data['new_password1']), second=8)
                r = self.client.post(path='/', data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._your_password_must_contain_at_least_6_unique_characters_errors_dict(field_names=self._first_password_field_names))
                self.assert_models_count(
                    entity_count=0,
                    user_count=0,
                    user_email_address_count=0,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=0,
                )

            def test_password_too_short_and_not_enough_unique_characters(self):
                data = self.data.copy()
                data['new_password1'] = '8' * 3
                self.assertEqual(first=len(data['new_password1']), second=3)
                r = self.client.post(path='/', data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_too_short_and_your_password_must_contain_at_least_6_unique_characters_errors_dict(field_names=self._first_password_field_names))
                self.assert_models_count(
                    entity_count=0,
                    user_count=0,
                    user_email_address_count=0,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=0,
                )

            def test_password_too_long_and_not_enough_unique_characters(self):
                data = self.data.copy()
                data['new_password1'] = '8' * 121
                self.assertEqual(first=len(data['new_password1']), second=121)
                r = self.client.post(path='/', data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_too_long_and_your_password_must_contain_at_least_6_unique_characters_errors_dict(field_names=self._first_password_field_names))
                self.assert_models_count(
                    entity_count=0,
                    user_count=0,
                    user_email_address_count=0,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=0,
                )

            def test_user_is_logged_in_after_registration(self):
                r = self.client.post(path='/', data=self.data)
                self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=302)
                r = self.client.get(path='/')
                if (django_settings.ACTIVATE_PROFILE_AFTER_REGISTRATION):
                    self.assertRedirects(response=r, expected_url='/{}/'.format(self.data['slug']), status_code=302, target_status_code=200, fetch_redirect_response=False)
                    r = self.client.get(path='/{}/'.format(self.data['slug']))
                else:
                    self.assertRedirects(response=r, expected_url='/registration-step-2/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                    r = self.client.get(path='/registration-step-2/')
                self.assertIs(expr1=r.context['user'].is_authenticated, expr2=True)
                self.assertEqual(first=r.context['user'].username, second='user1234')
                self.assertEqual(first=r.context['user'].slug, second='user-1234')
                self.assertIs(expr1=r.context['user'].is_active, expr2=True)
                self.assertIs(expr1=r.context['user'].speedy_net_profile.is_active, expr2=True)
                self.assertIs(expr1=r.context['user'].speedy_match_profile.is_active, expr2=False)
                if (django_settings.ACTIVATE_PROFILE_AFTER_REGISTRATION):
                    self.assertIs(expr1=r.context['user'].profile.is_active, expr2=True)
                    self.assertEqual(first=r.context['user'].profile, second=r.context['user'].speedy_net_profile)
                    self.assertNotEqual(first=r.context['user'].profile, second=r.context['user'].speedy_match_profile)
                else:
                    self.assertIs(expr1=r.context['user'].profile.is_active, expr2=False)
                    self.assertEqual(first=r.context['user'].profile, second=r.context['user'].speedy_match_profile)
                    self.assertNotEqual(first=r.context['user'].profile, second=r.context['user'].speedy_net_profile)
                self.assertEqual(first=r.context['user'].speedy_match_profile.activation_step, second=2)
                self.assertEqual(first=r.context['user'].speedy_match_profile.activation_step_en, second=2)
                self.assertEqual(first=r.context['user'].speedy_match_profile.activation_step_he, second=2)

            def test_user_gets_email_after_registration(self):
                self.assertEqual(first=len(mail.outbox), second=0)
                r = self.client.post(path='/', data=self.data)
                self.assertEqual(first=len(mail.outbox), second=1)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=1,
                )
                self.assertEqual(first=Entity.objects.filter(username=self.username).count(), second=1)
                self.assertEqual(first=User.objects.filter(username=self.username).count(), second=1)
                user = User.objects.get(username=self.username)
                email = user.email_addresses.first()
                email_address = UserEmailAddress.objects.get(email='email@example.com')
                self.assertIs(expr1=email.is_confirmed, expr2=False)
                self.assertEqual(first=email.confirmation_sent, second=1)
                self.assertEqual(first=mail.outbox[0].subject, second={
                    django_settings.SPEEDY_NET_SITE_ID: self._confirm_your_email_address_on_speedy_net_subject_dict_by_gender[user.get_gender()],
                    django_settings.SPEEDY_MATCH_SITE_ID: self._confirm_your_email_address_on_speedy_match_subject_dict_by_gender[user.get_gender()],
                }[self.site.id])
                self.assertIn(member=email_address.confirmation_token, container=mail.outbox[0].body)
                self.assertIn(member=self.full_http_host, container=mail.outbox[0].body)
                for other_full_http_host in self.all_other_full_http_hosts:
                    self.assertNotIn(member=other_full_http_host, container=mail.outbox[0].body)

            def test_cannot_register_taken_username(self):
                data = self.data.copy()
                existing_user = ActiveUserFactory(username='username', slug='user-name')
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=1,
                    unconfirmed_email_address_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                data['slug'] = 'us-er-na-me'
                r = self.client.post(path='/', data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._this_username_is_already_taken_errors_dict(slug_fail=True))
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=1,
                    unconfirmed_email_address_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )

            def test_email_gets_converted_to_lowercase(self):
                data = self.data.copy()
                data['email'] = 'EMAIL22@EXAMPLE.COM'
                r = self.client.post(path='/', data=data)
                self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=302)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=1,
                )
                self.assertEqual(first=Entity.objects.filter(username=self.username).count(), second=1)
                self.assertEqual(first=User.objects.filter(username=self.username).count(), second=1)
                user = User.objects.get(username=self.username)
                self.assertEqual(first=user.email_addresses.first().email, second='email22@example.com')

            def test_cannot_register_invalid_email(self):
                data = self.data.copy()
                data['email'] = 'email'
                r = self.client.post(path='/', data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._enter_a_valid_email_address_errors_dict())
                self.assert_models_count(
                    entity_count=0,
                    user_count=0,
                    user_email_address_count=0,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=0,
                )

            def test_invalid_date_of_birth_list_fail(self):
                for date_of_birth in tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST:
                    data = self.data.copy()
                    data['date_of_birth'] = date_of_birth
                    r = self.client.post(path='/', data=data)
                    self.assertEqual(first=r.status_code, second=200, msg="{} is a valid date of birth.".format(date_of_birth))
                    self.assertDictEqual(d1=r.context['form'].errors, d2=self._date_of_birth_errors_dict_by_date_of_birth(date_of_birth=date_of_birth), msg='"{}" - Unexpected error messages.'.format(date_of_birth))
                    self.assert_models_count(
                        entity_count=0,
                        user_count=0,
                        user_email_address_count=0,
                        confirmed_email_address_count=0,
                        unconfirmed_email_address_count=0,
                    )


        @only_on_sites_with_login
        class RegistrationViewWithLastNameAllLanguagesEnglishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in English alphabet.
                super().set_up()
                self.data.update({
                    'first_name_en': "Doron",
                    'last_name_en': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class RegistrationViewWithLastNameAllLanguagesFrenchTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in French alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fr': "Alizée",
                    'last_name_fr': "Jacotey",
                })
                self.first_name = "Alizée"
                self.last_name = "Jacotey"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class RegistrationViewWithLastNameAllLanguagesGermanTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in German alphabet.
                super().set_up()
                self.data.update({
                    'first_name_de': "Doron",
                    'last_name_de': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class RegistrationViewWithLastNameAllLanguagesSpanishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Spanish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_es': "Lionel",
                    'last_name_es': "Messi",
                })
                self.first_name = "Lionel"
                self.last_name = "Messi"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class RegistrationViewWithLastNameAllLanguagesPortugueseTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Portuguese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_pt': "Cristiano",
                    'last_name_pt': "Ronaldo",
                })
                self.first_name = "Cristiano"
                self.last_name = "Ronaldo"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class RegistrationViewWithLastNameAllLanguagesItalianTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Italian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_it': "Andrea",
                    'last_name_it': "Bocelli",
                })
                self.first_name = "Andrea"
                self.last_name = "Bocelli"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class RegistrationViewWithLastNameAllLanguagesDutchTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Dutch alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class RegistrationViewWithLastNameAllLanguagesSwedishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Swedish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_sv': "Doron",
                    'last_name_sv': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class RegistrationViewWithLastNameAllLanguagesKoreanTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Korean alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ko': "Doron",
                    'last_name_ko': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class RegistrationViewWithLastNameAllLanguagesFinnishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Finnish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fi': "Doron",
                    'last_name_fi': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class RegistrationViewWithLastNameAllLanguagesHebrewTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Hebrew alphabet.
                super().set_up()
                self.data.update({
                    'first_name_he': "דורון",
                    'last_name_he': "מטלון",
                })
                self.first_name = "דורון"
                self.last_name = "מטלון"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        class RegistrationViewWithoutLastNameAllLanguagesEnglishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in English alphabet.
                super().set_up()
                self.data.update({
                    'first_name_en': "Doron",
                    'last_name_en': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class RegistrationViewWithoutLastNameAllLanguagesFrenchTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in French alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fr': "Alizée",
                    'last_name_fr': "",
                })
                self.first_name = "Alizée"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class RegistrationViewWithoutLastNameAllLanguagesGermanTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in German alphabet.
                super().set_up()
                self.data.update({
                    'first_name_de': "Doron",
                    'last_name_de': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class RegistrationViewWithoutLastNameAllLanguagesSpanishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Spanish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_es': "Lionel",
                    'last_name_es': "",
                })
                self.first_name = "Lionel"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class RegistrationViewWithoutLastNameAllLanguagesPortugueseTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Portuguese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_pt': "Cristiano",
                    'last_name_pt': "",
                })
                self.first_name = "Cristiano"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class RegistrationViewWithoutLastNameAllLanguagesItalianTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Italian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_it': "Andrea",
                    'last_name_it': "",
                })
                self.first_name = "Andrea"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class RegistrationViewWithoutLastNameAllLanguagesDutchTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Dutch alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class RegistrationViewWithoutLastNameAllLanguagesSwedishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Swedish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_sv': "Doron",
                    'last_name_sv': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class RegistrationViewWithoutLastNameAllLanguagesKoreanTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Korean alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ko': "Doron",
                    'last_name_ko': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class RegistrationViewWithoutLastNameAllLanguagesFinnishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Finnish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fi': "Doron",
                    'last_name_fi': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class RegistrationViewWithoutLastNameAllLanguagesHebrewTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Hebrew alphabet.
                super().set_up()
                self.data.update({
                    'first_name_he': "דורון",
                    'last_name_he': "",
                })
                self.first_name = "דורון"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class LoginViewTestCaseMixin(RedirectMeMixin, SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            login_url = '/login/'
            _other_user_password = 'abcdef12'

            def set_up(self):
                super().set_up()
                user_factory_dict = dict(slug='slug.with.dots')
                self.random_choice_1 = random.choice([1, 2, 3])
                if (self.random_choice_1 == 1):
                    self.user = ActiveUserFactory(**user_factory_dict)
                elif (self.random_choice_1 == 2):
                    self.user = InactiveUserFactory(**user_factory_dict)
                elif (self.random_choice_1 == 3):
                    self.user = SpeedyNetInactiveUserFactory(**user_factory_dict)
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.user_email = UserEmailAddressFactory(user=self.user)
                self.random_choice_2 = random.choice([1, 2, 3])
                if (self.random_choice_2 == 1):
                    self.other_user = ActiveUserFactory()
                elif (self.random_choice_2 == 2):
                    self.other_user = InactiveUserFactory()
                elif (self.random_choice_2 == 3):
                    self.other_user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.other_user.set_password(raw_password=self._other_user_password)
                self.other_user.save_user_and_profile()
                self.other_user_email = UserEmailAddressFactory(user=self.other_user)
                self.inactive_user_1 = InactiveUserFactory()
                self.inactive_user_2 = SpeedyNetInactiveUserFactory()
                self.assertNotEqual(first=self.user_email.email, second=self.other_user_email.email)
                self.assertNotEqual(first=tests_settings.USER_PASSWORD, second=self._other_user_password)
                self.assert_models_count(
                    entity_count=4,
                    user_count=4,
                    user_email_address_count=3 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice_1)] + {"1": 1, "2": 0, "3": 1}[str(self.random_choice_2)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice_1)] + {"1": 1, "2": 0, "3": 1}[str(self.random_choice_2)],
                    unconfirmed_email_address_count=2,
                )

            def assert_me_url_redirects_after_login(self, user):
                if (user == self.user):
                    random_choice = self.random_choice_1
                elif (user == self.other_user):
                    random_choice = self.random_choice_2
                else:
                    raise NotImplementedError("Invalid user.")
                self.assert_me_url_redirects_after_login_by_site_user_and_random_choice(user=user, random_choice=random_choice)
                if (user == self.user):
                    if (random_choice == 1):
                        # Assert expected_url directly once to confirm.
                        self.assert_me_url_redirects(expected_url='/slug-with-dots/')

            def test_visitor_can_see_login_page(self):
                r = self.client.get(path=self.login_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/login.html')

            def test_visitor_can_login_using_slug(self):
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': self.user.slug,
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_username(self):
                self.assertEqual(first=self.user.username, second='slugwithdots')
                data = {
                    'username': self.user.username,
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_original_slug(self):
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': 'slug.with.dots',
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_slug_modified(self):
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': 'slug____with.....dots---',
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_slug_uppercase(self):
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': 'SLUG-WITH-DOTS',
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_email(self):
                data = {
                    'username': self.user_email.email,
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_email_uppercase(self):
                data = {
                    'username': self.user_email.email.upper(),
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_other_user_email_and_password(self):
                data = {
                    'username': self.other_user_email.email,
                    'password': self._other_user_password,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.other_user)

            def test_visitor_can_still_login_if_they_are_not_active_user_1(self):
                data = {
                    'username': self.inactive_user_1.slug,
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                if (django_settings.ACTIVATE_PROFILE_AFTER_REGISTRATION):
                    # Inactive users are redirected to welcome url ('/welcome/') instead of their user profile url.
                    self.assert_me_url_redirects_to_welcome_url()
                else:
                    # Inactive users are redirected to registration step 2 url ('/registration-step-2/') instead of their user profile url.
                    self.assert_me_url_redirects_to_registration_step_2_url()

            def test_visitor_can_still_login_if_they_are_not_active_user_2(self):
                data = {
                    'username': self.inactive_user_2.slug,
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                # Speedy Net inactive users are redirected to welcome url ('/welcome/') instead of their user profile url.
                self.assert_me_url_redirects_to_welcome_url()

            def test_visitor_can_login_using_email_if_there_are_two_users_returned(self):
                # Create another user with the slug as the email address of self.other_user.
                UserEmailAddressFactory(user=self.other_user, email="mike@example.com")
                user_factory_dict = dict(slug="mike@example.com")
                if (self.random_choice_2 == 1):
                    self.other_user_2 = ActiveUserFactory(**user_factory_dict)
                elif (self.random_choice_2 == 2):
                    self.other_user_2 = InactiveUserFactory(**user_factory_dict)
                elif (self.random_choice_2 == 3):
                    self.other_user_2 = SpeedyNetInactiveUserFactory(**user_factory_dict)
                else:
                    raise NotImplementedError("Invalid random choice.")
                data = {
                    'username': "mike@example.com",
                    'password': self._other_user_password,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.other_user)

            def test_visitor_can_login_using_short_password(self):
                # Using a password that is too short and with too few unique characters.
                from django.contrib.auth.hashers import make_password
                # Call make_password() directly because set_password() will raise an exception if the password is too short.
                self.user.password = make_password(password='123')
                self.user.save_user_and_profile()
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': self.user.slug,
                    'password': '123',
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_short_username_and_password(self):
                # Using a password that is too short and with too few unique characters, and a username that is too short.
                from django.contrib.auth.hashers import make_password
                # Call make_password() directly because set_password() will raise an exception if the password is too short.
                self.other_user.username, self.other_user.slug, self.other_user.special_username = 'aaa', 'aaa', True
                self.other_user.password = make_password(password='123')
                self.other_user.save_user_and_profile()
                self.assertEqual(first=self.other_user.slug, second='aaa')
                data = {
                    'username': 'aaa',
                    'password': '123',
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.other_user)

            def test_visitor_cannot_login_using_wrong_email(self):
                data = {
                    'username': self.other_user_email.email,
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._please_enter_a_correct_username_and_password_errors_dict())
                self.assert_me_url_redirects_to_login_url()

            def test_visitor_cannot_login_using_incorrect_password_1(self):
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': 'slug-with-dots',
                    'password': 'wrong password!!',
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._please_enter_a_correct_username_and_password_errors_dict())
                self.assert_me_url_redirects_to_login_url()

            def test_visitor_cannot_login_using_incorrect_password_2(self):
                # Using a password that is too short and with too few unique characters.
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': 'slug-with-dots',
                    'password': '123',
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._please_enter_a_correct_username_and_password_errors_dict())
                self.assert_me_url_redirects_to_login_url()

            def test_visitor_cannot_login_using_incorrect_username_and_password(self):
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': 'wrong username!!',
                    'password': 'wrong password!!',
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._please_enter_a_correct_username_and_password_errors_dict())
                self.assert_me_url_redirects_to_login_url()

            def test_visitor_cannot_login_using_non_existent_username_and_invalid_password_1(self):
                # Using a password that is too short and with too few unique characters.
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': 'wrong username!!',
                    'password': '123',
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._please_enter_a_correct_username_and_password_errors_dict())
                self.assert_me_url_redirects_to_login_url()

            def test_visitor_cannot_login_using_non_existent_username_and_invalid_password_2(self):
                # Using a password that is too short and with too few unique characters, and a username that is too short.
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': 'aaa',
                    'password': '123',
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._please_enter_a_correct_username_and_password_errors_dict())
                self.assert_me_url_redirects_to_login_url()

            def test_visitor_cannot_login_using_non_existent_username_and_invalid_password_3(self):
                # Using a password that is too short and with too few unique characters.
                too_short_password = '8' * 3
                data = {
                    'username': 'non-existent-username',
                    'password': too_short_password,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._please_enter_a_correct_username_and_password_errors_dict())
                self.assert_me_url_redirects_to_login_url()

            def test_visitor_cannot_login_without_username_and_password(self):
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {}
                r = self.client.post(path=self.login_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._login_form_all_the_required_fields_are_required_errors_dict())
                self.assert_me_url_redirects_to_login_url()

            def test_visitor_cannot_login_without_username(self):
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'password': 'wrong password!!',
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._username_is_required_errors_dict())
                self.assert_me_url_redirects_to_login_url()

            def test_visitor_cannot_login_without_password(self):
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': 'slug-with-dots',
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_is_required_errors_dict())
                self.assert_me_url_redirects_to_login_url()


        @only_on_sites_with_login
        class LoginViewAllLanguagesEnglishTestCase(LoginViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class LoginViewAllLanguagesFrenchTestCase(LoginViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class LoginViewAllLanguagesGermanTestCase(LoginViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class LoginViewAllLanguagesSpanishTestCase(LoginViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class LoginViewAllLanguagesPortugueseTestCase(LoginViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class LoginViewAllLanguagesItalianTestCase(LoginViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class LoginViewAllLanguagesDutchTestCase(LoginViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class LoginViewAllLanguagesSwedishTestCase(LoginViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class LoginViewAllLanguagesKoreanTestCase(LoginViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class LoginViewAllLanguagesFinnishTestCase(LoginViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class LoginViewAllLanguagesHebrewTestCase(LoginViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        class LogoutViewOnlyEnglishTestCase(SpeedyCoreAccountsModelsMixin, SiteTestCase):
            def set_up(self):
                super().set_up()
                self.random_choice = random.choice([1, 2, 3])
                if (self.random_choice == 1):
                    self.user = ActiveUserFactory()
                elif (self.random_choice == 2):
                    self.user = InactiveUserFactory()
                elif (self.random_choice == 3):
                    self.user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count={"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count={"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=0,
                )

            def assert_user_is_active_and_redirects(self, r):
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    if (self.random_choice == 1):
                        self.assertEqual(first=self.user.is_active, second=True)
                        self.assertEqual(first=self.user.profile.is_active, second=True)
                        self.assertEqual(first=self.user.speedy_net_profile.is_active, second=True)
                        self.assertEqual(first=self.user.speedy_match_profile.is_active, second=False)
                        self.assertRedirects(response=r, expected_url='/{}/'.format(self.user.slug), status_code=302, target_status_code=200, fetch_redirect_response=False)
                    elif (self.random_choice == 2):
                        self.assertEqual(first=self.user.is_active, second=False)
                        self.assertEqual(first=self.user.profile.is_active, second=False)
                        self.assertEqual(first=self.user.speedy_net_profile.is_active, second=False)
                        self.assertEqual(first=self.user.speedy_match_profile.is_active, second=False)
                        self.assertRedirects(response=r, expected_url='/welcome/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                    elif (self.random_choice == 3):
                        self.assertEqual(first=self.user.is_active, second=False)
                        self.assertEqual(first=self.user.profile.is_active, second=False)
                        self.assertEqual(first=self.user.speedy_net_profile.is_active, second=False)
                        self.assertEqual(first=self.user.speedy_match_profile.is_active, second=False)
                        self.assertRedirects(response=r, expected_url='/welcome/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                    else:
                        raise NotImplementedError("Invalid random choice.")
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    if (self.random_choice == 1):
                        self.assertEqual(first=self.user.is_active, second=True)
                        self.assertEqual(first=self.user.profile.is_active, second=True)
                        self.assertEqual(first=self.user.speedy_net_profile.is_active, second=True)
                        self.assertEqual(first=self.user.speedy_match_profile.is_active, second=True)
                        self.assertRedirects(response=r, expected_url='/matches/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                    elif (self.random_choice == 2):
                        self.assertEqual(first=self.user.is_active, second=True)
                        self.assertEqual(first=self.user.profile.is_active, second=False)
                        self.assertEqual(first=self.user.speedy_net_profile.is_active, second=True)
                        self.assertEqual(first=self.user.speedy_match_profile.is_active, second=False)
                        self.assertRedirects(response=r, expected_url='/registration-step-2/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                    elif (self.random_choice == 3):
                        self.assertEqual(first=self.user.is_active, second=False)
                        self.assertEqual(first=self.user.profile.is_active, second=False)
                        self.assertEqual(first=self.user.speedy_net_profile.is_active, second=False)
                        self.assertEqual(first=self.user.speedy_match_profile.is_active, second=False)
                        self.assertRedirects(response=r, expected_url='/welcome/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                    else:
                        raise NotImplementedError("Invalid random choice.")
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")

            def test_user_can_logout(self):
                r = self.client.get(path='/')
                self.assert_user_is_active_and_redirects(r=r)
                r = self.client.post(path='/logout/')
                self.assertEqual(first=r.status_code, second=200)
                r = self.client.get(path='/')
                self.assertIs(expr1=r.context['user'].is_authenticated, expr2=False)

            def test_user_cannot_logout_using_get_method(self):
                r = self.client.get(path='/')
                self.assert_user_is_active_and_redirects(r=r)
                r = self.client.get(path='/logout/')
                self.assertEqual(first=r.status_code, second=405)
                r = self.client.get(path='/', follow=True)
                self.assertIs(expr1=hasattr(r, 'redirect_chain'), expr2=True)
                self.assertIs(expr1=r.context['user'].is_authenticated, expr2=True)


        class EditProfileViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            page_url = '/edit-profile/'

            def set_up(self):
                super().set_up()
                self.random_choice = random.choice([1, 2, 3])
                if (self.random_choice == 1):
                    self.user = ActiveUserFactory()
                elif (self.random_choice == 2):
                    self.user = InactiveUserFactory()
                elif (self.random_choice == 3):
                    self.user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.original_first_name = self.user.first_name
                self.original_last_name = self.user.last_name
                self.data = {
                    'date_of_birth': '1976-06-03',
                    'slug': self.user.slug,
                    'gender': 1,
                }
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count={"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count={"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=0,
                )
                self.assertEqual(first=self.user.username, second=self.user.slug)
                self.assertEqual(first=len(self.user.username), second=12)
                self.assertEqual(first=len(self.user.slug), second=12)

            def set_up_required_fields(self):
                self.required_fields = self.data.keys() - {to_attribute(name="last_name", language_code=self.language_code)}
                self.assert_profile_form_required_fields(required_fields=self.required_fields)

            def test_visitor_has_no_access(self):
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_active_user_can_open_the_page(self):
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/profile.html')

            def test_inactive_user_can_open_the_page(self):
                self.user.profile.deactivate()
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/profile.html')
                self.user.speedy_net_profile.deactivate()
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/profile.html')

            def test_active_user_can_save_his_settings(self):
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=200)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.first_name, second=self.first_name)
                self.assertEqual(first=user.first_name_en, second={'en': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'en') else '__'])
                self.assertEqual(first=user.first_name_fr, second={'fr': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'fr') else '__'])
                self.assertEqual(first=user.first_name_de, second={'de': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'de') else '__'])
                self.assertEqual(first=user.first_name_es, second={'es': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'es') else '__'])
                self.assertEqual(first=user.first_name_pt, second={'pt': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'pt') else '__'])
                self.assertEqual(first=user.first_name_it, second={'it': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'it') else '__'])
                self.assertEqual(first=user.first_name_nl, second={'nl': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'nl') else '__'])
                self.assertEqual(first=user.first_name_sv, second={'sv': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'sv') else '__'])
                self.assertEqual(first=user.first_name_ko, second={'ko': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ko') else '__'])
                self.assertEqual(first=user.first_name_fi, second={'fi': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'fi') else '__'])
                self.assertEqual(first=user.first_name_he, second={'he': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'he') else '__'])
                self.assertEqual(first=user.last_name, second=self.last_name)
                self.assertEqual(first=user.last_name_en, second={'en': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'en') else '__'])
                self.assertEqual(first=user.last_name_fr, second={'fr': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'fr') else '__'])
                self.assertEqual(first=user.last_name_de, second={'de': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'de') else '__'])
                self.assertEqual(first=user.last_name_es, second={'es': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'es') else '__'])
                self.assertEqual(first=user.last_name_pt, second={'pt': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'pt') else '__'])
                self.assertEqual(first=user.last_name_it, second={'it': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'it') else '__'])
                self.assertEqual(first=user.last_name_nl, second={'nl': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'nl') else '__'])
                self.assertEqual(first=user.last_name_sv, second={'sv': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'sv') else '__'])
                self.assertEqual(first=user.last_name_ko, second={'ko': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ko') else '__'])
                self.assertEqual(first=user.last_name_fi, second={'fi': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'fi') else '__'])
                self.assertEqual(first=user.last_name_he, second={'he': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'he') else '__'])
                for (key, value) in self.data.items():
                    if (not (key in ['date_of_birth'])):
                        self.assertEqual(first=getattr(user, key), second=value)
                self.assertEqual(first=user.date_of_birth, second=date(year=1976, month=6, day=3))

            def test_inactive_user_can_save_his_settings(self):
                self.user.profile.deactivate()
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=200)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.first_name, second=self.first_name)
                self.assertEqual(first=user.last_name, second=self.last_name)
                for (key, value) in self.data.items():
                    if (not (key in ['date_of_birth'])):
                        self.assertEqual(first=getattr(user, key), second=value)
                self.assertEqual(first=user.date_of_birth, second=date(year=1976, month=6, day=3))

            def run_test_required_fields(self, data):
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._profile_form_all_the_required_fields_are_required_errors_dict())
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.first_name, second=self.original_first_name)
                self.assertEqual(first=user.last_name, second=self.original_last_name)
                self.assert_user_first_and_last_name_in_all_languages(user=user)

            def test_required_fields_1(self):
                data = {}
                self.run_test_required_fields(data=data)

            def test_required_fields_2(self):
                data = {field_name: '' for field_name in self.required_fields}
                self.run_test_required_fields(data=data)

            def run_test_user_can_change_his_slug(self, new_slug):
                old_slug = self.user.slug
                data = self.data.copy()
                data['slug'] = new_slug
                self.assertNotEqual(first=self.user.slug, second=normalize_slug(slug=new_slug))
                self.assertEqual(first=normalize_username(username=new_slug), second=self.user.username)
                r = self.client.post(path=self.page_url, data=data)
                self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=200)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.slug, second=normalize_slug(slug=new_slug))
                self.assertNotEqual(first=user.slug, second=old_slug)

            def run_test_user_can_change_his_slug_with_normalize_slug(self, new_slug, new_slug_normalized):
                self.assertNotEqual(first=normalize_slug(slug=new_slug), second=new_slug)
                self.assertEqual(first=normalize_slug(slug=new_slug), second=new_slug_normalized)
                self.run_test_user_can_change_his_slug(new_slug=new_slug)

            def test_user_can_change_his_slug(self):
                new_slug = '{}-{}-{}'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                self.assertEqual(first=normalize_slug(slug=new_slug), second=new_slug)
                self.run_test_user_can_change_his_slug(new_slug=new_slug)

            def test_user_can_change_his_slug_with_normalize_slug_1(self):
                new_slug = '{}.{}--{}'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                new_slug_normalized = '{}-{}-{}'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                self.run_test_user_can_change_his_slug_with_normalize_slug(new_slug=new_slug, new_slug_normalized=new_slug_normalized)

            def test_user_can_change_his_slug_with_normalize_slug_2(self):
                new_slug = '==-{}\\@!!#@#&^&*()({}=*&^%$)(\\/={}---'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                new_slug_normalized = '{}-{}-{}'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                self.run_test_user_can_change_his_slug_with_normalize_slug(new_slug=new_slug, new_slug_normalized=new_slug_normalized)

            def run_test_user_cannot_change_his_username(self, new_slug):
                old_slug = self.user.slug
                data = self.data.copy()
                data['slug'] = new_slug
                self.assertNotEqual(first=self.user.slug, second=new_slug)
                self.assertNotEqual(first=normalize_username(username=new_slug), second=self.user.username)
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._you_cant_change_your_username_errors_dict_by_gender(gender=self.user.get_gender()))
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.slug, second=old_slug)
                self.assertNotEqual(first=user.slug, second=new_slug)
                self.assertEqual(first=user.username, second=normalize_username(username=old_slug))
                self.assertNotEqual(first=user.username, second=normalize_username(username=new_slug))

            def run_test_user_cannot_change_his_username_with_normalize_slug(self, new_slug, new_slug_normalized):
                self.assertNotEqual(first=normalize_slug(slug=new_slug), second=new_slug)
                self.assertEqual(first=normalize_slug(slug=new_slug), second=new_slug_normalized)
                self.run_test_user_cannot_change_his_username(new_slug=new_slug)

            def test_user_cannot_change_his_username_1(self):
                new_slug = 'a{}'.format(self.user.slug)
                self.assertEqual(first=normalize_slug(slug=new_slug), second=new_slug)
                self.run_test_user_cannot_change_his_username(new_slug=new_slug)

            def test_user_cannot_change_his_username_2(self):
                new_slug = '{}-{}-1-{}'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                self.assertEqual(first=normalize_slug(slug=new_slug), second=new_slug)
                self.run_test_user_cannot_change_his_username(new_slug=new_slug)

            def test_user_cannot_change_his_username_with_normalize_slug(self):
                new_slug = '==-{}\\@!!#@#&^&*()({}=*&^%$1)(\\/={}---'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                new_slug_normalized = '{}-{}-1-{}'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                self.run_test_user_cannot_change_his_username_with_normalize_slug(new_slug=new_slug, new_slug_normalized=new_slug_normalized)

            def test_valid_date_of_birth_list_ok(self):
                self.user.allowed_to_change_date_of_birth_unlimited_times = True
                self.user.save_user_and_profile()
                for date_of_birth in tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST:
                    data = self.data.copy()
                    data['date_of_birth'] = date_of_birth
                    r = self.client.post(path=self.page_url, data=data)
                    self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=200, msg_prefix="{} is not a valid date of birth.".format(date_of_birth))
                    user = User.objects.get(pk=self.user.pk)
                    self.assertEqual(first=user.first_name, second=self.first_name)
                    self.assertEqual(first=user.first_name_en, second={'en': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'en') else '__'])
                    self.assertEqual(first=user.first_name_fr, second={'fr': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'fr') else '__'])
                    self.assertEqual(first=user.first_name_de, second={'de': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'de') else '__'])
                    self.assertEqual(first=user.first_name_es, second={'es': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'es') else '__'])
                    self.assertEqual(first=user.first_name_pt, second={'pt': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'pt') else '__'])
                    self.assertEqual(first=user.first_name_it, second={'it': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'it') else '__'])
                    self.assertEqual(first=user.first_name_nl, second={'nl': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'nl') else '__'])
                    self.assertEqual(first=user.first_name_sv, second={'sv': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'sv') else '__'])
                    self.assertEqual(first=user.first_name_ko, second={'ko': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ko') else '__'])
                    self.assertEqual(first=user.first_name_fi, second={'fi': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'fi') else '__'])
                    self.assertEqual(first=user.first_name_he, second={'he': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'he') else '__'])
                    self.assertEqual(first=user.last_name, second=self.last_name)
                    self.assertEqual(first=user.last_name_en, second={'en': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'en') else '__'])
                    self.assertEqual(first=user.last_name_fr, second={'fr': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'fr') else '__'])
                    self.assertEqual(first=user.last_name_de, second={'de': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'de') else '__'])
                    self.assertEqual(first=user.last_name_es, second={'es': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'es') else '__'])
                    self.assertEqual(first=user.last_name_pt, second={'pt': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'pt') else '__'])
                    self.assertEqual(first=user.last_name_it, second={'it': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'it') else '__'])
                    self.assertEqual(first=user.last_name_nl, second={'nl': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'nl') else '__'])
                    self.assertEqual(first=user.last_name_sv, second={'sv': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'sv') else '__'])
                    self.assertEqual(first=user.last_name_ko, second={'ko': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ko') else '__'])
                    self.assertEqual(first=user.last_name_fi, second={'fi': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'fi') else '__'])
                    self.assertEqual(first=user.last_name_he, second={'he': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'he') else '__'])
                    for (key, value) in self.data.items():
                        if (not (key in ['date_of_birth'])):
                            self.assertEqual(first=getattr(user, key), second=value)
                    self.assertEqual(first=user.date_of_birth, second=datetime.strptime(date_of_birth, '%Y-%m-%d').date())

            def test_change_date_of_birth_12_times(self):
                number_of_date_of_birth_changes = 0
                for date_of_birth in tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST[:12]:
                    data = self.data.copy()
                    data['date_of_birth'] = date_of_birth
                    r = self.client.post(path=self.page_url, data=data)
                    number_of_date_of_birth_changes += 1
                    if (number_of_date_of_birth_changes >= 12):
                        self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=302, fetch_redirect_response=False, msg_prefix="{} is not a valid date of birth.".format(date_of_birth))
                        r = self.client.get(path=self.page_url)
                        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)
                    else:
                        self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=200, msg_prefix="{} is not a valid date of birth.".format(date_of_birth))
                    user = User.objects.get(pk=self.user.pk)
                    self.assertEqual(first=user.first_name, second=self.first_name)
                    self.assertEqual(first=user.last_name, second=self.last_name)
                    for (key, value) in self.data.items():
                        if (not (key in ['date_of_birth'])):
                            self.assertEqual(first=getattr(user, key), second=value)
                    self.assertEqual(first=user.date_of_birth, second=datetime.strptime(date_of_birth, '%Y-%m-%d').date())
                    self.assertEqual(first=user.number_of_date_of_birth_changes, second=number_of_date_of_birth_changes)
                    self.assertIs(expr1=(user.allowed_to_change_date_of_birth_unlimited_times is False), expr2=True)
                    if ((number_of_date_of_birth_changes >= 1) and (number_of_date_of_birth_changes < 7)):
                        self.assertIs(expr1=(user.speedy_match_profile.not_allowed_to_use_speedy_match is False), expr2=True)
                        self.assertIs(expr1=(user.has_usable_password() is True), expr2=True)
                    elif ((number_of_date_of_birth_changes >= 7) and (number_of_date_of_birth_changes < 12)):
                        self.assertIs(expr1=(user.speedy_match_profile.not_allowed_to_use_speedy_match is True), expr2=True)
                        self.assertIs(expr1=(user.has_usable_password() is True), expr2=True)
                    elif (number_of_date_of_birth_changes == 12):
                        self.assertIs(expr1=(user.speedy_match_profile.not_allowed_to_use_speedy_match is True), expr2=True)
                        self.assertIs(expr1=(user.has_usable_password() is False), expr2=True)
                    else:
                        raise NotImplementedError("Invalid number_of_date_of_birth_changes.")
                self.assertIs(expr1=(number_of_date_of_birth_changes == 12), expr2=True)

            def test_change_date_of_birth_unlimited_times(self):
                self.user.allowed_to_change_date_of_birth_unlimited_times = True
                self.user.save_user_and_profile()
                number_of_date_of_birth_changes = 0
                for date_of_birth in tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST:
                    data = self.data.copy()
                    data['date_of_birth'] = date_of_birth
                    r = self.client.post(path=self.page_url, data=data)
                    number_of_date_of_birth_changes += 1
                    self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=200, msg_prefix="{} is not a valid date of birth.".format(date_of_birth))
                    user = User.objects.get(pk=self.user.pk)
                    self.assertEqual(first=user.first_name, second=self.first_name)
                    self.assertEqual(first=user.last_name, second=self.last_name)
                    for (key, value) in self.data.items():
                        if (not (key in ['date_of_birth'])):
                            self.assertEqual(first=getattr(user, key), second=value)
                    self.assertEqual(first=user.date_of_birth, second=datetime.strptime(date_of_birth, '%Y-%m-%d').date())
                    self.assertEqual(first=user.number_of_date_of_birth_changes, second=number_of_date_of_birth_changes)
                    self.assertIs(expr1=(user.allowed_to_change_date_of_birth_unlimited_times is True), expr2=True)
                    self.assertIs(expr1=(user.speedy_match_profile.not_allowed_to_use_speedy_match is False), expr2=True)
                    self.assertIs(expr1=(user.has_usable_password() is True), expr2=True)
                self.assertIs(expr1=(17 < number_of_date_of_birth_changes < 25), expr2=True)

            def test_invalid_date_of_birth_list_fail(self):
                self.date_of_birth = self.user.date_of_birth
                for date_of_birth in tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST:
                    data = self.data.copy()
                    data['date_of_birth'] = date_of_birth
                    r = self.client.post(path=self.page_url, data=data)
                    self.assertEqual(first=r.status_code, second=200, msg="{} is a valid date of birth.".format(date_of_birth))
                    self.assertDictEqual(d1=r.context['form'].errors, d2=self._date_of_birth_errors_dict_by_date_of_birth(date_of_birth=date_of_birth), msg='"{}" - Unexpected error messages.'.format(date_of_birth))
                    user = User.objects.get(pk=self.user.pk)
                    self.assertEqual(first=user.date_of_birth, second=self.date_of_birth)


        @only_on_sites_with_login
        class EditProfileViewWithLastNameAllLanguagesEnglishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in English alphabet.
                super().set_up()
                self.data.update({
                    'first_name_en': "Jennifer",
                    'last_name_en': "Connelly",
                })
                self.first_name = "Jennifer"
                self.last_name = "Connelly"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class EditProfileViewWithLastNameAllLanguagesFrenchTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in French alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fr': "Alizée",
                    'last_name_fr': "Jacotey",
                })
                self.first_name = "Alizée"
                self.last_name = "Jacotey"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class EditProfileViewWithLastNameAllLanguagesGermanTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in German alphabet.
                super().set_up()
                self.data.update({
                    'first_name_de': "Doron",
                    'last_name_de': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class EditProfileViewWithLastNameAllLanguagesSpanishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Spanish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_es': "Lionel",
                    'last_name_es': "Messi",
                })
                self.first_name = "Lionel"
                self.last_name = "Messi"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class EditProfileViewWithLastNameAllLanguagesPortugueseTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Portuguese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_pt': "Cristiano",
                    'last_name_pt': "Ronaldo",
                })
                self.first_name = "Cristiano"
                self.last_name = "Ronaldo"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class EditProfileViewWithLastNameAllLanguagesItalianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Italian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_it': "Andrea",
                    'last_name_it': "Bocelli",
                })
                self.first_name = "Andrea"
                self.last_name = "Bocelli"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class EditProfileViewWithLastNameAllLanguagesDutchTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Dutch alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class EditProfileViewWithLastNameAllLanguagesSwedishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Swedish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_sv': "Doron",
                    'last_name_sv': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class EditProfileViewWithLastNameAllLanguagesKoreanTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Korean alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ko': "Doron",
                    'last_name_ko': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class EditProfileViewWithLastNameAllLanguagesFinnishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Finnish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fi': "Doron",
                    'last_name_fi': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class EditProfileViewWithLastNameAllLanguagesHebrewTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Hebrew alphabet.
                super().set_up()
                self.data.update({
                    'first_name_he': "ג'ניפר",
                    'last_name_he': "קונלי",
                })
                self.first_name = "ג'ניפר"
                self.last_name = "קונלי"
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        class EditProfileViewWithoutLastNameAllLanguagesEnglishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in English alphabet.
                super().set_up()
                self.data.update({
                    'first_name_en': "Jennifer",
                    'last_name_en': "",
                })
                self.first_name = "Jennifer"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class EditProfileViewWithoutLastNameAllLanguagesFrenchTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in French alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fr': "Alizée",
                    'last_name_fr': "",
                })
                self.first_name = "Alizée"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class EditProfileViewWithoutLastNameAllLanguagesGermanTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in German alphabet.
                super().set_up()
                self.data.update({
                    'first_name_de': "Doron",
                    'last_name_de': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class EditProfileViewWithoutLastNameAllLanguagesSpanishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Spanish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_es': "Lionel",
                    'last_name_es': "",
                })
                self.first_name = "Lionel"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class EditProfileViewWithoutLastNameAllLanguagesPortugueseTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Portuguese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_pt': "Cristiano",
                    'last_name_pt': "",
                })
                self.first_name = "Cristiano"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class EditProfileViewWithoutLastNameAllLanguagesItalianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Italian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_it': "Andrea",
                    'last_name_it': "",
                })
                self.first_name = "Andrea"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class EditProfileViewWithoutLastNameAllLanguagesDutchTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Dutch alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class EditProfileViewWithoutLastNameAllLanguagesSwedishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Swedish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_sv': "Doron",
                    'last_name_sv': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class EditProfileViewWithoutLastNameAllLanguagesKoreanTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Korean alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ko': "Doron",
                    'last_name_ko': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class EditProfileViewWithoutLastNameAllLanguagesFinnishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Finnish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fi': "Doron",
                    'last_name_fi': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class EditProfileViewWithoutLastNameAllLanguagesHebrewTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Hebrew alphabet.
                super().set_up()
                self.data.update({
                    'first_name_he': "ג'ניפר",
                    'last_name_he': "",
                })
                self.first_name = "ג'ניפר"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        class EditProfilePrivacyViewOnlyEnglishTestCase(SpeedyCoreAccountsModelsMixin, SiteTestCase):
            page_url = '/edit-profile/privacy/'

            def set_up(self):
                super().set_up()
                self.random_choice = random.choice([1, 2, 3])
                if (self.random_choice == 1):
                    self.user = ActiveUserFactory()
                elif (self.random_choice == 2):
                    self.user = InactiveUserFactory()
                elif (self.random_choice == 3):
                    self.user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=0,
                )

            def test_visitor_has_no_access(self):
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_active_user_can_open_the_page(self):
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/privacy.html')

            def test_inactive_user_can_open_the_page(self):
                self.user.profile.deactivate()
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/privacy.html')

            def test_user_can_save_his_settings_1(self):
                data = {
                    'access_dob_day_month': '2',
                    'access_dob_year': '4',
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=200)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.access_dob_day_month, second=2)
                self.assertEqual(first=user.access_dob_year, second=4)

            def test_user_can_save_his_settings_2(self):
                data = {
                    'access_dob_day_month': '4',
                    'access_dob_year': '2',
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=200)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.access_dob_day_month, second=4)
                self.assertEqual(first=user.access_dob_year, second=2)


        class EditProfileNotificationsViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, TestCaseMixin):
            page_url = '/edit-profile/notifications/'

            def set_up(self):
                super().set_up()
                self.random_choice = random.choice([1, 2, 3])
                if (self.random_choice == 1):
                    self.user = ActiveUserFactory()
                elif (self.random_choice == 2):
                    self.user = InactiveUserFactory()
                elif (self.random_choice == 3):
                    self.user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count={"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count={"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=0,
                )

            def test_visitor_has_no_access(self):
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_active_user_can_open_the_page(self):
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/notifications.html')

            def test_inactive_user_can_open_the_page(self):
                self.user.profile.deactivate()
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/notifications.html')

            def test_user_can_save_his_settings(self):
                raise NotImplementedError("This test is not implemented in this mixin.")


        class EditProfileCredentialsViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            page_url = '/edit-profile/credentials/'

            def set_up(self):
                super().set_up()
                self.random_choice = random.choice([1, 2, 3])
                if (self.random_choice == 1):
                    self.user = ActiveUserFactory()
                elif (self.random_choice == 2):
                    self.user = InactiveUserFactory()
                elif (self.random_choice == 3):
                    self.user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=0,
                )

            def test_visitor_has_no_access(self):
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_active_user_can_open_the_page(self):
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/credentials.html')

            def test_inactive_user_can_open_the_page(self):
                self.user.profile.deactivate()
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/credentials.html')

            def test_user_can_change_password_1(self):
                new_password = 'abcdef12'
                incorrect_new_password = '1' * 8
                self.assertEqual(first=len(new_password), second=8)
                data = {
                    'old_password': tests_settings.USER_PASSWORD,
                    'new_password1': new_password,
                    'new_password2': new_password,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=200)
                user = User.objects.get(pk=self.user.pk)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=incorrect_new_password), expr2=False)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=False)

            def test_user_can_change_password_2(self):
                new_password = 'abcdef' + ('8' * 114)
                incorrect_new_password = 'abcde8' + ('8' * 114)
                self.assertEqual(first=len(new_password), second=120)
                data = {
                    'old_password': tests_settings.USER_PASSWORD,
                    'new_password1': new_password,
                    'new_password2': new_password,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=200)
                user = User.objects.get(pk=self.user.pk)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=incorrect_new_password), expr2=False)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=False)

            def test_user_can_change_password_3(self):
                new_password = 'abcd//' + ('8' * 114)
                incorrect_new_password = 'abcd/?' + ('8' * 114)
                self.assertEqual(first=len(new_password), second=120)
                data = {
                    'old_password': tests_settings.USER_PASSWORD,
                    'new_password1': new_password,
                    'new_password2': new_password,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=200)
                user = User.objects.get(pk=self.user.pk)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=incorrect_new_password), expr2=False)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=False)

            def test_old_password_incorrect(self):
                incorrect_old_password = '7' * 8
                new_password = 'abcdef12'
                self.assertEqual(first=len(new_password), second=8)
                data = {
                    'old_password': incorrect_old_password,
                    'new_password1': new_password,
                    'new_password2': new_password,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._your_old_password_was_entered_incorrectly_errors_dict())
                user = User.objects.get(pk=self.user.pk)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=False)
                self.assertIs(expr1=user.check_password(raw_password=incorrect_old_password), expr2=False)

            def test_password_too_short(self):
                new_password = 'abcdef'
                self.assertEqual(first=len(new_password), second=6)
                data = {
                    'old_password': tests_settings.USER_PASSWORD,
                    'new_password1': new_password,
                    'new_password2': new_password,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_too_short_errors_dict(field_names=self._both_password_field_names))
                user = User.objects.get(pk=self.user.pk)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=False)

            def test_password_too_long(self):
                new_password = 'abcdef' + ('8' * 115)
                self.assertEqual(first=len(new_password), second=121)
                data = {
                    'old_password': tests_settings.USER_PASSWORD,
                    'new_password1': new_password,
                    'new_password2': new_password,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_too_long_errors_dict(field_names=self._both_password_field_names))
                user = User.objects.get(pk=self.user.pk)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=False)

            def test_password_not_enough_unique_characters(self):
                new_password = '1234' * 2
                self.assertEqual(first=len(new_password), second=8)
                data = {
                    'old_password': tests_settings.USER_PASSWORD,
                    'new_password1': new_password,
                    'new_password2': new_password,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._your_password_must_contain_at_least_6_unique_characters_errors_dict(field_names=self._both_password_field_names))
                user = User.objects.get(pk=self.user.pk)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=False)

            def test_password_too_short_and_not_enough_unique_characters(self):
                new_password = '8' * 3
                self.assertEqual(first=len(new_password), second=3)
                data = {
                    'old_password': tests_settings.USER_PASSWORD,
                    'new_password1': new_password,
                    'new_password2': new_password,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_too_short_and_your_password_must_contain_at_least_6_unique_characters_errors_dict(field_names=self._both_password_field_names))
                user = User.objects.get(pk=self.user.pk)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=False)

            def test_password_too_long_and_not_enough_unique_characters(self):
                new_password = '8' * 121
                self.assertEqual(first=len(new_password), second=121)
                data = {
                    'old_password': tests_settings.USER_PASSWORD,
                    'new_password1': new_password,
                    'new_password2': new_password,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_too_long_and_your_password_must_contain_at_least_6_unique_characters_errors_dict(field_names=self._both_password_field_names))
                user = User.objects.get(pk=self.user.pk)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=False)

            def test_passwords_dont_match(self):
                new_password_1 = 'abcdef12'
                new_password_2 = 'abcdef34'
                data = {
                    'old_password': tests_settings.USER_PASSWORD,
                    'new_password1': new_password_1,
                    'new_password2': new_password_2,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._the_two_password_fields_didnt_match_errors_dict())
                user = User.objects.get(pk=self.user.pk)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=new_password_1), expr2=False)
                self.assertIs(expr1=user.check_password(raw_password=new_password_2), expr2=False)


        @only_on_sites_with_login
        class EditProfileCredentialsViewAllLanguagesEnglishTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class EditProfileCredentialsViewAllLanguagesFrenchTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class EditProfileCredentialsViewAllLanguagesGermanTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class EditProfileCredentialsViewAllLanguagesSpanishTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class EditProfileCredentialsViewAllLanguagesPortugueseTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class EditProfileCredentialsViewAllLanguagesItalianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class EditProfileCredentialsViewAllLanguagesDutchTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class EditProfileCredentialsViewAllLanguagesSwedishTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class EditProfileCredentialsViewAllLanguagesKoreanTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class EditProfileCredentialsViewAllLanguagesFinnishTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class EditProfileCredentialsViewAllLanguagesHebrewTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class ActivateSiteProfileViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, TestCaseMixin):
            page_url = '/welcome/'
            redirect_url = None

            def test_visitor_has_no_access(self):
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_inactive_user_has_no_access_to_other_pages(self):
                r = self.client.get(path='/other-page/')
                self.assertRedirects(response=r, expected_url=self.redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=False)

            def test_active_user_gets_redirected(self):
                self.client.logout()
                user_2 = ActiveUserFactory()
                self.client.login(username=user_2.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=user_2.is_active, second=True)
                self.assertEqual(first=user_2.profile.is_active, second=True)
                r = self.client.get(path=self.page_url)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=302)
                    r = self.client.get(path='/')
                    self.assertRedirects(response=r, expected_url='/{}/'.format(user_2.slug), status_code=302, target_status_code=200, fetch_redirect_response=False)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertRedirects(response=r, expected_url='/registration-step-10/', status_code=302, target_status_code=302)
                    r = self.client.get(path='/registration-step-10/')
                    self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=302)
                    r = self.client.get(path='/')
                    self.assertRedirects(response=r, expected_url='/matches/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")

            def test_inactive_user_can_open_the_page(self):
                r = self.client.get(path=self.page_url)
                self.assertIn(member=r.status_code, container={200, 302})
                if (r.status_code == 200):
                    self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/activate.html')

            def test_inactive_user_can_request_activation(self):
                raise NotImplementedError("This test is not implemented in this mixin.")


        class ActivateSiteProfileViewTestCaseMixin1(ActivateSiteProfileViewTestCaseMixin):
            def set_up(self):
                super().set_up()
                self.user = InactiveUserFactory()
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=self.user.is_active, second={django_settings.SPEEDY_NET_SITE_ID: False, django_settings.SPEEDY_MATCH_SITE_ID: True}[self.site.id])
                self.assertEqual(first=self.user.profile.is_active, second=False)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=0,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=0,
                )


        class ActivateSiteProfileViewTestCaseMixin2(ActivateSiteProfileViewTestCaseMixin):
            def set_up(self):
                super().set_up()
                self.user = SpeedyNetInactiveUserFactory()
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=self.user.is_active, second=False)
                self.assertEqual(first=self.user.profile.is_active, second=False)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=1,
                    unconfirmed_email_address_count=0,
                )


        @only_on_sites_with_login
        class DeactivateSiteProfileViewOnlyEnglishTestCase(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, SiteTestCase):
            page_url = '/edit-profile/deactivate/'

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

            def test_visitor_has_no_access(self):
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_active_user_can_open_the_page(self):
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/deactivate.html')

            def test_inactive_user_can_open_the_page(self):
                self.user.profile.deactivate()
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/deactivate.html')

            def test_user_can_deactivate_his_account(self):
                self.assertEqual(first=self.user.is_active, second=True)
                self.assertEqual(first=self.user.profile.is_active, second=True)
                data = {
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=302)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.is_active, second={django_settings.SPEEDY_NET_SITE_ID: False, django_settings.SPEEDY_MATCH_SITE_ID: True}[self.site.id])
                self.assertEqual(first=user.profile.is_active, second=False)

            def test_user_cannot_deactivate_his_account_using_incorrect_password(self):
                self.assertEqual(first=self.user.is_active, second=True)
                self.assertEqual(first=self.user.profile.is_active, second=True)
                data = {
                    'password': 'wrong password!!',
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._invalid_password_errors_dict())
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.profile.is_active, second=True)

            def test_user_cannot_deactivate_his_account_without_password(self):
                self.assertEqual(first=self.user.is_active, second=True)
                self.assertEqual(first=self.user.profile.is_active, second=True)
                data = {}
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_is_required_errors_dict())
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.profile.is_active, second=True)


        class VerifyUserEmailAddressViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            def set_up(self):
                super().set_up()
                self.random_choice_1 = random.choice([1, 2, 3])
                if (self.random_choice_1 == 1):
                    self.user = ActiveUserFactory()
                elif (self.random_choice_1 == 2):
                    self.user = InactiveUserFactory()
                elif (self.random_choice_1 == 3):
                    self.user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.random_choice_2 = random.choice([1, 2, 3])
                if (self.random_choice_2 == 1):
                    self.other_user = ActiveUserFactory()
                elif (self.random_choice_2 == 2):
                    self.other_user = InactiveUserFactory()
                elif (self.random_choice_2 == 3):
                    self.other_user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
                self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice_1)] + {"1": 1, "2": 0, "3": 1}[str(self.random_choice_2)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice_1)] + {"1": 1, "2": 0, "3": 1}[str(self.random_choice_2)],
                    unconfirmed_email_address_count=1,
                )

            def assert_verify_email_url_redirects_after_error(self, r, user):
                if (user == self.user):
                    random_choice = self.random_choice_1
                elif (user == self.other_user):
                    random_choice = self.random_choice_2
                else:
                    raise NotImplementedError("Invalid user.")
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    if (random_choice == 1):
                        self.assertEqual(first=user.is_active, second=True)
                        self.assertEqual(first=user.profile.is_active, second=True)
                        self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                        self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                    elif (random_choice == 2):
                        self.assertEqual(first=user.is_active, second=False)
                        self.assertEqual(first=user.profile.is_active, second=False)
                        self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
                        self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                    elif (random_choice == 3):
                        self.assertEqual(first=user.is_active, second=False)
                        self.assertEqual(first=user.profile.is_active, second=False)
                        self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
                        self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                    else:
                        raise NotImplementedError("Invalid random choice.")
                    self.assertRedirects(response=r, expected_url='/edit-profile/emails/', status_code=302, target_status_code=302)
                    r = self.client.get(path='/edit-profile/emails/')
                    self.assertRedirects(response=r, expected_url='/edit-profile/credentials/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                    r = self.client.get(path='/edit-profile/credentials/')
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    if (random_choice == 1):
                        self.assertEqual(first=user.is_active, second=True)
                        self.assertEqual(first=user.profile.is_active, second=True)
                        self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                        self.assertEqual(first=user.speedy_match_profile.is_active, second=True)
                        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', status_code=302, target_status_code=302)
                        r = self.client.get(path='/edit-profile/emails/')
                        self.assertRedirects(response=r, expected_url='/edit-profile/credentials/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                        r = self.client.get(path='/edit-profile/credentials/')
                    elif (random_choice == 2):
                        self.assertEqual(first=user.is_active, second=True)
                        self.assertEqual(first=user.profile.is_active, second=False)
                        self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                        self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                        self.assertRedirects(response=r, expected_url='/matches/', status_code=302, target_status_code=302)
                        r = self.client.get(path='/matches/')
                        self.assertRedirects(response=r, expected_url='/registration-step-2/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                        r = self.client.get(path='/registration-step-2/')
                    elif (random_choice == 3):
                        self.assertEqual(first=user.is_active, second=False)
                        self.assertEqual(first=user.profile.is_active, second=False)
                        self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
                        self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', status_code=302, target_status_code=302)
                        r = self.client.get(path='/edit-profile/emails/')
                        self.assertRedirects(response=r, expected_url='/edit-profile/credentials/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                        r = self.client.get(path='/edit-profile/credentials/')
                    else:
                        raise NotImplementedError("Invalid random choice.")
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                return r

            def test_wrong_link_gives_404(self):
                user_email_address = UserEmailAddressFactory()
                token = user_email_address._generate_confirmation_token()
                r = self.client.get(path='/edit-profile/emails/verify/{}/'.format(token))
                self.assertEqual(first=r.status_code, second=404)

            def test_wrong_email_id_gives_404(self):
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                email_id = "111"
                token = self.unconfirmed_email_address.confirmation_token
                r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
                self.assertEqual(first=r.status_code, second=404)

            def test_not_authenticated_user_redirects_to_login(self):
                self.client.logout()
                email_id = self.unconfirmed_email_address.id
                token = self.unconfirmed_email_address.confirmation_token
                r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
                self.assertRedirects(response=r, expected_url='/login/?next=/edit-profile/emails/{}/verify/{}/'.format(email_id, token), status_code=302, target_status_code=200)

            def test_confirmed_email_error_message(self):
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                email_id = self.confirmed_email_address.id
                token = "222"
                r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
                r = self.assert_verify_email_url_redirects_after_error(r=r, user=self.user)
                self.assertEqual(first=r.status_code, second=200)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._youve_already_confirmed_this_email_address_error_message])

            def test_unconfirmed_email_link_confirms_email(self):
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                email_id = self.unconfirmed_email_address.id
                token = self.unconfirmed_email_address.confirmation_token
                r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
                self.assertRedirects(response=r, expected_url='/edit-profile/emails/', status_code=302, target_status_code=302)
                r = self.client.get(path='/edit-profile/emails/')
                self.assertRedirects(response=r, expected_url='/edit-profile/credentials/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                r = self.client.get(path='/edit-profile/credentials/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._youve_confirmed_your_email_address_success_message_dict_by_gender[self.user.get_gender()]])
                self.assertIs(expr1=UserEmailAddress.objects.get(pk=self.unconfirmed_email_address.pk).is_confirmed, expr2=True)

            def test_wrong_user_login_logs_user_out_and_redirects_to_login(self):
                self.client.login(username=self.other_user.slug, password=tests_settings.USER_PASSWORD)
                email_id = self.unconfirmed_email_address.id
                token = self.unconfirmed_email_address.confirmation_token
                r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
                self.assertRedirects(response=r, expected_url='/edit-profile/emails/{}/verify/{}/'.format(email_id, token), status_code=302, target_status_code=302, fetch_redirect_response=False)
                r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
                self.assertRedirects(response=r, expected_url='/login/?next=/edit-profile/emails/{}/verify/{}/'.format(email_id, token), status_code=302, target_status_code=200)

            def test_wrong_confirmation_token_error_message(self):
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                email_id = self.unconfirmed_email_address.id
                token = "222"
                r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
                r = self.assert_verify_email_url_redirects_after_error(r=r, user=self.user)
                self.assertEqual(first=r.status_code, second=200)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._invalid_confirmation_link_error_message])
                self.assertIs(expr1=UserEmailAddress.objects.get(pk=self.unconfirmed_email_address.pk).is_confirmed, expr2=False)


        @only_on_sites_with_login
        class VerifyUserEmailAddressViewAllLanguagesEnglishTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class VerifyUserEmailAddressViewAllLanguagesFrenchTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class VerifyUserEmailAddressViewAllLanguagesGermanTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class VerifyUserEmailAddressViewAllLanguagesSpanishTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class VerifyUserEmailAddressViewAllLanguagesPortugueseTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class VerifyUserEmailAddressViewAllLanguagesItalianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class VerifyUserEmailAddressViewAllLanguagesDutchTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class VerifyUserEmailAddressViewAllLanguagesSwedishTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class VerifyUserEmailAddressViewAllLanguagesKoreanTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class VerifyUserEmailAddressViewAllLanguagesFinnishTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class VerifyUserEmailAddressViewAllLanguagesHebrewTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class AddUserEmailAddressViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            def set_up(self):
                super().set_up()
                self.random_choice = random.choice([1, 2, 3])
                if (self.random_choice == 1):
                    self.user = ActiveUserFactory()
                elif (self.random_choice == 2):
                    self.user = InactiveUserFactory()
                elif (self.random_choice == 3):
                    self.user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
                self.confirmed_email_address.make_primary()
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=0,
                )

            def test_visitor_has_no_access(self):
                self.client.logout()
                r = self.client.get(path='/edit-profile/emails/add/')
                self.assertRedirects(response=r, expected_url='/login/?next=/edit-profile/emails/add/', status_code=302, target_status_code=200)

            def test_active_user_can_open_the_page(self):
                r = self.client.get(path='/edit-profile/emails/add/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/email_address_form.html')

            def test_inactive_user_can_open_the_page(self):
                self.user.profile.deactivate()
                r = self.client.get(path='/edit-profile/emails/add/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/email_address_form.html')

            def test_non_unique_confirmed_email_address(self):
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=0,
                )
                data = {
                    'email': self.confirmed_email_address.email,
                }
                r = self.client.post(path='/edit-profile/emails/add/', data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._this_email_is_already_in_use_errors_dict())
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=0,
                )

            def test_non_unique_unconfirmed_email_address(self):
                self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=1,
                )
                data = {
                    'email': self.unconfirmed_email_address.email,
                }
                r = self.client.post(path='/edit-profile/emails/add/', data=data)
                email_address = UserEmailAddress.objects.get(email=self.unconfirmed_email_address.email)
                self.assertIs(expr1=email_address.is_primary, expr2=False)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=1,
                )

            def test_user_can_add_email_address(self):
                self.assertEqual(first=len(mail.outbox), second=0)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=0,
                )
                data = {
                    'email': 'email@example.com',
                }
                r = self.client.post(path='/edit-profile/emails/add/', data=data)
                self.assertRedirects(response=r, expected_url='/edit-profile/emails/', status_code=302, target_status_code=302)
                r = self.client.get(path='/edit-profile/emails/')
                self.assertRedirects(response=r, expected_url='/edit-profile/credentials/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                r = self.client.get(path='/edit-profile/credentials/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._a_confirmation_message_was_sent_to_email_address_success_message_by_email_address(email_address='email@example.com')])
                email_address = UserEmailAddress.objects.get(email='email@example.com')
                self.assertIs(expr1=email_address.is_primary, expr2=False)
                self.assertEqual(first=len(mail.outbox), second=1)
                self.assertEqual(first=mail.outbox[0].subject, second={
                    django_settings.SPEEDY_NET_SITE_ID: self._confirm_your_email_address_on_speedy_net_subject_dict_by_gender[self.user.get_gender()],
                    django_settings.SPEEDY_MATCH_SITE_ID: self._confirm_your_email_address_on_speedy_match_subject_dict_by_gender[self.user.get_gender()],
                }[self.site.id])
                self.assertIn(member=email_address.confirmation_token, container=mail.outbox[0].body)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=1,
                )

            def test_first_email_is_primary(self):
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=0,
                )
                self.confirmed_email_address.delete()
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count={"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count={"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=0,
                )
                data = {
                    'email': 'email@example.com',
                }
                r = self.client.post(path='/edit-profile/emails/add/', data=data)
                self.assertRedirects(response=r, expected_url='/edit-profile/emails/', status_code=302, target_status_code=302)
                r = self.client.get(path='/edit-profile/emails/')
                self.assertRedirects(response=r, expected_url='/edit-profile/credentials/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                r = self.client.get(path='/edit-profile/credentials/')
                self.assertEqual(first=r.status_code, second=200)
                email_address = UserEmailAddress.objects.get(email='email@example.com')
                self.assertIs(expr1=email_address.is_primary, expr2=True)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count={"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=1,
                )


        @only_on_sites_with_login
        class AddUserEmailAddressViewAllLanguagesEnglishTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AddUserEmailAddressViewAllLanguagesFrenchTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AddUserEmailAddressViewAllLanguagesGermanTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AddUserEmailAddressViewAllLanguagesSpanishTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AddUserEmailAddressViewAllLanguagesPortugueseTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AddUserEmailAddressViewAllLanguagesItalianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AddUserEmailAddressViewAllLanguagesDutchTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AddUserEmailAddressViewAllLanguagesSwedishTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AddUserEmailAddressViewAllLanguagesKoreanTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AddUserEmailAddressViewAllLanguagesFinnishTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AddUserEmailAddressViewAllLanguagesHebrewTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class SendConfirmationEmailViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            def set_up(self):
                super().set_up()
                self.random_choice = random.choice([1, 2, 3])
                if (self.random_choice == 1):
                    self.user = ActiveUserFactory()
                elif (self.random_choice == 2):
                    self.user = InactiveUserFactory()
                elif (self.random_choice == 3):
                    self.user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
                self.unconfirmed_email_address_url = '/edit-profile/emails/{}/confirm/'.format(self.unconfirmed_email_address.id)
                self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
                self.confirmed_email_address_url = '/edit-profile/emails/{}/confirm/'.format(self.confirmed_email_address.id)
                self.other_user_address = UserEmailAddressFactory()
                self.other_user_address_url = '/edit-profile/emails/{}/confirm/'.format(self.other_user_address.id)
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=3 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=2,
                )

            def test_visitor_has_no_access(self):
                self.client.logout()
                r = self.client.post(path=self.unconfirmed_email_address_url)
                self.assertEqual(first=r.status_code, second=403)

            def test_user_has_no_access_to_other_users_address(self):
                r = self.client.post(path=self.other_user_address_url)
                self.assertEqual(first=r.status_code, second=403)

            def test_user_can_resend_confirmation(self):
                self.assertEqual(first=len(mail.outbox), second=0)
                email_address = UserEmailAddress.objects.get(email=self.unconfirmed_email_address.email)
                r = self.client.post(path=self.unconfirmed_email_address_url)
                self.assertRedirects(response=r, expected_url='/edit-profile/emails/', status_code=302, target_status_code=302)
                r = self.client.get(path='/edit-profile/emails/')
                self.assertRedirects(response=r, expected_url='/edit-profile/credentials/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                r = self.client.get(path='/edit-profile/credentials/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._a_confirmation_message_was_sent_to_email_address_success_message_by_email_address(email_address=self.unconfirmed_email_address.email)])
                self.assertEqual(first=len(mail.outbox), second=1)
                self.assertEqual(first=mail.outbox[0].subject, second={
                    django_settings.SPEEDY_NET_SITE_ID: self._confirm_your_email_address_on_speedy_net_subject_dict_by_gender[self.user.get_gender()],
                    django_settings.SPEEDY_MATCH_SITE_ID: self._confirm_your_email_address_on_speedy_match_subject_dict_by_gender[self.user.get_gender()],
                }[self.site.id])
                self.assertIn(member=email_address.confirmation_token, container=mail.outbox[0].body)


        @only_on_sites_with_login
        class SendConfirmationEmailViewAllLanguagesEnglishTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class SendConfirmationEmailViewAllLanguagesFrenchTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class SendConfirmationEmailViewAllLanguagesGermanTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class SendConfirmationEmailViewAllLanguagesSpanishTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class SendConfirmationEmailViewAllLanguagesPortugueseTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class SendConfirmationEmailViewAllLanguagesItalianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class SendConfirmationEmailViewAllLanguagesDutchTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class SendConfirmationEmailViewAllLanguagesSwedishTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class SendConfirmationEmailViewAllLanguagesKoreanTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class SendConfirmationEmailViewAllLanguagesFinnishTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class SendConfirmationEmailViewAllLanguagesHebrewTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class DeleteUserEmailAddressViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            def set_up(self):
                super().set_up()
                self.random_choice = random.choice([1, 2, 3])
                if (self.random_choice == 1):
                    self.user = ActiveUserFactory()
                elif (self.random_choice == 2):
                    self.user = InactiveUserFactory()
                elif (self.random_choice == 3):
                    self.user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
                self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=False)
                self.confirmed_email_address_url = '/edit-profile/emails/{}/delete/'.format(self.confirmed_email_address.id)
                self.primary_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
                self.primary_address.make_primary()
                self.primary_address_url = '/edit-profile/emails/{}/delete/'.format(self.primary_address.id)
                self.other_user_address = UserEmailAddressFactory(is_primary=False)
                self.other_user_address_url = '/edit-profile/emails/{}/delete/'.format(self.other_user_address.id)
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=4 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=2,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=3 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_unconfirmed_email_addresses_count=1,
                )

            def test_visitor_has_no_access(self):
                self.client.logout()
                r = self.client.post(path=self.confirmed_email_address_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=4 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=2,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=3 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_unconfirmed_email_addresses_count=1,
                )

            def test_user_has_no_access_to_other_users_address(self):
                r = self.client.post(path=self.other_user_address_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=4 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=2,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=3 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_unconfirmed_email_addresses_count=1,
                )

            def test_user_cannot_delete_primary_email_address(self):
                r = self.client.post(path=self.primary_address_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=4 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=2,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=3 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_unconfirmed_email_addresses_count=1,
                )

            def test_user_cannot_delete_only_confirmed_email_address(self):
                for user_email_address in self.user.email_addresses.filter(is_confirmed=True).exclude(pk=self.confirmed_email_address.pk):
                    user_email_address.delete()
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=3,
                    confirmed_email_address_count=1,
                    unconfirmed_email_address_count=2,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=2,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=1,
                )
                r = self.client.post(path=self.confirmed_email_address_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=3,
                    confirmed_email_address_count=1,
                    unconfirmed_email_address_count=2,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=2,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=1,
                )

            def test_user_can_delete_email_address_if_not_only_confirmed_email_address(self):
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    confirmed_email_address_2 = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=False)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    pass
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=4 + {django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 0}[self.site.id] + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=2 + {django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 0}[self.site.id] + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=2,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=3 + {django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 0}[self.site.id] + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=2 + {django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 0}[self.site.id] + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_unconfirmed_email_addresses_count=1,
                )
                r = self.client.post(path=self.confirmed_email_address_url)
                self.assertRedirects(response=r, expected_url='/edit-profile/emails/', status_code=302, target_status_code=302)
                r = self.client.get(path='/edit-profile/emails/')
                self.assertRedirects(response=r, expected_url='/edit-profile/credentials/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                r = self.client.get(path='/edit-profile/credentials/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._the_email_address_was_deleted_success_message])
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=3 + {django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 0}[self.site.id] + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 0}[self.site.id] + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=2,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=2 + {django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 0}[self.site.id] + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1 + {django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 0}[self.site.id] + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_unconfirmed_email_addresses_count=1,
                )

            def test_cannot_delete_user_email_addresses_with_queryset_delete(self):
                with self.assertRaises(NotImplementedError) as cm:
                    self.user.email_addresses.filter(is_confirmed=True).exclude(pk=self.confirmed_email_address.pk).delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    self.user.email_addresses.delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    self.user.email_addresses.all().delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    self.user.email_addresses.filter(is_confirmed=True).delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")


        @only_on_sites_with_login
        class DeleteUserEmailAddressViewAllLanguagesEnglishTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class DeleteUserEmailAddressViewAllLanguagesFrenchTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class DeleteUserEmailAddressViewAllLanguagesGermanTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class DeleteUserEmailAddressViewAllLanguagesSpanishTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class DeleteUserEmailAddressViewAllLanguagesPortugueseTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class DeleteUserEmailAddressViewAllLanguagesItalianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class DeleteUserEmailAddressViewAllLanguagesDutchTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class DeleteUserEmailAddressViewAllLanguagesSwedishTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class DeleteUserEmailAddressViewAllLanguagesKoreanTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class DeleteUserEmailAddressViewAllLanguagesFinnishTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class DeleteUserEmailAddressViewAllLanguagesHebrewTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class SetPrimaryUserEmailAddressViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            def set_up(self):
                super().set_up()
                self.random_choice = random.choice([1, 2, 3])
                if (self.random_choice == 1):
                    self.user = ActiveUserFactory()
                elif (self.random_choice == 2):
                    self.user = InactiveUserFactory()
                elif (self.random_choice == 3):
                    self.user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
                self.unconfirmed_email_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.unconfirmed_email_address.id)
                self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
                self.confirmed_email_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.confirmed_email_address.id)
                self.primary_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
                self.primary_address.make_primary()
                self.primary_address_url = '/edit-profile/emails/{}/delete/'.format(self.primary_address.id)
                self.other_user_address = UserEmailAddressFactory()
                self.other_user_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.other_user_address.id)
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=4 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=2,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=3 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_unconfirmed_email_addresses_count=1,
                )

            def test_visitor_has_no_access(self):
                self.client.logout()
                r = self.client.post(path=self.confirmed_email_address_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=4 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=2,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=3 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_unconfirmed_email_addresses_count=1,
                )

            def test_user_has_no_access_to_other_users_address(self):
                r = self.client.post(path=self.other_user_address_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=4 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=2,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=3 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_unconfirmed_email_addresses_count=1,
                )

            def test_user_cannot_make_unconfirmed_email_address_primary(self):
                r = self.client.post(path=self.unconfirmed_email_address_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=4 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=2,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=3 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_unconfirmed_email_addresses_count=1,
                )

            def test_user_can_make_confirmed_email_address_primary(self):
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=3 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_unconfirmed_email_addresses_count=1,
                )
                self.assertEqual(first=self.user.email_addresses.get(is_primary=True), second=self.primary_address)
                r = self.client.post(path=self.confirmed_email_address_url)
                self.assertRedirects(response=r, expected_url='/edit-profile/emails/', status_code=302, target_status_code=302)
                r = self.client.get(path='/edit-profile/emails/')
                self.assertRedirects(response=r, expected_url='/edit-profile/credentials/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                r = self.client.get(path='/edit-profile/credentials/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._you_have_changed_your_primary_email_address_success_message])
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=4 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=2,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=3 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=2 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_unconfirmed_email_addresses_count=1,
                )
                self.assertEqual(first=self.user.email_addresses.get(is_primary=True), second=self.confirmed_email_address)


        @only_on_sites_with_login
        class SetPrimaryUserEmailAddressViewAllLanguagesEnglishTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class SetPrimaryUserEmailAddressViewAllLanguagesFrenchTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class SetPrimaryUserEmailAddressViewAllLanguagesGermanTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class SetPrimaryUserEmailAddressViewAllLanguagesSpanishTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class SetPrimaryUserEmailAddressViewAllLanguagesPortugueseTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class SetPrimaryUserEmailAddressViewAllLanguagesItalianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class SetPrimaryUserEmailAddressViewAllLanguagesDutchTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class SetPrimaryUserEmailAddressViewAllLanguagesSwedishTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class SetPrimaryUserEmailAddressViewAllLanguagesKoreanTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class SetPrimaryUserEmailAddressViewAllLanguagesFinnishTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class SetPrimaryUserEmailAddressViewAllLanguagesHebrewTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        class PasswordResetViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            def set_up(self):
                super().set_up()
                self.random_choice = random.choice([1, 2, 3])
                if (self.random_choice == 1):
                    self.user = ActiveUserFactory()
                elif (self.random_choice == 2):
                    self.user = InactiveUserFactory()
                elif (self.random_choice == 3):
                    self.user = SpeedyNetInactiveUserFactory()
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
                self.email.make_primary()
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=0,
                )

            def test_visitor_can_open_the_page(self):
                r = self.client.get(path='/reset-password/')
                self.assertEqual(first=r.status_code, second=200)

            def test_visitor_can_reset_password(self):
                self.assertEqual(first=len(mail.outbox), second=0)
                data = {
                    'email': self.email.email,
                }
                r = self.client.post(path='/reset-password/', data=data)
                self.assertRedirects(response=r, expected_url='/reset-password/done/', status_code=302, target_status_code=200)
                self.assertEqual(first=len(mail.outbox), second=1)
                self.assertEqual(first=mail.outbox[0].subject, second={
                    django_settings.SPEEDY_NET_SITE_ID: self._password_reset_on_speedy_net_subject,
                    django_settings.SPEEDY_MATCH_SITE_ID: self._password_reset_on_speedy_match_subject,
                }[self.site.id])

            def test_visitor_cannot_reset_password_if_account_is_deleted_and_doesnt_have_usable_password(self):
                self.user.speedy_net_profile.deactivate()
                self.user.set_unusable_password()
                self.user.save()
                self.user._mark_as_deleted()
                self.user.save()
                self.user.save_user_and_profile()
                self.assertIs(expr1=self.user.is_deleted, expr2=True)
                self.assertIs(expr1=self.user.is_deleted_time is None, expr2=False)
                self.assertEqual(first=self.user.is_active, second=False)
                self.assertEqual(first=self.user.profile.is_active, second=False)
                self.assertEqual(first=self.user.speedy_net_profile.is_active, second=False)
                self.assertEqual(first=self.user.speedy_match_profile.is_active, second=False)
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    confirmed_email_address_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    unconfirmed_email_address_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=self.user,
                    user_email_addresses_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1 + {"1": 1, "2": 0, "3": 1}[str(self.random_choice)],
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assertEqual(first=len(mail.outbox), second=0)
                data = {
                    'email': self.email.email,
                }
                r = self.client.post(path='/reset-password/', data=data)
                self.assertRedirects(response=r, expected_url='/reset-password/done/', status_code=302, target_status_code=200)
                self.assertEqual(first=len(mail.outbox), second=0)


        @only_on_sites_with_login
        class PasswordResetViewAllLanguagesEnglishTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class PasswordResetViewAllLanguagesFrenchTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class PasswordResetViewAllLanguagesGermanTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class PasswordResetViewAllLanguagesSpanishTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class PasswordResetViewAllLanguagesPortugueseTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class PasswordResetViewAllLanguagesItalianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class PasswordResetViewAllLanguagesDutchTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class PasswordResetViewAllLanguagesSwedishTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class PasswordResetViewAllLanguagesKoreanTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class PasswordResetViewAllLanguagesFinnishTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class PasswordResetViewAllLanguagesHebrewTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


