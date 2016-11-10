from datetime import date

from django.contrib.sites.models import Site
from django.core import mail
from speedy.core.test import TestCase

from speedy.core.test import exclude_on_speedy_match
from .models import Entity, User, UserEmailAddress, SiteProfileBase
from .test_factories import UserFactory, UserEmailAddressFactory


class IndexViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_visitor_gets_redirected_to_registration(self):
        r = self.client.get('/')
        self.assertRedirects(r, '/register/')

    def test_user_gets_redirected_to_his_profile(self):
        self.client.login(username=self.user.slug, password='111')
        r = self.client.get('/')
        self.assertRedirects(r, '/me/', target_status_code=302)


class MeViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(slug='markmark')

    def test_visitor_has_no_access(self):
        r = self.client.get('/me/')
        self.assertRedirects(r, '/login/?next=/me/')

    def test_uset_gets_redirected_to_his_profile(self):
        self.client.login(username=self.user.slug, password='111')
        r = self.client.get('/me/')
        self.assertRedirects(r, '/markmark/')


class RegistrationViewTestCase(TestCase):
    def setUp(self):
        self.data = {
            'first_name_en': 'First',
            'last_name_en': 'Last',
            'email': 'email@example.com',
            'slug': 'user1234',
            'date_of_birth': 'August 28, 1980',
            'gender': 1,
            'new_password1': 'password',
            # 'password2': 'password',
        }

    def test_visitor_can_see_registration_page(self):
        r = self.client.get('/register/')
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'accounts/registration.html')

    def test_non_unique_email_address(self):
        UserEmailAddressFactory(email=self.data['email'], is_confirmed=True)
        r = self.client.post('/register/', data=self.data)
        self.assertFormError(r, 'form', 'email', 'This email is already in use.')

    def test_visitor_can_register(self):
        r = self.client.post('/register/', data=self.data)
        self.assertRedirects(r, '/', target_status_code=302)
        self.assertEqual(1, Entity.objects.count())
        self.assertEqual(1, User.objects.count())
        entity = Entity.objects.all()[0]
        user = User.objects.all()[0]
        self.assertEqual(user, entity.user)
        self.assertEqual(user.id, entity.id)
        self.assertEqual(20, len(entity.id))
        self.assertTrue(user.check_password('password'))
        self.assertEqual(user.first_name, 'First')
        self.assertEqual(user.first_name_en, 'First')
        self.assertEqual(user.last_name, 'Last')
        self.assertEqual(user.last_name_en, 'Last')
        self.assertEqual(user.slug, 'user1234')
        self.assertEqual(user.email_addresses.count(), 1)
        self.assertEqual(user.email_addresses.all()[0].email, 'email@example.com')
        self.assertFalse(user.email_addresses.all()[0].is_confirmed)
        self.assertTrue(user.email_addresses.all()[0].is_primary)

    def test_user_is_logged_in_after_registration(self):
        r = self.client.post('/register/', data=self.data)
        self.assertRedirects(r, '/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertTrue(r.context['user'].is_authenticated())
        self.assertTrue(r.context['user'].slug, 'user1234')

    def test_user_gets_email_after_registration(self):
        r = self.client.post('/register/', data=self.data)
        self.assertEqual(len(mail.outbox), 1)
        site = Site.objects.get_current()
        user = User.objects.first()
        email = user.email_addresses.first()
        self.assertFalse(email.is_confirmed)
        self.assertEqual(email.confirmation_sent, 1)
        self.assertEqual(mail.outbox[0].subject, 'Confirm your email address on {}'.format(site.name))
        self.assertIn(UserEmailAddress.objects.get(email='email@example.com').confirmation_token, mail.outbox[0].body)


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(slug='slug.with.dots')
        self.user_email = UserEmailAddressFactory(user=self.user)
        self.other_user_email = UserEmailAddressFactory()
        self.inactive_user = UserFactory(is_active=False)

    def test_visitor_can_see_login_page(self):
        r = self.client.get('/login/')
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'accounts/login.html')

    def test_visitor_can_login_using_slug(self):
        self.assertEqual(self.user.slug, 'slug-with-dots')
        r = self.client.post('/login/', data={
            # 'username': 'slug-with-dots',
            'username': 'slug.with.dots',
            'password': '111',
        })
        self.assertRedirects(r, '/me/', target_status_code=302)

    def test_visitor_can_login_using_slug_modified(self):
        self.assertEqual(self.user.slug, 'slug-with-dots')
        r = self.client.post('/login/', data={
            'username': 'slug____with.....dots---',
            'password': '111',
        })
        self.assertRedirects(r, '/me/', target_status_code=302)

    def test_visitor_can_login_using_email(self):
        r = self.client.post('/login/', data={
            'username': self.user_email.email,
            'password': '111',
        })
        self.assertRedirects(r, '/me/', target_status_code=302)

    def test_visitor_still_can_login_if_he_is_not_active_user(self):
        r = self.client.post('/login/', data={
            'username': self.inactive_user.slug,
            'password': '111',
        })
        self.assertRedirects(r, '/me/', target_status_code=302)


class LogoutViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.login(username=self.user.slug, password='111')

    def test_user_can_logout(self):
        r = self.client.get('/logout/')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/register/')
        self.assertFalse(r.context['user'].is_authenticated())


class EditProfileViewTestCase(TestCase):
    page_url = '/edit-profile/'

    def setUp(self):
        self.user = UserFactory()
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'accounts/edit_profile/account.html')

    def test_user_can_save_his_settings(self):
        data = {
            'first_name_en': 'Johnny',
            'last_name_en': 'English',
            'date_of_birth': 'June 3, 1976',
            'slug': self.user.slug,
            'gender': 1,
        }
        r = self.client.post(self.page_url, data)
        self.assertRedirects(r, self.page_url)
        user = User.objects.get(id=self.user.id)
        for (key, value) in data.items():
            if key == 'date_of_birth':
                continue
            self.assertEqual(getattr(user, key), value)
        self.assertEqual(user.date_of_birth, date(1976, 6, 3))


class EditProfilePrivacyViewTestCase(TestCase):
    page_url = '/edit-profile/privacy/'

    def setUp(self):
        self.user = UserFactory()
        self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'accounts/edit_profile/privacy.html')

    @exclude_on_speedy_match
    def test_user_can_save_his_settings(self):
        self.assertEqual(self.user.profile.access_account, 4)
        data = {
            'access_account': '1',
            'access_dob_day_month': '2',
            'access_dob_year': '4',
        }
        r = self.client.post(self.page_url, data)
        self.assertRedirects(r, self.page_url)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.profile.access_account, 1)
        self.assertEqual(user.profile.access_dob_day_month, 2)
        self.assertEqual(user.profile.access_dob_year, 4)


class EditProfileNotificationsViewTestCase(TestCase):
    page_url = '/edit-profile/notifications/'

    def setUp(self):
        self.user = UserFactory()
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'accounts/edit_profile/notifications.html')

    @exclude_on_speedy_match
    def test_user_can_save_his_settings(self):
        self.assertEqual(self.user.profile.notify_on_message, SiteProfileBase.NOTIFICATIONS_ON)
        data = {
            'notify_on_message': SiteProfileBase.NOTIFICATIONS_OFF,
        }
        r = self.client.post(self.page_url, data)
        self.assertRedirects(r, self.page_url)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.profile.notify_on_message, SiteProfileBase.NOTIFICATIONS_OFF)


class EditProfileCredentialsViewTestCase(TestCase):
    page_url = '/edit-profile/credentials/'

    def setUp(self):
        self.user = UserFactory()
        self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'accounts/edit_profile/credentials.html')

    def test_user_can_change_password(self):
        r = self.client.post(self.page_url, {
            'old_password': '111',
            'new_password1': '88888888',
            'new_password2': '88888888',
        })
        self.assertRedirects(r, self.page_url)
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.check_password('88888888'))


class DeactivateAccountViewTestCase(TestCase):
    page_url = '/edit-profile/deactivate/'

    def setUp(self):
        self.user = UserFactory()
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next=' + self.page_url)

    def test_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'accounts/edit_profile/deactivate.html')

    def test_user_can_deactivate_his_account(self):
        self.assertTrue(self.user.is_active)
        r = self.client.post(self.page_url, {
            'password': '111',
        })
        self.assertRedirects(r, '/', target_status_code=302)
        user = User.objects.get(id=self.user.id)
        self.assertFalse(user.is_active)


class ActivateAccountViewTestCase(TestCase):
    page_url = '/activate/'

    def setUp(self):
        self.active_user = UserFactory(is_active=True)
        self.user = UserFactory(is_active=True)
        UserEmailAddressFactory(user=self.user, is_primary=True, is_confirmed=True)
        self.client.login(username=self.user.slug, password='111')
        # django test client don't authenticate inactive users
        self.user.deactivate()

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next=' + self.page_url)

    def test_inactive_user_has_no_access_to_other_pages(self):
        r = self.client.get('/other-page/')
        self.assertRedirects(r, self.page_url)

    def test_inactive_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'accounts/activate/form.html')

    def test_inactive_user_can_request_activation(self):
        r = self.client.post(self.page_url)
        self.assertRedirects(r, '/activate/done/')
        self.assertEqual(len(mail.outbox), 1)
        site = Site.objects.get_current()
        self.assertEqual(mail.outbox[0].subject, 'Account Activation on {}'.format(site.name))


class VerifyUserEmailAddressViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.confirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.unconfirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)

    def test_wrong_link_gives_404(self):
        token = UserEmailAddress._generate_confirmation_token()
        r = self.client.get('/edit-profile/emails/verify/{}/'.format(token))
        self.assertEqual(r.status_code, 404)

    def test_confirmed_email_link_redirects_to_edit_profile(self):
        self.client.login(username=self.user.slug, password='111')
        token = self.confirmed_address.confirmation_token
        r = self.client.get('/edit-profile/emails/verify/{}/'.format(token))
        self.assertRedirects(r, '/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn('You\'ve already confirmed this email address.', map(str, r.context['messages']))

    def test_unconfirmed_email_link_confirms_email(self):
        self.client.login(username=self.user.slug, password='111')
        token = self.unconfirmed_address.confirmation_token
        r = self.client.get('/edit-profile/emails/verify/{}/'.format(token))
        self.assertRedirects(r, '/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn('You\'ve confirmed your email address.', map(str, r.context['messages']))
        self.assertTrue(UserEmailAddress.objects.get(id=self.unconfirmed_address.id).is_confirmed)


class AddUserEmailAddressViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.confirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get('/edit-profile/emails/add/')
        self.assertRedirects(r, '/login/?next=/edit-profile/emails/add/')

    def test_user_can_open_the_page(self):
        r = self.client.get('/edit-profile/emails/add/')
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'accounts/email_address_form.html')

    def test_non_unique_email_address(self):
        r = self.client.post('/edit-profile/emails/add/', data={
            'email': self.confirmed_address.email,
        })
        self.assertFormError(r, 'form', 'email', 'This email is already in use.')

    def test_user_can_add_email_address(self):
        r = self.client.post('/edit-profile/emails/add/', data={
            'email': 'email@example.com',
        })
        self.assertRedirects(r, '/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn('A confirmation was sent to email@example.com', map(str, r.context['messages']))
        self.assertEqual(len(mail.outbox), 1)
        site = Site.objects.get_current()
        self.assertEqual(mail.outbox[0].subject, 'Confirm your email address on {}'.format(site.name))
        self.assertIn(UserEmailAddress.objects.get(email='email@example.com').confirmation_token,
                      mail.outbox[0].body)


class SendConfirmationEmailViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.unconfirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.unconfirmed_address_url = '/edit-profile/emails/{}/confirm/'.format(self.unconfirmed_address.id)
        self.confirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.confirmed_address_url = '/edit-profile/emails/{}/confirm/'.format(self.confirmed_address.id)
        self.other_users_address = UserEmailAddressFactory()
        self.other_users_address_url = '/edit-profile/emails/{}/confirm/'.format(self.other_users_address.id)
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.unconfirmed_address_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.unconfirmed_address_url))

    def test_user_has_no_access_to_other_users_address(self):
        r = self.client.post(self.other_users_address_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.other_users_address_url))

    def test_user_can_resend_confirmation(self):
        r = self.client.post(self.unconfirmed_address_url)
        self.assertRedirects(r, '/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn('A confirmation was sent to {}'.format(self.unconfirmed_address.email),
                      map(str, r.context['messages']))
        self.assertEqual(len(mail.outbox), 1)
        site = Site.objects.get_current()
        self.assertEqual(mail.outbox[0].subject, 'Confirm your email address on {}'.format(site.name))
        self.assertIn(UserEmailAddress.objects.get(email=self.unconfirmed_address.email).confirmation_token,
                      mail.outbox[0].body)


class DeleteUserEmailAddressViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.confirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=False)
        self.confirmed_address_url = '/edit-profile/emails/{}/delete/'.format(self.confirmed_address.id)
        self.primary_address = UserEmailAddressFactory(user=self.user, is_primary=True)
        self.primary_address_url = '/edit-profile/emails/{}/delete/'.format(self.primary_address.id)
        self.other_users_address = UserEmailAddressFactory(is_primary=False)
        self.other_users_address_url = '/edit-profile/emails/{}/delete/'.format(self.other_users_address.id)
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.confirmed_address_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.confirmed_address_url))

    def test_user_has_no_access_to_other_users_address(self):
        r = self.client.post(self.other_users_address_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.other_users_address_url))

    def test_user_cannot_delete_primary_email_address(self):
        r = self.client.post(self.primary_address_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.primary_address_url))

    def test_user_can_delete_email_address(self):
        self.assertEqual(self.user.email_addresses.count(), 2)
        r = self.client.post(self.confirmed_address_url)
        self.assertRedirects(r, '/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn('The email address was deleted.', map(str, r.context['messages']))
        self.assertEqual(self.user.email_addresses.count(), 1)


class SetPrimaryUserEmailAddressViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.unconfirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.unconfirmed_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.unconfirmed_address.id)
        self.confirmed_address = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.confirmed_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.confirmed_address.id)
        self.primary_address = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.primary_address_url = '/edit-profile/emails/{}/delete/'.format(self.primary_address.id)
        self.other_users_address = UserEmailAddressFactory()
        self.other_users_address_url = '/edit-profile/emails/{}/set-primary/'.format(self.other_users_address.id)
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.confirmed_address_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.confirmed_address_url))

    def test_user_has_no_access_to_other_users_address(self):
        r = self.client.post(self.other_users_address_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.other_users_address_url))

    def test_user_cannot_make_unconfirmed_address_primary(self):
        r = self.client.post(self.unconfirmed_address_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.unconfirmed_address_url))

    def test_user_can_make_confirmed_address_primary(self):
        self.assertEqual(self.user.email_addresses.count(), 3)
        self.assertEqual(self.user.email_addresses.filter(is_confirmed=True).count(), 2)
        self.assertEqual(self.user.email_addresses.get(is_primary=True), self.primary_address)
        r = self.client.post(self.confirmed_address_url)
        self.assertRedirects(r, '/edit-profile/emails/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertIn('You have changed your primary email address.', map(str, r.context['messages']))
        self.assertEqual(self.user.email_addresses.count(), 3)
        self.assertEqual(self.user.email_addresses.filter(is_confirmed=True).count(), 2)
        self.assertEqual(self.user.email_addresses.get(is_primary=True), self.confirmed_address)


class PasswordResetViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.email = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)

    def test_visitor_can_open_the_page(self):
        r = self.client.get('/reset-password/')
        self.assertEqual(r.status_code, 200)

    def test_visitor_can_reset_password(self):
        r = self.client.post('/reset-password/', {
            'email': self.email.email,
        })
        self.assertRedirects(r, '/reset-password/done/')
        self.assertEqual(len(mail.outbox), 1)
        site = Site.objects.get_current()
        self.assertEqual(mail.outbox[0].subject, 'Password Reset on {}'.format(site.name))
