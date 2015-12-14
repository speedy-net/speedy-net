from datetime import timedelta
from django.test import (TestCase,)
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from base.views import (Login, Register)
from base.models import (UserProfile, UserEmailAddress, Identity, Token)
from base.util import generate_token

# Create your tests here.
class LoginTest(TestCase):

    @classmethod
    def setUpTestData(self):
        self.identity, created = Identity.objects.get_or_create(
            username='test',
            slug='te-st',
            model_type=Identity.USER_MODEL
        )
        self.username = 'test'
        self.email = 'dima.orman+speedytest@initech.co.il'
        self.password = 'abcd1234'
        self.login, created = User.objects.get_or_create(
            username=self.username,
            is_active=True,
            first_name='Test',
            last_name='Testotron'
        )
        self.login.set_password(self.password)
        self.login.save()
        self.profile, created = UserProfile.objects.get_or_create(
            user=self.login,
            identity=self.identity
        )
        self.email_address, created = UserEmailAddress.objects.get_or_create(
            email=self.email,
            verified=True,
            token=None,
            profile=self.profile
        )

    def test_login_username(self):
        response = self.client.post(reverse('base:login'), { 'login': self.username, 'password': self.password })
        self.assertRedirects(response, '/')

    def test_login_email(self):
        response = self.client.post(reverse('base:login'), { 'login': self.email, 'password': self.password })
        self.assertRedirects(response, '/')


class RegisterTest(TestCase):
    @classmethod
    def setUpTestData(self):
        # setup user to test taken registration
        identity, created = Identity.objects.get_or_create(
            username='test',
            slug='te-st',
            model_type=Identity.USER_MODEL
        )
        login, created = User.objects.get_or_create(
            username='test',
            is_active=True,
            first_name='Test',
            last_name='Testotron'
        )
        login.set_password('abcd1234')
        login.save()
        profile, created = UserProfile.objects.get_or_create(
            user=login,
            identity=identity
        )
        email_address, created = UserEmailAddress.objects.get_or_create(
            email='dima.orman+speedytest@initech.co.il',
            verified=True,
            token=None,
            profile=profile
        )

        self.password = '123qweasd'
        self.username = 'regtest'
        self.email = 'dima.orman+speedyreg@initech.co.il'

    def test_register_correct(self):
        form = {
            'username': self.username,
            'slug': 'reg-test',
            'password': self.password,
            'email1': self.email,
            'email2': self.email,
        }
        response = self.client.post(reverse('base:register'), form)
        self.assertEquals(response.status_code, 200)

    def test_register_username_taken(self):
        form = {
            'username': 'test',
            'slug': 'reg-test',
            'password': self.password,
            'email1': self.email,
            'email2': self.email,
        }
        response = self.client.post(reverse('base:register'), form)
        self.assertEquals(response.status_code, 400)

    def test_register_email_taken(self):
        form = {
            'username': self.username,
            'slug': 'reg-test',
            'password': self.password,
            'email1': 'dima.orman+speedytest@initech.co.il',
            'email2': 'dima.orman+speedytest@initech.co.il',
        }
        response = self.client.post(reverse('base:register'), form)
        self.assertEquals(response.status_code, 400)

    def test_register_email_nonequal(self):
        form = {
            'username': self.username,
            'slug': 'reg-test',
            'password': self.password,
            'email1': self.email,
            'email2': 'dima.orman+speedyreg2@initech.co.il',
        }
        response = self.client.post(reverse('base:register'), form)
        self.assertEquals(response.status_code, 400)


class EmailActivationTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.expired_token = Token(token=generate_token(), created=timezone.now() - timedelta(days=30))
        self.expired_token.save()

        self.no_email_token = Token(token=generate_token())
        self.no_email_token.save()

    def test_activation_failed(self):
        response = self.client.get(reverse('base:activate_email'), { 'token': 'dummytoken' })
        self.assertEquals(response.status_code, 400)

    def test_method_not_allowed(self):
        response = self.client.post(reverse('base:activate_email'), { 'token': '1234' })
        self.assertEquals(response.status_code, 405)

    def test_no_token(self):
        response = self.client.get(reverse('base:activate_email'), { 'token': None })
        self.assertEquals(response.status_code, 400)

    def test_expired_token(self):
        response = self.client.get(reverse('base:activate_email'), { 'token': self.expired_token.token })
        self.assertEquals(response.status_code, 400)

    def test_no_email_token(self):
        response = self.client.get(reverse('base:activate_email'), { 'token': self.no_email_token.token })
        self.assertEquals(response.status_code, 400)


class PasswordResetTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.username = 'passtest'
        self.oldpass = '123qweasd'
        self.newpass = '1q2w3e4r5t'
        self.email_addr = 'dima.orman+speedypasstest@initech.co.il'
        # create reset token
        self.reset_token = Token(token=generate_token())
        self.reset_token.save()
        # create identity and user objects
        self.identity, created = Identity.objects.get_or_create(
            username=self.username,
            slug='pass-test',
            model_type=Identity.USER_MODEL
        )
        self.login, created = User.objects.get_or_create(
            username=self.username,
            is_active=True,
            first_name='Test',
            last_name='Testotron'
        )
        self.login.set_password(self.oldpass)
        self.login.save()
        # create profile and email for reset
        self.profile, created = UserProfile.objects.get_or_create(
            user=self.login,
            identity=self.identity,
            password_reset_token=self.reset_token
        )
        self.email, created = UserEmailAddress.objects.get_or_create(
            email=self.email_addr,
            verified=True,
            token=None,
            profile=self.profile
        )


    def test_password_reset_change(self):
        form = {
            'password1': self.newpass,
            'password2': self.newpass,
            'token': self.reset_token.token
        }
        response = self.client.post(reverse('base:password_reset'), form)
        self.assertRedirects(response, reverse('base:login'))
        self.assertEquals(True, User.objects.get(username=self.username).check_password(self.newpass))

    def test_password_link_sent(self):
        response = self.client.post(reverse('base:password_reset_confirm'), { 'email': self.email_addr })
        self.assertEquals(response.status_code, 200)

    def test_password_reset_token(self):
        response = self.client.get(reverse('base:password_reset_confirm'), { 'token': self.reset_token.token })
        self.assertEquals(response.status_code, 200)
