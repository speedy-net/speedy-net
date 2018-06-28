from speedy.core.accounts.tests.test_factories import ActiveUserFactory, UserEmailAddressFactory
from speedy.core.accounts.models import UserEmailAddress
from speedy.core.accounts.forms import RegistrationForm, PasswordResetForm, SiteProfileDeactivationForm, ProfileNotificationsForm
from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software, exclude_on_speedy_match


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class RegistrationFormTestCase(TestCase):
    def setUp(self):
        self.valid_data = {
            'first_name_en': 'First',
            'last_name_en': 'Last',
            'email': 'email@example.com',
            'slug': 'user22',
            'gender': 1,
            'new_password1': 'password',
            'date_of_birth': '1980-01-01',
        }

    def test_required_fields(self):
        form = RegistrationForm({})
        required_fields = self.valid_data.keys()
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        for field in required_fields:
            self.assertEqual(first='This field is required.', second=form.errors[field][0])

    def test_dots_in_slug_are_allowed(self):
        form = RegistrationForm({'slug': 'user-rrrrr'})
        form.full_clean()
        self.assertNotIn(member='slug', container=form.errors)

    @exclude_on_speedy_match # On speedy match user already is created with confirmed email
    def test_non_unique_primary_confirmed_email(self):
        existing_user = ActiveUserFactory()
        existing_user.email_addresses.create(email='email@example.com', is_confirmed=True)
        form = RegistrationForm(self.valid_data)
        self.assertEqual(first=form.errors['email'][0], second='This email is already in use.')
        self.assertEqual(first=existing_user.email_addresses.count(), second=1)

    def test_slug_validation_reserved(self):
        data = self.valid_data.copy()
        data['slug'] = 'editprofile'
        form = RegistrationForm(data)
        self.assertEqual(first=form.errors['slug'][0], second='This username is already taken.')

    def test_slug_validation_already_taken(self):
        ActiveUserFactory(slug='validslug')
        data = self.valid_data.copy()
        data['slug'] = 'valid-slug'
        form = RegistrationForm(data)
        self.assertEqual(first=form.errors['slug'][0], second='This username is already taken.')

    def test_slug_validation_too_short(self):
        data = self.valid_data.copy()
        data['slug'] = 'a' * 5
        form = RegistrationForm(data)
        self.assertEqual(first=form.errors['slug'][0], second='Ensure this value has at least 6 characters (it has 5).')

    def test_slug_validation_too_long(self):
        data = self.valid_data.copy()
        data['slug'] = 'a' * 201
        form = RegistrationForm(data)
        self.assertEqual(first=form.errors['slug'][0], second='Ensure this value has at most 200 characters (it has 201).')

    def test_slug_validation_regex(self):
        data = self.valid_data.copy()
        data['slug'] = '1234567890digits'
        form = RegistrationForm(data)
        self.assertEqual(first=form.errors['slug'][0], second='Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.')

    def test_slug_gets_converted_to_username(self):
        data = self.valid_data.copy()
        data['slug'] = 'this-is-a-slug'
        form = RegistrationForm(data)
        form.full_clean()
        user = form.save()
        self.assertEqual(first=user.slug, second='this-is-a-slug')
        self.assertEqual(first=user.username, second='thisisaslug')

    def test_slug_dots_and_underscores_gets_converted_to_dashes(self):
        data = self.valid_data.copy()
        data['slug'] = 'this.is__a.slug'
        form = RegistrationForm(data)
        form.full_clean()
        user = form.save()
        self.assertEqual(first=user.slug, second='this-is-a-slug')
        self.assertEqual(first=user.username, second='thisisaslug')

    def test_slug_dashes_are_trimmed_and_double_dashes_are_converted_to_single_dashes(self):
        data = self.valid_data.copy()
        data['slug'] = '--this--is---a--slug--'
        form = RegistrationForm(data)
        form.full_clean()
        user = form.save()
        self.assertEqual(first=user.slug, second='this-is-a-slug')
        self.assertEqual(first=user.username, second='thisisaslug')

    def test_slug_gets_converted_to_lowercase(self):
        data = self.valid_data.copy()
        data['slug'] = 'THIS-IS-A-SLUG'
        form = RegistrationForm(data)
        form.full_clean()
        user = form.save()
        self.assertEqual(first=user.slug, second='this-is-a-slug')
        self.assertEqual(first=user.username, second='thisisaslug')

    def test_email_gets_converted_to_lowercase(self):
        data = self.valid_data.copy()
        data['email'] = 'EMAIL22@EXAMPLE.COM'
        form = RegistrationForm(data)
        form.full_clean()
        user = form.save()
        email_addresses = UserEmailAddress.objects.filter(user=user)
        email_addresses_set = {e.email for e in email_addresses}
        self.assertEqual(first=email_addresses_set, second={'email22@example.com'})


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class ProfilePrivacyFormTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.primary_email = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.confirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.unconfirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.other_user_email = UserEmailAddressFactory(user=self.other_user, is_confirmed=True)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class ProfileNotificationsFormTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()

    @exclude_on_speedy_match
    def test_has_correct_fields(self):
        form = ProfileNotificationsForm(instance=self.user)
        self.assertListEqual(list1=list(form.fields.keys()), list2=[
            'notify_on_message',
        ])


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class PasswordResetFormTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.primary_email = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.confirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.unconfirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.other_user_email = UserEmailAddressFactory(user=self.other_user, is_confirmed=True)
        self.form = PasswordResetForm()

    def test_can_reset_using_primary_email(self):
        self.assertSetEqual(set1=self.form.get_users(self.primary_email.email), set2={self.user})

    def test_can_reset_using_confirmed_email(self):
        self.assertSetEqual(set1=self.form.get_users(self.confirmed_email.email), set2={self.user})

    def test_can_reset_using_unconfirmed_email(self):
        self.assertSetEqual(set1=self.form.get_users(self.unconfirmed_email.email), set2={self.user})


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class DeactivationFormTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()

    def test_incorrect_password(self):
        form = SiteProfileDeactivationForm(user=self.user, data={
            'password': 'wrong password',
        })
        self.assertFalse(expr=form.is_valid())

    def test_correct_password(self):
        form = SiteProfileDeactivationForm(user=self.user, data={
            'password': '111',
        })
        self.assertTrue(expr=form.is_valid())
