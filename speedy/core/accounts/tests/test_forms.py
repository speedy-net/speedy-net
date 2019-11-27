from datetime import date

from django.conf import settings as django_settings
from django.test import override_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test import tests_settings
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_sites_with_login
    from speedy.core.base.test.utils import get_django_settings_class_with_override_settings
    from speedy.core.accounts.test.mixins import SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin
    from speedy.core.base.utils import normalize_slug, normalize_username
    from speedy.core.accounts.models import Entity, User, UserEmailAddress
    from speedy.core.accounts.forms import RegistrationForm, PasswordResetForm, SiteProfileDeactivationForm

    from speedy.core.base.test.utils import get_random_user_password
    from speedy.core.accounts.test.user_factories import ActiveUserFactory
    from speedy.core.accounts.test.user_email_address_factories import UserEmailAddressFactory


    class RegistrationFormTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin):
        def set_up(self):
            super().set_up()
            self.password = get_random_user_password()
            self.data = {
                'email': 'email@example.com',
                'slug': 'user-22',
                'new_password1': self.password,
                'gender': 1,
                'date_of_birth': '1980-01-01',
            }
            self.username = normalize_username(username=self.data['slug'])
            self.slug = normalize_slug(slug=self.data['slug'])
            self.assertNotEqual(first=self.password, second=tests_settings.USER_PASSWORD)
            self.assertEqual(first=self.username, second='user22')
            self.assertEqual(first=self.slug, second='user-22')
            self.assertNotEqual(first=self.username, second=self.slug)
            self.assert_models_count(
                entity_count=0,
                user_count=0,
                user_email_address_count=0,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=0,
            )

        def set_up_required_fields(self):
            self.required_fields = self.data.keys()
            self.assert_registration_form_required_fields(required_fields=self.required_fields)

        def run_test_all_slugs_to_test_list(self, test_settings):
            ok_count, model_save_failures_count = 0, 0
            for slug_dict in tests_settings.SLUGS_TO_TEST_LIST:
                data = self.data.copy()
                data['slug'] = slug_dict["slug"]
                username = normalize_username(username=data['slug'])
                slug = normalize_slug(slug=data['slug'])
                data['email'] = "{username}@example.com".format(username=username)
                self.assertEqual(first=slug_dict["slug_length"], second=len(slug))
                if (slug_dict["slug_length"] >= User.settings.MIN_SLUG_LENGTH):
                    form = RegistrationForm(language_code=self.language_code, data=data)
                    form.full_clean()
                    self.assertTrue(expr=form.is_valid())
                    self.assertDictEqual(d1=form.errors, d2={})
                    user = form.save()
                    self.assertEqual(first=User.objects.filter(username=username).count(), second=1)
                    user = User.objects.get(username=username)
                    self.assertEqual(first=user.username, second=username)
                    self.assertEqual(first=user.slug, second=slug)
                    ok_count += 1
                else:
                    form = RegistrationForm(language_code=self.language_code, data=data)
                    form.full_clean()
                    self.assertFalse(expr=form.is_valid())
                    self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_least_min_length_characters_errors_dict_by_value_length(model=User, slug_fail=True, slug_value_length=slug_dict["slug_length"]))
                    self.assertEqual(first=User.objects.filter(username=username).count(), second=0)
                    model_save_failures_count += 1
            counts_tuple = (ok_count, model_save_failures_count)
            self.assert_models_count(
                entity_count=ok_count,
                user_count=ok_count,
                user_email_address_count=ok_count,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=ok_count,
            )
            self.assertEqual(first=sum(counts_tuple), second=len(tests_settings.SLUGS_TO_TEST_LIST))
            self.assertTupleEqual(tuple1=counts_tuple, tuple2=test_settings["expected_counts_tuple"])

        def test_visitor_can_register(self):
            form = RegistrationForm(language_code=self.language_code, data=self.data)
            form.full_clean()
            self.assertTrue(expr=form.is_valid())
            self.assertDictEqual(d1=form.errors, d2={})
            user = form.save()
            self.assert_models_count(
                entity_count=1,
                user_count=1,
                user_email_address_count=1,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=1,
            )
            self.assertEqual(first=Entity.objects.filter(username=self.username).count(), second=1)
            self.assertEqual(first=User.objects.filter(username=self.username).count(), second=1)
            entity = Entity.objects.get(username=self.username)
            user = User.objects.get(username=self.username)
            self.assertEqual(first=user, second=entity.user)
            self.assertEqual(first=entity.id, second=user.id)
            self.assertEqual(first=entity.username, second=user.username)
            self.assertEqual(first=entity.slug, second=user.slug)
            self.assertEqual(first=len(entity.id), second=15)
            self.assertTrue(expr=user.check_password(raw_password=self.password))
            self.assertFalse(expr=user.check_password(raw_password=tests_settings.USER_PASSWORD))
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
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
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

        def test_required_fields_1(self):
            data = {}
            self.run_test_required_fields(data=data)

        def test_required_fields_2(self):
            data = {field_name: '' for field_name in self.required_fields}
            self.run_test_required_fields(data=data)

        def test_non_unique_confirmed_email_address(self):
            existing_user_email = UserEmailAddressFactory(email=self.data['email'], is_confirmed=True)
            existing_user = existing_user_email.user
            self.assert_models_count(
                entity_count=1,
                user_count=1,
                user_email_address_count=1,
                confirmed_email_address_count=1,
                unconfirmed_email_address_count=0,
            )
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=1,
                user_unconfirmed_email_addresses_count=0,
            )
            form = RegistrationForm(language_code=self.language_code, data=self.data)
            form.full_clean()
            self.assertFalse(expr=form.is_valid())
            self.assertDictEqual(d1=form.errors, d2=self._this_email_is_already_in_use_errors_dict())
            self.assert_models_count(
                entity_count=1,
                user_count=1,
                user_email_address_count=1,
                confirmed_email_address_count=1,
                unconfirmed_email_address_count=0,
            )
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=1,
                user_unconfirmed_email_addresses_count=0,
            )
            existing_user = User.objects.get(pk=existing_user.pk)
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=1,
                user_unconfirmed_email_addresses_count=0,
            )

        def test_non_unique_unconfirmed_email_address(self):
            # Unconfirmed email address is deleted if another user adds it again.
            existing_user_email = UserEmailAddressFactory(email=self.data['email'], is_confirmed=False)
            existing_user = existing_user_email.user
            self.assert_models_count(
                entity_count=1,
                user_count=1,
                user_email_address_count=1,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=1,
            )
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            form = RegistrationForm(language_code=self.language_code, data=self.data)
            form.full_clean()
            self.assertTrue(expr=form.is_valid())
            self.assertDictEqual(d1=form.errors, d2={})
            user = form.save()
            self.assert_models_count(
                entity_count=2,
                user_count=2,
                user_email_address_count=1,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=1,
            )
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=0,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=0,
            )
            existing_user = User.objects.get(pk=existing_user.pk)
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=0,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=0,
            )

        def test_slug_validation_fails_with_reserved_username(self):
            data = self.data.copy()
            data['slug'] = 'webmaster'
            form = RegistrationForm(language_code=self.language_code, data=data)
            form.full_clean()
            self.assertFalse(expr=form.is_valid())
            self.assertDictEqual(d1=form.errors, d2=self._this_username_is_already_taken_errors_dict(slug_fail=True))

        def test_slug_validation_fails_with_reserved_and_too_short_username(self):
            data = self.data.copy()
            data['slug'] = 'mail'
            form = RegistrationForm(language_code=self.language_code, data=data)
            form.full_clean()
            self.assertFalse(expr=form.is_valid())
            self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_value_length=4))

        def test_slug_validation_fails_with_username_already_taken(self):
            ActiveUserFactory(slug='validslug')
            data = self.data.copy()
            data['slug'] = 'valid-slug'
            form = RegistrationForm(language_code=self.language_code, data=data)
            form.full_clean()
            self.assertFalse(expr=form.is_valid())
            self.assertDictEqual(d1=form.errors, d2=self._this_username_is_already_taken_errors_dict(slug_fail=True))

        def test_slug_validation_ok(self):
            slug_list = ['a' * 6, '---a--a--a--a--a--a---']
            for slug in slug_list:
                data = self.data.copy()
                data['slug'] = slug
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertTrue(expr=form.is_valid())
                self.assertDictEqual(d1=form.errors, d2={})
                user = form.save()
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=1,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=1,
                )
                user = User.objects.get(username=normalize_username(username=slug))
                user.delete()
                self.assert_models_count(
                    entity_count=0,
                    user_count=0,
                    user_email_address_count=0,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=0,
                )

        def test_slug_validation_fails_with_username_too_short(self):
            slug_list = ['a' * 5, 'aa-aa', 'a-a-a-a', '---a--a--a--a---', '---a--a--a--a--a---']
            for slug in slug_list:
                username_value_length = len(normalize_username(username=slug))
                if (slug in ['a' * 5, '---a--a--a--a--a---']):
                    self.assertEqual(first=username_value_length, second=5)
                else:
                    self.assertEqual(first=username_value_length, second=4)
                data = self.data.copy()
                data['slug'] = slug
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertFalse(expr=form.is_valid())
                self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_value_length=username_value_length))

        def test_slug_and_username_min_length_ok(self):
            # print("test_slug_and_username_min_length_ok: django_settings.USER_SETTINGS.MIN_SLUG_LENGTH", django_settings.USER_SETTINGS.MIN_SLUG_LENGTH)####
            # print("test_slug_and_username_min_length_ok: django_settings.USER_SETTINGS.MAX_SLUG_LENGTH", django_settings.USER_SETTINGS.MAX_SLUG_LENGTH)####
            # print("test_slug_and_username_min_length_ok: User.settings.MIN_SLUG_LENGTH", User.settings.MIN_SLUG_LENGTH)####
            # print("test_slug_and_username_min_length_ok: User.settings.MAX_SLUG_LENGTH", User.settings.MAX_SLUG_LENGTH)####
            self.assertEqual(first=User.settings.MIN_SLUG_LENGTH, second=6)
            test_settings = {
                "expected_counts_tuple": (8, 0),
            }
            self.run_test_all_slugs_to_test_list(test_settings=test_settings)

        @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MIN_SLUG_LENGTH=tests_settings.OVERRIDE_USER_SETTINGS.MIN_SLUG_LENGTH))
        def test_slug_min_length_fail_username_min_length_ok(self):
            self.assertEqual(first=User.settings.MIN_SLUG_LENGTH, second=60)
            test_settings = {
                "expected_counts_tuple": (4, 4),
            }
            self.run_test_all_slugs_to_test_list(test_settings=test_settings)

        def test_slug_validation_fails_with_username_too_long(self):
            data = self.data.copy()
            data['slug'] = 'a' * 201
            form = RegistrationForm(language_code=self.language_code, data=data)
            form.full_clean()
            self.assertFalse(expr=form.is_valid())
            self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_value_length=201))

        def test_slug_validation_fails_with_invalid_username_regex(self):
            slug_list = ['0' * 6, '0test1', '1234567890digits', 'aaa', 'aaa 9999', 'aaa-9999', 'aaa+9999']
            for slug in slug_list:
                data = self.data.copy()
                data['slug'] = slug
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertFalse(expr=form.is_valid(), msg="{} is a valid slug.".format(slug))
                self.assertDictEqual(d1=form.errors, d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True), msg='"{}" - Unexpected error messages.'.format(slug))

        def test_cannot_register_invalid_email(self):
            data = self.data.copy()
            data['email'] = 'email'
            form = RegistrationForm(language_code=self.language_code, data=data)
            form.full_clean()
            self.assertFalse(expr=form.is_valid())
            self.assertDictEqual(d1=form.errors, d2=self._enter_a_valid_email_address_errors_dict())

        def test_invalid_date_of_birth_list_fail(self):
            for date_of_birth in tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST:
                data = self.data.copy()
                data['date_of_birth'] = date_of_birth
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertFalse(expr=form.is_valid(), msg="{} is a valid date of birth.".format(date_of_birth))
                self.assertDictEqual(d1=form.errors, d2=self._date_of_birth_errors_dict_by_date_of_birth(date_of_birth=date_of_birth), msg='"{}" - Unexpected error messages.'.format(date_of_birth))


    @only_on_sites_with_login
    class RegistrationFormEnglishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
        def set_up(self):
            super().set_up()
            self.data.update({
                'first_name_en': "Doron",
                'last_name_en': "Matalon",
            })
            self.first_name = "Doron"
            self.last_name = "Matalon"
            self.set_up_required_fields()

        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='en')


    @only_on_sites_with_login
    @override_settings(LANGUAGE_CODE='he')
    class RegistrationFormHebrewTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
        def set_up(self):
            super().set_up()
            self.data.update({
                'first_name_he': "דורון",
                'last_name_he': "מטלון",
            })
            self.first_name = "דורון"
            self.last_name = "מטלון"
            self.set_up_required_fields()

        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='he')


    @only_on_sites_with_login
    class ProfilePrivacyFormTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user = ActiveUserFactory()
            self.other_user = ActiveUserFactory()
            self.primary_email = UserEmailAddressFactory(user=self.user, is_confirmed=True, is_primary=True)
            self.confirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
            self.unconfirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=False)
            self.other_user_email = UserEmailAddressFactory(user=self.other_user, is_confirmed=True)


    class ProfileNotificationsFormTestCaseMixin(object):
        def set_up(self):
            super().set_up()
            self.user = ActiveUserFactory()

        def test_has_correct_fields(self):
            raise NotImplementedError()


    @only_on_sites_with_login
    class PasswordResetFormTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
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


    class DeactivationFormTestCaseMixin(SpeedyCoreAccountsLanguageMixin):
        def set_up(self):
            super().set_up()
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
                'password': tests_settings.USER_PASSWORD,
            }
            form = SiteProfileDeactivationForm(user=self.user, data=data)
            self.assertTrue(expr=form.is_valid())
            self.assertDictEqual(d1=form.errors, d2={})


    @only_on_sites_with_login
    class DeactivationFormEnglishTestCase(DeactivationFormTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='en')


    @only_on_sites_with_login
    @override_settings(LANGUAGE_CODE='he')
    class DeactivationFormHebrewTestCase(DeactivationFormTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='he')


    # ~~~~ TODO: test ProfileForm - try to change username and get error message. ("You can't change your username.")
