from django.core import mail
from django.test import TestCase

from .models import Entity, User, UserEmailAddress
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
        self.user = UserFactory(slug='mark')

    def test_visitor_has_no_access(self):
        r = self.client.get('/me/')
        self.assertRedirects(r, '/login/?next=/me/')

    def test_uset_gets_redirected_to_his_profile(self):
        self.client.login(username=self.user.slug, password='111')
        r = self.client.get('/me/')
        self.assertRedirects(r, '/mark/')


class RegistrationViewTestCase(TestCase):
    def setUp(self):
        self.data = {
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'email@example.com',
            'slug': 'user',
            'gender': 1,
            'password1': 'password',
            'password2': 'password',
        }

    def test_visitor_can_see_registration_page(self):
        r = self.client.get('/register/')
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'accounts/registration.html')

    def test_non_unique_email_address(self):
        UserEmailAddressFactory(email=self.data['email'])
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
        self.assertEqual(15, len(entity.id))
        self.assertTrue(user.check_password('password'))
        self.assertEqual(user.first_name, 'First')
        self.assertEqual(user.first_name_en, 'First')
        self.assertEqual(user.last_name, 'Last')
        self.assertEqual(user.last_name_en, 'Last')
        self.assertEqual(user.slug, 'user')
        self.assertEqual(user.email_addresses.count(), 1)
        self.assertEqual(user.email_addresses.all()[0].email, 'email@example.com')
        self.assertFalse(user.email_addresses.all()[0].is_confirmed)
        self.assertTrue(user.email_addresses.all()[0].is_primary)

    def test_user_is_logged_in_after_registration(self):
        r = self.client.post('/register/', data=self.data)
        self.assertRedirects(r, '/', target_status_code=302)
        r = self.client.get('/edit-profile/')
        self.assertTrue(r.context['user'].is_authenticated())
        self.assertTrue(r.context['user'].slug, 'user')

    def test_user_gets_email_after_registration(self):
        r = self.client.post('/register/', data=self.data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Confirm your email address on Speedy Net')
        self.assertIn(UserEmailAddress.objects.get(email='email@example.com').confirmation_token,
                      mail.outbox[0].body)


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user_email = UserEmailAddressFactory(user=self.user)
        self.other_user_email = UserEmailAddressFactory()

    def test_visitor_can_see_login_page(self):
        r = self.client.get('/login/')
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'accounts/login.html')

    def test_visitor_can_login_using_slug(self):
        r = self.client.post('/login/', data={
            'username': self.user.slug,
            'password': '111',
        })
        self.assertEqual(r.status_code, 302)

    def test_visitor_can_login_using_email(self):
        r = self.client.post('/login/', data={
            'username': self.user_email.email,
            'password': '111',
        })
        self.assertEqual(r.status_code, 302)


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
    def setUp(self):
        self.user = UserFactory()
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get('/edit-profile/')
        self.assertRedirects(r, '/login/?next=/edit-profile/')

    def test_user_can_open_the_page(self):
        r = self.client.get('/edit-profile/')
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'accounts/edit_profile/account.html')


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
        self.assertEqual(mail.outbox[0].subject, 'Confirm your email address on Speedy Net')
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
        self.assertEqual(mail.outbox[0].subject, 'Confirm your email address on Speedy Net')
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
