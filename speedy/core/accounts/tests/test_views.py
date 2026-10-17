"""
Test cases for the views of the Speedy Core accounts app: registration, login, logout, editing the profile, site profile activation, user email addresses and password reset.
"""
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
        from speedy.core.accounts.fields import UserAccessField
        from speedy.core.accounts.models import Entity, User, UserEmailAddress


        class RedirectMeMixin(TestCaseMixin):
            """
            Provides assertion helpers for checking where '/me/' redirects a user, based on the active site and the user's activation state.
            """

            def assert_me_url_redirects(self, expected_url):
                """
                Asserts that GET '/me/' redirects to the given expected URL.

                :param expected_url: The URL '/me/' is expected to redirect to.
                """
                r = self.client.get(path='/me/')
                self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200)

            def assert_me_url_redirects_to_login_url(self):
                """
                Asserts that '/me/' redirects to the login page.
                """
                expected_url = '/login/?next=/me/'
                self.assert_me_url_redirects(expected_url=expected_url)

            def assert_me_url_redirects_to_user_profile_url(self, user):
                """
                Asserts that '/me/' redirects to the given user's profile page.

                :param user: The user whose profile page '/me/' is expected to redirect to.
                """
                expected_url = '/{}/'.format(user.slug)
                self.assert_me_url_redirects(expected_url=expected_url)

            def assert_me_url_redirects_to_welcome_url(self):
                """
                Asserts that '/me/' redirects to the welcome page.
                """
                expected_url = '/welcome/'
                self.assert_me_url_redirects(expected_url=expected_url)

            def assert_me_url_redirects_to_registration_step_2_url(self):
                """
                Asserts that '/me/' redirects to the registration step 2 page.
                """
                expected_url = '/registration-step-2/'
                self.assert_me_url_redirects(expected_url=expected_url)

            def assert_me_url_redirects_after_login_by_site_user_and_random_choice(self, user, random_choice):
                """
                Asserts the expected active/profile states of the user, and where '/me/' redirects to, depending on the current site and the given random choice.

                :param user: The logged-in user.
                :param random_choice: The random choice (1, 2 or 3) that determined how the user and his profiles were set up.
                """
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
            """
            Tests the main/index page, for both visitors and registered users (active, inactive, or Speedy Net-inactive), including canonical URL redirects.
            """

            def set_up(self):
                """
                Creates a user in a randomly chosen activation state (active, inactive, or Speedy Net-inactive).
                """
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
                """
                Asserts a visitor opening the main page gets the registration page, served with a 200 status code.
                """
                r = self.client.get(path='/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='main/main_page.html')

            def test_visitor_gets_redirected_to_canonical_url_1(self):
                """
                Asserts that '/?a=1' redirects (301) to the canonical main page URL '/'.
                """
                r = self.client.get(path='/?a=1')
                self.assertRedirects(response=r, expected_url='/', status_code=301, target_status_code=200)

            def test_visitor_gets_redirected_to_canonical_url_2(self):
                """
                Asserts that '/?b=2' redirects (301) to the canonical main page URL '/'.
                """
                r = self.client.get(path='/?b=2')
                self.assertRedirects(response=r, expected_url='/', status_code=301, target_status_code=200)


        @only_on_sites_with_login
        class MeViewOnlyEnglishTestCase(RedirectMeMixin, SpeedyCoreAccountsModelsMixin, SiteTestCase):
            """
            Tests the '/me/' view, for a visitor (who has no access and is redirected to login) and for a logged-in user (who gets redirected to his own profile page).
            """

            def set_up(self):
                """
                Creates an active user with a fixed slug ('markmark').
                """
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
                """
                Asserts a visitor opening '/me/' is redirected to the login page.
                """
                self.assert_me_url_redirects_to_login_url()

            def test_user_gets_redirected_to_his_profile(self):
                """
                Asserts a logged-in user opening '/me/' is redirected to his own profile page.
                """
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_to_user_profile_url(user=self.user)
                # Assert expected_url directly once to confirm.
                self.assert_me_url_redirects(expected_url='/markmark/')


        @only_on_sites_with_login
        class LoginOnlyEnglishTestCase(RedirectMeMixin, SpeedyCoreAccountsModelsMixin, SiteTestCase):
            """
            Tests logging in via '/me/' using a user's slug, username, confirmed email, or unconfirmed email, for a user in a randomly chosen activation state, as well as login failures with wrong credentials.
            """

            def set_up(self):
                """
                Creates a user in a randomly chosen activation state, with a confirmed and an unconfirmed email address.
                """
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
                """
                Asserts where '/me/' redirects to after logging in as the given user, based on the random choice made in set_up.

                :param user: The user that was logged in; must be self.user.
                """
                if (user == self.user):
                    random_choice = self.random_choice
                else:
                    raise NotImplementedError("Invalid user.")
                self.assert_me_url_redirects_after_login_by_site_user_and_random_choice(user=user, random_choice=random_choice)

            def test_user_can_login_with_slug(self):
                """
                Asserts a user can log in using his slug and is redirected as expected afterwards.
                """
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_user_can_login_with_username(self):
                """
                Asserts a user can log in using his username and is redirected as expected afterwards.
                """
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_user_can_login_with_confirmed_email_address(self):
                """
                Asserts a user can log in using his confirmed email address and is redirected as expected afterwards.
                """
                self.client.login(username=self.confirmed_email_address.email, password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_user_can_login_with_unconfirmed_email_address(self):
                """
                Asserts a user can log in using his unconfirmed email address and is redirected as expected afterwards.
                """
                self.client.login(username=self.unconfirmed_email_address.email, password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_user_cannot_login_with_wrong_slug(self):
                """
                Asserts that logging in with a slug that doesn't match any user fails, and '/me/' redirects to the login page.
                """
                self.client.login(username='a{}'.format(self.user.slug), password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_to_login_url()

            def test_user_cannot_login_with_wrong_username(self):
                """
                Asserts that logging in with a username that doesn't match any user fails, and '/me/' redirects to the login page.
                """
                self.client.login(username='a{}'.format(self.user.username), password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_to_login_url()

            def test_user_cannot_login_with_wrong_email(self):
                """
                Asserts that logging in with an email address that doesn't match any user fails, and '/me/' redirects to the login page.
                """
                self.client.login(username='a{}'.format(self.confirmed_email_address.email), password=tests_settings.USER_PASSWORD)
                self.assert_me_url_redirects_to_login_url()

            def test_user_cannot_login_with_incorrect_password(self):
                """
                Asserts that logging in with an incorrect password fails, and '/me/' redirects to the login page.
                """
                self.client.login(username=self.user.slug, password='{}-'.format(tests_settings.USER_PASSWORD))
                self.assert_me_url_redirects_to_login_url()


        class RegistrationViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the registration view: registering, required fields, password validation, duplicate email handling, and the data and models created on successful registration.
            """

            def set_up(self):
                """
                Builds the registration form data (email, slug, password, gender, date of birth) for a new user.
                """
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
                """
                Computes the set of required registration fields (excluding last name), and asserts they're reported as required when missing.
                """
                self.required_fields = self.data.keys() - {to_attribute(name="last_name", language_code=self.language_code)}
                self.assert_registration_form_required_fields(required_fields=self.required_fields)

            def test_visitor_can_see_registration_page(self):
                """
                Asserts the main page is served with the registration page template.
                """
                r = self.client.get(path='/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='main/main_page.html')

            def test_visitor_can_register(self):
                """
                Asserts a visitor can register, and the created entity, user and email address match the submitted data.
                """
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
                """
                Registers a user and asserts the expected number of "New user" log records were emitted.

                :param number_of_records_logged: The expected number of "New user" log records.
                """
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
                """
                Asserts registering with DEBUG=True logs exactly one "New user" record.
                """
                self.run_test_visitor_register_logs_n_records(number_of_records_logged=1)

            @override_settings(LOGGING=tests_settings.OVERRIDE_LOGGING_SETTINGS.LOGGING, DEBUG=True)
            def test_visitor_register_logs_two_records_with_override_settings(self):
                """
                Asserts registering with overridden logging settings and DEBUG=True logs exactly two "New user" records.
                """
                self.run_test_visitor_register_logs_n_records(number_of_records_logged=2)

            def run_test_required_fields(self, data):
                """
                Posts the given (incomplete) data and asserts the expected required-field errors are returned, and no models are created.

                :param data: The form data to post, missing one or more required fields.
                """
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
                """
                Asserts posting an empty dict reports all required fields as missing.
                """
                data = {}
                self.run_test_required_fields(data=data)

            def test_required_fields_2(self):
                """
                Asserts posting empty values for all required fields reports them as missing.
                """
                data = {field_name: '' for field_name in self.required_fields}
                self.run_test_required_fields(data=data)

            def test_non_unique_confirmed_email_address(self):
                """
                Asserts registration fails if the submitted email address is already confirmed by another user, and the existing user and email address are unaffected.
                """
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
                """
                Asserts registration succeeds if another user has a confirmed email address that differs from the one submitted.
                """
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
                """
                Asserts registration fails with an "already in use" error if the submitted email address is unconfirmed by another user and was added less than 5 minutes ago, leaving the other user's email address unaffected.
                """
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
                """
                Asserts registration succeeds and deletes the other user's unconfirmed email address, since it was added 6 minutes ago (more than the 5-minute "still in use" grace period).
                """
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
                """
                Asserts registration succeeds if another user has an unconfirmed email address that differs from the one submitted, leaving that user's email address unaffected.
                """
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
                """
                Asserts registration fails with a "password too short" error when the password is too short.
                """
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
                """
                Asserts registration fails with a "password too long" error when the password is too long.
                """
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
                """
                Asserts registration fails with a "not enough unique characters" error when the password doesn't have enough unique characters.
                """
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
                """
                Asserts registration fails with both "too short" and "not enough unique characters" errors.
                """
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
                """
                Asserts registration fails with both "too long" and "not enough unique characters" errors.
                """
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
                """
                Asserts a user is automatically logged in and redirected correctly right after registration, with the expected active/profile state for both sites.
                """
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

            def test_registration_site_id_and_language_code_are_set_from_http_host(self):
                """
                Asserts a new user gets the SITE_ID and the language code of the HTTP host used to register.
                """
                r = self.client.post(path='/', data=self.data)
                self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=302)
                user = User.objects.get(username=self.username)
                self.assertEqual(first=user.registration_site_id, second=django_settings.SITE_ID)
                self.assertEqual(first=user.registration_language_code, second=self.language_code)
                self.assertEqual(first=user.main_language_code, second=self.language_code)

            def test_user_gets_email_after_registration(self):
                """
                Asserts a confirmation email with the expected subject and confirmation token is sent to a new user after registration, and the token appears only for the current site's host.
                """
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
                """
                Asserts registration fails with a "username already taken" error if the normalized username matches an existing user's, even with a differently formatted slug.
                """
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
                """
                Asserts the registered email address is stored in lowercase, regardless of the case submitted.
                """
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
                """
                Asserts registration fails with an "enter a valid email address" error for an invalid email.
                """
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
                """
                Asserts registration fails for each date of birth in the invalid dates list, reporting the expected error and creating no models.
                """
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
        class RegistrationViewWithLastNameAllMainPlusLanguagesEnglishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (English).
            """

            def set_up(self):
                """
                Sets the first and last name fields in English and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class RegistrationViewWithLastNameAllMainPlusLanguagesFrenchTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (French).
            """

            def set_up(self):
                """
                Sets the first and last name fields in French and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class RegistrationViewWithLastNameAllMainPlusLanguagesGermanTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (German).
            """

            def set_up(self):
                """
                Sets the first and last name fields in German and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class RegistrationViewWithLastNameAllMainPlusLanguagesSpanishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Spanish).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Spanish and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class RegistrationViewWithLastNameAllMainPlusLanguagesPortugueseTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Portuguese).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Portuguese and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class RegistrationViewWithLastNameAllMainPlusLanguagesItalianTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Italian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Italian and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class RegistrationViewWithLastNameAllMainPlusLanguagesDutchTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Dutch).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Dutch and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class RegistrationViewWithLastNameAllMainPlusLanguagesJapaneseTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Japanese).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Japanese and prepares the required fields for this language.
                """
                # Check names in Japanese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ja': "ドロン",
                    'last_name_ja': "マタロン",
                })
                self.first_name = "ドロン"
                self.last_name = "マタロン"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class RegistrationViewWithLastNameAllMainPlusLanguagesRussianTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Russian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Russian and prepares the required fields for this language.
                """
                # Check names in Russian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ru': "Дорон",
                    'last_name_ru': "Маталон",
                })
                self.first_name = "Дорон"
                self.last_name = "Маталон"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class RegistrationViewWithLastNameAllMainPlusLanguagesChineseTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Chinese).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Chinese and prepares the required fields for this language.
                """
                # Check names in Chinese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_zh': "多伦",
                    'last_name_zh': "马塔隆",
                })
                self.first_name = "多伦"
                self.last_name = "马塔隆"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class RegistrationViewWithLastNameAllMainPlusLanguagesPolishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Polish).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Polish and prepares the required fields for this language.
                """
                # Check names in Polish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_pl': "Łukasz",
                    'last_name_pl': "Wójcik",
                })
                self.first_name = "Łukasz"
                self.last_name = "Wójcik"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class RegistrationViewWithLastNameAllMainPlusLanguagesPersianTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Persian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Persian and prepares the required fields for this language.
                """
                # Check names in Persian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fa': "درون",
                    'last_name_fa': "متالون",
                })
                self.first_name = "درون"
                self.last_name = "متالون"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class RegistrationViewWithLastNameAllMainPlusLanguagesHebrewTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Hebrew).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Hebrew and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class RegistrationViewWithLastNameAllMainPlusLanguagesKoreanTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Korean).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Korean and prepares the required fields for this language.
                """
                # Check names in Korean alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ko': "도론",
                    'last_name_ko': "마탈론",
                })
                self.first_name = "도론"
                self.last_name = "마탈론"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class RegistrationViewWithLastNameAllMainPlusLanguagesArabicTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Arabic).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Arabic and prepares the required fields for this language.
                """
                # Check names in Arabic alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ar': "دورون",
                    'last_name_ar': "ماتالون",
                })
                self.first_name = "دورون"
                self.last_name = "ماتالون"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class RegistrationViewWithLastNameAllMainPlusLanguagesIndonesianTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Indonesian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Indonesian and prepares the required fields for this language.
                """
                # Check names in Indonesian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_id': "Doron",
                    'last_name_id': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class RegistrationViewWithLastNameAllMainPlusLanguagesUkrainianTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Ukrainian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Ukrainian and prepares the required fields for this language.
                """
                # Check names in Ukrainian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_uk': "Дорон",
                    'last_name_uk': "Маталон",
                })
                self.first_name = "Дорон"
                self.last_name = "Маталон"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class RegistrationViewWithLastNameAllMainPlusLanguagesTurkishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Turkish).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Turkish and prepares the required fields for this language.
                """
                # Check names in Turkish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_tr': "Doron",
                    'last_name_tr': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class RegistrationViewWithLastNameAllMainPlusLanguagesVietnameseTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Vietnamese).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Vietnamese and prepares the required fields for this language.
                """
                # Check names in Vietnamese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_vi': "Doron",
                    'last_name_vi': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class RegistrationViewWithLastNameAllMainPlusLanguagesCzechTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Czech).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Czech and prepares the required fields for this language.
                """
                # Check names in Czech alphabet.
                super().set_up()
                self.data.update({
                    'first_name_cs': "Doron",
                    'last_name_cs': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class RegistrationViewWithLastNameAllMainPlusLanguagesSwedishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Swedish).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Swedish and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class RegistrationViewWithLastNameAllMainPlusLanguagesFinnishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Finnish).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Finnish and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class RegistrationViewWithLastNameAllMainPlusLanguagesCantoneseTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (with a last name) for all main plus languages (Cantonese).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Cantonese and prepares the required fields for this language.
                """
                # Check names in Cantonese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_zh_yue': "多倫",
                    'last_name_zh_yue': "馬塔倫",
                })
                self.first_name = "多倫"
                self.last_name = "馬塔倫"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesEnglishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (English).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in English and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesFrenchTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (French).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in French and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesGermanTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (German).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in German and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesSpanishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Spanish).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Spanish and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesPortugueseTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Portuguese).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Portuguese and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesItalianTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Italian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Italian and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesDutchTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Dutch).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Dutch and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesJapaneseTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Japanese).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Japanese and prepares the required fields for this language.
                """
                # Check names in Japanese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ja': "ドロン",
                    'last_name_ja': "",
                })
                self.first_name = "ドロン"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesRussianTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Russian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Russian and prepares the required fields for this language.
                """
                # Check names in Russian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ru': "Дорон",
                    'last_name_ru': "",
                })
                self.first_name = "Дорон"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesChineseTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Chinese).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Chinese and prepares the required fields for this language.
                """
                # Check names in Chinese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_zh': "多伦",
                    'last_name_zh': "",
                })
                self.first_name = "多伦"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesPolishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Polish).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Polish and prepares the required fields for this language.
                """
                # Check names in Polish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_pl': "Łukasz",
                    'last_name_pl': "",
                })
                self.first_name = "Łukasz"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesPersianTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Persian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Persian and prepares the required fields for this language.
                """
                # Check names in Persian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fa': "درون",
                    'last_name_fa': "",
                })
                self.first_name = "درون"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesHebrewTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Hebrew).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Hebrew and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesKoreanTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Korean).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Korean and prepares the required fields for this language.
                """
                # Check names in Korean alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ko': "도론",
                    'last_name_ko': "",
                })
                self.first_name = "도론"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesArabicTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Arabic).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Arabic and prepares the required fields for this language.
                """
                # Check names in Arabic alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ar': "دورون",
                    'last_name_ar': "",
                })
                self.first_name = "دورون"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesIndonesianTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Indonesian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Indonesian and prepares the required fields for this language.
                """
                # Check names in Indonesian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_id': "Doron",
                    'last_name_id': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesUkrainianTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Ukrainian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Ukrainian and prepares the required fields for this language.
                """
                # Check names in Ukrainian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_uk': "Дорон",
                    'last_name_uk': "",
                })
                self.first_name = "Дорон"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesTurkishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Turkish).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Turkish and prepares the required fields for this language.
                """
                # Check names in Turkish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_tr': "Doron",
                    'last_name_tr': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesVietnameseTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Vietnamese).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Vietnamese and prepares the required fields for this language.
                """
                # Check names in Vietnamese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_vi': "Doron",
                    'last_name_vi': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesCzechTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Czech).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Czech and prepares the required fields for this language.
                """
                # Check names in Czech alphabet.
                super().set_up()
                self.data.update({
                    'first_name_cs': "Doron",
                    'last_name_cs': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesSwedishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Swedish).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Swedish and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesFinnishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Finnish).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Finnish and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class RegistrationViewWithoutLastNameAllMainPlusLanguagesCantoneseTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
            """
            Tests the registration view (without a last name) for all main plus languages (Cantonese).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Cantonese and prepares the required fields for this language.
                """
                # Check names in Cantonese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_zh_yue': "多倫",
                    'last_name_zh_yue': "",
                })
                self.first_name = "多倫"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        class LoginViewTestCaseMixin(RedirectMeMixin, SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the login view, covering login by slug, username, and email (in various forms and cases), login of users in different activation states, and login failures with incorrect credentials.
            """
            login_url = '/login/'
            _other_user_password = 'abcdef12'

            def set_up(self):
                """
                Creates a user with a dotted slug and email address (in a randomly chosen activation state), another user with a known password (in a randomly chosen activation state), and two further inactive users.
                """
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
                """
                Asserts where '/me/' redirects to after logging in as the given user, based on the random choices made in set_up.

                :param user: The user that was logged in; must be self.user or self.other_user.
                """
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
                """
                Asserts the login page is served with the login template.
                """
                r = self.client.get(path=self.login_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/login.html')

            def test_visitor_can_login_using_slug(self):
                """
                Asserts a user can log in using his normalized slug.
                """
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': self.user.slug,
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_username(self):
                """
                Asserts a user can log in using his username.
                """
                self.assertEqual(first=self.user.username, second='slugwithdots')
                data = {
                    'username': self.user.username,
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_original_slug(self):
                """
                Asserts a user can log in using his original (unnormalized, dotted) slug.
                """
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': 'slug.with.dots',
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_slug_modified(self):
                """
                Asserts a user can log in using a differently formatted (extra dots, underscores and dashes) variant of his slug.
                """
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': 'slug____with.....dots---',
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_slug_uppercase(self):
                """
                Asserts a user can log in using an uppercase variant of his slug.
                """
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': 'SLUG-WITH-DOTS',
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_email(self):
                """
                Asserts a user can log in using his email address.
                """
                data = {
                    'username': self.user_email.email,
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_email_uppercase(self):
                """
                Asserts a user can log in using an uppercase variant of his email address.
                """
                data = {
                    'username': self.user_email.email.upper(),
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.user)

            def test_visitor_can_login_using_other_user_email_and_password(self):
                """
                Asserts another user can log in using his own email address and password.
                """
                data = {
                    'username': self.other_user_email.email,
                    'password': self._other_user_password,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                self.assert_me_url_redirects_after_login(user=self.other_user)

            def test_visitor_can_still_login_if_they_are_not_active_user_1(self):
                """
                Asserts an inactive user can still log in, and gets redirected to the welcome page or the registration step 2 page, depending on settings.
                """
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
                """
                Asserts a Speedy Net-inactive user can still log in, and gets redirected to the welcome page.
                """
                data = {
                    'username': self.inactive_user_2.slug,
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertRedirects(response=r, expected_url='/me/', status_code=302, target_status_code=302)
                # Speedy Net inactive users are redirected to welcome url ('/welcome/') instead of their user profile url.
                self.assert_me_url_redirects_to_welcome_url()

            def test_visitor_can_login_using_email_if_there_are_two_users_returned(self):
                """
                Asserts a user can log in by his email address even when another user's slug happens to match that email address.
                """
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
                """
                Asserts a user whose password was set directly to a too-short value (bypassing validation) can still log in with it.
                """
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
                """
                Asserts a user whose username and password were set directly to too-short values (bypassing validation) can still log in with them.
                """
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
                """
                Asserts login fails using another user's email address together with the wrong password.
                """
                data = {
                    'username': self.other_user_email.email,
                    'password': tests_settings.USER_PASSWORD,
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._please_enter_a_correct_username_and_password_errors_dict())
                self.assert_me_url_redirects_to_login_url()

            def test_visitor_cannot_login_using_incorrect_password_1(self):
                """
                Asserts login fails with an incorrect password.
                """
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
                """
                Asserts login fails with an incorrect password that is also too short.
                """
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
                """
                Asserts login fails with both an incorrect username and an incorrect password.
                """
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
                """
                Asserts login fails with a non-existent username and a too-short password.
                """
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
                """
                Asserts login fails with a too-short, non-existent username and a too-short password.
                """
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
                """
                Asserts login fails with a non-existent username and a too-short password with too few unique characters.
                """
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
                """
                Asserts login fails and reports both username and password as required when neither is submitted.
                """
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {}
                r = self.client.post(path=self.login_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._login_form_all_the_required_fields_are_required_errors_dict())
                self.assert_me_url_redirects_to_login_url()

            def test_visitor_cannot_login_without_username(self):
                """
                Asserts login fails and reports the username as required when it's missing.
                """
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'password': 'wrong password!!',
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._username_is_required_errors_dict())
                self.assert_me_url_redirects_to_login_url()

            def test_visitor_cannot_login_without_password(self):
                """
                Asserts login fails and reports the password as required when it's missing.
                """
                self.assertEqual(first=self.user.slug, second='slug-with-dots')
                data = {
                    'username': 'slug-with-dots',
                }
                r = self.client.post(path=self.login_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_is_required_errors_dict())
                self.assert_me_url_redirects_to_login_url()


        @only_on_sites_with_login
        class LoginViewAllMainLanguagesEnglishTestCase(LoginViewTestCaseMixin, SiteTestCase):
            """
            Tests the login view for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class LoginViewAllMainLanguagesFrenchTestCase(LoginViewTestCaseMixin, SiteTestCase):
            """
            Tests the login view for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class LoginViewAllMainLanguagesGermanTestCase(LoginViewTestCaseMixin, SiteTestCase):
            """
            Tests the login view for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class LoginViewAllMainLanguagesSpanishTestCase(LoginViewTestCaseMixin, SiteTestCase):
            """
            Tests the login view for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class LoginViewAllMainLanguagesPortugueseTestCase(LoginViewTestCaseMixin, SiteTestCase):
            """
            Tests the login view for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class LoginViewAllMainLanguagesItalianTestCase(LoginViewTestCaseMixin, SiteTestCase):
            """
            Tests the login view for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class LoginViewAllMainLanguagesDutchTestCase(LoginViewTestCaseMixin, SiteTestCase):
            """
            Tests the login view for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class LoginViewAllMainLanguagesJapaneseTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class LoginViewAllMainLanguagesRussianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class LoginViewAllMainLanguagesChineseTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class LoginViewAllMainLanguagesPolishTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class LoginViewAllMainLanguagesPersianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class LoginViewAllMainLanguagesHebrewTestCase(LoginViewTestCaseMixin, SiteTestCase):
            """
            Tests the login view for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class LoginViewAllMainLanguagesKoreanTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class LoginViewAllMainLanguagesArabicTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class LoginViewAllMainLanguagesIndonesianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class LoginViewAllMainLanguagesUkrainianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class LoginViewAllMainLanguagesTurkishTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class LoginViewAllMainLanguagesVietnameseTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class LoginViewAllMainLanguagesCzechTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class LoginViewAllMainLanguagesSwedishTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class LoginViewAllMainLanguagesFinnishTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class LoginViewAllMainLanguagesHungarianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class LoginViewAllMainLanguagesThaiTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class LoginViewAllMainLanguagesGreekTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class LoginViewAllMainLanguagesMalayTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class LoginViewAllMainLanguagesSerbianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class LoginViewAllMainLanguagesRomanianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class LoginViewAllMainLanguagesBengaliTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class LoginViewAllMainLanguagesCatalanTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class LoginViewAllMainLanguagesNorwegianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class LoginViewAllMainLanguagesBulgarianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class LoginViewAllMainLanguagesDanishTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class LoginViewAllMainLanguagesSlovakTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class LoginViewAllMainLanguagesHindiTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class LoginViewAllMainLanguagesEstonianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class LoginViewAllMainLanguagesCroatianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class LoginViewAllMainLanguagesAzerbaijaniTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class LoginViewAllMainLanguagesCantoneseTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class LoginViewAllMainLanguagesLithuanianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class LoginViewAllMainLanguagesSlovenianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class LoginViewAllMainLanguagesBasqueTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class LoginViewAllMainLanguagesArmenianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class LoginViewAllMainLanguagesUzbekTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class LoginViewAllMainLanguagesTamilTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class LoginViewAllMainLanguagesLatvianTestCase(LoginViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the login view for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        @only_on_sites_with_login
        class LogoutViewOnlyEnglishTestCase(SpeedyCoreAccountsModelsMixin, SiteTestCase):
            """
            Tests the logout view: logging out a user in various activation states, and that logout requires POST.
            """

            def set_up(self):
                """
                Logs in as a user in a randomly chosen activation state (active, inactive, or Speedy Net-inactive).
                """
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
                """
                Asserts the user's activation state and that the given response redirects accordingly, based on the site and the random choice made in set_up.

                :param r: The HTTP response to check for the expected redirect.
                """
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
                """
                Asserts a logged-in user can log out via POST and becomes anonymous afterwards.
                """
                r = self.client.get(path='/')
                self.assert_user_is_active_and_redirects(r=r)
                r = self.client.post(path='/logout/')
                self.assertEqual(first=r.status_code, second=200)
                r = self.client.get(path='/')
                self.assertIs(expr1=r.context['user'].is_authenticated, expr2=False)

            def test_user_cannot_logout_using_get_method(self):
                """
                Asserts logging out via GET fails with a 405 response and the user remains logged in.
                """
                r = self.client.get(path='/')
                self.assert_user_is_active_and_redirects(r=r)
                r = self.client.get(path='/logout/')
                self.assertEqual(first=r.status_code, second=405)
                r = self.client.get(path='/', follow=True)
                self.assertIs(expr1=hasattr(r, 'redirect_chain'), expr2=True)
                self.assertIs(expr1=r.context['user'].is_authenticated, expr2=True)


        class EditProfileViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the edit profile view: access rules, saving settings (name, slug, gender), required fields, slug/username change rules, and date of birth change limits.
            """
            page_url = '/edit-profile/'

            def set_up(self):
                """
                Creates a user in a randomly chosen activation state, logs in as that user, and prepares the base form data (date of birth, slug, gender) for the tests.
                """
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
                """
                Computes the set of required form fields (excluding the last name, which is optional) and asserts they are reported as required when missing.
                """
                self.required_fields = self.data.keys() - {to_attribute(name="last_name", language_code=self.language_code)}
                self.assert_profile_form_required_fields(required_fields=self.required_fields)

            def test_visitor_has_no_access(self):
                """
                Asserts a logged-out visitor is redirected to the login page.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_active_user_can_open_the_page(self):
                """
                Asserts an active user can open the edit profile page.
                """
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/profile.html')

            def test_inactive_user_can_open_the_page(self):
                """
                Asserts an inactive user, and a Speedy Net-inactive user, can both open the edit profile page.
                """
                self.user.profile.deactivate()
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/profile.html')
                self.user.speedy_net_profile.deactivate()
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/profile.html')

            def test_active_user_can_save_his_settings(self):
                """
                Asserts an active user can save his settings, and the name is updated for the test's language code while other per-language name fields are unchanged.
                """
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
                self.assertEqual(first=user.first_name_ja, second={'ja': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ja') else '__'])
                self.assertEqual(first=user.first_name_ru, second={'ru': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ru') else '__'])
                self.assertEqual(first=user.first_name_zh, second={'zh': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'zh') else '__'])
                self.assertEqual(first=user.first_name_pl, second={'pl': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'pl') else '__'])
                self.assertEqual(first=user.first_name_fa, second={'fa': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'fa') else '__'])
                self.assertEqual(first=user.first_name_he, second={'he': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'he') else '__'])
                self.assertEqual(first=user.first_name_ko, second={'ko': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ko') else '__'])
                self.assertEqual(first=user.first_name_ar, second={'ar': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ar') else '__'])
                self.assertEqual(first=user.first_name_id, second={'id': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'id') else '__'])
                self.assertEqual(first=user.first_name_uk, second={'uk': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'uk') else '__'])
                self.assertEqual(first=user.first_name_tr, second={'tr': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'tr') else '__'])
                self.assertEqual(first=user.first_name_vi, second={'vi': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'vi') else '__'])
                self.assertEqual(first=user.first_name_cs, second={'cs': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'cs') else '__'])
                self.assertEqual(first=user.first_name_sv, second={'sv': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'sv') else '__'])
                self.assertEqual(first=user.first_name_fi, second={'fi': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'fi') else '__'])
                self.assertEqual(first=user.first_name_hu, second={'hu': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'hu') else '__'])
                self.assertEqual(first=user.first_name_th, second={'th': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'th') else '__'])
                self.assertEqual(first=user.first_name_el, second={'el': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'el') else '__'])
                self.assertEqual(first=user.first_name_ms, second={'ms': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ms') else '__'])
                self.assertEqual(first=user.first_name_sr, second={'sr': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'sr') else '__'])
                self.assertEqual(first=user.first_name_ro, second={'ro': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ro') else '__'])
                self.assertEqual(first=user.first_name_bn, second={'bn': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'bn') else '__'])
                self.assertEqual(first=user.first_name_ca, second={'ca': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ca') else '__'])
                self.assertEqual(first=user.first_name_no, second={'no': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'no') else '__'])
                self.assertEqual(first=user.first_name_bg, second={'bg': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'bg') else '__'])
                self.assertEqual(first=user.first_name_da, second={'da': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'da') else '__'])
                self.assertEqual(first=user.first_name_sk, second={'sk': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'sk') else '__'])
                self.assertEqual(first=user.first_name_hi, second={'hi': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'hi') else '__'])
                self.assertEqual(first=user.first_name_et, second={'et': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'et') else '__'])
                self.assertEqual(first=user.first_name_hr, second={'hr': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'hr') else '__'])
                self.assertEqual(first=user.first_name_az, second={'az': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'az') else '__'])
                self.assertEqual(first=user.first_name_zh_yue, second={'zh-yue': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'zh-yue') else '__'])
                self.assertEqual(first=user.first_name_lt, second={'lt': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'lt') else '__'])
                self.assertEqual(first=user.first_name_sl, second={'sl': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'sl') else '__'])
                self.assertEqual(first=user.first_name_eu, second={'eu': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'eu') else '__'])
                self.assertEqual(first=user.first_name_hy, second={'hy': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'hy') else '__'])
                self.assertEqual(first=user.first_name_uz, second={'uz': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'uz') else '__'])
                self.assertEqual(first=user.first_name_ta, second={'ta': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ta') else '__'])
                self.assertEqual(first=user.first_name_lv, second={'lv': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'lv') else '__'])
                self.assertEqual(first=user.last_name, second=self.last_name)
                self.assertEqual(first=user.last_name_en, second={'en': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'en') else '__'])
                self.assertEqual(first=user.last_name_fr, second={'fr': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'fr') else '__'])
                self.assertEqual(first=user.last_name_de, second={'de': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'de') else '__'])
                self.assertEqual(first=user.last_name_es, second={'es': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'es') else '__'])
                self.assertEqual(first=user.last_name_pt, second={'pt': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'pt') else '__'])
                self.assertEqual(first=user.last_name_it, second={'it': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'it') else '__'])
                self.assertEqual(first=user.last_name_nl, second={'nl': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'nl') else '__'])
                self.assertEqual(first=user.last_name_ja, second={'ja': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ja') else '__'])
                self.assertEqual(first=user.last_name_ru, second={'ru': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ru') else '__'])
                self.assertEqual(first=user.last_name_zh, second={'zh': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'zh') else '__'])
                self.assertEqual(first=user.last_name_pl, second={'pl': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'pl') else '__'])
                self.assertEqual(first=user.last_name_fa, second={'fa': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'fa') else '__'])
                self.assertEqual(first=user.last_name_he, second={'he': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'he') else '__'])
                self.assertEqual(first=user.last_name_ko, second={'ko': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ko') else '__'])
                self.assertEqual(first=user.last_name_ar, second={'ar': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ar') else '__'])
                self.assertEqual(first=user.last_name_id, second={'id': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'id') else '__'])
                self.assertEqual(first=user.last_name_uk, second={'uk': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'uk') else '__'])
                self.assertEqual(first=user.last_name_tr, second={'tr': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'tr') else '__'])
                self.assertEqual(first=user.last_name_vi, second={'vi': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'vi') else '__'])
                self.assertEqual(first=user.last_name_cs, second={'cs': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'cs') else '__'])
                self.assertEqual(first=user.last_name_sv, second={'sv': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'sv') else '__'])
                self.assertEqual(first=user.last_name_fi, second={'fi': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'fi') else '__'])
                self.assertEqual(first=user.last_name_hu, second={'hu': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'hu') else '__'])
                self.assertEqual(first=user.last_name_th, second={'th': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'th') else '__'])
                self.assertEqual(first=user.last_name_el, second={'el': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'el') else '__'])
                self.assertEqual(first=user.last_name_ms, second={'ms': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ms') else '__'])
                self.assertEqual(first=user.last_name_sr, second={'sr': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'sr') else '__'])
                self.assertEqual(first=user.last_name_ro, second={'ro': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ro') else '__'])
                self.assertEqual(first=user.last_name_bn, second={'bn': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'bn') else '__'])
                self.assertEqual(first=user.last_name_ca, second={'ca': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ca') else '__'])
                self.assertEqual(first=user.last_name_no, second={'no': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'no') else '__'])
                self.assertEqual(first=user.last_name_bg, second={'bg': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'bg') else '__'])
                self.assertEqual(first=user.last_name_da, second={'da': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'da') else '__'])
                self.assertEqual(first=user.last_name_sk, second={'sk': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'sk') else '__'])
                self.assertEqual(first=user.last_name_hi, second={'hi': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'hi') else '__'])
                self.assertEqual(first=user.last_name_et, second={'et': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'et') else '__'])
                self.assertEqual(first=user.last_name_hr, second={'hr': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'hr') else '__'])
                self.assertEqual(first=user.last_name_az, second={'az': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'az') else '__'])
                self.assertEqual(first=user.last_name_zh_yue, second={'zh-yue': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'zh-yue') else '__'])
                self.assertEqual(first=user.last_name_lt, second={'lt': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'lt') else '__'])
                self.assertEqual(first=user.last_name_sl, second={'sl': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'sl') else '__'])
                self.assertEqual(first=user.last_name_eu, second={'eu': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'eu') else '__'])
                self.assertEqual(first=user.last_name_hy, second={'hy': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'hy') else '__'])
                self.assertEqual(first=user.last_name_uz, second={'uz': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'uz') else '__'])
                self.assertEqual(first=user.last_name_ta, second={'ta': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ta') else '__'])
                self.assertEqual(first=user.last_name_lv, second={'lv': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'lv') else '__'])
                for (key, value) in self.data.items():
                    if (not (key in ['date_of_birth'])):
                        self.assertEqual(first=getattr(user, key), second=value)
                self.assertEqual(first=user.date_of_birth, second=date(year=1976, month=6, day=3))

            def test_inactive_user_can_save_his_settings(self):
                """
                Asserts an inactive user can save his settings.
                """
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
                """
                Posts the given data and asserts all required fields are reported as missing, and the user's name is left unchanged.

                :param data: The form data to submit, expected to be missing required fields.
                """
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._profile_form_all_the_required_fields_are_required_errors_dict())
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.first_name, second=self.original_first_name)
                self.assertEqual(first=user.last_name, second=self.original_last_name)
                self.assert_user_first_and_last_name_in_all_languages(user=user)

            def test_required_fields_1(self):
                """
                Asserts all required fields are reported as required when the form is submitted empty.
                """
                data = {}
                self.run_test_required_fields(data=data)

            def test_required_fields_2(self):
                """
                Asserts all required fields are reported as required when submitted as empty strings.
                """
                data = {field_name: '' for field_name in self.required_fields}
                self.run_test_required_fields(data=data)

            def run_test_user_can_change_his_slug(self, new_slug):
                """
                Asserts the user can change his slug to the given new slug (normalized), and the slug is updated.

                :param new_slug: The new slug to submit, which must normalize to a value different from the user's current slug.
                """
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
                """
                Asserts the given new slug normalizes to the expected value, then asserts the user can change his slug to it.

                :param new_slug: The new, unnormalized slug to submit.
                :param new_slug_normalized: The expected normalized form of new_slug.
                """
                self.assertNotEqual(first=normalize_slug(slug=new_slug), second=new_slug)
                self.assertEqual(first=normalize_slug(slug=new_slug), second=new_slug_normalized)
                self.run_test_user_can_change_his_slug(new_slug=new_slug)

            def test_user_can_change_his_slug(self):
                """
                Asserts the user can change his slug to another already-normalized slug.
                """
                new_slug = '{}-{}-{}'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                self.assertEqual(first=normalize_slug(slug=new_slug), second=new_slug)
                self.run_test_user_can_change_his_slug(new_slug=new_slug)

            def test_user_can_change_his_slug_with_normalize_slug_1(self):
                """
                Asserts the user can change his slug to a slug containing dots and double dashes that gets normalized.
                """
                new_slug = '{}.{}--{}'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                new_slug_normalized = '{}-{}-{}'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                self.run_test_user_can_change_his_slug_with_normalize_slug(new_slug=new_slug, new_slug_normalized=new_slug_normalized)

            def test_user_can_change_his_slug_with_normalize_slug_2(self):
                """
                Asserts the user can change his slug to a slug containing many special characters that gets normalized.
                """
                new_slug = '==-{}\\@!!#@#&^&*()({}=*&^%$)(\\/={}---'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                new_slug_normalized = '{}-{}-{}'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                self.run_test_user_can_change_his_slug_with_normalize_slug(new_slug=new_slug, new_slug_normalized=new_slug_normalized)

            def run_test_user_cannot_change_his_username(self, new_slug):
                """
                Asserts the user cannot change his slug when the new slug would change his username, and nothing is modified.

                :param new_slug: The new slug to submit, which normalizes to a username different from the user's current username.
                """
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
                """
                Asserts the given new slug normalizes to the expected value, then asserts the user cannot change his username using it.

                :param new_slug: The new, unnormalized slug to submit.
                :param new_slug_normalized: The expected normalized form of new_slug.
                """
                self.assertNotEqual(first=normalize_slug(slug=new_slug), second=new_slug)
                self.assertEqual(first=normalize_slug(slug=new_slug), second=new_slug_normalized)
                self.run_test_user_cannot_change_his_username(new_slug=new_slug)

            def test_user_cannot_change_his_username_1(self):
                """
                Asserts the user cannot change his username by prefixing an extra character to his slug.
                """
                new_slug = 'a{}'.format(self.user.slug)
                self.assertEqual(first=normalize_slug(slug=new_slug), second=new_slug)
                self.run_test_user_cannot_change_his_username(new_slug=new_slug)

            def test_user_cannot_change_his_username_2(self):
                """
                Asserts the user cannot change his username by inserting an extra digit into his slug.
                """
                new_slug = '{}-{}-1-{}'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                self.assertEqual(first=normalize_slug(slug=new_slug), second=new_slug)
                self.run_test_user_cannot_change_his_username(new_slug=new_slug)

            def test_user_cannot_change_his_username_with_normalize_slug(self):
                """
                Asserts the user cannot change his username even when the new slug is normalized from one containing many special characters.
                """
                new_slug = '==-{}\\@!!#@#&^&*()({}=*&^%$1)(\\/={}---'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                new_slug_normalized = '{}-{}-1-{}'.format(self.user.slug[0:4], self.user.slug[4:8], self.user.slug[8:12])
                self.run_test_user_cannot_change_his_username_with_normalize_slug(new_slug=new_slug, new_slug_normalized=new_slug_normalized)

            def test_valid_date_of_birth_list_ok(self):
                """
                Asserts every valid date of birth in the test settings list is accepted and saved correctly, along with the name in all languages.
                """
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
                    self.assertEqual(first=user.first_name_ja, second={'ja': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ja') else '__'])
                    self.assertEqual(first=user.first_name_ru, second={'ru': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ru') else '__'])
                    self.assertEqual(first=user.first_name_zh, second={'zh': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'zh') else '__'])
                    self.assertEqual(first=user.first_name_pl, second={'pl': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'pl') else '__'])
                    self.assertEqual(first=user.first_name_fa, second={'fa': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'fa') else '__'])
                    self.assertEqual(first=user.first_name_he, second={'he': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'he') else '__'])
                    self.assertEqual(first=user.first_name_ko, second={'ko': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ko') else '__'])
                    self.assertEqual(first=user.first_name_ar, second={'ar': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ar') else '__'])
                    self.assertEqual(first=user.first_name_id, second={'id': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'id') else '__'])
                    self.assertEqual(first=user.first_name_uk, second={'uk': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'uk') else '__'])
                    self.assertEqual(first=user.first_name_tr, second={'tr': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'tr') else '__'])
                    self.assertEqual(first=user.first_name_vi, second={'vi': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'vi') else '__'])
                    self.assertEqual(first=user.first_name_cs, second={'cs': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'cs') else '__'])
                    self.assertEqual(first=user.first_name_sv, second={'sv': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'sv') else '__'])
                    self.assertEqual(first=user.first_name_fi, second={'fi': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'fi') else '__'])
                    self.assertEqual(first=user.first_name_hu, second={'hu': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'hu') else '__'])
                    self.assertEqual(first=user.first_name_th, second={'th': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'th') else '__'])
                    self.assertEqual(first=user.first_name_el, second={'el': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'el') else '__'])
                    self.assertEqual(first=user.first_name_ms, second={'ms': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ms') else '__'])
                    self.assertEqual(first=user.first_name_sr, second={'sr': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'sr') else '__'])
                    self.assertEqual(first=user.first_name_ro, second={'ro': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ro') else '__'])
                    self.assertEqual(first=user.first_name_bn, second={'bn': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'bn') else '__'])
                    self.assertEqual(first=user.first_name_ca, second={'ca': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ca') else '__'])
                    self.assertEqual(first=user.first_name_no, second={'no': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'no') else '__'])
                    self.assertEqual(first=user.first_name_bg, second={'bg': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'bg') else '__'])
                    self.assertEqual(first=user.first_name_da, second={'da': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'da') else '__'])
                    self.assertEqual(first=user.first_name_sk, second={'sk': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'sk') else '__'])
                    self.assertEqual(first=user.first_name_hi, second={'hi': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'hi') else '__'])
                    self.assertEqual(first=user.first_name_et, second={'et': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'et') else '__'])
                    self.assertEqual(first=user.first_name_hr, second={'hr': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'hr') else '__'])
                    self.assertEqual(first=user.first_name_az, second={'az': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'az') else '__'])
                    self.assertEqual(first=user.first_name_zh_yue, second={'zh-yue': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'zh-yue') else '__'])
                    self.assertEqual(first=user.first_name_lt, second={'lt': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'lt') else '__'])
                    self.assertEqual(first=user.first_name_sl, second={'sl': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'sl') else '__'])
                    self.assertEqual(first=user.first_name_eu, second={'eu': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'eu') else '__'])
                    self.assertEqual(first=user.first_name_hy, second={'hy': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'hy') else '__'])
                    self.assertEqual(first=user.first_name_uz, second={'uz': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'uz') else '__'])
                    self.assertEqual(first=user.first_name_ta, second={'ta': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'ta') else '__'])
                    self.assertEqual(first=user.first_name_lv, second={'lv': self.first_name, '__': self.original_first_name}[self.language_code if (self.language_code == 'lv') else '__'])
                    self.assertEqual(first=user.last_name, second=self.last_name)
                    self.assertEqual(first=user.last_name_en, second={'en': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'en') else '__'])
                    self.assertEqual(first=user.last_name_fr, second={'fr': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'fr') else '__'])
                    self.assertEqual(first=user.last_name_de, second={'de': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'de') else '__'])
                    self.assertEqual(first=user.last_name_es, second={'es': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'es') else '__'])
                    self.assertEqual(first=user.last_name_pt, second={'pt': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'pt') else '__'])
                    self.assertEqual(first=user.last_name_it, second={'it': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'it') else '__'])
                    self.assertEqual(first=user.last_name_nl, second={'nl': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'nl') else '__'])
                    self.assertEqual(first=user.last_name_ja, second={'ja': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ja') else '__'])
                    self.assertEqual(first=user.last_name_ru, second={'ru': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ru') else '__'])
                    self.assertEqual(first=user.last_name_zh, second={'zh': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'zh') else '__'])
                    self.assertEqual(first=user.last_name_pl, second={'pl': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'pl') else '__'])
                    self.assertEqual(first=user.last_name_fa, second={'fa': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'fa') else '__'])
                    self.assertEqual(first=user.last_name_he, second={'he': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'he') else '__'])
                    self.assertEqual(first=user.last_name_ko, second={'ko': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ko') else '__'])
                    self.assertEqual(first=user.last_name_ar, second={'ar': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ar') else '__'])
                    self.assertEqual(first=user.last_name_id, second={'id': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'id') else '__'])
                    self.assertEqual(first=user.last_name_uk, second={'uk': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'uk') else '__'])
                    self.assertEqual(first=user.last_name_tr, second={'tr': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'tr') else '__'])
                    self.assertEqual(first=user.last_name_vi, second={'vi': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'vi') else '__'])
                    self.assertEqual(first=user.last_name_cs, second={'cs': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'cs') else '__'])
                    self.assertEqual(first=user.last_name_sv, second={'sv': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'sv') else '__'])
                    self.assertEqual(first=user.last_name_fi, second={'fi': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'fi') else '__'])
                    self.assertEqual(first=user.last_name_hu, second={'hu': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'hu') else '__'])
                    self.assertEqual(first=user.last_name_th, second={'th': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'th') else '__'])
                    self.assertEqual(first=user.last_name_el, second={'el': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'el') else '__'])
                    self.assertEqual(first=user.last_name_ms, second={'ms': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ms') else '__'])
                    self.assertEqual(first=user.last_name_sr, second={'sr': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'sr') else '__'])
                    self.assertEqual(first=user.last_name_ro, second={'ro': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ro') else '__'])
                    self.assertEqual(first=user.last_name_bn, second={'bn': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'bn') else '__'])
                    self.assertEqual(first=user.last_name_ca, second={'ca': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ca') else '__'])
                    self.assertEqual(first=user.last_name_no, second={'no': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'no') else '__'])
                    self.assertEqual(first=user.last_name_bg, second={'bg': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'bg') else '__'])
                    self.assertEqual(first=user.last_name_da, second={'da': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'da') else '__'])
                    self.assertEqual(first=user.last_name_sk, second={'sk': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'sk') else '__'])
                    self.assertEqual(first=user.last_name_hi, second={'hi': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'hi') else '__'])
                    self.assertEqual(first=user.last_name_et, second={'et': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'et') else '__'])
                    self.assertEqual(first=user.last_name_hr, second={'hr': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'hr') else '__'])
                    self.assertEqual(first=user.last_name_az, second={'az': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'az') else '__'])
                    self.assertEqual(first=user.last_name_zh_yue, second={'zh-yue': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'zh-yue') else '__'])
                    self.assertEqual(first=user.last_name_lt, second={'lt': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'lt') else '__'])
                    self.assertEqual(first=user.last_name_sl, second={'sl': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'sl') else '__'])
                    self.assertEqual(first=user.last_name_eu, second={'eu': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'eu') else '__'])
                    self.assertEqual(first=user.last_name_hy, second={'hy': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'hy') else '__'])
                    self.assertEqual(first=user.last_name_uz, second={'uz': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'uz') else '__'])
                    self.assertEqual(first=user.last_name_ta, second={'ta': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'ta') else '__'])
                    self.assertEqual(first=user.last_name_lv, second={'lv': self.last_name, '__': self.original_last_name}[self.language_code if (self.language_code == 'lv') else '__'])
                    for (key, value) in self.data.items():
                        if (not (key in ['date_of_birth'])):
                            self.assertEqual(first=getattr(user, key), second=value)
                    self.assertEqual(first=user.date_of_birth, second=datetime.strptime(date_of_birth, '%Y-%m-%d').date())

            def test_change_date_of_birth_12_times(self):
                """
                Asserts a user without unlimited date-of-birth changes allowed can change it normally up to the 11th time, and the 12th change blocks Speedy Match, invalidates his password, and logs him out.
                """
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
                """
                Asserts a user allowed to change his date of birth unlimited times can do so repeatedly without being blocked from Speedy Match or losing his password.
                """
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
                """
                Asserts every invalid date of birth in the test settings list is rejected with the expected errors and the date of birth is left unchanged.
                """
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
        class EditProfileViewWithLastNameAllMainLanguagesEnglishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (with a last name) for all main languages (English).
            """

            def set_up(self):
                """
                Sets the first and last name fields in English and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class EditProfileViewWithLastNameAllMainLanguagesFrenchTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (with a last name) for all main languages (French).
            """

            def set_up(self):
                """
                Sets the first and last name fields in French and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class EditProfileViewWithLastNameAllMainLanguagesGermanTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (with a last name) for all main languages (German).
            """

            def set_up(self):
                """
                Sets the first and last name fields in German and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class EditProfileViewWithLastNameAllMainLanguagesSpanishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (with a last name) for all main languages (Spanish).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Spanish and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class EditProfileViewWithLastNameAllMainLanguagesPortugueseTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (with a last name) for all main languages (Portuguese).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Portuguese and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class EditProfileViewWithLastNameAllMainLanguagesItalianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (with a last name) for all main languages (Italian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Italian and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class EditProfileViewWithLastNameAllMainLanguagesDutchTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (with a last name) for all main languages (Dutch).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Dutch and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class EditProfileViewWithLastNameAllMainLanguagesJapaneseTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Japanese).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Japanese and prepares the required fields for this language.
                """
                # Check names in Japanese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class EditProfileViewWithLastNameAllMainLanguagesRussianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Russian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Russian and prepares the required fields for this language.
                """
                # Check names in Russian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class EditProfileViewWithLastNameAllMainLanguagesChineseTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Chinese).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Chinese and prepares the required fields for this language.
                """
                # Check names in Chinese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class EditProfileViewWithLastNameAllMainLanguagesPolishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Polish).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Polish and prepares the required fields for this language.
                """
                # Check names in Polish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class EditProfileViewWithLastNameAllMainLanguagesPersianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Persian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Persian and prepares the required fields for this language.
                """
                # Check names in Persian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class EditProfileViewWithLastNameAllMainLanguagesHebrewTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (with a last name) for all main languages (Hebrew).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Hebrew and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class EditProfileViewWithLastNameAllMainLanguagesKoreanTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Korean).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Korean and prepares the required fields for this language.
                """
                # Check names in Korean alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class EditProfileViewWithLastNameAllMainLanguagesArabicTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Arabic).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Arabic and prepares the required fields for this language.
                """
                # Check names in Arabic alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class EditProfileViewWithLastNameAllMainLanguagesIndonesianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Indonesian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Indonesian and prepares the required fields for this language.
                """
                # Check names in Indonesian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class EditProfileViewWithLastNameAllMainLanguagesUkrainianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Ukrainian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Ukrainian and prepares the required fields for this language.
                """
                # Check names in Ukrainian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class EditProfileViewWithLastNameAllMainLanguagesTurkishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Turkish).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Turkish and prepares the required fields for this language.
                """
                # Check names in Turkish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class EditProfileViewWithLastNameAllMainLanguagesVietnameseTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Vietnamese).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Vietnamese and prepares the required fields for this language.
                """
                # Check names in Vietnamese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class EditProfileViewWithLastNameAllMainLanguagesCzechTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Czech).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Czech and prepares the required fields for this language.
                """
                # Check names in Czech alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class EditProfileViewWithLastNameAllMainLanguagesSwedishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Swedish).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Swedish and prepares the required fields for this language.
                """
                # Check names in Swedish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class EditProfileViewWithLastNameAllMainLanguagesFinnishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Finnish).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Finnish and prepares the required fields for this language.
                """
                # Check names in Finnish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class EditProfileViewWithLastNameAllMainLanguagesHungarianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Hungarian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Hungarian and prepares the required fields for this language.
                """
                # Check names in Hungarian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class EditProfileViewWithLastNameAllMainLanguagesThaiTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Thai).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Thai and prepares the required fields for this language.
                """
                # Check names in Thai alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class EditProfileViewWithLastNameAllMainLanguagesGreekTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Greek).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Greek and prepares the required fields for this language.
                """
                # Check names in Greek alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class EditProfileViewWithLastNameAllMainLanguagesMalayTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Malay).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Malay and prepares the required fields for this language.
                """
                # Check names in Malay alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class EditProfileViewWithLastNameAllMainLanguagesSerbianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Serbian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Serbian and prepares the required fields for this language.
                """
                # Check names in Serbian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class EditProfileViewWithLastNameAllMainLanguagesRomanianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Romanian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Romanian and prepares the required fields for this language.
                """
                # Check names in Romanian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class EditProfileViewWithLastNameAllMainLanguagesBengaliTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Bengali).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Bengali and prepares the required fields for this language.
                """
                # Check names in Bengali alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class EditProfileViewWithLastNameAllMainLanguagesCatalanTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Catalan).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Catalan and prepares the required fields for this language.
                """
                # Check names in Catalan alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class EditProfileViewWithLastNameAllMainLanguagesNorwegianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Norwegian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Norwegian and prepares the required fields for this language.
                """
                # Check names in Norwegian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class EditProfileViewWithLastNameAllMainLanguagesBulgarianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Bulgarian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Bulgarian and prepares the required fields for this language.
                """
                # Check names in Bulgarian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class EditProfileViewWithLastNameAllMainLanguagesDanishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Danish).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Danish and prepares the required fields for this language.
                """
                # Check names in Danish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class EditProfileViewWithLastNameAllMainLanguagesSlovakTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Slovak).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Slovak and prepares the required fields for this language.
                """
                # Check names in Slovak alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class EditProfileViewWithLastNameAllMainLanguagesHindiTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Hindi).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Hindi and prepares the required fields for this language.
                """
                # Check names in Hindi alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class EditProfileViewWithLastNameAllMainLanguagesEstonianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Estonian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Estonian and prepares the required fields for this language.
                """
                # Check names in Estonian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class EditProfileViewWithLastNameAllMainLanguagesCroatianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Croatian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Croatian and prepares the required fields for this language.
                """
                # Check names in Croatian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class EditProfileViewWithLastNameAllMainLanguagesAzerbaijaniTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Azerbaijani).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Azerbaijani and prepares the required fields for this language.
                """
                # Check names in Azerbaijani alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class EditProfileViewWithLastNameAllMainLanguagesCantoneseTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Cantonese).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Cantonese and prepares the required fields for this language.
                """
                # Check names in Cantonese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class EditProfileViewWithLastNameAllMainLanguagesLithuanianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Lithuanian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Lithuanian and prepares the required fields for this language.
                """
                # Check names in Lithuanian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class EditProfileViewWithLastNameAllMainLanguagesSlovenianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Slovenian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Slovenian and prepares the required fields for this language.
                """
                # Check names in Slovenian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class EditProfileViewWithLastNameAllMainLanguagesBasqueTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Basque).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Basque and prepares the required fields for this language.
                """
                # Check names in Basque alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class EditProfileViewWithLastNameAllMainLanguagesArmenianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Armenian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Armenian and prepares the required fields for this language.
                """
                # Check names in Armenian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class EditProfileViewWithLastNameAllMainLanguagesUzbekTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Uzbek).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Uzbek and prepares the required fields for this language.
                """
                # Check names in Uzbek alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class EditProfileViewWithLastNameAllMainLanguagesTamilTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Tamil).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Tamil and prepares the required fields for this language.
                """
                # Check names in Tamil alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class EditProfileViewWithLastNameAllMainLanguagesLatvianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (with a last name) for all main languages (Latvian).
            """

            def set_up(self):
                """
                Sets the first and last name fields in Latvian and prepares the required fields for this language.
                """
                # Check names in Latvian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        @only_on_sites_with_login
        class EditProfileViewWithoutLastNameAllMainLanguagesEnglishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (without a last name) for all main languages (English).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in English and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class EditProfileViewWithoutLastNameAllMainLanguagesFrenchTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (without a last name) for all main languages (French).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in French and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class EditProfileViewWithoutLastNameAllMainLanguagesGermanTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (without a last name) for all main languages (German).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in German and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class EditProfileViewWithoutLastNameAllMainLanguagesSpanishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (without a last name) for all main languages (Spanish).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Spanish and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class EditProfileViewWithoutLastNameAllMainLanguagesPortugueseTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (without a last name) for all main languages (Portuguese).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Portuguese and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class EditProfileViewWithoutLastNameAllMainLanguagesItalianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (without a last name) for all main languages (Italian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Italian and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class EditProfileViewWithoutLastNameAllMainLanguagesDutchTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (without a last name) for all main languages (Dutch).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Dutch and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class EditProfileViewWithoutLastNameAllMainLanguagesJapaneseTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Japanese).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Japanese and prepares the required fields for this language.
                """
                # Check names in Japanese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class EditProfileViewWithoutLastNameAllMainLanguagesRussianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Russian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Russian and prepares the required fields for this language.
                """
                # Check names in Russian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class EditProfileViewWithoutLastNameAllMainLanguagesChineseTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Chinese).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Chinese and prepares the required fields for this language.
                """
                # Check names in Chinese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class EditProfileViewWithoutLastNameAllMainLanguagesPolishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Polish).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Polish and prepares the required fields for this language.
                """
                # Check names in Polish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class EditProfileViewWithoutLastNameAllMainLanguagesPersianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Persian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Persian and prepares the required fields for this language.
                """
                # Check names in Persian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class EditProfileViewWithoutLastNameAllMainLanguagesHebrewTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile view (without a last name) for all main languages (Hebrew).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Hebrew and prepares the required fields for this language.
                """
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
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class EditProfileViewWithoutLastNameAllMainLanguagesKoreanTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Korean).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Korean and prepares the required fields for this language.
                """
                # Check names in Korean alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class EditProfileViewWithoutLastNameAllMainLanguagesArabicTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Arabic).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Arabic and prepares the required fields for this language.
                """
                # Check names in Arabic alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class EditProfileViewWithoutLastNameAllMainLanguagesIndonesianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Indonesian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Indonesian and prepares the required fields for this language.
                """
                # Check names in Indonesian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class EditProfileViewWithoutLastNameAllMainLanguagesUkrainianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Ukrainian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Ukrainian and prepares the required fields for this language.
                """
                # Check names in Ukrainian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class EditProfileViewWithoutLastNameAllMainLanguagesTurkishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Turkish).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Turkish and prepares the required fields for this language.
                """
                # Check names in Turkish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class EditProfileViewWithoutLastNameAllMainLanguagesVietnameseTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Vietnamese).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Vietnamese and prepares the required fields for this language.
                """
                # Check names in Vietnamese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class EditProfileViewWithoutLastNameAllMainLanguagesCzechTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Czech).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Czech and prepares the required fields for this language.
                """
                # Check names in Czech alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class EditProfileViewWithoutLastNameAllMainLanguagesSwedishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Swedish).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Swedish and prepares the required fields for this language.
                """
                # Check names in Swedish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class EditProfileViewWithoutLastNameAllMainLanguagesFinnishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Finnish).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Finnish and prepares the required fields for this language.
                """
                # Check names in Finnish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class EditProfileViewWithoutLastNameAllMainLanguagesHungarianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Hungarian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Hungarian and prepares the required fields for this language.
                """
                # Check names in Hungarian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class EditProfileViewWithoutLastNameAllMainLanguagesThaiTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Thai).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Thai and prepares the required fields for this language.
                """
                # Check names in Thai alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class EditProfileViewWithoutLastNameAllMainLanguagesGreekTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Greek).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Greek and prepares the required fields for this language.
                """
                # Check names in Greek alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class EditProfileViewWithoutLastNameAllMainLanguagesMalayTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Malay).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Malay and prepares the required fields for this language.
                """
                # Check names in Malay alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class EditProfileViewWithoutLastNameAllMainLanguagesSerbianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Serbian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Serbian and prepares the required fields for this language.
                """
                # Check names in Serbian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class EditProfileViewWithoutLastNameAllMainLanguagesRomanianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Romanian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Romanian and prepares the required fields for this language.
                """
                # Check names in Romanian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class EditProfileViewWithoutLastNameAllMainLanguagesBengaliTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Bengali).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Bengali and prepares the required fields for this language.
                """
                # Check names in Bengali alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class EditProfileViewWithoutLastNameAllMainLanguagesCatalanTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Catalan).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Catalan and prepares the required fields for this language.
                """
                # Check names in Catalan alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class EditProfileViewWithoutLastNameAllMainLanguagesNorwegianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Norwegian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Norwegian and prepares the required fields for this language.
                """
                # Check names in Norwegian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class EditProfileViewWithoutLastNameAllMainLanguagesBulgarianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Bulgarian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Bulgarian and prepares the required fields for this language.
                """
                # Check names in Bulgarian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class EditProfileViewWithoutLastNameAllMainLanguagesDanishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Danish).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Danish and prepares the required fields for this language.
                """
                # Check names in Danish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class EditProfileViewWithoutLastNameAllMainLanguagesSlovakTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Slovak).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Slovak and prepares the required fields for this language.
                """
                # Check names in Slovak alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class EditProfileViewWithoutLastNameAllMainLanguagesHindiTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Hindi).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Hindi and prepares the required fields for this language.
                """
                # Check names in Hindi alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class EditProfileViewWithoutLastNameAllMainLanguagesEstonianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Estonian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Estonian and prepares the required fields for this language.
                """
                # Check names in Estonian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class EditProfileViewWithoutLastNameAllMainLanguagesCroatianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Croatian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Croatian and prepares the required fields for this language.
                """
                # Check names in Croatian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class EditProfileViewWithoutLastNameAllMainLanguagesAzerbaijaniTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Azerbaijani).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Azerbaijani and prepares the required fields for this language.
                """
                # Check names in Azerbaijani alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class EditProfileViewWithoutLastNameAllMainLanguagesCantoneseTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Cantonese).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Cantonese and prepares the required fields for this language.
                """
                # Check names in Cantonese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class EditProfileViewWithoutLastNameAllMainLanguagesLithuanianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Lithuanian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Lithuanian and prepares the required fields for this language.
                """
                # Check names in Lithuanian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class EditProfileViewWithoutLastNameAllMainLanguagesSlovenianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Slovenian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Slovenian and prepares the required fields for this language.
                """
                # Check names in Slovenian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class EditProfileViewWithoutLastNameAllMainLanguagesBasqueTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Basque).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Basque and prepares the required fields for this language.
                """
                # Check names in Basque alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class EditProfileViewWithoutLastNameAllMainLanguagesArmenianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Armenian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Armenian and prepares the required fields for this language.
                """
                # Check names in Armenian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class EditProfileViewWithoutLastNameAllMainLanguagesUzbekTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Uzbek).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Uzbek and prepares the required fields for this language.
                """
                # Check names in Uzbek alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class EditProfileViewWithoutLastNameAllMainLanguagesTamilTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Tamil).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Tamil and prepares the required fields for this language.
                """
                # Check names in Tamil alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class EditProfileViewWithoutLastNameAllMainLanguagesLatvianTestCase(EditProfileViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile view (without a last name) for all main languages (Latvian).
            """

            def set_up(self):
                """
                Sets the first name field (with an empty last name) in Latvian and prepares the required fields for this language.
                """
                # Check names in Latvian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        @only_on_sites_with_login
        class EditProfilePrivacyViewOnlyEnglishTestCase(SpeedyCoreAccountsModelsMixin, SiteTestCase):
            """
            Tests the edit profile privacy settings view: access rules and saving the date-of-birth visibility settings.
            """
            page_url = '/edit-profile/privacy/'

            def set_up(self):
                """
                Creates a user in a randomly chosen activation state with a confirmed email address, and logs in as that user.
                """
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
                """
                Asserts a logged-out visitor is redirected to the login page.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_active_user_can_open_the_page(self):
                """
                Asserts an active user can open the privacy settings page.
                """
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/privacy.html')

            def test_inactive_user_can_open_the_page(self):
                """
                Asserts an inactive user can open the privacy settings page.
                """
                self.user.profile.deactivate()
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/privacy.html')

            def test_user_can_save_his_settings_1(self):
                """
                Asserts a user can save his date-of-birth access settings (day/month and year visibility).
                """
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
                """
                Asserts a user can save his date-of-birth access settings with the reversed combination of values.
                """
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
            """
            Tests the edit profile notification settings view: access rules and saving settings.
            """
            page_url = '/edit-profile/notifications/'

            def set_up(self):
                """
                Creates a user in a randomly chosen activation state and logs in as that user.
                """
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
                """
                Asserts a logged-out visitor is redirected to the login page.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_active_user_can_open_the_page(self):
                """
                Asserts an active user can open the notifications settings page.
                """
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/notifications.html')

            def test_inactive_user_can_open_the_page(self):
                """
                Asserts an inactive user can open the notifications settings page.
                """
                self.user.profile.deactivate()
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/notifications.html')

            def test_user_can_save_his_settings(self):
                """
                Not implemented in this mixin; subclasses must override this method with a concrete implementation.
                """
                raise NotImplementedError("test_user_can_save_his_settings must be defined in classes inherited from EditProfileNotificationsViewTestCaseMixin.")


        class EditProfileCredentialsViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the edit profile credentials (password change) view: access rules and password change validation (length, uniqueness, matching, old password correctness).
            """
            page_url = '/edit-profile/credentials/'

            def set_up(self):
                """
                Creates a user in a randomly chosen activation state with a confirmed email address, and logs in as that user.
                """
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
                """
                Asserts a logged-out visitor is redirected to the login page.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_active_user_can_open_the_page(self):
                """
                Asserts an active user can open the credentials page.
                """
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/credentials.html')

            def test_inactive_user_can_open_the_page(self):
                """
                Asserts an inactive user can open the credentials page.
                """
                self.user.profile.deactivate()
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/credentials.html')

            def test_user_can_change_password_1(self):
                """
                Asserts a user can change his password to a new valid 8-character password.
                """
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
                """
                Asserts a user can change his password to a new valid 120-character password.
                """
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
                """
                Asserts a user can change his password to a new valid 120-character password that contains slashes.
                """
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
                """
                Asserts changing the password fails with the "old password was entered incorrectly" error when the old password is wrong, and the password is unchanged.
                """
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
                """
                Asserts changing the password fails when the new password is too short, and the password is unchanged.
                """
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
                """
                Asserts changing the password fails when the new password is too long, and the password is unchanged.
                """
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
                """
                Asserts changing the password fails when the new password doesn't have enough unique characters, and the password is unchanged.
                """
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
                """
                Asserts changing the password fails and reports both errors when the new password is both too short and lacks unique characters, and the password is unchanged.
                """
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
                """
                Asserts changing the password fails and reports both errors when the new password is both too long and lacks unique characters, and the password is unchanged.
                """
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
                """
                Asserts changing the password fails when the two new password fields don't match, and the password is unchanged.
                """
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
        class EditProfileCredentialsViewAllMainLanguagesEnglishTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile credentials view for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class EditProfileCredentialsViewAllMainLanguagesFrenchTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile credentials view for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class EditProfileCredentialsViewAllMainLanguagesGermanTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile credentials view for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class EditProfileCredentialsViewAllMainLanguagesSpanishTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile credentials view for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class EditProfileCredentialsViewAllMainLanguagesPortugueseTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile credentials view for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class EditProfileCredentialsViewAllMainLanguagesItalianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile credentials view for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class EditProfileCredentialsViewAllMainLanguagesDutchTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile credentials view for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class EditProfileCredentialsViewAllMainLanguagesJapaneseTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class EditProfileCredentialsViewAllMainLanguagesRussianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class EditProfileCredentialsViewAllMainLanguagesChineseTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class EditProfileCredentialsViewAllMainLanguagesPolishTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class EditProfileCredentialsViewAllMainLanguagesPersianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class EditProfileCredentialsViewAllMainLanguagesHebrewTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
            """
            Tests the edit profile credentials view for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class EditProfileCredentialsViewAllMainLanguagesKoreanTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class EditProfileCredentialsViewAllMainLanguagesArabicTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class EditProfileCredentialsViewAllMainLanguagesIndonesianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class EditProfileCredentialsViewAllMainLanguagesUkrainianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class EditProfileCredentialsViewAllMainLanguagesTurkishTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class EditProfileCredentialsViewAllMainLanguagesVietnameseTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class EditProfileCredentialsViewAllMainLanguagesCzechTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class EditProfileCredentialsViewAllMainLanguagesSwedishTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class EditProfileCredentialsViewAllMainLanguagesFinnishTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class EditProfileCredentialsViewAllMainLanguagesHungarianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class EditProfileCredentialsViewAllMainLanguagesThaiTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class EditProfileCredentialsViewAllMainLanguagesGreekTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class EditProfileCredentialsViewAllMainLanguagesMalayTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class EditProfileCredentialsViewAllMainLanguagesSerbianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class EditProfileCredentialsViewAllMainLanguagesRomanianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class EditProfileCredentialsViewAllMainLanguagesBengaliTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class EditProfileCredentialsViewAllMainLanguagesCatalanTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class EditProfileCredentialsViewAllMainLanguagesNorwegianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class EditProfileCredentialsViewAllMainLanguagesBulgarianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class EditProfileCredentialsViewAllMainLanguagesDanishTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class EditProfileCredentialsViewAllMainLanguagesSlovakTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class EditProfileCredentialsViewAllMainLanguagesHindiTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class EditProfileCredentialsViewAllMainLanguagesEstonianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class EditProfileCredentialsViewAllMainLanguagesCroatianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class EditProfileCredentialsViewAllMainLanguagesAzerbaijaniTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class EditProfileCredentialsViewAllMainLanguagesCantoneseTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class EditProfileCredentialsViewAllMainLanguagesLithuanianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class EditProfileCredentialsViewAllMainLanguagesSlovenianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class EditProfileCredentialsViewAllMainLanguagesBasqueTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class EditProfileCredentialsViewAllMainLanguagesArmenianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class EditProfileCredentialsViewAllMainLanguagesUzbekTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class EditProfileCredentialsViewAllMainLanguagesTamilTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class EditProfileCredentialsViewAllMainLanguagesLatvianTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the edit profile credentials view for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class ActivateSiteProfileViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, TestCaseMixin):
            """
            Tests the site profile activation (welcome) view: access rules for logged-out visitors and already-active users, and that inactive users can open and request activation on the page.
            """
            page_url = '/welcome/'
            redirect_url = None

            def test_visitor_has_no_access(self):
                """
                Asserts a logged-out visitor is redirected to the login page.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_inactive_user_has_no_access_to_other_pages(self):
                """
                Asserts an inactive user is redirected to the activation page when trying to access another page.
                """
                r = self.client.get(path='/other-page/')
                self.assertRedirects(response=r, expected_url=self.redirect_url, status_code=302, target_status_code=200, fetch_redirect_response=False)

            def test_active_user_gets_redirected(self):
                """
                Asserts an already-active user is redirected away from the activation page to the site's home or matches page.
                """
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
                """
                Asserts an inactive user can open the activation page (directly or after being redirected to it).
                """
                r = self.client.get(path=self.page_url)
                self.assertIn(member=r.status_code, container={200, 302})
                if (r.status_code == 200):
                    self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/activate.html')

            def test_inactive_user_can_request_activation(self):
                """
                Not implemented in this mixin; subclasses must override this method with a concrete implementation.
                """
                raise NotImplementedError("test_inactive_user_can_request_activation must be defined in classes inherited from ActivateSiteProfileViewTestCaseMixin.")


        class ActivateSiteProfileViewWithInactiveUserTestCaseMixin(ActivateSiteProfileViewTestCaseMixin):
            """
            Tests site profile activation behavior for an inactive user.
            """

            def set_up(self):
                """
                Creates an inactive user with no email addresses, and logs in as that user.
                """
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


        class ActivateSiteProfileViewWithSpeedyNetInactiveUserTestCaseMixin(ActivateSiteProfileViewTestCaseMixin):
            """
            Tests site profile activation behavior for a Speedy Net-inactive user.
            """

            def set_up(self):
                """
                Creates a Speedy Net-inactive user with a confirmed email address, and logs in as that user.
                """
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
            """
            Tests the deactivate site profile view: access rules and deactivating the account with correct/incorrect/missing password.
            """
            page_url = '/edit-profile/deactivate/'

            def set_up(self):
                """
                Creates an active user with a confirmed email address, and logs in as that user.
                """
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
                """
                Asserts a logged-out visitor is redirected to the login page.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_active_user_can_open_the_page(self):
                """
                Asserts an active user can open the deactivate account page.
                """
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/deactivate.html')

            def test_inactive_user_can_open_the_page(self):
                """
                Asserts an inactive user can open the deactivate account page.
                """
                self.user.profile.deactivate()
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/deactivate.html')

            def test_user_can_deactivate_his_account(self):
                """
                Asserts a user can deactivate his account by submitting his correct password.
                """
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
                """
                Asserts deactivation fails with the invalid password error, and the account stays active, when the password is incorrect.
                """
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
                """
                Asserts deactivation fails and reports the password as required when it's missing, and the account stays active.
                """
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
            """
            Tests the verify email address view: error handling for invalid/wrong links, already-confirmed emails, wrong confirmation tokens, and the wrong logged-in user, plus the successful confirmation flow.
            """

            def set_up(self):
                """
                Creates two users (each in a randomly chosen activation state), and gives the first user one confirmed and one unconfirmed email address.
                """
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
                """
                Asserts where a verification error redirects to, based on the given user's activation state and the site, and returns the final response obtained after following the redirect chain.

                :param r: The initial HTTP response to check for the expected redirect.
                :param user: The user the verification link belongs to; must be self.user or self.other_user.
                :return: The response obtained after following the redirect chain to its final page.
                """
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
                """
                Asserts a verification link for an email address belonging to no known user gives a 404.
                """
                user_email_address = UserEmailAddressFactory()
                token = user_email_address._generate_confirmation_token()
                r = self.client.get(path='/edit-profile/emails/verify/{}/'.format(token))
                self.assertEqual(first=r.status_code, second=404)

            def test_wrong_email_id_gives_404(self):
                """
                Asserts a verification link with a non-existent email address id gives a 404.
                """
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                email_id = "111"
                token = self.unconfirmed_email_address.confirmation_token
                r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
                self.assertEqual(first=r.status_code, second=404)

            def test_not_authenticated_user_redirects_to_login(self):
                """
                Asserts a logged-out visitor following a verification link is redirected to the login page.
                """
                self.client.logout()
                email_id = self.unconfirmed_email_address.id
                token = self.unconfirmed_email_address.confirmation_token
                r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
                self.assertRedirects(response=r, expected_url='/login/?next=/edit-profile/emails/{}/verify/{}/'.format(email_id, token), status_code=302, target_status_code=200)

            def test_confirmed_email_error_message(self):
                """
                Asserts visiting the verification link for an already-confirmed email address shows the "already confirmed" error message.
                """
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                email_id = self.confirmed_email_address.id
                token = "222"
                r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
                r = self.assert_verify_email_url_redirects_after_error(r=r, user=self.user)
                self.assertEqual(first=r.status_code, second=200)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._youve_already_confirmed_this_email_address_error_message])

            def test_unconfirmed_email_link_confirms_email(self):
                """
                Asserts following a valid verification link confirms the unconfirmed email address and shows the success message.
                """
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
                """
                Asserts following another user's verification link while logged in as a different user logs the current user out and redirects to the login page.
                """
                self.client.login(username=self.other_user.slug, password=tests_settings.USER_PASSWORD)
                email_id = self.unconfirmed_email_address.id
                token = self.unconfirmed_email_address.confirmation_token
                r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
                self.assertRedirects(response=r, expected_url='/edit-profile/emails/{}/verify/{}/'.format(email_id, token), status_code=302, target_status_code=302, fetch_redirect_response=False)
                r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
                self.assertRedirects(response=r, expected_url='/login/?next=/edit-profile/emails/{}/verify/{}/'.format(email_id, token), status_code=302, target_status_code=200)

            def test_wrong_confirmation_token_error_message(self):
                """
                Asserts an incorrect confirmation token shows the "invalid confirmation link" error and leaves the email address unconfirmed.
                """
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                email_id = self.unconfirmed_email_address.id
                token = "222"
                r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
                r = self.assert_verify_email_url_redirects_after_error(r=r, user=self.user)
                self.assertEqual(first=r.status_code, second=200)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._invalid_confirmation_link_error_message])
                self.assertIs(expr1=UserEmailAddress.objects.get(pk=self.unconfirmed_email_address.pk).is_confirmed, expr2=False)


        @only_on_sites_with_login
        class VerifyUserEmailAddressViewAllMainLanguagesEnglishTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the verify user email address view for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class VerifyUserEmailAddressViewAllMainLanguagesFrenchTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the verify user email address view for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class VerifyUserEmailAddressViewAllMainLanguagesGermanTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the verify user email address view for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class VerifyUserEmailAddressViewAllMainLanguagesSpanishTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the verify user email address view for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class VerifyUserEmailAddressViewAllMainLanguagesPortugueseTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the verify user email address view for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class VerifyUserEmailAddressViewAllMainLanguagesItalianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the verify user email address view for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class VerifyUserEmailAddressViewAllMainLanguagesDutchTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the verify user email address view for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class VerifyUserEmailAddressViewAllMainLanguagesJapaneseTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class VerifyUserEmailAddressViewAllMainLanguagesRussianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class VerifyUserEmailAddressViewAllMainLanguagesChineseTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class VerifyUserEmailAddressViewAllMainLanguagesPolishTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class VerifyUserEmailAddressViewAllMainLanguagesPersianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class VerifyUserEmailAddressViewAllMainLanguagesHebrewTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the verify user email address view for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class VerifyUserEmailAddressViewAllMainLanguagesKoreanTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class VerifyUserEmailAddressViewAllMainLanguagesArabicTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class VerifyUserEmailAddressViewAllMainLanguagesIndonesianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class VerifyUserEmailAddressViewAllMainLanguagesUkrainianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class VerifyUserEmailAddressViewAllMainLanguagesTurkishTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class VerifyUserEmailAddressViewAllMainLanguagesVietnameseTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class VerifyUserEmailAddressViewAllMainLanguagesCzechTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class VerifyUserEmailAddressViewAllMainLanguagesSwedishTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class VerifyUserEmailAddressViewAllMainLanguagesFinnishTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class VerifyUserEmailAddressViewAllMainLanguagesHungarianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class VerifyUserEmailAddressViewAllMainLanguagesThaiTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class VerifyUserEmailAddressViewAllMainLanguagesGreekTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class VerifyUserEmailAddressViewAllMainLanguagesMalayTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class VerifyUserEmailAddressViewAllMainLanguagesSerbianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class VerifyUserEmailAddressViewAllMainLanguagesRomanianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class VerifyUserEmailAddressViewAllMainLanguagesBengaliTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class VerifyUserEmailAddressViewAllMainLanguagesCatalanTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class VerifyUserEmailAddressViewAllMainLanguagesNorwegianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class VerifyUserEmailAddressViewAllMainLanguagesBulgarianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class VerifyUserEmailAddressViewAllMainLanguagesDanishTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class VerifyUserEmailAddressViewAllMainLanguagesSlovakTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class VerifyUserEmailAddressViewAllMainLanguagesHindiTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class VerifyUserEmailAddressViewAllMainLanguagesEstonianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class VerifyUserEmailAddressViewAllMainLanguagesCroatianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class VerifyUserEmailAddressViewAllMainLanguagesAzerbaijaniTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class VerifyUserEmailAddressViewAllMainLanguagesCantoneseTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class VerifyUserEmailAddressViewAllMainLanguagesLithuanianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class VerifyUserEmailAddressViewAllMainLanguagesSlovenianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class VerifyUserEmailAddressViewAllMainLanguagesBasqueTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class VerifyUserEmailAddressViewAllMainLanguagesArmenianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class VerifyUserEmailAddressViewAllMainLanguagesUzbekTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class VerifyUserEmailAddressViewAllMainLanguagesTamilTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class VerifyUserEmailAddressViewAllMainLanguagesLatvianTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the verify user email address view for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class AddUserEmailAddressViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the add email address view: access rules, uniqueness validation, confirmation email sending, and primary-email assignment.
            """

            def set_up(self):
                """
                Creates a user in a randomly chosen activation state with a confirmed, primary email address, and logs in as that user.
                """
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
                """
                Asserts a logged-out visitor is redirected to the login page.
                """
                self.client.logout()
                r = self.client.get(path='/edit-profile/emails/add/')
                self.assertRedirects(response=r, expected_url='/login/?next=/edit-profile/emails/add/', status_code=302, target_status_code=200)

            def test_active_user_can_open_the_page(self):
                """
                Asserts an active user can open the add email address page.
                """
                r = self.client.get(path='/edit-profile/emails/add/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/email_address_form.html')

            def test_inactive_user_can_open_the_page(self):
                """
                Asserts an inactive user can open the add email address page.
                """
                self.user.profile.deactivate()
                r = self.client.get(path='/edit-profile/emails/add/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='accounts/email_address_form.html')

            def test_non_unique_confirmed_email_address(self):
                """
                Asserts adding an email address that is already confirmed for the user fails with the "already in use" error and no model counts change.
                """
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
                """
                Asserts adding an email address that is already unconfirmed for the user does not create a new record and leaves it non-primary.
                """
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
                """
                Asserts a user can add a new email address, which is created unconfirmed and non-primary, and a confirmation email is sent.
                """
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
                """
                Asserts that after deleting the user's only confirmed email address, a newly added email address becomes primary.
                """
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
        class AddUserEmailAddressViewAllMainLanguagesEnglishTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the add user email address view for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AddUserEmailAddressViewAllMainLanguagesFrenchTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the add user email address view for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AddUserEmailAddressViewAllMainLanguagesGermanTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the add user email address view for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AddUserEmailAddressViewAllMainLanguagesSpanishTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the add user email address view for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AddUserEmailAddressViewAllMainLanguagesPortugueseTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the add user email address view for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AddUserEmailAddressViewAllMainLanguagesItalianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the add user email address view for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AddUserEmailAddressViewAllMainLanguagesDutchTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the add user email address view for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class AddUserEmailAddressViewAllMainLanguagesJapaneseTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class AddUserEmailAddressViewAllMainLanguagesRussianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class AddUserEmailAddressViewAllMainLanguagesChineseTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class AddUserEmailAddressViewAllMainLanguagesPolishTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class AddUserEmailAddressViewAllMainLanguagesPersianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AddUserEmailAddressViewAllMainLanguagesHebrewTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the add user email address view for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AddUserEmailAddressViewAllMainLanguagesKoreanTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class AddUserEmailAddressViewAllMainLanguagesArabicTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class AddUserEmailAddressViewAllMainLanguagesIndonesianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class AddUserEmailAddressViewAllMainLanguagesUkrainianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class AddUserEmailAddressViewAllMainLanguagesTurkishTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class AddUserEmailAddressViewAllMainLanguagesVietnameseTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class AddUserEmailAddressViewAllMainLanguagesCzechTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AddUserEmailAddressViewAllMainLanguagesSwedishTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AddUserEmailAddressViewAllMainLanguagesFinnishTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class AddUserEmailAddressViewAllMainLanguagesHungarianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class AddUserEmailAddressViewAllMainLanguagesThaiTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class AddUserEmailAddressViewAllMainLanguagesGreekTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class AddUserEmailAddressViewAllMainLanguagesMalayTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class AddUserEmailAddressViewAllMainLanguagesSerbianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class AddUserEmailAddressViewAllMainLanguagesRomanianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class AddUserEmailAddressViewAllMainLanguagesBengaliTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class AddUserEmailAddressViewAllMainLanguagesCatalanTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class AddUserEmailAddressViewAllMainLanguagesNorwegianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class AddUserEmailAddressViewAllMainLanguagesBulgarianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class AddUserEmailAddressViewAllMainLanguagesDanishTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class AddUserEmailAddressViewAllMainLanguagesSlovakTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class AddUserEmailAddressViewAllMainLanguagesHindiTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class AddUserEmailAddressViewAllMainLanguagesEstonianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class AddUserEmailAddressViewAllMainLanguagesCroatianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class AddUserEmailAddressViewAllMainLanguagesAzerbaijaniTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class AddUserEmailAddressViewAllMainLanguagesCantoneseTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class AddUserEmailAddressViewAllMainLanguagesLithuanianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class AddUserEmailAddressViewAllMainLanguagesSlovenianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class AddUserEmailAddressViewAllMainLanguagesBasqueTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class AddUserEmailAddressViewAllMainLanguagesArmenianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class AddUserEmailAddressViewAllMainLanguagesUzbekTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class AddUserEmailAddressViewAllMainLanguagesTamilTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class AddUserEmailAddressViewAllMainLanguagesLatvianTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the add user email address view for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class SendConfirmationEmailViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the resend confirmation email view: access rules (logged-out visitor, other users' addresses) and resending a confirmation email.
            """

            def set_up(self):
                """
                Creates a user in a randomly chosen activation state with an unconfirmed and a confirmed email address, plus another user's email address, and logs in as the first user.
                """
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
                """
                Asserts a logged-out visitor is forbidden (403) from resending a confirmation email.
                """
                self.client.logout()
                r = self.client.post(path=self.unconfirmed_email_address_url)
                self.assertEqual(first=r.status_code, second=403)

            def test_user_has_no_access_to_other_users_address(self):
                """
                Asserts a user is forbidden (403) from resending a confirmation email for another user's address.
                """
                r = self.client.post(path=self.other_user_address_url)
                self.assertEqual(first=r.status_code, second=403)

            def test_user_can_resend_confirmation(self):
                """
                Asserts a user can resend a confirmation email for his own unconfirmed address, and the email is sent with the confirmation token.
                """
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
        class SendConfirmationEmailViewAllMainLanguagesEnglishTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            """
            Tests the send confirmation email view for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class SendConfirmationEmailViewAllMainLanguagesFrenchTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            """
            Tests the send confirmation email view for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class SendConfirmationEmailViewAllMainLanguagesGermanTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            """
            Tests the send confirmation email view for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class SendConfirmationEmailViewAllMainLanguagesSpanishTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            """
            Tests the send confirmation email view for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class SendConfirmationEmailViewAllMainLanguagesPortugueseTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            """
            Tests the send confirmation email view for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class SendConfirmationEmailViewAllMainLanguagesItalianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            """
            Tests the send confirmation email view for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class SendConfirmationEmailViewAllMainLanguagesDutchTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            """
            Tests the send confirmation email view for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class SendConfirmationEmailViewAllMainLanguagesJapaneseTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class SendConfirmationEmailViewAllMainLanguagesRussianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class SendConfirmationEmailViewAllMainLanguagesChineseTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class SendConfirmationEmailViewAllMainLanguagesPolishTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class SendConfirmationEmailViewAllMainLanguagesPersianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class SendConfirmationEmailViewAllMainLanguagesHebrewTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
            """
            Tests the send confirmation email view for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class SendConfirmationEmailViewAllMainLanguagesKoreanTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class SendConfirmationEmailViewAllMainLanguagesArabicTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class SendConfirmationEmailViewAllMainLanguagesIndonesianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class SendConfirmationEmailViewAllMainLanguagesUkrainianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class SendConfirmationEmailViewAllMainLanguagesTurkishTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class SendConfirmationEmailViewAllMainLanguagesVietnameseTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class SendConfirmationEmailViewAllMainLanguagesCzechTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class SendConfirmationEmailViewAllMainLanguagesSwedishTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class SendConfirmationEmailViewAllMainLanguagesFinnishTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class SendConfirmationEmailViewAllMainLanguagesHungarianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class SendConfirmationEmailViewAllMainLanguagesThaiTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class SendConfirmationEmailViewAllMainLanguagesGreekTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class SendConfirmationEmailViewAllMainLanguagesMalayTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class SendConfirmationEmailViewAllMainLanguagesSerbianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class SendConfirmationEmailViewAllMainLanguagesRomanianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class SendConfirmationEmailViewAllMainLanguagesBengaliTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class SendConfirmationEmailViewAllMainLanguagesCatalanTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class SendConfirmationEmailViewAllMainLanguagesNorwegianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class SendConfirmationEmailViewAllMainLanguagesBulgarianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class SendConfirmationEmailViewAllMainLanguagesDanishTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class SendConfirmationEmailViewAllMainLanguagesSlovakTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class SendConfirmationEmailViewAllMainLanguagesHindiTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class SendConfirmationEmailViewAllMainLanguagesEstonianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class SendConfirmationEmailViewAllMainLanguagesCroatianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class SendConfirmationEmailViewAllMainLanguagesAzerbaijaniTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class SendConfirmationEmailViewAllMainLanguagesCantoneseTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class SendConfirmationEmailViewAllMainLanguagesLithuanianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class SendConfirmationEmailViewAllMainLanguagesSlovenianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class SendConfirmationEmailViewAllMainLanguagesBasqueTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class SendConfirmationEmailViewAllMainLanguagesArmenianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class SendConfirmationEmailViewAllMainLanguagesUzbekTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class SendConfirmationEmailViewAllMainLanguagesTamilTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class SendConfirmationEmailViewAllMainLanguagesLatvianTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the send confirmation email view for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class DeleteUserEmailAddressViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the delete email address view: access rules, protecting the primary and only-confirmed addresses from deletion, successful deletion, and the ORM-level protection against bulk queryset deletion.
            """

            def set_up(self):
                """
                Creates a user in a randomly chosen activation state with an unconfirmed, a confirmed non-primary, and a primary email address, plus another user's email address, and logs in as the first user.
                """
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
                """
                Asserts a logged-out visitor is forbidden (403) from deleting an email address, and model counts are unchanged.
                """
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
                """
                Asserts a user is forbidden (403) from deleting another user's email address, and model counts are unchanged.
                """
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
                """
                Asserts a user cannot delete his primary email address, and model counts are unchanged.
                """
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
                """
                Asserts a user cannot delete his only confirmed email address, and model counts are unchanged.
                """
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
                """
                Asserts a user can delete a confirmed, non-primary email address when he has another confirmed address, and a success message is shown.
                """
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
                """
                Asserts bulk queryset deletion of email addresses raises NotImplementedError.
                """
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
        class DeleteUserEmailAddressViewAllMainLanguagesEnglishTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the delete user email address view for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class DeleteUserEmailAddressViewAllMainLanguagesFrenchTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the delete user email address view for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class DeleteUserEmailAddressViewAllMainLanguagesGermanTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the delete user email address view for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class DeleteUserEmailAddressViewAllMainLanguagesSpanishTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the delete user email address view for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class DeleteUserEmailAddressViewAllMainLanguagesPortugueseTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the delete user email address view for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class DeleteUserEmailAddressViewAllMainLanguagesItalianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the delete user email address view for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class DeleteUserEmailAddressViewAllMainLanguagesDutchTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the delete user email address view for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class DeleteUserEmailAddressViewAllMainLanguagesJapaneseTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class DeleteUserEmailAddressViewAllMainLanguagesRussianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class DeleteUserEmailAddressViewAllMainLanguagesChineseTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class DeleteUserEmailAddressViewAllMainLanguagesPolishTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class DeleteUserEmailAddressViewAllMainLanguagesPersianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class DeleteUserEmailAddressViewAllMainLanguagesHebrewTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the delete user email address view for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class DeleteUserEmailAddressViewAllMainLanguagesKoreanTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class DeleteUserEmailAddressViewAllMainLanguagesArabicTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class DeleteUserEmailAddressViewAllMainLanguagesIndonesianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class DeleteUserEmailAddressViewAllMainLanguagesUkrainianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class DeleteUserEmailAddressViewAllMainLanguagesTurkishTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class DeleteUserEmailAddressViewAllMainLanguagesVietnameseTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class DeleteUserEmailAddressViewAllMainLanguagesCzechTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class DeleteUserEmailAddressViewAllMainLanguagesSwedishTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class DeleteUserEmailAddressViewAllMainLanguagesFinnishTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class DeleteUserEmailAddressViewAllMainLanguagesHungarianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class DeleteUserEmailAddressViewAllMainLanguagesThaiTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class DeleteUserEmailAddressViewAllMainLanguagesGreekTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class DeleteUserEmailAddressViewAllMainLanguagesMalayTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class DeleteUserEmailAddressViewAllMainLanguagesSerbianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class DeleteUserEmailAddressViewAllMainLanguagesRomanianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class DeleteUserEmailAddressViewAllMainLanguagesBengaliTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class DeleteUserEmailAddressViewAllMainLanguagesCatalanTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class DeleteUserEmailAddressViewAllMainLanguagesNorwegianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class DeleteUserEmailAddressViewAllMainLanguagesBulgarianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class DeleteUserEmailAddressViewAllMainLanguagesDanishTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class DeleteUserEmailAddressViewAllMainLanguagesSlovakTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class DeleteUserEmailAddressViewAllMainLanguagesHindiTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class DeleteUserEmailAddressViewAllMainLanguagesEstonianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class DeleteUserEmailAddressViewAllMainLanguagesCroatianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class DeleteUserEmailAddressViewAllMainLanguagesAzerbaijaniTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class DeleteUserEmailAddressViewAllMainLanguagesCantoneseTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class DeleteUserEmailAddressViewAllMainLanguagesLithuanianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class DeleteUserEmailAddressViewAllMainLanguagesSlovenianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class DeleteUserEmailAddressViewAllMainLanguagesBasqueTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class DeleteUserEmailAddressViewAllMainLanguagesArmenianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class DeleteUserEmailAddressViewAllMainLanguagesUzbekTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class DeleteUserEmailAddressViewAllMainLanguagesTamilTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class DeleteUserEmailAddressViewAllMainLanguagesLatvianTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the delete user email address view for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class SetPrimaryUserEmailAddressViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the set primary email address view: access rules, protecting unconfirmed addresses from becoming primary, and successfully making a confirmed address primary.
            """

            def set_up(self):
                """
                Creates a user in a randomly chosen activation state with an unconfirmed, a confirmed non-primary, and a primary email address, plus another user's email address, and logs in as the first user.
                """
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
                """
                Asserts a logged-out visitor is forbidden (403) from setting an email address as primary, and model counts are unchanged.
                """
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
                """
                Asserts a user is forbidden (403) from setting another user's email address as primary, and model counts are unchanged.
                """
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
                """
                Asserts a user cannot make an unconfirmed email address his primary address, and model counts are unchanged.
                """
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
                """
                Asserts a user can make a confirmed, non-primary email address his primary address, and the primary address changes accordingly.
                """
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
        class SetPrimaryUserEmailAddressViewAllMainLanguagesEnglishTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the set primary user email address view for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesFrenchTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the set primary user email address view for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesGermanTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the set primary user email address view for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesSpanishTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the set primary user email address view for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesPortugueseTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the set primary user email address view for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesItalianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the set primary user email address view for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesDutchTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the set primary user email address view for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesJapaneseTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesRussianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesChineseTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesPolishTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesPersianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesHebrewTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
            """
            Tests the set primary user email address view for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesKoreanTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesArabicTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesIndonesianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesUkrainianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesTurkishTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesVietnameseTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesCzechTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesSwedishTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesFinnishTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesHungarianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesThaiTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesGreekTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesMalayTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesSerbianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesRomanianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesBengaliTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesCatalanTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesNorwegianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesBulgarianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesDanishTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesSlovakTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesHindiTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesEstonianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesCroatianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesAzerbaijaniTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesCantoneseTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesLithuanianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesSlovenianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesBasqueTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesArmenianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesUzbekTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesTamilTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class SetPrimaryUserEmailAddressViewAllMainLanguagesLatvianTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the set primary user email address view for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        @only_on_sites_with_login
        class ChangeUserEmailAddressPrivacyViewOnlyEnglishTestCase(SpeedyCoreAccountsModelsMixin, SiteTestCase):
            """
            Tests the change email address privacy view: access rules and changing an email address's privacy setting.
            """

            def set_up(self):
                """
                Creates a user in a randomly chosen activation state with a confirmed email address (access set to 'me') and another user's email address, and logs in as the first user.
                """
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
                self.email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
                self.email_address_url = '/edit-profile/emails/{}/privacy/'.format(self.email_address.id)
                self.other_user_address = UserEmailAddressFactory()
                self.other_user_address_url = '/edit-profile/emails/{}/privacy/'.format(self.other_user_address.id)
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=self.email_address.access, second=UserAccessField.ACCESS_ME)

            def test_visitor_has_no_access(self):
                """
                Asserts a logged-out visitor is forbidden (403) from changing the privacy of an email address, and the access setting is unchanged.
                """
                self.client.logout()
                r = self.client.post(path=self.email_address_url, data={'access': UserAccessField.ACCESS_ANYONE})
                self.assertEqual(first=r.status_code, second=403)
                self.email_address.refresh_from_db()
                self.assertEqual(first=self.email_address.access, second=UserAccessField.ACCESS_ME)

            def test_user_has_no_access_to_other_users_address(self):
                """
                Asserts a user is forbidden (403) from changing the privacy of another user's email address, and the access setting is unchanged.
                """
                r = self.client.post(path=self.other_user_address_url, data={'access': UserAccessField.ACCESS_ANYONE})
                self.assertEqual(first=r.status_code, second=403)
                self.other_user_address.refresh_from_db()
                self.assertEqual(first=self.other_user_address.access, second=UserAccessField.ACCESS_ME)

            def test_get_redirects_to_edit_profile_emails_page(self):
                """
                Asserts a GET request to the privacy URL redirects to the emails page without changing the access setting.
                """
                r = self.client.get(path=self.email_address_url)
                self.assertRedirects(response=r, expected_url='/edit-profile/emails/', status_code=302, target_status_code=302)
                self.email_address.refresh_from_db()
                self.assertEqual(first=self.email_address.access, second=UserAccessField.ACCESS_ME)

            def test_user_can_change_email_address_privacy_to_friends(self):
                """
                Asserts a user can change his email address privacy to friends.
                """
                r = self.client.post(path=self.email_address_url, data={'access': UserAccessField.ACCESS_FRIENDS})
                self.assertRedirects(response=r, expected_url='/edit-profile/emails/', status_code=302, target_status_code=302)
                self.email_address.refresh_from_db()
                self.assertEqual(first=self.email_address.access, second=UserAccessField.ACCESS_FRIENDS)

            def test_user_can_change_email_address_privacy_to_anyone(self):
                """
                Asserts a user can change his email address privacy to anyone.
                """
                r = self.client.post(path=self.email_address_url, data={'access': UserAccessField.ACCESS_ANYONE})
                self.assertRedirects(response=r, expected_url='/edit-profile/emails/', status_code=302, target_status_code=302)
                self.email_address.refresh_from_db()
                self.assertEqual(first=self.email_address.access, second=UserAccessField.ACCESS_ANYONE)


        @only_on_sites_with_login
        class ResendConfirmationEmailViewOnlyEnglishTestCase(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, SiteTestCase):
            """
            Tests the resend confirmation email view (English only): access rules and resending a confirmation email.
            """

            def set_up(self):
                """
                Creates a user in a randomly chosen activation state with an unconfirmed email address, a confirmed non-primary email address, and another user's unconfirmed email address, and logs in as the first user.
                """
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
                self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=False)
                self.confirmed_email_address_url = '/edit-profile/emails/{}/confirm/'.format(self.confirmed_email_address.id)
                self.other_user_address = UserEmailAddressFactory(is_confirmed=False)
                self.other_user_address_url = '/edit-profile/emails/{}/confirm/'.format(self.other_user_address.id)
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)

            def test_visitor_has_no_access(self):
                """
                Asserts a logged-out visitor is forbidden (403) from resending a confirmation email, and no email is sent.
                """
                self.client.logout()
                r = self.client.post(path=self.unconfirmed_email_address_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assertEqual(first=len(mail.outbox), second=0)

            def test_user_has_no_access_to_other_users_address(self):
                """
                Asserts a user is forbidden (403) from resending a confirmation email for another user's address, and no email is sent.
                """
                r = self.client.post(path=self.other_user_address_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assertEqual(first=len(mail.outbox), second=0)

            def test_user_cannot_resend_confirmation_for_already_confirmed_address(self):
                """
                Asserts a user cannot resend a confirmation email for an already-confirmed address, and no email is sent.
                """
                r = self.client.post(path=self.confirmed_email_address_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assertEqual(first=len(mail.outbox), second=0)

            def test_get_redirects_to_edit_profile_emails_page_without_sending_email(self):
                """
                Asserts a GET request to the resend URL redirects to the emails page without sending an email.
                """
                r = self.client.get(path=self.unconfirmed_email_address_url)
                self.assertRedirects(response=r, expected_url='/edit-profile/emails/', status_code=302, target_status_code=302)
                self.assertEqual(first=len(mail.outbox), second=0)

            def test_user_can_resend_confirmation_email(self):
                """
                Asserts a user can resend a confirmation email for his own unconfirmed address, and the email contains the confirmation token.
                """
                self.assertEqual(first=len(mail.outbox), second=0)
                r = self.client.post(path=self.unconfirmed_email_address_url)
                self.assertRedirects(response=r, expected_url='/edit-profile/emails/', status_code=302, target_status_code=302)
                r = self.client.get(path='/edit-profile/emails/')
                self.assertRedirects(response=r, expected_url='/edit-profile/credentials/', status_code=302, target_status_code=200, fetch_redirect_response=False)
                r = self.client.get(path='/edit-profile/credentials/')
                self.assertEqual(first=r.status_code, second=200)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._a_confirmation_message_was_sent_to_email_address_success_message_by_email_address(email_address=self.unconfirmed_email_address.email)])
                self.assertEqual(first=len(mail.outbox), second=1)
                self.assertIn(member=self.unconfirmed_email_address.confirmation_token, container=mail.outbox[0].body)


        @only_on_sites_with_login
        class PasswordResetViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the password reset view: opening the page, requesting a password reset email, and the deleted-account edge case.
            """

            def set_up(self):
                """
                Creates a user in a randomly chosen activation state with a confirmed primary email address.
                """
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
                """
                Asserts the password reset page can be opened.
                """
                r = self.client.get(path='/reset-password/')
                self.assertEqual(first=r.status_code, second=200)

            def test_visitor_can_reset_password(self):
                """
                Asserts requesting a password reset for an existing email address sends a password reset email with the correct subject.
                """
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
                """
                Asserts no password reset email is sent when requesting a reset for a deleted account without a usable password.
                """
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
        class PasswordResetViewAllMainLanguagesEnglishTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            """
            Tests the password reset view for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class PasswordResetViewAllMainLanguagesFrenchTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            """
            Tests the password reset view for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class PasswordResetViewAllMainLanguagesGermanTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            """
            Tests the password reset view for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class PasswordResetViewAllMainLanguagesSpanishTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            """
            Tests the password reset view for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class PasswordResetViewAllMainLanguagesPortugueseTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            """
            Tests the password reset view for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class PasswordResetViewAllMainLanguagesItalianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            """
            Tests the password reset view for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class PasswordResetViewAllMainLanguagesDutchTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            """
            Tests the password reset view for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class PasswordResetViewAllMainLanguagesJapaneseTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class PasswordResetViewAllMainLanguagesRussianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class PasswordResetViewAllMainLanguagesChineseTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class PasswordResetViewAllMainLanguagesPolishTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class PasswordResetViewAllMainLanguagesPersianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class PasswordResetViewAllMainLanguagesHebrewTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):
            """
            Tests the password reset view for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class PasswordResetViewAllMainLanguagesKoreanTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class PasswordResetViewAllMainLanguagesArabicTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class PasswordResetViewAllMainLanguagesIndonesianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class PasswordResetViewAllMainLanguagesUkrainianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class PasswordResetViewAllMainLanguagesTurkishTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class PasswordResetViewAllMainLanguagesVietnameseTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class PasswordResetViewAllMainLanguagesCzechTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class PasswordResetViewAllMainLanguagesSwedishTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class PasswordResetViewAllMainLanguagesFinnishTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class PasswordResetViewAllMainLanguagesHungarianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class PasswordResetViewAllMainLanguagesThaiTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class PasswordResetViewAllMainLanguagesGreekTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class PasswordResetViewAllMainLanguagesMalayTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class PasswordResetViewAllMainLanguagesSerbianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class PasswordResetViewAllMainLanguagesRomanianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class PasswordResetViewAllMainLanguagesBengaliTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class PasswordResetViewAllMainLanguagesCatalanTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class PasswordResetViewAllMainLanguagesNorwegianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class PasswordResetViewAllMainLanguagesBulgarianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class PasswordResetViewAllMainLanguagesDanishTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class PasswordResetViewAllMainLanguagesSlovakTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class PasswordResetViewAllMainLanguagesHindiTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class PasswordResetViewAllMainLanguagesEstonianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class PasswordResetViewAllMainLanguagesCroatianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class PasswordResetViewAllMainLanguagesAzerbaijaniTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class PasswordResetViewAllMainLanguagesCantoneseTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class PasswordResetViewAllMainLanguagesLithuanianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class PasswordResetViewAllMainLanguagesSlovenianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class PasswordResetViewAllMainLanguagesBasqueTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class PasswordResetViewAllMainLanguagesArmenianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class PasswordResetViewAllMainLanguagesUzbekTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class PasswordResetViewAllMainLanguagesTamilTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class PasswordResetViewAllMainLanguagesLatvianTestCase(PasswordResetViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the password reset view for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


