from django.test import TestCase

from .models import Entity, User
from .test_factories import UserFactory, UserEmailAddressFactory


class IndexViewTestCase(TestCase):
    def setUp(self):
        self.user = User()

    def test_visitor_gets_redirected_to_registration(self):
        r = self.client.get('/')
        self.assertRedirects(r, '/register/')

    def test_user_gets_redirected_to_his_profile(self):
        self.client.login(username=self.user.slug, password='111')
        r = self.client.get('/')
        self.assertRedirects(r, '/me/')


class MeViewTestCase(TestCase):
    def setUp(self):
        self.user = User(slug='mark')

    def test_visitor_has_no_access(self):
        r = self.client.get('/me/')
        self.assertRedirects(r, '/login/?next=/me/')

    def test_uset_gets_redirected_to_his_profile(self):
        self.client.login(username=self.user.slug, password='111')
        r = self.client.get('/me/')
        self.assertRedirects(r, '/mark/')


class RegistrationViewTestCase(TestCase):
    def setUp(self):
        self.valid_data = {
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

    def test_visitor_can_register(self):
        r = self.client.post('/register/', data=self.valid_data)
        self.assertRedirects(r, '/register/success/')
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
        r = self.client.post('/register/', data=self.valid_data)
        self.assertRedirects(r, '/register/success/')
        r = self.client.get('/register/success/')
        self.assertTrue(r.context['user'].is_authenticated())
        self.assertTrue(r.context['user'].slug, 'user')


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
