from datetime import date, datetime

from django.conf import settings as django_settings
from django.test import override_settings
from django.core import mail

from speedy.core.base.test import tests_settings
from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_sites_with_login, exclude_on_speedy_match
from speedy.core.accounts.tests.test_mixins import SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin
from speedy.core.base.utils import normalize_slug, normalize_username
from speedy.core.accounts.models import Entity, User, UserEmailAddress

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.utils import get_random_user_password
    from speedy.core.accounts.tests.test_factories  import ActiveUserFactory, UserEmailAddressFactory, InactiveUserFactory


class RedirectMeMixin(object):
    def assert_me_url_redirects(self, expected_url):
        r = self.client.get(path='/me/')
        self.assertRedirects(response=r, expected_url=expected_url)

    def assert_me_url_redirects_to_login_url(self):
        expected_url = '/login/?next=/me/'
        self.assert_me_url_redirects(expected_url=expected_url)

    def assert_me_url_redirects_to_user_profile_url(self, user):
        expected_url = '/{}/'.format(user.slug)
        self.assert_me_url_redirects(expected_url=expected_url)

    def assert_me_url_redirects_to_welcome_url(self):
        expected_url = '/welcome/'
        self.assert_me_url_redirects(expected_url=expected_url)


@only_on_sites_with_login
class IndexViewTestCase(SpeedyCoreAccountsModelsMixin, SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            unconfirmed_email_address_count=0,
        )

    def test_visitor_gets_registration_page(self):
        r = self.client.get(path='/')
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/registration.html')


@only_on_sites_with_login
class MeViewTestCase(RedirectMeMixin, SpeedyCoreAccountsModelsMixin, SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory(slug='markmark')
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
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
class LoginTestCase(RedirectMeMixin, SpeedyCoreAccountsModelsMixin, SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 2, django_settings.SPEEDY_MATCH_SITE_ID: 3}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=1,
        )

    def test_user_can_login_with_slug(self):
        self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_user_can_login_with_username(self):
        self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_user_can_login_with_confirmed_email_address(self):
        self.client.login(username=self.confirmed_email_address.email, password=tests_settings.USER_PASSWORD)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_user_can_login_with_unconfirmed_email_address(self):
        self.client.login(username=self.unconfirmed_email_address.email, password=tests_settings.USER_PASSWORD)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_user_cannot_login_with_wrong_slug(self):
        self.client.login(username='a{}'.format(self.user.slug), password=tests_settings.USER_PASSWORD)
        self.assert_me_url_redirects_to_login_url()

    def test_user_cannot_login_with_wrong_username(self):
        self.client.login(username='a{}'.format(self.user.slug), password=tests_settings.USER_PASSWORD)
        self.assert_me_url_redirects_to_login_url()

    def test_user_cannot_login_with_wrong_email(self):
        self.client.login(username='a{}'.format(self.confirmed_email_address.email), password=tests_settings.USER_PASSWORD)
        self.assert_me_url_redirects_to_login_url()

    def test_user_cannot_login_with_wrong_password(self):
        self.client.login(username=self.user.slug, password='{}-'.format(tests_settings.USER_PASSWORD))
        self.assert_me_url_redirects_to_login_url()


class RegistrationViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin):
    def setup(self):
        super().setup()
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

    def setup_required_fields(self):
        self.required_fields = self.data.keys()
        self.assert_registration_form_required_fields(required_fields=self.required_fields)

    def test_visitor_can_see_registration_page(self):
        r = self.client.get(path='/')
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/registration.html')

    def test_visitor_can_register(self):
        r = self.client.post(path='/', data=self.data)
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
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
        self.assertTrue(expr=user.check_password(raw_password=self.password))
        self.assertFalse(expr=user.check_password(raw_password=tests_settings.USER_PASSWORD))
        # TODO - uncomment these lines
        self.assertEqual(first=user.first_name, second=self.first_name)
        self.assertEqual(first=user.first_name_en, second=self.first_name)
        self.assertEqual(first=user.first_name_he, second=self.first_name) # ~~~~ TODO - uncomment these lines
        self.assertEqual(first=user.last_name, second=self.last_name)
        self.assertEqual(first=user.last_name_en, second=self.last_name)
        self.assertEqual(first=user.last_name_he, second=self.last_name) # ~~~~ TODO - uncomment these lines
        self.assertEqual(first=user.username, second=self.username)
        self.assertEqual(first=user.username, second='user1234')
        self.assertEqual(first=user.slug, second=self.slug)
        self.assertEqual(first=user.slug, second='user-1234')
        self.assertEqual(first=user.email_addresses.count(), second=1)
        self.assertEqual(first=user.email_addresses.first().email, second='email@example.com')
        self.assertFalse(expr=user.email_addresses.first().is_confirmed)
        self.assertTrue(expr=user.email_addresses.first().is_primary)
        for (key, value) in self.data.items():
            if (not (key in ['new_password1', 'date_of_birth'])):
                self.assertEqual(first=getattr(user, key), second=value)
        self.assertEqual(first=user.date_of_birth, second=date(year=1980, month=8, day=20))

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
        self.assertEqual(first=existing_user.email_addresses.count(), second=1)
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
        self.assertEqual(first=existing_user.email_addresses.count(), second=1)
        existing_user = User.objects.get(pk=existing_user.pk) # ~~~~ TODO: remove this line!
        self.assertEqual(first=existing_user.email_addresses.count(), second=1)

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
        self.assertEqual(first=existing_user.email_addresses.count(), second=1)
        r = self.client.post(path='/', data=self.data)
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        self.assert_models_count(
            entity_count=2,
            user_count=2,
            user_email_address_count=2,
            confirmed_email_address_count=1,
            unconfirmed_email_address_count=1,
        )
        self.assertEqual(first=existing_user.email_addresses.count(), second=1)
        existing_user = User.objects.get(pk=existing_user.pk) # ~~~~ TODO: remove this line!
        self.assertEqual(first=existing_user.email_addresses.count(), second=1)

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
        self.assertEqual(first=existing_user.email_addresses.count(), second=1)
        r = self.client.post(path='/', data=self.data)
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        self.assert_models_count(
            entity_count=2,
            user_count=2,
            user_email_address_count=1,
            confirmed_email_address_count=0,
            unconfirmed_email_address_count=1,
        )
        self.assertEqual(first=existing_user.email_addresses.count(), second=0)
        existing_user = User.objects.get(pk=existing_user.pk) # ~~~~ TODO: remove this line!
        self.assertEqual(first=existing_user.email_addresses.count(), second=0) # ~~~~ TODO: remove this line!

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
        self.assertEqual(first=existing_user.email_addresses.count(), second=1)
        r = self.client.post(path='/', data=self.data)
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        self.assert_models_count(
            entity_count=2,
            user_count=2,
            user_email_address_count=2,
            confirmed_email_address_count=0,
            unconfirmed_email_address_count=2,
        )
        self.assertEqual(first=existing_user.email_addresses.count(), second=1)
        existing_user = User.objects.get(pk=existing_user.pk) # ~~~~ TODO: remove this line!
        self.assertEqual(first=existing_user.email_addresses.count(), second=1)

    def test_password_too_short(self):
        data = self.data.copy()
        data['new_password1'] = '8' * 3
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
        data['new_password1'] = '8' * 121
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

    def test_user_is_logged_in_after_registration(self):
        r = self.client.post(path='/', data=self.data)
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        r = self.client.get(path='/')
        if (django_settings.ACTIVATE_PROFILE_AFTER_REGISTRATION):
            self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
            r = self.client.get(path='/{}/'.format(self.data['slug']))
        else:
            self.assertRedirects(response=r, expected_url='/welcome/', fetch_redirect_response=False)
            r = self.client.get(path='/welcome/')
        self.assertTrue(expr=r.context['user'].is_authenticated)
        self.assertEqual(first=r.context['user'].username, second='user1234')
        self.assertEqual(first=r.context['user'].slug, second='user-1234')

    def test_user_gets_email_after_registration(self):
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
        self.assertFalse(expr=email.is_confirmed)
        self.assertEqual(first=email.confirmation_sent, second=1)
        self.assertEqual(first=mail.outbox[0].subject, second='Confirm your email address on {}'.format(self.site.name))
        self.assertIn(member=email_address.confirmation_token, container=mail.outbox[0].body)
        # self.assertIn(member=UserEmailAddress.objects.get(email='email@example.com').confirmation_token, container=mail.outbox[0].body) # ~~~~ TODO: remove this line!
        self.assertIn(member=self.full_http_host, container=mail.outbox[0].body)
        for other_full_http_host in self.all_other_full_http_host_list:
            self.assertNotIn(member=other_full_http_host, container=mail.outbox[0].body)

    def test_cannot_register_taken_username(self):
        data = self.data.copy()
        existing_user = ActiveUserFactory(username='username', slug='user-name')
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            unconfirmed_email_address_count=0,
        )
        self.assertEqual(first=existing_user.email_addresses.count(), second={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        data['slug'] = 'us-er-na-me'
        r = self.client.post(path='/', data=data)
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._this_username_is_already_taken_errors_dict(slug_fail=True))
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            unconfirmed_email_address_count=0,
        )
        self.assertEqual(first=existing_user.email_addresses.count(), second={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        existing_user = User.objects.get(pk=existing_user.pk) # ~~~~ TODO: remove this line!
        self.assertEqual(first=existing_user.email_addresses.count(), second={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])

    def test_email_gets_converted_to_lowercase(self):
        data = self.data.copy()
        data['email'] = 'EMAIL22@EXAMPLE.COM'
        r = self.client.post(path='/', data=data)
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
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
            print("test_invalid_date_of_birth_list_fail", date_of_birth) # ~~~~ TODO: remove this line!
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
class RegistrationViewEnglishTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
    def setup(self):
        super().setup()
        self.data.update({
            'first_name_en': "Doron",
            'last_name_en': "Matalon",
        })
        self.first_name = "Doron"
        self.last_name = "Matalon"
        self.setup_required_fields()

    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='en')


@only_on_sites_with_login
@override_settings(LANGUAGE_CODE='he')
class RegistrationViewHebrewTestCase(RegistrationViewTestCaseMixin, SiteTestCase):
    def setup(self):
        super().setup()
        self.data.update({
            'first_name_he': "דורון",
            'last_name_he': "מטלון",
        })
        self.first_name = "דורון"
        self.last_name = "מטלון"
        self.setup_required_fields()

    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='he')


class LoginViewTestCaseMixin(RedirectMeMixin, SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin):
    login_url = '/login/'
    _other_user_password = '8' * 8

    def setup(self):
        super().setup()
        self.user = ActiveUserFactory(slug='slug.with.dots')
        self.user_email = UserEmailAddressFactory(user=self.user)
        self.other_user = ActiveUserFactory()
        self.other_user.set_password(raw_password=self._other_user_password)
        self.other_user.save_user_and_profile()
        self.other_user_email = UserEmailAddressFactory(user=self.other_user)
        self.inactive_user = InactiveUserFactory()
        self.assertNotEqual(first=self.user_email.email, second=self.other_user_email.email)
        self.assertNotEqual(first=tests_settings.USER_PASSWORD, second=self._other_user_password)
        self.assert_models_count(
            entity_count=3,
            user_count=3,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 2, django_settings.SPEEDY_MATCH_SITE_ID: 4}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=2,
        )

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
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)
        # Assert expected_url directly once to confirm.
        self.assert_me_url_redirects(expected_url='/slug-with-dots/')

    def test_visitor_can_login_using_username(self):
        self.assertEqual(first=self.user.username, second='slugwithdots')
        data = {
            'username': self.user.username,
            'password': tests_settings.USER_PASSWORD,
        }
        r = self.client.post(path=self.login_url, data=data)
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_visitor_can_login_using_original_slug(self):
        self.assertEqual(first=self.user.slug, second='slug-with-dots')
        data = {
            'username': 'slug.with.dots',
            'password': tests_settings.USER_PASSWORD,
        }
        r = self.client.post(path=self.login_url, data=data)
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_visitor_can_login_using_slug_modified(self):
        self.assertEqual(first=self.user.slug, second='slug-with-dots')
        data = {
            'username': 'slug____with.....dots---',
            'password': tests_settings.USER_PASSWORD,
        }
        r = self.client.post(path=self.login_url, data=data)
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_visitor_can_login_using_slug_uppercase(self):
        self.assertEqual(first=self.user.slug, second='slug-with-dots')
        data = {
            'username': 'SLUG-WITH-DOTS',
            'password': tests_settings.USER_PASSWORD,
        }
        r = self.client.post(path=self.login_url, data=data)
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_visitor_can_login_using_email(self):
        data = {
            'username': self.user_email.email,
            'password': tests_settings.USER_PASSWORD,
        }
        r = self.client.post(path=self.login_url, data=data)
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_visitor_can_login_using_email_uppercase(self):
        data = {
            'username': self.user_email.email.upper(),
            'password': tests_settings.USER_PASSWORD,
        }
        r = self.client.post(path=self.login_url, data=data)
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_visitor_can_login_using_other_user_email_and_password(self):
        data = {
            'username': self.other_user_email.email,
            'password': self._other_user_password,
        }
        r = self.client.post(path=self.login_url, data=data)
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.other_user)

    def test_visitor_still_can_login_if_he_is_not_active_user(self):
        data = {
            'username': self.inactive_user.slug,
            'password': tests_settings.USER_PASSWORD,
        }
        r = self.client.post(path=self.login_url, data=data)
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        # Inactive users are redirected to welcome url ('/welcome/') instead of their user profile url.
        self.assert_me_url_redirects_to_welcome_url()

    def test_visitor_cannot_login_using_wrong_email(self):
        data = {
            'username': self.other_user_email.email,
            'password': tests_settings.USER_PASSWORD,
        }
        r = self.client.post(path=self.login_url, data=data)
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._please_enter_a_correct_username_and_password_errors_dict())
        self.assert_me_url_redirects_to_login_url()

    def test_visitor_cannot_login_using_wrong_password(self):
        self.assertEqual(first=self.user.slug, second='slug-with-dots')
        data = {
            'username': 'slug-with-dots',
            'password': 'wrong password!!',
        }
        r = self.client.post(path=self.login_url, data=data)
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._please_enter_a_correct_username_and_password_errors_dict())
        self.assert_me_url_redirects_to_login_url()


@only_on_sites_with_login
class LoginViewEnglishTestCase(LoginViewTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='en')


@only_on_sites_with_login
@override_settings(LANGUAGE_CODE='he')
class LoginViewHebrewTestCase(LoginViewTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='he')


@only_on_sites_with_login
class LogoutViewTestCase(SpeedyCoreAccountsModelsMixin, SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            unconfirmed_email_address_count=0,
        )

    def test_user_can_logout(self):
        r = self.client.get(path='/logout/')
        self.assertEqual(first=r.status_code, second=200)
        r = self.client.get(path='/')
        self.assertFalse(expr=r.context['user'].is_authenticated)


class EditProfileViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin):
    page_url = '/edit-profile/'

    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.data = {
            'date_of_birth': '1976-06-03',
            'slug': self.user.slug,
            'gender': 1,
        }
        self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            unconfirmed_email_address_count=0,
        )
        self.assertEqual(first=self.user.username, second=self.user.slug)
        self.assertEqual(first=len(self.user.username), second=12)
        self.assertEqual(first=len(self.user.slug), second=12)

    def setup_required_fields(self):
        self.required_fields = self.data.keys()
        self.assert_profile_form_required_fields(required_fields=self.required_fields)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(path=self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/account.html')

    def test_user_can_save_his_settings(self):
        r = self.client.post(path=self.page_url, data=self.data)
        self.assertRedirects(response=r, expected_url=self.page_url)
        user = User.objects.get(pk=self.user.pk)
        # TODO - uncomment these lines
        self.assertEqual(first=user.first_name, second=self.first_name)
        self.assertEqual(first=user.first_name_en, second=self.first_name)
        self.assertEqual(first=user.first_name_he, second=self.first_name) # ~~~~ TODO - uncomment these lines
        self.assertEqual(first=user.last_name, second=self.last_name)
        self.assertEqual(first=user.last_name_en, second=self.last_name)
        self.assertEqual(first=user.last_name_he, second=self.last_name) # ~~~~ TODO - uncomment these lines
        for (key, value) in self.data.items():
            if (not (key in ['date_of_birth'])):
                self.assertEqual(first=getattr(user, key), second=value)
        self.assertEqual(first=user.date_of_birth, second=date(year=1976, month=6, day=3))

    def run_test_required_fields(self, data):
        self.first_name = self.user.first_name
        self.last_name = self.user.last_name
        r = self.client.post(path=self.page_url, data=data)
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._profile_form_all_the_required_fields_are_required_errors_dict())
        user = User.objects.get(pk=self.user.pk)
        # TODO - uncomment these lines
        self.assertEqual(first=user.first_name, second=self.first_name)
        self.assertEqual(first=user.first_name_en, second=self.first_name)
        self.assertEqual(first=user.first_name_he, second=self.first_name) # ~~~~ TODO - uncomment these lines
        self.assertEqual(first=user.last_name, second=self.last_name)
        self.assertEqual(first=user.last_name_en, second=self.last_name)
        self.assertEqual(first=user.last_name_he, second=self.last_name) # ~~~~ TODO - uncomment these lines

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
        self.assertRedirects(response=r, expected_url=self.page_url)
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(first=user.slug, second=normalize_slug(slug=new_slug))
        self.assertNotEqual(first=user.slug, second=old_slug)
        # print("run_test_user_can_change_his_slug", old_slug, normalize_username(username=old_slug), new_slug, normalize_username(username=new_slug), user.slug, normalize_username(username=user.slug)) # ~~~~ TODO: remove this line!

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
        # print("run_test_user_cannot_change_his_username", old_slug, normalize_username(username=old_slug), new_slug, normalize_username(username=new_slug), user.slug, normalize_username(username=user.slug)) # ~~~~ TODO: remove this line!

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
        for date_of_birth in tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST:
            print("test_valid_date_of_birth_list_ok", date_of_birth) # ~~~~ TODO: remove this line!
            data = self.data.copy()
            data['date_of_birth'] = date_of_birth
            r = self.client.post(path=self.page_url, data=data)
            self.assertRedirects(response=r, expected_url=self.page_url, msg_prefix="{} is not a valid date of birth.".format(date_of_birth))
            user = User.objects.get(pk=self.user.pk)
            # TODO - uncomment these lines
            self.assertEqual(first=user.first_name, second=self.first_name)
            self.assertEqual(first=user.first_name_en, second=self.first_name)
            self.assertEqual(first=user.first_name_he, second=self.first_name)
            self.assertEqual(first=user.last_name, second=self.last_name)
            self.assertEqual(first=user.last_name_en, second=self.last_name)
            self.assertEqual(first=user.last_name_he, second=self.last_name)
            for (key, value) in self.data.items():
                if (not (key in ['date_of_birth'])):
                    self.assertEqual(first=getattr(user, key), second=value)
            self.assertEqual(first=user.date_of_birth, second=datetime.strptime(date_of_birth, '%Y-%m-%d').date())

    def test_invalid_date_of_birth_list_fail(self):
        self.date_of_birth = self.user.date_of_birth
        self.last_name = self.user.last_name
        for date_of_birth in tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST:
            print("test_invalid_date_of_birth_list_fail", date_of_birth) # ~~~~ TODO: remove this line!
            data = self.data.copy()
            data['date_of_birth'] = date_of_birth
            r = self.client.post(path=self.page_url, data=data)
            self.assertEqual(first=r.status_code, second=200, msg="{} is a valid date of birth.".format(date_of_birth))
            self.assertDictEqual(d1=r.context['form'].errors, d2=self._date_of_birth_errors_dict_by_date_of_birth(date_of_birth=date_of_birth), msg='"{}" - Unexpected error messages.'.format(date_of_birth))
            user = User.objects.get(pk=self.user.pk)
            self.assertEqual(first=user.date_of_birth, second=self.date_of_birth)


@only_on_sites_with_login
class EditProfileViewEnglishTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
    def setup(self):
        super().setup()
        self.data.update({
            'first_name_en': "Jennifer",
            'last_name_en': "Connelly",
        })
        self.first_name = "Jennifer"
        self.last_name = "Connelly"
        self.setup_required_fields()

    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='en')


@only_on_sites_with_login
@override_settings(LANGUAGE_CODE='he')
class EditProfileViewHebrewTestCase(EditProfileViewTestCaseMixin, SiteTestCase):
    def setup(self):
        super().setup()
        self.data.update({
            'first_name_he': "ג'ניפר",
            'last_name_he': "קונלי",
        })
        self.first_name = "ג'ניפר"
        self.last_name = "קונלי"
        self.setup_required_fields()

    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='he')


@only_on_sites_with_login
class EditProfilePrivacyViewTestCase(SpeedyCoreAccountsModelsMixin, SiteTestCase):
    page_url = '/edit-profile/privacy/'

    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=0,
        )

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(path=self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/privacy.html')

    def test_user_can_save_his_settings_1(self):
        data = {
            'access_dob_day_month': '2',
            'access_dob_year': '4',
        }
        r = self.client.post(path=self.page_url, data=data)
        self.assertRedirects(response=r, expected_url=self.page_url)
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(first=user.access_dob_day_month, second=2)
        self.assertEqual(first=user.access_dob_year, second=4)

    def test_user_can_save_his_settings_2(self):
        data = {
            'access_dob_day_month': '4',
            'access_dob_year': '2',
        }
        r = self.client.post(path=self.page_url, data=data)
        self.assertRedirects(response=r, expected_url=self.page_url)
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(first=user.access_dob_day_month, second=4)
        self.assertEqual(first=user.access_dob_year, second=2)


@only_on_sites_with_login
class EditProfileNotificationsViewTestCase(SpeedyCoreAccountsModelsMixin, SiteTestCase):
    page_url = '/edit-profile/notifications/'

    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            unconfirmed_email_address_count=0,
        )

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(path=self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/notifications.html')

    @exclude_on_speedy_match
    def test_user_can_save_his_settings(self):
        self.assertEqual(first=self.user.notify_on_message, second=User.NOTIFICATIONS_ON)
        data = {
            'notify_on_message': User.NOTIFICATIONS_OFF,
        }
        r = self.client.post(path=self.page_url, data=data)
        self.assertRedirects(response=r, expected_url=self.page_url)
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(first=user.notify_on_message, second=User.NOTIFICATIONS_OFF)


class EditProfileCredentialsViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin):
    page_url = '/edit-profile/credentials/'

    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=0,
        )

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(path=self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/credentials.html')

    def test_user_can_change_password(self):
        new_password = '8' * 8
        incorrect_new_password = '1' * 8
        data = {
            'old_password': tests_settings.USER_PASSWORD,
            'new_password1': new_password,
            'new_password2': new_password,
        }
        r = self.client.post(path=self.page_url, data=data)
        self.assertRedirects(response=r, expected_url=self.page_url)
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(expr=user.check_password(raw_password=new_password))
        self.assertFalse(expr=user.check_password(raw_password=incorrect_new_password))
        self.assertFalse(expr=user.check_password(raw_password=tests_settings.USER_PASSWORD))

    def test_old_password_incorrect(self):
        incorrect_old_password = '7' * 8
        new_password = '8' * 8
        data = {
            'old_password': incorrect_old_password,
            'new_password1': new_password,
            'new_password2': new_password,
        }
        r = self.client.post(path=self.page_url, data=data)
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._your_old_password_was_entered_incorrectly_errors_dict())
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(expr=user.check_password(raw_password=tests_settings.USER_PASSWORD))
        self.assertFalse(expr=user.check_password(raw_password=new_password))
        self.assertFalse(expr=user.check_password(raw_password=incorrect_old_password))

    def test_password_too_short(self):
        new_password = '8' * 3
        data = {
            'old_password': tests_settings.USER_PASSWORD,
            'new_password1': new_password,
            'new_password2': new_password,
        }
        r = self.client.post(path=self.page_url, data=data)
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_too_short_errors_dict(field_names=self._both_password_field_names))
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(expr=user.check_password(raw_password=tests_settings.USER_PASSWORD))
        self.assertFalse(expr=user.check_password(raw_password=new_password))

    def test_password_too_long(self):
        new_password = '8' * 121
        data = {
            'old_password': tests_settings.USER_PASSWORD,
            'new_password1': new_password,
            'new_password2': new_password,
        }
        r = self.client.post(path=self.page_url, data=data)
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_too_long_errors_dict(field_names=self._both_password_field_names))
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(expr=user.check_password(raw_password=tests_settings.USER_PASSWORD))
        self.assertFalse(expr=user.check_password(raw_password=new_password))

    def test_passwords_dont_match(self):
        new_password_1 = '8' * 8
        new_password_2 = '7' * 8
        data = {
            'old_password': tests_settings.USER_PASSWORD,
            'new_password1': new_password_1,
            'new_password2': new_password_2,
        }
        r = self.client.post(path=self.page_url, data=data)
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._the_two_password_fields_didnt_match_errors_dict())
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(expr=user.check_password(raw_password=tests_settings.USER_PASSWORD))
        self.assertFalse(expr=user.check_password(raw_password=new_password_1))
        self.assertFalse(expr=user.check_password(raw_password=new_password_2))


@only_on_sites_with_login
class EditProfileCredentialsViewEnglishTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='en')


@only_on_sites_with_login
@override_settings(LANGUAGE_CODE='he')
class EditProfileCredentialsViewHebrewTestCase(EditProfileCredentialsViewTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='he')


@only_on_sites_with_login
class ActivateSiteProfileViewTestCase(SpeedyCoreAccountsModelsMixin, SiteTestCase):
    page_url = '/welcome/'

    def setup(self):
        super().setup()
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

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_inactive_user_has_no_access_to_other_pages(self):
        r = self.client.get(path='/other-page/')
        self.assertRedirects(response=r, expected_url=self.page_url, fetch_redirect_response=False)

    def test_inactive_user_can_open_the_page(self):
        r = self.client.get(path=self.page_url)
        self.assertIn(member=r.status_code, container={200, 302})
        if (r.status_code == 200):
            self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/activate.html')

    @exclude_on_speedy_match
    def test_inactive_user_can_request_activation(self):
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(first=user.is_active, second=True)
        self.assertEqual(first=user.profile.is_active, second=True)


@only_on_sites_with_login
class DeactivateSiteProfileViewTestCase(SpeedyCoreAccountsModelsMixin, SiteTestCase):
    page_url = '/edit-profile/deactivate/'

    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            unconfirmed_email_address_count=0,
        )

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
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
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(first=user.is_active, second={django_settings.SPEEDY_NET_SITE_ID: False, django_settings.SPEEDY_MATCH_SITE_ID: True}[self.site.id])
        self.assertEqual(first=user.profile.is_active, second=False)


class VerifyUserEmailAddressViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 2, django_settings.SPEEDY_MATCH_SITE_ID: 3}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=1,
        )

    def test_wrong_link_gives_404(self):
        user_email_address = UserEmailAddressFactory()
        token = user_email_address._generate_confirmation_token()
        r = self.client.get(path='/edit-profile/emails/verify/{}/'.format(token))
        self.assertEqual(first=r.status_code, second=404)

    def test_confirmed_email_link_redirects_to_edit_profile(self):
        self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
        email_id = self.confirmed_email_address.id
        token = self.confirmed_email_address.confirmation_token
        r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get(path='/edit-profile/')
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._youve_already_confirmed_this_email_address_error_message])

    def test_unconfirmed_email_link_confirms_email(self):
        self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
        email_id = self.unconfirmed_email_address.id
        token = self.unconfirmed_email_address.confirmation_token
        r = self.client.get(path='/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get(path='/edit-profile/')
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._youve_confirmed_your_email_address_error_message])
        self.assertTrue(expr=UserEmailAddress.objects.get(pk=self.unconfirmed_email_address.pk).is_confirmed)


@only_on_sites_with_login
class VerifyUserEmailAddressViewEnglishTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='en')


@only_on_sites_with_login
@override_settings(LANGUAGE_CODE='he')
class VerifyUserEmailAddressViewHebrewTestCase(VerifyUserEmailAddressViewTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='he')


class AddUserEmailAddressViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=0,
        )

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(path='/edit-profile/emails/add/')
        self.assertRedirects(response=r, expected_url='/login/?next=/edit-profile/emails/add/')

    def test_user_can_open_the_page(self):
        r = self.client.get(path='/edit-profile/emails/add/')
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/email_address_form.html')

    def test_non_unique_confirmed_email_address(self):
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
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
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=0,
        )

    def test_non_unique_unconfirmed_email_address(self):
        self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 2, django_settings.SPEEDY_MATCH_SITE_ID: 3}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=1,
        )
        data = {
            'email': self.unconfirmed_email_address.email,
        }
        r = self.client.post(path='/edit-profile/emails/add/', data=data)
        email_address = UserEmailAddress.objects.get(email=self.unconfirmed_email_address.email)
        self.assertFalse(expr=email_address.is_primary)
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 2, django_settings.SPEEDY_MATCH_SITE_ID: 3}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=1,
        )

    def test_user_can_add_email_address(self):
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=0,
        )
        data = {
            'email': 'email@example.com',
        }
        r = self.client.post(path='/edit-profile/emails/add/', data=data)
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        email_address = UserEmailAddress.objects.get(email='email@example.com')
        self.assertFalse(expr=email_address.is_primary)
        r = self.client.get(path='/edit-profile/')
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._a_confirmation_message_was_sent_to_email_address_error_message_by_email_address(email_address='email@example.com')])
        self.assertEqual(first=len(mail.outbox), second=1)
        self.assertEqual(first=mail.outbox[0].subject, second='Confirm your email address on {}'.format(self.site.name))
        self.assertIn(member=email_address.confirmation_token, container=mail.outbox[0].body)
        # self.assertIn(member=UserEmailAddress.objects.get(email='email@example.com').confirmation_token, container=mail.outbox[0].body) # ~~~~ TODO: remove this line!
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 2, django_settings.SPEEDY_MATCH_SITE_ID: 3}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=1,
        )

    def test_first_email_is_primary(self):
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=0,
        )
        self.confirmed_email_address.delete()
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            unconfirmed_email_address_count=0,
        )
        data = {
            'email': 'email@example.com',
        }
        r = self.client.post(path='/edit-profile/emails/add/', data=data)
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        email_address = UserEmailAddress.objects.get(email='email@example.com')
        self.assertTrue(expr=email_address.is_primary)
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 0, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id],
            unconfirmed_email_address_count=1,
        )


@only_on_sites_with_login
class AddUserEmailAddressViewEnglishTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='en')


@only_on_sites_with_login
@override_settings(LANGUAGE_CODE='he')
class AddUserEmailAddressViewHebrewTestCase(AddUserEmailAddressViewTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='he')


class SendConfirmationEmailViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
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
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 3, django_settings.SPEEDY_MATCH_SITE_ID: 4}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=2,
        )

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(path=self.unconfirmed_email_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.unconfirmed_email_address_url))

    def test_user_has_no_access_to_other_users_address(self):
        r = self.client.post(path=self.other_user_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.other_user_address_url))

    def test_user_can_resend_confirmation(self):
        email_address = UserEmailAddress.objects.get(email=self.unconfirmed_email_address.email)
        r = self.client.post(path=self.unconfirmed_email_address_url)
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get(path='/edit-profile/')
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._a_confirmation_message_was_sent_to_email_address_error_message_by_email_address(email_address=self.unconfirmed_email_address.email)])
        self.assertEqual(first=len(mail.outbox), second=1)
        self.assertEqual(first=mail.outbox[0].subject, second='Confirm your email address on {}'.format(self.site.name))
        self.assertIn(member=email_address.confirmation_token, container=mail.outbox[0].body)
        # self.assertIn(member=UserEmailAddress.objects.get(email=self.unconfirmed_email_address.email).confirmation_token, container=mail.outbox[0].body) # ~~~~ TODO: remove this line!


@only_on_sites_with_login
class SendConfirmationEmailViewEnglishTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='en')


@only_on_sites_with_login
@override_settings(LANGUAGE_CODE='he')
class SendConfirmationEmailViewHebrewTestCase(SendConfirmationEmailViewTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='he')


class DeleteUserEmailAddressViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=False)
        self.confirmed_email_address_url = '/edit-profile/emails/{}/delete/'.format(self.confirmed_email_address.id)
        self.primary_address = UserEmailAddressFactory(user=self.user, is_primary=True)
        self.primary_address_url = '/edit-profile/emails/{}/delete/'.format(self.primary_address.id)
        self.other_user_address = UserEmailAddressFactory(is_primary=False)
        self.other_user_address_url = '/edit-profile/emails/{}/delete/'.format(self.other_user_address.id)
        self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
        self.assert_models_count(
            entity_count=2,
            user_count=2,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 3, django_settings.SPEEDY_MATCH_SITE_ID: 4}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=2,
        )

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(path=self.confirmed_email_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.confirmed_email_address_url))

    def test_user_has_no_access_to_other_users_address(self):
        r = self.client.post(path=self.other_user_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.other_user_address_url))

    def test_user_cannot_delete_primary_email_address(self):
        r = self.client.post(path=self.primary_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.primary_address_url))

    @exclude_on_speedy_match
    def test_user_can_delete_email_address(self):
        self.assertEqual(first=self.user.email_addresses.count(), second=2)
        r = self.client.post(path=self.confirmed_email_address_url)
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get(path='/edit-profile/')
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._the_email_address_was_deleted_error_message])
        self.assertEqual(first=self.user.email_addresses.count(), second=1)


@only_on_sites_with_login
class DeleteUserEmailAddressViewEnglishTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='en')


@only_on_sites_with_login
@override_settings(LANGUAGE_CODE='he')
class DeleteUserEmailAddressViewHebrewTestCase(DeleteUserEmailAddressViewTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='he')


class SetPrimaryUserEmailAddressViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.unconfirmed_email_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.unconfirmed_email_address.id)
        self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.confirmed_email_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.confirmed_email_address.id)
        self.primary_address = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.primary_address_url = '/edit-profile/emails/{}/delete/'.format(self.primary_address.id)
        self.other_user_address = UserEmailAddressFactory()
        self.other_user_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.other_user_address.id)
        self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
        self.assert_models_count(
            entity_count=2,
            user_count=2,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 4, django_settings.SPEEDY_MATCH_SITE_ID: 5}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 2, django_settings.SPEEDY_MATCH_SITE_ID: 3}[self.site.id],
            unconfirmed_email_address_count=2,
        )

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(path=self.confirmed_email_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.confirmed_email_address_url))

    def test_user_has_no_access_to_other_users_address(self):
        r = self.client.post(path=self.other_user_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.other_user_address_url))

    def test_user_cannot_make_unconfirmed_email_address_primary(self):
        r = self.client.post(path=self.unconfirmed_email_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.unconfirmed_email_address_url))

    @exclude_on_speedy_match
    def test_user_can_make_confirmed_email_address_primary(self):
        self.assertEqual(first=self.user.email_addresses.count(), second=3)
        self.assertEqual(first=self.user.email_addresses.filter(is_confirmed=True).count(), second=2)
        self.assertEqual(first=self.user.email_addresses.get(is_primary=True), second=self.primary_address)
        r = self.client.post(path=self.confirmed_email_address_url)
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get(path='/edit-profile/')
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._you_have_changed_your_primary_email_address_error_message])
        self.assertEqual(first=self.user.email_addresses.count(), second=3)
        self.assertEqual(first=self.user.email_addresses.filter(is_confirmed=True).count(), second=2)
        self.assertEqual(first=self.user.email_addresses.get(is_primary=True), second=self.confirmed_email_address)


@only_on_sites_with_login
class SetPrimaryUserEmailAddressViewEnglishTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='en')


@only_on_sites_with_login
@override_settings(LANGUAGE_CODE='he')
class SetPrimaryUserEmailAddressViewHebrewTestCase(SetPrimaryUserEmailAddressViewTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='he')


@only_on_sites_with_login
class PasswordResetViewTestCase(SpeedyCoreAccountsModelsMixin, SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.assert_models_count(
            entity_count=1,
            user_count=1,
            user_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            confirmed_email_address_count={django_settings.SPEEDY_NET_SITE_ID: 1, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id],
            unconfirmed_email_address_count=0,
        )

    def test_visitor_can_open_the_page(self):
        r = self.client.get(path='/reset-password/')
        self.assertEqual(first=r.status_code, second=200)

    def test_visitor_can_reset_password(self):
        data = {
            'email': self.email.email,
        }
        r = self.client.post(path='/reset-password/', data=data)
        self.assertRedirects(response=r, expected_url='/reset-password/done/')
        self.assertEqual(first=len(mail.outbox), second=1)
        self.assertEqual(first=mail.outbox[0].subject, second='Password Reset on {}'.format(self.site.name))


# ~~~~ TODO: test ProfileForm - try to change username and get error message. ("You can't change your username.")
