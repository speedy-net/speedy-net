from datetime import date

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail

from speedy.core.accounts.models import Entity, User, UserEmailAddress
from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software, exclude_on_speedy_match, exclude_on_speedy_net
from .test_factories import USER_PASSWORD, ActiveUserFactory, UserEmailAddressFactory, InactiveUserFactory


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
    def setUp(self):
        self.user = ActiveUserFactory()

    def test_visitor_gets_registration_page(self):
        r = self.client.get('/')
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/registration.html')


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class MeViewTestCase(RedirectMeMixin, TestCase):
    def setUp(self):
        self.user = ActiveUserFactory(slug='markmark')

    def test_visitor_has_no_access(self):
        self.assert_me_url_redirects_to_login_url()

    def test_user_gets_redirected_to_his_profile(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)
        # Assert expected_url directly once to confirm.
        self.assert_me_url_redirects(expected_url='/markmark/')


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class RegistrationViewTestCase(TestCase):
    def setUp(self):
        self.data = {
            'first_name_en': 'First',
            'last_name_en': 'Last',
            'email': 'email@example.com',
            'slug': 'user1234',
            'date_of_birth': '1980-08-20',
            'gender': 1,
            'new_password1': 'password',
            # 'password2': 'password',
        }
        site = Site.objects.get_current()
        site.domain = 'localhost'
        site.save()

    def test_visitor_can_see_registration_page(self):
        r = self.client.get('/')
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/registration.html')

    def test_non_unique_email_address(self):
        UserEmailAddressFactory(email=self.data['email'], is_confirmed=True)
        r = self.client.post('/', data=self.data)
        self.assertFormError(response=r, form='form', field='email', errors='This email is already in use.')

    def test_visitor_can_register(self):
        r = self.client.post('/', data=self.data)
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        self.assertEqual(first=1, second=Entity.objects.count())
        self.assertEqual(first=1, second=User.objects.count())
        entity = Entity.objects.all()[0]
        user = User.objects.all()[0]
        self.assertEqual(first=user, second=entity.user)
        self.assertEqual(first=user.id, second=entity.id)
        self.assertEqual(first=15, second=len(entity.id))
        self.assertTrue(expr=user.check_password(raw_password='password'))
        self.assertEqual(first=user.first_name, second='First')
        self.assertEqual(first=user.first_name_en, second='First')
        self.assertEqual(first=user.last_name, second='Last')
        self.assertEqual(first=user.last_name_en, second='Last')
        self.assertEqual(first=user.slug, second='user1234')
        self.assertEqual(first=user.username, second='user1234')
        self.assertEqual(first=user.email_addresses.count(), second=1)
        self.assertEqual(first=user.email_addresses.all()[0].email, second='email@example.com')
        self.assertFalse(expr=user.email_addresses.all()[0].is_confirmed)
        self.assertTrue(expr=user.email_addresses.all()[0].is_primary)

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
        self.assertEqual(first=r.context['user'].slug, second='user1234')

    def test_user_gets_email_after_registration_in_english(self):
        r = self.client.post('/', data=self.data)
        self.assertEqual(first=len(mail.outbox), second=1)
        site = Site.objects.get_current()
        user = User.objects.first()
        email = user.email_addresses.first()
        self.assertFalse(expr=email.is_confirmed)
        self.assertEqual(first=email.confirmation_sent, second=1)
        self.assertEqual(first=mail.outbox[0].subject, second='Confirm your email address on {}'.format(site.name))
        self.assertIn(member=UserEmailAddress.objects.get(email='email@example.com').confirmation_token, container=mail.outbox[0].body)
        self.assertIn(member='http://en.localhost/', container=mail.outbox[0].body)

    def test_user_gets_email_after_registration_in_hebrew(self):
        self.data['first_name_he'] = 'First HE'
        self.data['last_name_he'] = 'Last HE'
        r = self.client.post('/', data=self.data, HTTP_HOST='he.localhost')
        # site = Site.objects.get_current()
        # self.assertEqual(first=mail.outbox[0].subject, second='Confirm your email address on {}'.format(site.name))
        self.assertIn(member='http://he.localhost/', container=mail.outbox[0].body)

    def test_cannot_register_taken_username(self):
        existing_user = ActiveUserFactory(username='username', slug='user-name')
        self.data['slug'] = 'us-er-na-me'
        r = self.client.post('/', data=self.data)
        self.assertFormError(response=r, form='form', field='slug', errors='This username is already taken.')


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class LoginViewTestCase(RedirectMeMixin, TestCase):
    def setUp(self):
        self.user = ActiveUserFactory(slug='slug.with.dots')
        self.user_email = UserEmailAddressFactory(user=self.user)
        self.other_user_email = UserEmailAddressFactory()
        self.inactive_user = InactiveUserFactory()

    def test_visitor_can_see_login_page(self):
        r = self.client.get('/login/')
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/login.html')

    def test_visitor_can_login_using_slug(self):
        self.assertEqual(first=self.user.slug, second='slug-with-dots')
        r = self.client.post('/login/', data={
            'username': 'slug-with-dots',
            'password': USER_PASSWORD,
        })
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        self.assert_me_url_redirects_to_user_profile_url(user=self.user)
        # Assert expected_url directly once to confirm.
        self.assert_me_url_redirects(expected_url='/slug-with-dots/')

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

    def test_visitor_still_can_login_if_he_is_not_active_user(self):
        r = self.client.post('/login/', data={
            'username': self.inactive_user.slug,
            'password': USER_PASSWORD,
        })
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)
        # Inactive users are redirected to welcome url ('/welcome/') instead of their user profile url.
        self.assert_me_url_redirects_to_welcome_url()

    def test_visitor_cannot_login_using_wrong_password(self):
        self.assertEqual(first=self.user.slug, second='slug-with-dots')
        r = self.client.post('/login/', data={
            'username': 'slug-with-dots',
            'password': 'wrong password!!',
        })
        self.assertEqual(first=r.status_code, second=200)
        self.assertEqual(first=r.context['form'].errors, second={'__all__': ['Please enter a correct username and password. Note that both fields may be case-sensitive.']})
        self.assert_me_url_redirects_to_login_url()


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class LogoutViewTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.client.login(username=self.user.slug, password=USER_PASSWORD)

    def test_user_can_logout(self):
        r = self.client.get('/logout/')
        self.assertEqual(first=r.status_code, second=200)
        r = self.client.get('/')
        self.assertFalse(expr=r.context['user'].is_authenticated)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class EditProfileViewTestCase(TestCase):
    page_url = '/edit-profile/'

    def setUp(self):
        self.user = ActiveUserFactory()
        self.client.login(username=self.user.slug, password=USER_PASSWORD)

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
        self.assertEqual(first=user.date_of_birth, second=date(1976, 6, 3))


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class EditProfilePrivacyViewTestCase(TestCase):
    page_url = '/edit-profile/privacy/'

    def setUp(self):
        self.user = ActiveUserFactory()
        self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)

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

    def setUp(self):
        self.user = ActiveUserFactory()
        self.client.login(username=self.user.slug, password=USER_PASSWORD)

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

    def setUp(self):
        self.user = ActiveUserFactory()
        self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/credentials.html')

    def test_user_can_change_password(self):
        r = self.client.post(self.page_url, {
            'old_password': USER_PASSWORD,
            'new_password1': '8' * 8,
            'new_password2': '8' * 8,
        })
        self.assertRedirects(response=r, expected_url=self.page_url)
        user = User.objects.get(id=self.user.id)
        self.assertTrue(expr=user.check_password(raw_password='8' * 8))
        self.assertFalse(expr=user.check_password(raw_password='1' * 8))
        self.assertFalse(expr=user.check_password(raw_password=USER_PASSWORD))

    def test_old_password_incorrect(self):
        r = self.client.post(self.page_url, {
            'old_password': '7' * 8,
            'new_password1': '8' * 8,
            'new_password2': '8' * 8,
        })
        self.assertEqual(first=r.status_code, second=200)
        self.assertEqual(first=r.context['form'].errors, second={'old_password': ['Your old password was entered incorrectly. Please enter it again.']})
        user = User.objects.get(id=self.user.id)
        self.assertTrue(expr=user.check_password(raw_password=USER_PASSWORD))
        self.assertFalse(expr=user.check_password(raw_password='8' * 8))
        self.assertFalse(expr=user.check_password(raw_password='7' * 8))

    def test_password_too_short(self):
        r = self.client.post(self.page_url, {
            'old_password': USER_PASSWORD,
            'new_password1': '8' * 3,
            'new_password2': '8' * 3,
        })
        self.assertEqual(first=r.status_code, second=200)
        self.assertEqual(first=r.context['form'].errors, second={'new_password1': ['Password too short.']})
        user = User.objects.get(id=self.user.id)
        self.assertTrue(expr=user.check_password(raw_password=USER_PASSWORD))
        self.assertFalse(expr=user.check_password(raw_password='8' * 3))

    def test_password_too_long(self):
        r = self.client.post(self.page_url, {
            'old_password': USER_PASSWORD,
            'new_password1': '8' * 121,
            'new_password2': '8' * 121,
        })
        self.assertEqual(first=r.status_code, second=200)
        self.assertEqual(first=r.context['form'].errors, second={'new_password1': ['Password too long.']})
        user = User.objects.get(id=self.user.id)
        self.assertTrue(expr=user.check_password(raw_password=USER_PASSWORD))
        self.assertFalse(expr=user.check_password(raw_password='8' * 121))

    def test_passwords_dont_match(self):
        r = self.client.post(self.page_url, {
            'old_password': USER_PASSWORD,
            'new_password1': '8' * 8,
            'new_password2': '7' * 8,
        })
        self.assertEqual(first=r.status_code, second=200)
        self.assertEqual(first=r.context['form'].errors, second={'new_password2': ["The two password fields didn't match."]})
        user = User.objects.get(id=self.user.id)
        self.assertTrue(expr=user.check_password(raw_password=USER_PASSWORD))
        self.assertFalse(expr=user.check_password(raw_password='8' * 8))
        self.assertFalse(expr=user.check_password(raw_password='7' * 8))


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class ActivateSiteProfileViewTestCase(TestCase):
    page_url = '/welcome/'

    def setUp(self):
        self.user = InactiveUserFactory()
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertFalse(expr=self.user.profile.is_active)

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
        self.assertTrue(expr=user.profile.is_active)

    # @exclude_on_speedy_net
    # @exclude_on_speedy_match
    # def test_inactive_match_profile_inactive_net_profile_cannot_activate(self):
    #     r = self.client.post(self.page_url)
    #     self.assertRedirects(response=r, expected_url='/', target_status_code=302)
    #     user = User.objects.get(id=self.user.id)
    #     self.assertFalse(expr=user.profile.is_active)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class DeactivateSiteProfileViewTestCase(TestCase):
    page_url = '/edit-profile/deactivate/'

    def setUp(self):
        self.user = ActiveUserFactory()
        self.client.login(username=self.user.slug, password=USER_PASSWORD)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/edit_profile/deactivate.html')

    def test_user_can_deactivate_his_account(self):
        self.assertTrue(expr=self.user.is_active)
        r = self.client.post(self.page_url, {
            'password': USER_PASSWORD,
        })
        self.assertRedirects(response=r, expected_url='/', target_status_code=302)
        user = User.objects.get(id=self.user.id)
        self.assertFalse(expr=user.profile.is_active)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class VerifyUserEmailAddressViewTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.confirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.unconfirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)

    def test_wrong_link_gives_404(self):
        user_email_address = UserEmailAddress()
        token = user_email_address._generate_confirmation_token()
        r = self.client.get('/edit-profile/emails/verify/{}/'.format(token))
        self.assertEqual(first=r.status_code, second=404)

    def test_confirmed_email_link_redirects_to_edit_profile(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        email_id = self.confirmed_address.id
        token = self.confirmed_address.confirmation_token
        r = self.client.get('/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn(member='You\'ve already confirmed this email address.', container=map(str, r.context['messages']))

    def test_unconfirmed_email_link_confirms_email(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        email_id = self.unconfirmed_address.id
        token = self.unconfirmed_address.confirmation_token
        r = self.client.get('/edit-profile/emails/{}/verify/{}/'.format(email_id, token))
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn(member='You\'ve confirmed your email address.', container=map(str, r.context['messages']))
        self.assertTrue(expr=UserEmailAddress.objects.get(id=self.unconfirmed_address.id).is_confirmed)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class AddUserEmailAddressViewTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.confirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get('/edit-profile/emails/add/')
        self.assertRedirects(response=r, expected_url='/login/?next=/edit-profile/emails/add/')

    def test_user_can_open_the_page(self):
        r = self.client.get('/edit-profile/emails/add/')
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/email_address_form.html')

    def test_non_unique_email_address(self):
        r = self.client.post('/edit-profile/emails/add/', data={
            'email': self.confirmed_address.email,
        })
        self.assertFormError(response=r, form='form', field='email', errors='This email is already in use.')

    def test_user_can_add_email_address(self):
        r = self.client.post('/edit-profile/emails/add/', data={
            'email': 'email@example.com',
        })
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        email_address = UserEmailAddress.objects.get(email='email@example.com')
        self.assertFalse(expr=email_address.is_primary)
        r = self.client.get('/edit-profile/')
        self.assertIn(member='A confirmation message was sent to email@example.com',container= map(str, r.context['messages']))
        self.assertEqual(first=len(mail.outbox), second=1)
        site = Site.objects.get_current()
        self.assertEqual(first=mail.outbox[0].subject, second='Confirm your email address on {}'.format(site.name))
        self.assertIn(member=UserEmailAddress.objects.get(email='email@example.com').confirmation_token, container=mail.outbox[0].body)

    def test_first_email_is_primary(self):
        self.confirmed_address.delete()
        r = self.client.post('/edit-profile/emails/add/', data={
            'email': 'email@example.com',
        })
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        email_address = UserEmailAddress.objects.get(email='email@example.com')
        self.assertTrue(expr=email_address.is_primary)

@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class SendConfirmationEmailViewTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.unconfirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.unconfirmed_address_url = '/edit-profile/emails/{}/confirm/'.format(self.unconfirmed_address.id)
        self.confirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.confirmed_address_url = '/edit-profile/emails/{}/confirm/'.format(self.confirmed_address.id)
        self.other_users_address = UserEmailAddressFactory()
        self.other_users_address_url = '/edit-profile/emails/{}/confirm/'.format(self.other_users_address.id)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.unconfirmed_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.unconfirmed_address_url))

    def test_user_has_no_access_to_other_users_address(self):
        r = self.client.post(self.other_users_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.other_users_address_url))

    def test_user_can_resend_confirmation(self):
        r = self.client.post(self.unconfirmed_address_url)
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn(member='A confirmation message was sent to {}'.format(self.unconfirmed_address.email), container=map(str, r.context['messages']))
        self.assertEqual(first=len(mail.outbox), second=1)
        site = Site.objects.get_current()
        self.assertEqual(first=mail.outbox[0].subject, second='Confirm your email address on {}'.format(site.name))
        self.assertIn(member=UserEmailAddress.objects.get(email=self.unconfirmed_address.email).confirmation_token, container=mail.outbox[0].body)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class DeleteUserEmailAddressViewTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.confirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=False)
        self.confirmed_address_url = '/edit-profile/emails/{}/delete/'.format(self.confirmed_address.id)
        self.primary_address = UserEmailAddressFactory(user=self.user, is_primary=True)
        self.primary_address_url = '/edit-profile/emails/{}/delete/'.format(self.primary_address.id)
        self.other_users_address = UserEmailAddressFactory(is_primary=False)
        self.other_users_address_url = '/edit-profile/emails/{}/delete/'.format(self.other_users_address.id)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.confirmed_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.confirmed_address_url))

    def test_user_has_no_access_to_other_users_address(self):
        r = self.client.post(self.other_users_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.other_users_address_url))

    def test_user_cannot_delete_primary_email_address(self):
        r = self.client.post(self.primary_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.primary_address_url))

    @exclude_on_speedy_match
    def test_user_can_delete_email_address(self):
        self.assertEqual(first=self.user.email_addresses.count(), second=2)
        r = self.client.post(self.confirmed_address_url)
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn(member='The email address was deleted.', container=map(str, r.context['messages']))
        self.assertEqual(first=self.user.email_addresses.count(), second=1)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class SetPrimaryUserEmailAddressViewTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.unconfirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.unconfirmed_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.unconfirmed_address.id)
        self.confirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.confirmed_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.confirmed_address.id)
        self.primary_address = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.primary_address_url = '/edit-profile/emails/{}/delete/'.format(self.primary_address.id)
        self.other_users_address = UserEmailAddressFactory()
        self.other_users_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.other_users_address.id)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.confirmed_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.confirmed_address_url))

    def test_user_has_no_access_to_other_users_address(self):
        r = self.client.post(self.other_users_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.other_users_address_url))

    def test_user_cannot_make_unconfirmed_address_primary(self):
        r = self.client.post(self.unconfirmed_address_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.unconfirmed_address_url))

    @exclude_on_speedy_match
    def test_user_can_make_confirmed_address_primary(self):
        self.assertEqual(first=self.user.email_addresses.count(), second=3)
        self.assertEqual(first=self.user.email_addresses.filter(is_confirmed=True).count(), second=2)
        self.assertEqual(first=self.user.email_addresses.get(is_primary=True), second=self.primary_address)
        r = self.client.post(self.confirmed_address_url)
        self.assertRedirects(response=r, expected_url='/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn(member='You have changed your primary email address.', container=map(str, r.context['messages']))
        self.assertEqual(first=self.user.email_addresses.count(), second=3)
        self.assertEqual(first=self.user.email_addresses.filter(is_confirmed=True).count(), second=2)
        self.assertEqual(first=self.user.email_addresses.get(is_primary=True), second=self.confirmed_address)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class PasswordResetViewTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)

    def test_visitor_can_open_the_page(self):
        r = self.client.get('/reset-password/')
        self.assertEqual(first=r.status_code, second=200)

    def test_visitor_can_reset_password(self):
        r = self.client.post('/reset-password/', {
            'email': self.email.email,
        })
        self.assertRedirects(response=r, expected_url='/reset-password/done/')
        self.assertEqual(first=len(mail.outbox), second=1)
        site = Site.objects.get_current()
        self.assertEqual(first=mail.outbox[0].subject, second='Password Reset on {}'.format(site.name))
