from datetime import date

from django.conf import settings
from django.test import override_settings

from speedy.core.base.test import TestCase, only_on_sites_with_login, exclude_on_speedy_match
from .test_mixins import SpeedyCoreAccountsLanguageMixin
from .test_factories import get_random_user_password, USER_PASSWORD, ActiveUserFactory, UserEmailAddressFactory
from speedy.core.base.utils import normalize_slug, normalize_username
from speedy.core.accounts.models import Entity, User, UserEmailAddress
from speedy.core.accounts.forms import RegistrationForm, PasswordResetForm, SiteProfileDeactivationForm, ProfileNotificationsForm


class RegistrationFormTestCaseMixin(object):
    def setup(self):
        super().setup()
        self.password = get_random_user_password()
        self.data = {
            'email': 'email@example.com',
            'slug': 'user-22',
            'new_password1': self.password,
            'gender': 1,
            'date_of_birth': '1980-01-01',
        }
        self.username = normalize_username(slug=self.data['slug'])
        self.slug = normalize_slug(slug=self.data['slug'])
        self.assertNotEqual(first=self.password, second=USER_PASSWORD)
        self.assertEqual(first=self.username, second='user22')
        self.assertEqual(first=self.slug, second='user-22')
        self.assertNotEqual(first=self.username, second=self.slug)
        self.assertEqual(first=Entity.objects.count(), second=0)
        self.assertEqual(first=User.objects.count(), second=0)
        self.assertEqual(first=UserEmailAddress.objects.count(), second=0)
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second=0)

    def setup_required_fields(self):
        self.required_fields = self.data.keys()
        self.assert_registration_form_required_fields(required_fields=self.required_fields)

    def test_visitor_can_register(self):
        form = RegistrationForm(language_code=self.language_code, data=self.data)
        form.full_clean()
        self.assertTrue(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2={})
        user = form.save()
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
        self.assertEqual(first=user.first_name, second=self.first_name)
        self.assertEqual(first=user.first_name_en, second=self.first_name)
        self.assertEqual(first=user.first_name_he, second=self.first_name)
        self.assertEqual(first=user.last_name, second=self.last_name)
        self.assertEqual(first=user.last_name_en, second=self.last_name)
        self.assertEqual(first=user.last_name_he, second=self.last_name)
        self.assertEqual(first=user.username, second=self.username)
        self.assertEqual(first=user.username, second='user22')
        self.assertEqual(first=user.slug, second=self.slug)
        self.assertEqual(first=user.slug, second='user-22')
        self.assertEqual(first=user.email_addresses.count(), second=1)
        self.assertEqual(first=user.email_addresses.first().email, second='email@example.com')
        self.assertFalse(expr=user.email_addresses.first().is_confirmed)
        self.assertTrue(expr=user.email_addresses.first().is_primary)
        for (key, value) in self.data.items():
            if (not (key in ['new_password1', 'date_of_birth'])):
                self.assertEqual(first=getattr(user, key), second=value)
        self.assertEqual(first=user.date_of_birth, second=date(year=1980, month=1, day=1))

    def test_slug_gets_converted_to_username(self):
        data = self.data.copy()
        data['slug'] = 'this-is-a-slug'
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertTrue(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2={})
        user = form.save()
        self.assertEqual(first=user.slug, second='this-is-a-slug')
        self.assertEqual(first=user.username, second='thisisaslug')

    def test_slug_dots_and_underscores_gets_converted_to_dashes(self):
        data = self.data.copy()
        data['slug'] = 'this.is__a.slug'
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertTrue(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2={})
        user = form.save()
        self.assertEqual(first=user.slug, second='this-is-a-slug')
        self.assertEqual(first=user.username, second='thisisaslug')

    def test_slug_dashes_are_trimmed_and_double_dashes_are_converted_to_single_dashes(self):
        data = self.data.copy()
        data['slug'] = '--this--is---a--slug--'
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertTrue(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2={})
        user = form.save()
        self.assertEqual(first=user.slug, second='this-is-a-slug')
        self.assertEqual(first=user.username, second='thisisaslug')

    def test_slug_gets_converted_to_lowercase(self):
        data = self.data.copy()
        data['slug'] = 'THIS-IS-A-SLUG'
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertTrue(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2={})
        user = form.save()
        self.assertEqual(first=user.slug, second='this-is-a-slug')
        self.assertEqual(first=user.username, second='thisisaslug')

    def test_email_gets_converted_to_lowercase(self):
        data = self.data.copy()
        data['email'] = 'EMAIL22@EXAMPLE.COM'
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertTrue(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2={})
        user = form.save()
        email_addresses = UserEmailAddress.objects.filter(user=user)
        email_addresses_set = {e.email for e in email_addresses}
        self.assertSetEqual(set1=email_addresses_set, set2={'email22@example.com'})

    def run_test_required_fields(self, data):
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._registration_form_all_the_required_fields_are_required_errors_dict())
        # for field in required_fields:
        #     self.assertEqual(first=form.errors[field][0], second=self._this_field_is_required_error_message) # ~~~~ TODO: remove this line!

    def test_required_fields_1(self):
        data = {}
        self.run_test_required_fields(data=data)

    def test_required_fields_2(self):
        data = {field_name: '' for field_name in self.required_fields}
        self.run_test_required_fields(data=data)

    def test_non_unique_confirmed_email_address(self):
        existing_user_email = UserEmailAddressFactory(email=self.data['email'], is_confirmed=True)
        existing_user = existing_user_email.user
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={settings.SPEEDY_NET_SITE_ID: 1, settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={settings.SPEEDY_NET_SITE_ID: 1, settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        # existing_user = ActiveUserFactory() # ~~~~ TODO: remove this line!
        # existing_user.email_addresses.create(email='email@example.com', is_confirmed=True) # ~~~~ TODO: remove this line!
        self.assertEqual(first=existing_user.email_addresses.count(), second={settings.SPEEDY_NET_SITE_ID: 1, settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        form = RegistrationForm(language_code=self.language_code, data=self.data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._this_email_is_already_in_use_errors_dict())
        # self.assertEqual(first=form.errors['email'][0], second=self._this_email_is_already_in_use_error_message) # ~~~~ TODO: remove this line!
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={settings.SPEEDY_NET_SITE_ID: 1, settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={settings.SPEEDY_NET_SITE_ID: 1, settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=existing_user.email_addresses.count(), second={settings.SPEEDY_NET_SITE_ID: 1, settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        existing_user = User.objects.get(pk=existing_user.pk)  # ~~~~ TODO: remove this line!
        self.assertEqual(first=existing_user.email_addresses.count(), second={settings.SPEEDY_NET_SITE_ID: 1, settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])

    def test_non_unique_unconfirmed_email_address(self):
        # Unconfirmed email address is deleted if another user adds it again.
        existing_user_email = UserEmailAddressFactory(email=self.data['email'], is_confirmed=False)
        existing_user = existing_user_email.user
        self.assertEqual(first=Entity.objects.count(), second=1)
        self.assertEqual(first=User.objects.count(), second=1)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={settings.SPEEDY_NET_SITE_ID: 1, settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={settings.SPEEDY_NET_SITE_ID: 0, settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        # existing_user = ActiveUserFactory() # ~~~~ TODO: remove this line!
        # existing_user.email_addresses.create(email='email@example.com', is_confirmed=False) # ~~~~ TODO: remove this line!
        self.assertEqual(first=existing_user.email_addresses.count(), second={settings.SPEEDY_NET_SITE_ID: 1, settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        form = RegistrationForm(language_code=self.language_code, data=self.data)
        form.full_clean()
        self.assertTrue(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2={})
        user = form.save()
        # self.assertEqual(first=form.errors['email'][0], second=self._this_email_is_already_in_use_error_message) # ~~~~ TODO: remove this line!
        self.assertEqual(first=Entity.objects.count(), second=2)
        self.assertEqual(first=User.objects.count(), second=2)
        self.assertEqual(first=UserEmailAddress.objects.count(), second={settings.SPEEDY_NET_SITE_ID: 1, settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
        self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second={settings.SPEEDY_NET_SITE_ID: 0, settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        self.assertEqual(first=existing_user.email_addresses.count(), second={settings.SPEEDY_NET_SITE_ID: 0, settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        # self.assertEqual(first=existing_user.email_addresses.count(), second={settings.SPEEDY_NET_SITE_ID: 1, settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id]) # ~~~~ TODO: remove this line!
        existing_user = User.objects.get(pk=existing_user.pk)  # ~~~~ TODO: remove this line!
        self.assertEqual(first=existing_user.email_addresses.count(), second={settings.SPEEDY_NET_SITE_ID: 0, settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
        # self.assertEqual(first=existing_user.email_addresses.count(), second={settings.SPEEDY_NET_SITE_ID: 1, settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id]) # ~~~~ TODO: remove this line!

    def test_slug_validation_fails_with_reserved_username(self):
        data = self.data.copy()
        data['slug'] = 'webmaster'
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._this_username_is_already_taken_errors_dict(slug_fail=True))
        # self.assertEqual(first=form.errors['slug'][0], second=self._this_username_is_already_taken_error_message) # ~~~~ TODO: remove this line!

    def test_slug_validation_fails_with_reserved_and_too_short_username(self):
        data = self.data.copy()
        data['slug'] = 'mail'
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_value_length=4))
        # self.assertDictEqual(d1=form.errors, d2=self._this_username_is_already_taken_errors_dict(slug_fail=True))
        # self.assertEqual(first=form.errors['slug'][0], second=self._this_username_is_already_taken_error_message) # ~~~~ TODO: remove this line!

    def test_slug_validation_fails_with_username_already_taken(self):
        ActiveUserFactory(slug='validslug')
        data = self.data.copy()
        data['slug'] = 'valid-slug'
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._this_username_is_already_taken_errors_dict(slug_fail=True))
        # self.assertEqual(first=form.errors['slug'][0], second=self._this_username_is_already_taken_error_message) # ~~~~ TODO: remove this line!

    def test_slug_validation_fails_with_username_too_short_1(self):  #### TODO
        data = self.data.copy()
        data['slug'] = 'a' * 5
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_value_length=5))
        # self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_value_length=5))
        # self.assertDictEqual(d1=form.errors, d2=self._user_slug_min_length_fail_errors_dict_by_value_length(value_length=5))
        # self.assertEqual(first=form.errors['slug'][0], second=self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=5)) # ~~~~ TODO: remove this line!

    def test_slug_validation_fails_with_username_too_short_2(self):  #### TODO
        data = self.data.copy()
        data['slug'] = 'aa-aa'
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_value_length=4))
        # self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_value_length=4))
        # self.assertDictEqual(d1=form.errors, d2=self._user_slug_min_length_fail_errors_dict_by_value_length(value_length=5))
        # self.assertEqual(first=form.errors['slug'][0], second=self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=5)) # ~~~~ TODO: remove this line!

    def test_slug_validation_fails_with_username_too_short_3(self):  #### TODO
        data = self.data.copy()
        data['slug'] = 'a-a-a-a'
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_value_length=4))
        # self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_value_length=4))
        # self.assertDictEqual(d1=form.errors, d2=self._user_slug_min_length_fail_errors_dict_by_value_length(value_length=5))
        # self.assertEqual(first=form.errors['slug'][0], second=self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=5)) # ~~~~ TODO: remove this line!

    def test_slug_validation_fails_with_username_too_short_4(self):  #### TODO
        data = self.data.copy()
        data['slug'] = '---a--a--a--a---'
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_value_length=4))
        # self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_value_length=4))
        # self.assertDictEqual(d1=form.errors, d2=self._user_slug_min_length_fail_errors_dict_by_value_length(value_length=5))
        # self.assertEqual(first=form.errors['slug'][0], second=self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=5)) # ~~~~ TODO: remove this line!

    def test_zzz(self):  #### TODO
        # a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a-a - 60 chars ok; 59 too short; override settings MIN_SLUG_LENGTH = 60; test also in views and models; also in Hebrew.
        # נא לוודא ששם המשתמש/ת מכיל 60 תווים לפחות (מכיל 59).
        raise Exception

    def test_slug_validation_fails_with_username_too_long(self):
        data = self.data.copy()
        data['slug'] = 'a' * 201
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_value_length=201))
        # self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_value_length=201))
        # self.assertDictEqual(d1=form.errors, d2=self._user_slug_max_length_fail_errors_dict_by_value_length(value_length=201))
        # self.assertEqual(first=form.errors['slug'][0], second=self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=200, value_length=201)) # ~~~~ TODO: remove this line!

    def test_slug_validation_fails_with_invalid_username_regex(self):
        data = self.data.copy()
        data['slug'] = '1234567890digits'
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True))
        # self.assertDictEqual(d1=form.errors, d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=Entity, slug_fail=True))
        # self.assertDictEqual(d1=form.errors, d2=self._user_slug_username_must_start_with_4_or_more_letters_errors_dict())
        # self.assertEqual(first=form.errors['slug'][0], second=self._user_username_must_start_with_4_or_more_letters_error_message) # ~~~~ TODO: remove this line!

    def test_cannot_register_invalid_email(self):
        data = self.data.copy()
        data['email'] = 'email'
        form = RegistrationForm(language_code=self.language_code, data=data)
        form.full_clean()
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._enter_a_valid_email_address_errors_dict())

    def test_invalid_date_of_birth_list_fail(self):
        # import speedy.core.settings.tests as tests_settings # ~~~~ TODO: remove this line!
        for date_of_birth in settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST:
            print(date_of_birth)
            data = self.data.copy()
            data['date_of_birth'] = date_of_birth
            form = RegistrationForm(language_code=self.language_code, data=data)
            form.full_clean()
            self.assertFalse(expr=form.is_valid(), msg="{} is a valid date of birth.".format(date_of_birth))
            self.assertDictEqual(d1=form.errors, d2=self._date_of_birth_errors_dict_by_date_of_birth(date_of_birth=date_of_birth), msg='"{}" - Unexpected error messages.'.format(date_of_birth))


@only_on_sites_with_login
class RegistrationFormEnglishTestCase(RegistrationFormTestCaseMixin, SpeedyCoreAccountsLanguageMixin, TestCase):
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
class RegistrationFormHebrewTestCase(RegistrationFormTestCaseMixin, SpeedyCoreAccountsLanguageMixin, TestCase):
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


@only_on_sites_with_login
class ProfilePrivacyFormTestCase(TestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.primary_email = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.confirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.unconfirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.other_user_email = UserEmailAddressFactory(user=self.other_user, is_confirmed=True)


@only_on_sites_with_login
class ProfileNotificationsFormTestCase(TestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()

    @exclude_on_speedy_match
    def test_has_correct_fields(self):
        form = ProfileNotificationsForm(instance=self.user)
        self.assertListEqual(list1=list(form.fields.keys()), list2=[
            'notify_on_message',
        ])


@only_on_sites_with_login
class PasswordResetFormTestCase(TestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.primary_email = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
        self.confirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
        self.unconfirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=False)
        self.other_user_email = UserEmailAddressFactory(user=self.other_user, is_confirmed=True)
        self.form = PasswordResetForm()

    def test_can_reset_using_primary_email(self):
        self.assertSetEqual(set1=self.form.get_users(email=self.primary_email.email), set2={self.user})

    def test_can_reset_using_primary_email_uppercase(self):
        self.assertSetEqual(set1=self.form.get_users(email=self.primary_email.email.upper()), set2={self.user})

    def test_can_reset_using_confirmed_email(self):
        self.assertSetEqual(set1=self.form.get_users(email=self.confirmed_email.email), set2={self.user})

    def test_can_reset_using_unconfirmed_email(self):
        self.assertSetEqual(set1=self.form.get_users(email=self.unconfirmed_email.email), set2={self.user})

    def test_can_reset_using_other_user_email(self):
        self.assertSetEqual(set1=self.form.get_users(email=self.other_user_email.email), set2={self.other_user})

    def test_cannot_reset_using_unknown_email(self):
        self.assertSetEqual(set1=self.form.get_users(email='email@example.com'), set2=set())


class DeactivationFormTestCaseMixin(object):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()

    def test_incorrect_password(self):
        data = {
            'password': 'wrong password!!',
        }
        form = SiteProfileDeactivationForm(user=self.user, data=data)
        self.assertFalse(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2=self._invalid_password_errors_dict())

    def test_correct_password(self):
        data = {
            'password': USER_PASSWORD,
        }
        form = SiteProfileDeactivationForm(user=self.user, data=data)
        self.assertTrue(expr=form.is_valid())
        self.assertDictEqual(d1=form.errors, d2={})


@only_on_sites_with_login
class DeactivationFormEnglishTestCase(DeactivationFormTestCaseMixin, SpeedyCoreAccountsLanguageMixin, TestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='en')


@only_on_sites_with_login
@override_settings(LANGUAGE_CODE='he')
class DeactivationFormHebrewTestCase(DeactivationFormTestCaseMixin, SpeedyCoreAccountsLanguageMixin, TestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='he')


# ~~~~ TODO: test ProfileForm - try to change username and get error message. ("You can't change your username.")
