from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software, exclude_on_speedy_match
from speedy.core.accounts.tests.test_factories import USER_PASSWORD, ActiveUserFactory, UserEmailAddressFactory
from speedy.core.accounts.models import UserEmailAddress
from speedy.core.accounts.forms import RegistrationForm, PasswordResetForm, SiteProfileDeactivationForm, ProfileNotificationsForm


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class RegistrationFormTestCase(TestCase):
    def set_up(self):
        self.valid_data = {
            'first_name_en': 'First',
            'last_name_en': 'Last',
            'email': 'email@example.com',
            'slug': 'user22',
            'new_password1': 'password',
            'gender': 1,
            'date_of_birth': '1980-01-01',
        }

    def test_required_fields(self):
        form = RegistrationForm({})
        required_fields = self.valid_data.keys()
        # self.assertEqual(first=self._registration_form_all_the_required_fields_are_required_errors_dict.keys(), second={field: [self._this_field_is_required_error_message] for field in required_fields}.keys()) # ~~~~ TODO: remove this line!
        # self.assertSetEqual(set1=set(self._registration_form_all_the_required_fields_are_required_errors_dict.keys()), set2=set({field: [self._this_field_is_required_error_message] for field in required_fields}.keys())) # ~~~~ TODO: remove this line!
        self.assertDictEqual(d1=self._registration_form_all_the_required_fields_are_required_errors_dict, d2={field: [self._this_field_is_required_error_message] for field in required_fields})
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._registration_form_all_the_required_fields_are_required_errors_dict)
        # for field in required_fields:
        #     self.assertEqual(first=form.errors[field][0], second=self._this_field_is_required_error_message) # ~~~~ TODO: remove this line!

    # ~~~~ TODO - remove @exclude_on_speedy_match
    # @exclude_on_speedy_match # On speedy match user already is created with confirmed email
    def test_non_unique_primary_confirmed_email(self):
        existing_user = ActiveUserFactory()
        existing_user.email_addresses.create(email='email@example.com', is_confirmed=True)
        form = RegistrationForm(self.valid_data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._this_email_is_already_in_use_errors_dict)
        # self.assertEqual(first=form.errors['email'][0], second=self._this_email_is_already_in_use_error_message) # ~~~~ TODO: remove this line!
        self.assertEqual(first=existing_user.email_addresses.count(), second=1)

    def test_slug_validation_reserved(self):
        data = self.valid_data.copy()
        data['slug'] = 'editprofile'
        form = RegistrationForm(data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._slug_this_username_is_already_taken_errors_dict)
        # self.assertEqual(first=form.errors['slug'][0], second=self._this_username_is_already_taken_error_message) # ~~~~ TODO: remove this line!

    def test_slug_validation_already_taken(self):
        ActiveUserFactory(slug='validslug')
        data = self.valid_data.copy()
        data['slug'] = 'valid-slug'
        form = RegistrationForm(data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._slug_this_username_is_already_taken_errors_dict)
        # self.assertEqual(first=form.errors['slug'][0], second=self._this_username_is_already_taken_error_message) # ~~~~ TODO: remove this line!

    def test_slug_validation_too_short(self):
        data = self.valid_data.copy()
        data['slug'] = 'a' * 5
        form = RegistrationForm(data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._user_slug_min_length_fail_errors_dict_by_value_length(value_length=5))
        # self.assertEqual(first=form.errors['slug'][0], second=self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=5)) # ~~~~ TODO: remove this line!

    def test_slug_validation_too_long(self):
        data = self.valid_data.copy()
        data['slug'] = 'a' * 201
        form = RegistrationForm(data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._user_slug_max_length_fail_errors_dict_by_value_length(value_length=201))
        # self.assertEqual(first=form.errors['slug'][0], second=self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=200, value_length=201)) # ~~~~ TODO: remove this line!

    def test_slug_validation_regex(self):
        data = self.valid_data.copy()
        data['slug'] = '1234567890digits'
        form = RegistrationForm(data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._user_slug_username_must_start_with_4_or_more_letters_errors_dict)
        # self.assertEqual(first=form.errors['slug'][0], second=self._user_username_must_start_with_4_or_more_letters_error_message) # ~~~~ TODO: remove this line!

    def test_slug_gets_converted_to_username(self):
        data = self.valid_data.copy()
        data['slug'] = 'this-is-a-slug'
        form = RegistrationForm(data)
        form.full_clean()
        self.assertTrue(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2={})
        user = form.save()
        self.assertEqual(first=user.slug, second='this-is-a-slug')
        self.assertEqual(first=user.username, second='thisisaslug')

    def test_slug_dots_and_underscores_gets_converted_to_dashes(self):
        data = self.valid_data.copy()
        data['slug'] = 'this.is__a.slug'
        form = RegistrationForm(data)
        form.full_clean()
        self.assertTrue(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2={})
        user = form.save()
        self.assertEqual(first=user.slug, second='this-is-a-slug')
        self.assertEqual(first=user.username, second='thisisaslug')

    def test_slug_dashes_are_trimmed_and_double_dashes_are_converted_to_single_dashes(self):
        data = self.valid_data.copy()
        data['slug'] = '--this--is---a--slug--'
        form = RegistrationForm(data)
        form.full_clean()
        self.assertTrue(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2={})
        user = form.save()
        self.assertEqual(first=user.slug, second='this-is-a-slug')
        self.assertEqual(first=user.username, second='thisisaslug')

    def test_slug_gets_converted_to_lowercase(self):
        data = self.valid_data.copy()
        data['slug'] = 'THIS-IS-A-SLUG'
        form = RegistrationForm(data)
        form.full_clean()
        self.assertTrue(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2={})
        user = form.save()
        self.assertEqual(first=user.slug, second='this-is-a-slug')
        self.assertEqual(first=user.username, second='thisisaslug')

    def test_email_gets_converted_to_lowercase(self):
        data = self.valid_data.copy()
        data['email'] = 'EMAIL22@EXAMPLE.COM'
        form = RegistrationForm(data)
        form.full_clean()
        self.assertTrue(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2={})
        user = form.save()
        email_addresses = UserEmailAddress.objects.filter(user=user)
        email_addresses_set = {e.email for e in email_addresses}
        self.assertSetEqual(set1=email_addresses_set, set2={'email22@example.com'})


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class ProfilePrivacyFormTestCase(TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.primary_email = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.confirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.unconfirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.other_user_email = UserEmailAddressFactory(user=self.other_user, is_confirmed=True)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class ProfileNotificationsFormTestCase(TestCase):
    def set_up(self):
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
    def set_up(self):
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
    def set_up(self):
        self.user = ActiveUserFactory()

    def test_incorrect_password(self):
        form = SiteProfileDeactivationForm(user=self.user, data={
            'password': 'wrong password!!',
        })
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._invalid_password_errors_dict)

    def test_correct_password(self):
        form = SiteProfileDeactivationForm(user=self.user, data={
            'password': USER_PASSWORD,
        })
        self.assertTrue(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2={})


