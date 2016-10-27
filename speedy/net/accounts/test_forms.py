from speedy.core.test import TestCase

from speedy.core.test import exclude_on_speedy_match
from speedy.net.accounts.test_factories import UserFactory, UserEmailAddressFactory
from .forms import RegistrationForm, PasswordResetForm, DeactivationForm, ProfilePrivacyForm, ProfileNotificationsForm


class RegistrationFormTestCase(TestCase):
    def setUp(self):
        self.valid_data = {
            'first_name_en': 'First',
            'last_name_en': 'Last',
            'email': 'email@example.com',
            'slug': 'user',
            'gender': 1,
            'new_password1': 'password',
            # 'new_password2': 'password',
            'date_of_birth': '1980-01-01',
        }

    def test_required_fields(self):
        form = RegistrationForm({})
        required_fields = self.valid_data.keys()
        form.full_clean()
        self.assertFalse(form.is_valid())
        for field in required_fields:
            self.assertEqual('This field is required.', form.errors[field][0])

    def test_dots_in_slug_are_allowed(self):
        form = RegistrationForm({'slug': 'user.rrrrr'})
        form.full_clean()
        self.assertNotIn('slug', form.errors)

    def test_non_unique_primary_confirmed_email(self):
        existing_user = UserFactory()
        existing_user.email_addresses.create(email='email@example.com', is_confirmed=True)
        form = RegistrationForm(self.valid_data)
        self.assertEqual(form.errors['email'][0], 'This email is already in use.')
        self.assertEqual(existing_user.email_addresses.count(), 1)

    def test_slug_validation_reserved(self):
        data = self.valid_data.copy()
        data['slug'] = 'editprofile'
        form = RegistrationForm(data)
        self.assertEqual(form.errors['slug'][0], 'This username is already taken.')

    def test_slug_validation_already_taken(self):
        UserFactory(slug='validslug')
        data = self.valid_data.copy()
        data['slug'] = 'validslug'
        form = RegistrationForm(data)
        self.assertEqual(form.errors['slug'][0], 'This username is already taken.')

    def test_slug_validation_too_short(self):
        data = self.valid_data.copy()
        data['slug'] = 'a' * 5
        form = RegistrationForm(data)
        self.assertEqual(form.errors['slug'][0], 'Ensure this value has at least 6 characters (it has 5).')

    def test_slug_validation_too_long(self):
        data = self.valid_data.copy()
        data['slug'] = 'a' * 200
        form = RegistrationForm(data)
        self.assertEqual(form.errors['slug'][0], 'Ensure this value has at most 120 characters (it has 200).')

    def test_slug_validation_regex(self):
        data = self.valid_data.copy()
        data['slug'] = '1234567890digits'
        form = RegistrationForm(data)
        self.assertEqual(form.errors['slug'][0], 'Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.')

    def test_slug_gets_converted_to_username(self):
        data = self.valid_data.copy()
        data['slug'] = 'this----is_a.slug'
        form = RegistrationForm(data)
        form.full_clean()
        user = form.save()
        self.assertEqual(user.slug, 'this-is-a-slug')
        self.assertEqual(user.username, 'thisisaslug')


    # def test_passwords_mismatch(self):
    #     data = self.valid_data.copy()
    #     data['new_password2'] = 'haha'
    #     form = RegistrationForm(data)
    #     form.full_clean()
    #     self.assertEqual(form.errors['new_password2'][0], 'The two password fields didn\'t match.')


class ProfilePrivacyFormTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.primary_email = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.confirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.unconfirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.other_user_email = UserEmailAddressFactory(user=self.other_user, is_confirmed=True)

    def test_user_cannot_see_other_users_email(self):
        form = ProfilePrivacyForm(instance=self.user.profile)
        choices_ids = [c[0] for c in form.fields['public_email'].choices]
        self.assertEqual(len(choices_ids), 3)
        self.assertIn(self.primary_email.id, choices_ids)
        self.assertIn(self.confirmed_email.id, choices_ids)
        self.assertNotIn(self.unconfirmed_email.id, choices_ids)
        self.assertNotIn(self.other_user_email.id, choices_ids)


class ProfileNotificationsFormTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()

    @exclude_on_speedy_match
    def test_has_correct_fields(self):
        form = ProfileNotificationsForm(instance=self.user.profile)
        self.assertListEqual(list(form.fields.keys()), [
            'notify_on_message',
        ])


class PasswordResetFormTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.primary_email = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.confirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.unconfirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.other_user_email = UserEmailAddressFactory(user=self.other_user, is_confirmed=True)
        self.form = PasswordResetForm()

    def test_can_reset_using_primary_email(self):
        self.assertSetEqual(self.form.get_users(self.primary_email.email), {self.user})

    def test_can_reset_using_confirmed_email(self):
        self.assertSetEqual(self.form.get_users(self.confirmed_email.email), {self.user})

    def test_can_reset_using_unconfirmed_email(self):
        self.assertSetEqual(self.form.get_users(self.unconfirmed_email.email), {self.user})


class DeactivationFormTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_incorrect_password(self):
        form = DeactivationForm(user=self.user, data={
            'password': 'wrong password',
        })
        self.assertFalse(form.is_valid())

    def test_correct_password(self):
        form = DeactivationForm(user=self.user, data={
            'password': '111',
        })
        self.assertTrue(form.is_valid())
