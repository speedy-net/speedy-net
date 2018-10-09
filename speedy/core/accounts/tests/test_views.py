from datetime import date

from django.conf import settings
from django.core import mail

from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software, exclude_on_speedy_match, exclude_on_speedy_net
from speedy.core.accounts.models import normalize_slug, normalize_username, Entity, User, UserEmailAddress
from .test_factories import get_random_user_password, USER_PASSWORD, ActiveUserFactory, UserEmailAddressFactory, InactiveUserFactory


class RedirectMeMixin(object):
    def assert_me_url_redirects(self, expected_url):
        r = self.client.get('/me/')
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


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class IndexViewTestCase(TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])

    def test_visitor_gets_registration_page(self):
        r = self.client.get('/')
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/registration.html')


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class MeViewTestCase(RedirectMeMixin, TestCase):
    def set_up(self):
        self.user = ActiveUserFactory(slug='markmark')
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])

    def test_visitor_has_no_access(self):
        self.assert_me_url_redirects_to_login_url()

    def test_user_gets_redirected_to_his_profile(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)
        # Assert expected_url directly once to confirm.
        self.assert_me_url_redirects(expected_url='/markmark/')


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class LoginTestCase(RedirectMeMixin, TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()
        self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 2, self.SPEEDY_MATCH_SITE_ID: 3}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])

    def test_user_can_login_with_slug(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_user_can_login_with_username(self):
        self.client.login(username=self.user.username, password=USER_PASSWORD)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_user_can_login_with_confirmed_email_address(self):
        self.client.login(username=self.confirmed_email_address.email, password=USER_PASSWORD)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_user_can_login_with_unconfirmed_email_address(self):
        self.client.login(username=self.unconfirmed_email_address.email, password=USER_PASSWORD)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_user_cannot_login_with_wrong_slug(self):
        self.client.login(username='a{}'.format(self.user.slug), password=USER_PASSWORD)
        self.assert_me_url_redirects_to_login_url()

    def test_user_cannot_login_with_wrong_username(self):
        self.client.login(username='a{}'.format(self.user.slug), password=USER_PASSWORD)
        self.assert_me_url_redirects_to_login_url()

    def test_user_cannot_login_with_wrong_email(self):
        self.client.login(username='a{}'.format(self.confirmed_email_address.email), password=USER_PASSWORD)
        self.assert_me_url_redirects_to_login_url()

    def test_user_cannot_login_with_wrong_password(self):
        self.client.login(username=self.user.slug, password='{}-'.format(USER_PASSWORD))
        self.assert_me_url_redirects_to_login_url()


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class RegistrationViewTestCase(TestCase):
    def set_up(self):
        self.password = get_random_user_password()
        self.data = {
            'first_name_en': 'First',
            'last_name_en': 'Last',
            'email': 'email@example.com',
            'slug': 'user-1234',
            'date_of_birth': '1980-08-20',
            'gender': 1,
            'new_password1': self.password,
        }
        self.username = normalize_username(self.data['slug'])
        self.slug = normalize_slug(self.data['slug'])
        self.assertNotEqual(first=self.password, second=USER_PASSWORD)
        self.assertEqual(first=self.username, second='user1234')
        self.assertEqual(first=self.slug, second='user-1234')
        self.assertNotEqual(first=self.username, second=self.slug)
        self.assertEqual(first=Entity.objects.count(), second=0)
        self.assertEqual(first=User.objects.count(), second=0)
        self.assertEqual(first=UserEmailAddress.objects.count(), second=0)
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second=0)

    def test_visitor_can_see_registration_page(self):
        r = self.client.get('/')
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/registration.html')

    def test_visitor_can_register(self):
        r = self.client.post('/', data=self.data)
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second=0)
        entity = Entity.objects.get(username=self.username)
        user = User.objects.get(username=self.username)
        self.assertEqual(first=user, second=entity.user)
        self.assertEqual(first=entity.id, second=user.id)
        self.assertEqual(first=entity.username, second=user.username)
        self.assertEqual(first=entity.slug, second=user.slug)
        self.assertEqual(first=len(entity.id), second=15)
        self.assertTrue(expr=user.check_password(raw_password=self.password))
        self.assertFalse(expr=user.check_password(raw_password=USER_PASSWORD))
        self.assertEqual(first=user.first_name, second='First')
        self.assertEqual(first=user.first_name_en, second='First')
        self.assertEqual(first=user.last_name, second='Last')
        self.assertEqual(first=user.last_name_en, second='Last')
        self.assertEqual(first=user.username, second=self.username)
        self.assertEqual(first=user.username, second='user1234')
        self.assertEqual(first=user.slug, second=self.slug)
        self.assertEqual(first=user.slug, second='user-1234')
        self.assertEqual(first=user.email_addresses.count(), second=1)
        self.assertEqual(first=user.email_addresses.first().email, second='email@example.com')
        self.assertFalse(expr=user.email_addresses.first().is_confirmed)
        self.assertTrue(expr=user.email_addresses.first().is_primary)

    def test_non_unique_confirmed_email_address(self):
        UserEmailAddressFactory(email=self.data['email'], is_confirmed=True)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        r = self.client.post('/', data=self.data)
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._this_email_is_already_in_use_errors_dict)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])

    def test_unique_confirmed_email_address(self):
        UserEmailAddressFactory(email='a{}'.format(self.data['email']), is_confirmed=True)
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        r = self.client.post('/', data=self.data)
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        self.assertEqual(first=Entity.objects.count(), second=2)
        self.assertEqual(first=User.objects.count(), second=2)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 2, self.SPEEDY_MATCH_SITE_ID: 3}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])

    def test_non_unique_unconfirmed_email_address(self):
        # Unconfirmed email address is deleted if another user adds it again.
        UserEmailAddressFactory(email=self.data['email'], is_confirmed=False)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        r = self.client.post('/', data=self.data)
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        self.assertEqual(first=Entity.objects.count(), second=2)
        self.assertEqual(first=User.objects.count(), second=2)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])

    def test_unique_unconfirmed_email_address(self):
        UserEmailAddressFactory(email='a{}'.format(self.data['email']), is_confirmed=False)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        r = self.client.post('/', data=self.data)
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        self.assertEqual(first=Entity.objects.count(), second=2)
        self.assertEqual(first=User.objects.count(), second=2)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 2, self.SPEEDY_MATCH_SITE_ID: 3}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])

    def test_password_too_short(self):
        self.data['new_password1'] = '8' * 3
        r = self.client.post('/', data=self.data)
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_too_short_errors_dict)
        self.assertEqual(first=Entity.objects.count(), second=0)
        self.assertEqual(first=User.objects.count(), second=0)
        self.assertEqual(first=UserEmailAddress.objects.count(), second=0)

    def test_password_too_long(self):
        self.data['new_password1'] = '8' * 121
        r = self.client.post('/', data=self.data)
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_too_long_errors_dict)
        self.assertEqual(first=Entity.objects.count(), second=0)
        self.assertEqual(first=User.objects.count(), second=0)
        self.assertEqual(first=UserEmailAddress.objects.count(), second=0)

    def test_user_is_logged_in_after_registration(self):
        r = self.client.post('/', data=self.data)
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        r = self.client.get('/')
        if settings.ACTIVATE_PROFILE_AFTER_REGISTRATION:
            self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
            r = self.client.get('/{}/'.format(self.data['slug']))
        else:
            self.assertRedirects(response=r, expected_url='/welcome/', fetch_redirect_response=False)
            r = self.client.get('/welcome/')
        self.assertTrue(expr=r.context['user'].is_authenticated)
        self.assertEqual(first=r.context['user'].username, second='user1234')
        self.assertEqual(first=r.context['user'].slug, second='user-1234')

    def test_user_gets_email_after_registration_in_english(self):
        r = self.client.post('/', data=self.data)
        self.assertEqual(first=len(mail.outbox), second=1)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second=0)
        user = User.objects.get(username=self.username)
        email = user.email_addresses.first()
        self.assertFalse(expr=email.is_confirmed)
        self.assertEqual(first=email.confirmation_sent, second=1)
        self.assertEqual(first=mail.outbox[0].subject, second='Confirm your email address on {}'.format(self.site.name))
        self.assertIn(member=UserEmailAddress.objects.get(email='email@example.com').confirmation_token, container=mail.outbox[0].body)
        self.assertIn(member='http://en.localhost/', container=mail.outbox[0].body)

    def test_user_gets_email_after_registration_in_hebrew(self):
        self.data['first_name_he'] = 'First HE'
        self.data['last_name_he'] = 'Last HE'
        r = self.client.post('/', data=self.data, HTTP_HOST='he.localhost')
        self.assertIn(member='http://he.localhost/', container=mail.outbox[0].body)

    def test_cannot_register_taken_username(self):
        existing_user = ActiveUserFactory(username='username', slug='user-name')
        self.data['slug'] = 'us-er-na-me'
        r = self.client.post('/', data=self.data)
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._this_username_is_already_taken_errors_dict)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class LoginViewTestCase(RedirectMeMixin, TestCase):
    _other_user_password = '8' * 8
    
    def set_up(self):
        self.user = ActiveUserFactory(slug='slug.with.dots')
        self.user_email = UserEmailAddressFactory(user=self.user)
        self.other_user_email = UserEmailAddressFactory()
        self.other_user = self.other_user_email.user
        self.other_user.set_password(raw_password=self._other_user_password)
        self.other_user.save_user_and_profile()
        self.inactive_user = InactiveUserFactory()
        self.assertNotEqual(first=self.user_email.email, second=self.other_user_email.email)
        self.assertNotEqual(first=USER_PASSWORD, second=self._other_user_password)
        self.assertEqual(first=Entity.objects.count(), second=3)
        self.assertEqual(first=User.objects.count(), second=3)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 2, self.SPEEDY_MATCH_SITE_ID: 4}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])

    def test_visitor_can_see_login_page(self):
        r = self.client.get('/login/')
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/login.html')

    def test_visitor_can_login_using_slug(self):
        self.assertEqual(first=self.user.slug, second='slug-with-dots')
        r = self.client.post('/login/', data={
            'username': self.user.slug,
            'password': USER_PASSWORD,
        })
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)
        # Assert expected_url directly once to confirm.
        self.assert_me_url_redirects(expected_url='/slug-with-dots/')

    def test_visitor_can_login_using_username(self):
        self.assertEqual(first=self.user.username, second='slugwithdots')
        r = self.client.post('/login/', data={
            'username': self.user.username,
            'password': USER_PASSWORD,
        })
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_visitor_can_login_using_original_slug(self):
        self.assertEqual(first=self.user.slug, second='slug-with-dots')
        r = self.client.post('/login/', data={
            'username': 'slug.with.dots',
            'password': USER_PASSWORD,
        })
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_visitor_can_login_using_slug_modified(self):
        self.assertEqual(first=self.user.slug, second='slug-with-dots')
        r = self.client.post('/login/', data={
            'username': 'slug____with.....dots---',
            'password': USER_PASSWORD,
        })
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_visitor_can_login_using_slug_uppercase(self):
        self.assertEqual(first=self.user.slug, second='slug-with-dots')
        r = self.client.post('/login/', data={
            'username': 'SLUG-WITH-DOTS',
            'password': USER_PASSWORD,
        })
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_visitor_can_login_using_email(self):
        r = self.client.post('/login/', data={
            'username': self.user_email.email,
            'password': USER_PASSWORD,
        })
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_visitor_can_login_using_email_uppercase(self):
        r = self.client.post('/login/', data={
            'username': self.user_email.email.upper(),
            'password': USER_PASSWORD,
        })
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)

    def test_visitor_can_login_using_other_user_email_and_password(self):
        r = self.client.post('/login/', data={
            'username': self.other_user_email.email,
            'password': self._other_user_password,
        })
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.other_user)

    def test_visitor_still_can_login_if_he_is_not_active_user(self):
        r = self.client.post('/login/', data={
            'username': self.inactive_user.slug,
            'password': USER_PASSWORD,
        })
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        # Inactive users are redirected to welcome url ('/welcome/') instead of their user profile url.
        self.assert_me_url_redirects_to_welcome_url()

    def test_visitor_cannot_login_using_wrong_email(self):
        r = self.client.post('/login/', data={
            'username': self.other_user_email.email,
            'password': USER_PASSWORD,
        })
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._incorrect_username_and_password_errors_dict)
        self.assert_me_url_redirects_to_login_url()

    def test_visitor_cannot_login_using_wrong_password(self):
        self.assertEqual(first=self.user.slug, second='slug-with-dots')
        r = self.client.post('/login/', data={
            'username': 'slug-with-dots',
            'password': 'wrong password!!',
        })
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._incorrect_username_and_password_errors_dict)
        self.assert_me_url_redirects_to_login_url()


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class LogoutViewTestCase(TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])

    def test_user_can_logout(self):
        r = self.client.get('/logout/')
        self.assertEqual(first=r.status_code, second=200)
        r = self.client.get('/')
        self.assertFalse(expr=r.context['user'].is_authenticated)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class EditProfileViewTestCase(TestCase):
    page_url = '/edit-profile/'

    def set_up(self):
        self.user = ActiveUserFactory()
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/account.html')

    def test_user_can_save_his_settings(self):
        data = {
            'first_name_en': 'Johnny',
            'last_name_en': 'English',
            'date_of_birth': '1976-06-03',
            'slug': self.user.slug,
            'gender': 1,
        }
        r = self.client.post(self.page_url, data)
        self.assertRedirects(response=r, expected_url=self.page_url)
        user = User.objects.get(id=self.user.id)
        for (key, value) in data.items():
            if key == 'date_of_birth':
                pass
            else:
                self.assertEqual(first=getattr(user, key), second=value)
        self.assertEqual(first=user.date_of_birth, second=date(year=1976, month=6, day=3))


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class EditProfilePrivacyViewTestCase(TestCase):
    page_url = '/edit-profile/privacy/'

    def set_up(self):
        self.user = ActiveUserFactory()
        self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/privacy.html')

    def test_user_can_save_his_settings_1(self):
        data = {
            'access_dob_day_month': '2',
            'access_dob_year': '4',
        }
        r = self.client.post(self.page_url, data)
        self.assertRedirects(response=r, expected_url=self.page_url)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(first=user.access_dob_day_month, second=2)
        self.assertEqual(first=user.access_dob_year, second=4)

    def test_user_can_save_his_settings_2(self):
        data = {
            'access_dob_day_month': '4',
            'access_dob_year': '2',
        }
        r = self.client.post(self.page_url, data)
        self.assertRedirects(response=r, expected_url=self.page_url)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(first=user.access_dob_day_month, second=4)
        self.assertEqual(first=user.access_dob_year, second=2)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class EditProfileNotificationsViewTestCase(TestCase):
    page_url = '/edit-profile/notifications/'

    def set_up(self):
        self.user = ActiveUserFactory()
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/notifications.html')

    @exclude_on_speedy_match
    def test_user_can_save_his_settings(self):
        self.assertEqual(first=self.user.notify_on_message, second=User.NOTIFICATIONS_ON)
        data = {
            'notify_on_message': User.NOTIFICATIONS_OFF,
        }
        r = self.client.post(self.page_url, data)
        self.assertRedirects(response=r, expected_url=self.page_url)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(first=user.notify_on_message, second=User.NOTIFICATIONS_OFF)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class EditProfileCredentialsViewTestCase(TestCase):
    page_url = '/edit-profile/credentials/'

    def set_up(self):
        self.user = ActiveUserFactory()
        self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/credentials.html')

    def test_user_can_change_password(self):
        new_password = '8' * 8
        incorrect_new_password = '1' * 8
        r = self.client.post(self.page_url, {
            'old_password': USER_PASSWORD,
            'new_password1': new_password,
            'new_password2': new_password,
        })
        self.assertRedirects(response=r, expected_url=self.page_url)
        user = User.objects.get(id=self.user.id)
        self.assertTrue(expr=user.check_password(raw_password=new_password))
        self.assertFalse(expr=user.check_password(raw_password=incorrect_new_password))
        self.assertFalse(expr=user.check_password(raw_password=USER_PASSWORD))

    def test_old_password_incorrect(self):
        incorrect_old_password = '7' * 8
        new_password = '8' * 8
        r = self.client.post(self.page_url, {
            'old_password': incorrect_old_password,
            'new_password1': new_password,
            'new_password2': new_password,
        })
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._your_old_password_was_entered_incorrectly_errors_dict)
        user = User.objects.get(id=self.user.id)
        self.assertTrue(expr=user.check_password(raw_password=USER_PASSWORD))
        self.assertFalse(expr=user.check_password(raw_password=new_password))
        self.assertFalse(expr=user.check_password(raw_password=incorrect_old_password))

    def test_password_too_short(self):
        new_password = '8' * 3
        r = self.client.post(self.page_url, {
            'old_password': USER_PASSWORD,
            'new_password1': new_password,
            'new_password2': new_password,
        })
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_too_short_errors_dict)
        user = User.objects.get(id=self.user.id)
        self.assertTrue(expr=user.check_password(raw_password=USER_PASSWORD))
        self.assertFalse(expr=user.check_password(raw_password=new_password))

    def test_password_too_long(self):
        new_password = '8' * 121
        r = self.client.post(self.page_url, {
            'old_password': USER_PASSWORD,
            'new_password1': new_password,
            'new_password2': new_password,
        })
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._password_too_long_errors_dict)
        user = User.objects.get(id=self.user.id)
        self.assertTrue(expr=user.check_password(raw_password=USER_PASSWORD))
        self.assertFalse(expr=user.check_password(raw_password=new_password))

    def test_passwords_dont_match(self):
        new_password_1 = '8' * 8
        new_password_2 = '7' * 8
        r = self.client.post(self.page_url, {
            'old_password': USER_PASSWORD,
            'new_password1': new_password_1,
            'new_password2': new_password_2,
        })
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._the_two_password_fields_didnt_match_errors_dict)
        user = User.objects.get(id=self.user.id)
        self.assertTrue(expr=user.check_password(raw_password=USER_PASSWORD))
        self.assertFalse(expr=user.check_password(raw_password=new_password_1))
        self.assertFalse(expr=user.check_password(raw_password=new_password_2))


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class ActivateSiteProfileViewTestCase(TestCase):
    page_url = '/welcome/'

    def set_up(self):
        self.user = InactiveUserFactory()
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertEqual(first=self.user.is_active, second={self.SPEEDY_NET_SITE_ID: False, self.SPEEDY_MATCH_SITE_ID: True}[self.site.id])
        self.assertEqual(first=self.user.profile.is_active, second=False)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second=0)
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second=0)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_inactive_user_has_no_access_to_other_pages(self):
        r = self.client.get('/other-page/')
        self.assertRedirects(response=r, expected_url=self.page_url, fetch_redirect_response=False)

    def test_inactive_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertIn(member=r.status_code, container={200, 302})
        if r.status_code == 200:
            self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/activate.html')

    @exclude_on_speedy_match
    def test_inactive_user_can_request_activation(self):
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(first=user.is_active, second=True)
        self.assertEqual(first=user.profile.is_active, second=True)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class DeactivateSiteProfileViewTestCase(TestCase):
    page_url = '/edit-profile/deactivate/'

    def set_up(self):
        self.user = ActiveUserFactory()
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/deactivate.html')

    def test_user_can_deactivate_his_account(self):
        self.assertEqual(first=self.user.is_active, second=True)
        self.assertEqual(first=self.user.profile.is_active, second=True)
        r = self.client.post(self.page_url, {
            'password': USER_PASSWORD,
        })
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(first=user.is_active, second={self.SPEEDY_NET_SITE_ID: False, self.SPEEDY_MATCH_SITE_ID: True}[self.site.id])
        self.assertEqual(first=user.profile.is_active, second=False)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class VerifyUserEmailAddressViewTestCase(TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()
        self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 2, self.SPEEDY_MATCH_SITE_ID: 3}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])

    def test_wrong_link_gives_404(self):
        user_email_address = UserEmailAddress()
        token = user_email_address._generate_confirmation_token()
        r = self.client.get('/edit-profile/emails/verify/{}/'.format(token))
        self.assertEqual(first=r.status_code, second=404)

    def test_confirmed_email_link_redirects_to_edit_profile(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        email_id = self.confirmed_email_address.id
        token = self.confirmed_email_address.confirmation_token
        r = self.client.get('/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn(member='You\'ve already confirmed this email address.', container=map(str, r.context['messages']))

    def test_unconfirmed_email_link_confirms_email(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        email_id = self.unconfirmed_email_address.id
        token = self.unconfirmed_email_address.confirmation_token
        r = self.client.get('/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn(member='You\'ve confirmed your email address.', container=map(str, r.context['messages']))
        self.assertTrue(expr=UserEmailAddress.objects.get(id=self.unconfirmed_email_address.id).is_confirmed)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class AddUserEmailAddressViewTestCase(TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()
        self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get('/edit-profile/emails/add/')
        self.assertRedirects(response=r, expected_url='/login/?next=/edit-profile/emails/add/')

    def test_user_can_open_the_page(self):
        r = self.client.get('/edit-profile/emails/add/')
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/email_address_form.html')

    def test_non_unique_confirmed_email_address(self):
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        r = self.client.post('/edit-profile/emails/add/', data={
            'email': self.confirmed_email_address.email,
        })
        self.assertEqual(first=r.status_code, second=200)
        self.assertDictEqual(d1=r.context['form'].errors, d2=self._this_email_is_already_in_use_errors_dict)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])

    def test_non_unique_unconfirmed_email_address(self):
        self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 2, self.SPEEDY_MATCH_SITE_ID: 3}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        r = self.client.post('/edit-profile/emails/add/', data={
            'email': self.unconfirmed_email_address.email,
        })
        email_address = UserEmailAddress.objects.get(email=self.unconfirmed_email_address.email)
        self.assertFalse(expr=email_address.is_primary)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 2, self.SPEEDY_MATCH_SITE_ID: 3}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])

    def test_user_can_add_email_address(self):
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        r = self.client.post('/edit-profile/emails/add/', data={
            'email': 'email@example.com',
        })
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        email_address = UserEmailAddress.objects.get(email='email@example.com')
        self.assertFalse(expr=email_address.is_primary)
        r = self.client.get('/edit-profile/')
        self.assertIn(member='A confirmation message was sent to email@example.com', container=map(str, r.context['messages']))
        self.assertEqual(first=len(mail.outbox), second=1)
        self.assertEqual(first=mail.outbox[0].subject, second='Confirm your email address on {}'.format(self.site.name))
        self.assertIn(member=UserEmailAddress.objects.get(email='email@example.com').confirmation_token, container=mail.outbox[0].body)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 2, self.SPEEDY_MATCH_SITE_ID: 3}[self.site.id])

    def test_first_email_is_primary(self):
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.confirmed_email_address.delete()
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 0, self.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        r = self.client.post('/edit-profile/emails/add/', data={
            'email': 'email@example.com',
        })
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        email_address = UserEmailAddress.objects.get(email='email@example.com')
        self.assertTrue(expr=email_address.is_primary)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class SendConfirmationEmailViewTestCase(TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()
        self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.unconfirmed_email_address_url = '/edit-profile/emails/{}/confirm/'.format(self.unconfirmed_email_address.id)
        self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.confirmed_email_address_url = '/edit-profile/emails/{}/confirm/'.format(self.confirmed_email_address.id)
        self.other_users_address = UserEmailAddressFactory()
        self.other_users_address_url = '/edit-profile/emails/{}/confirm/'.format(self.other_users_address.id)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertEqual(first=Entity.objects.count(), second=2)
        self.assertEqual(first=User.objects.count(), second=2)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 3, self.SPEEDY_MATCH_SITE_ID: 5}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 3}[self.site.id])

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.unconfirmed_email_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.unconfirmed_email_address_url))

    def test_user_has_no_access_to_other_users_address(self):
        r = self.client.post(self.other_users_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.other_users_address_url))

    def test_user_can_resend_confirmation(self):
        r = self.client.post(self.unconfirmed_email_address_url)
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn(member='A confirmation message was sent to {}'.format(self.unconfirmed_email_address.email), container=map(str, r.context['messages']))
        self.assertEqual(first=len(mail.outbox), second=1)
        self.assertEqual(first=mail.outbox[0].subject, second='Confirm your email address on {}'.format(self.site.name))
        self.assertIn(member=UserEmailAddress.objects.get(email=self.unconfirmed_email_address.email).confirmation_token, container=mail.outbox[0].body)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class DeleteUserEmailAddressViewTestCase(TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()
        self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=False)
        self.confirmed_email_address_url = '/edit-profile/emails/{}/delete/'.format(self.confirmed_email_address.id)
        self.primary_address = UserEmailAddressFactory(user=self.user, is_primary=True)
        self.primary_address_url = '/edit-profile/emails/{}/delete/'.format(self.primary_address.id)
        self.other_users_address = UserEmailAddressFactory(is_primary=False)
        self.other_users_address_url = '/edit-profile/emails/{}/delete/'.format(self.other_users_address.id)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertEqual(first=Entity.objects.count(), second=2)
        self.assertEqual(first=User.objects.count(), second=2)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 3, self.SPEEDY_MATCH_SITE_ID: 5}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 3}[self.site.id])

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.confirmed_email_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.confirmed_email_address_url))

    def test_user_has_no_access_to_other_users_address(self):
        r = self.client.post(self.other_users_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.other_users_address_url))

    def test_user_cannot_delete_primary_email_address(self):
        r = self.client.post(self.primary_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.primary_address_url))

    @exclude_on_speedy_match
    def test_user_can_delete_email_address(self):
        self.assertEqual(first=self.user.email_addresses.count(), second=2)
        r = self.client.post(self.confirmed_email_address_url)
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn(member='The email address was deleted.', container=map(str, r.context['messages']))
        self.assertEqual(first=self.user.email_addresses.count(), second=1)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class SetPrimaryUserEmailAddressViewTestCase(TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()
        self.unconfirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.unconfirmed_email_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.unconfirmed_email_address.id)
        self.confirmed_email_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.confirmed_email_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.confirmed_email_address.id)
        self.primary_address = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.primary_address_url = '/edit-profile/emails/{}/delete/'.format(self.primary_address.id)
        self.other_users_address = UserEmailAddressFactory()
        self.other_users_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.other_users_address.id)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertEqual(first=Entity.objects.count(), second=2)
        self.assertEqual(first=User.objects.count(), second=2)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 4, self.SPEEDY_MATCH_SITE_ID: 6}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 2, self.SPEEDY_MATCH_SITE_ID: 4}[self.site.id])

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.confirmed_email_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.confirmed_email_address_url))

    def test_user_has_no_access_to_other_users_address(self):
        r = self.client.post(self.other_users_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.other_users_address_url))

    def test_user_cannot_make_unconfirmed_email_address_primary(self):
        r = self.client.post(self.unconfirmed_email_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.unconfirmed_email_address_url))

    @exclude_on_speedy_match
    def test_user_can_make_confirmed_email_address_primary(self):
        self.assertEqual(first=self.user.email_addresses.count(), second=3)
        self.assertEqual(first=self.user.email_addresses.filter(is_confirmed=True).count(), second=2)
        self.assertEqual(first=self.user.email_addresses.get(is_primary=True), second=self.primary_address)
        r = self.client.post(self.confirmed_email_address_url)
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn(member='You have changed your primary email address.', container=map(str, r.context['messages']))
        self.assertEqual(first=self.user.email_addresses.count(), second=3)
        self.assertEqual(first=self.user.email_addresses.filter(is_confirmed=True).count(), second=2)
        self.assertEqual(first=self.user.email_addresses.get(is_primary=True), second=self.confirmed_email_address)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class PasswordResetViewTestCase(TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()
        self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={self.SPEEDY_NET_SITE_ID: 1, self.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])

    def test_visitor_can_open_the_page(self):
        r = self.client.get('/reset-password/')
        self.assertEqual(first=r.status_code, second=200)

    def test_visitor_can_reset_password(self):
        r = self.client.post('/reset-password/', {
            'email': self.email.email,
        })
        self.assertRedirects(response=r, expected_url='/reset-password/done/')
        self.assertEqual(first=len(mail.outbox), second=1)
        self.assertEqual(first=mail.outbox[0].subject, second='Password Reset on {}'.format(self.site.name))


