"""
Test cases for the forms of the Speedy Core accounts app: registration, profile notifications, password reset and deactivation forms.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from datetime import date, timedelta

        from django.test import override_settings

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.base.test.utils import get_django_settings_class_with_override_settings, get_random_user_password
        from speedy.core.accounts.test.mixins import SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin

        from speedy.core.accounts.test.user_factories import ActiveUserFactory
        from speedy.core.accounts.test.user_email_address_factories import UserEmailAddressFactory

        from speedy.core.base.utils import normalize_slug, normalize_username, to_attribute
        from speedy.core.accounts.models import Entity, User, UserEmailAddress
        from speedy.core.accounts.forms import RegistrationForm, PasswordResetForm, SiteProfileDeactivationForm


        class RegistrationFormTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Test mixin for the registration form, covering slug/username normalization, validation and required fields, duplicate emails, and invalid dates of birth.
            """

            def set_up(self):
                """
                Creates the base registration data dict, password and expected username/slug, and asserts no models exist yet.
                """
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
                """
                Computes the set of required fields (all data fields except last name for the current language) and asserts the form reports them as required.
                """
                self.required_fields = self.data.keys() - {to_attribute(name="last_name", language_code=self.language_code)}
                self.assert_registration_form_required_fields(required_fields=self.required_fields)

            def run_test_all_slugs_to_test_list(self, test_settings):
                """
                Registers a user for each slug in tests_settings.SLUGS_TO_TEST_LIST, asserting success for slugs that are long enough and failure (with the minimum length error) otherwise, then checks the total counts against test_settings["expected_counts_tuple"].

                :param test_settings: A dict with the key "expected_counts_tuple", the expected (ok_count, model_save_failures_count) tuple.
                :type test_settings: dict
                """
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
                        self.assertIs(expr1=form.is_valid(), expr2=True)
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
                        self.assertIs(expr1=form.is_valid(), expr2=False)
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
                """
                Verify a visitor can register and that the created entity/user and its email address have all the expected values.
                """
                form = RegistrationForm(language_code=self.language_code, data=self.data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=True)
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
                self.assertIs(expr1=user.check_password(raw_password=self.password), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=False)
                self.assertEqual(first=user.first_name, second=self.first_name)
                self.assertEqual(first=user.first_name_en, second=self.first_name)
                self.assertEqual(first=user.first_name_fr, second=self.first_name)
                self.assertEqual(first=user.first_name_de, second=self.first_name)
                self.assertEqual(first=user.first_name_es, second=self.first_name)
                self.assertEqual(first=user.first_name_pt, second=self.first_name)
                self.assertEqual(first=user.first_name_it, second=self.first_name)
                self.assertEqual(first=user.first_name_nl, second=self.first_name)
                self.assertEqual(first=user.first_name_ja, second=self.first_name)
                self.assertEqual(first=user.first_name_ru, second=self.first_name)
                self.assertEqual(first=user.first_name_zh, second=self.first_name)
                self.assertEqual(first=user.first_name_pl, second=self.first_name)
                self.assertEqual(first=user.first_name_fa, second=self.first_name)
                self.assertEqual(first=user.first_name_he, second=self.first_name)
                self.assertEqual(first=user.first_name_ko, second=self.first_name)
                self.assertEqual(first=user.first_name_ar, second=self.first_name)
                self.assertEqual(first=user.first_name_id, second=self.first_name)
                self.assertEqual(first=user.first_name_uk, second=self.first_name)
                self.assertEqual(first=user.first_name_tr, second=self.first_name)
                self.assertEqual(first=user.first_name_vi, second=self.first_name)
                self.assertEqual(first=user.first_name_cs, second=self.first_name)
                self.assertEqual(first=user.first_name_sv, second=self.first_name)
                self.assertEqual(first=user.first_name_fi, second=self.first_name)
                self.assertEqual(first=user.first_name_hu, second=self.first_name)
                self.assertEqual(first=user.first_name_th, second=self.first_name)
                self.assertEqual(first=user.first_name_el, second=self.first_name)
                self.assertEqual(first=user.first_name_ms, second=self.first_name)
                self.assertEqual(first=user.first_name_sr, second=self.first_name)
                self.assertEqual(first=user.first_name_ro, second=self.first_name)
                self.assertEqual(first=user.first_name_bn, second=self.first_name)
                self.assertEqual(first=user.first_name_ca, second=self.first_name)
                self.assertEqual(first=user.first_name_no, second=self.first_name)
                self.assertEqual(first=user.first_name_bg, second=self.first_name)
                self.assertEqual(first=user.first_name_da, second=self.first_name)
                self.assertEqual(first=user.first_name_sk, second=self.first_name)
                self.assertEqual(first=user.first_name_hi, second=self.first_name)
                self.assertEqual(first=user.first_name_et, second=self.first_name)
                self.assertEqual(first=user.first_name_hr, second=self.first_name)
                self.assertEqual(first=user.first_name_az, second=self.first_name)
                self.assertEqual(first=user.first_name_zh_yue, second=self.first_name)
                self.assertEqual(first=user.first_name_lt, second=self.first_name)
                self.assertEqual(first=user.first_name_sl, second=self.first_name)
                self.assertEqual(first=user.first_name_eu, second=self.first_name)
                self.assertEqual(first=user.first_name_hy, second=self.first_name)
                self.assertEqual(first=user.first_name_uz, second=self.first_name)
                self.assertEqual(first=user.first_name_ta, second=self.first_name)
                self.assertEqual(first=user.first_name_lv, second=self.first_name)
                self.assertEqual(first=user.last_name, second=self.last_name)
                self.assertEqual(first=user.last_name_en, second=self.last_name)
                self.assertEqual(first=user.last_name_fr, second=self.last_name)
                self.assertEqual(first=user.last_name_de, second=self.last_name)
                self.assertEqual(first=user.last_name_es, second=self.last_name)
                self.assertEqual(first=user.last_name_pt, second=self.last_name)
                self.assertEqual(first=user.last_name_it, second=self.last_name)
                self.assertEqual(first=user.last_name_nl, second=self.last_name)
                self.assertEqual(first=user.last_name_ja, second=self.last_name)
                self.assertEqual(first=user.last_name_ru, second=self.last_name)
                self.assertEqual(first=user.last_name_zh, second=self.last_name)
                self.assertEqual(first=user.last_name_pl, second=self.last_name)
                self.assertEqual(first=user.last_name_fa, second=self.last_name)
                self.assertEqual(first=user.last_name_he, second=self.last_name)
                self.assertEqual(first=user.last_name_ko, second=self.last_name)
                self.assertEqual(first=user.last_name_ar, second=self.last_name)
                self.assertEqual(first=user.last_name_id, second=self.last_name)
                self.assertEqual(first=user.last_name_uk, second=self.last_name)
                self.assertEqual(first=user.last_name_tr, second=self.last_name)
                self.assertEqual(first=user.last_name_vi, second=self.last_name)
                self.assertEqual(first=user.last_name_cs, second=self.last_name)
                self.assertEqual(first=user.last_name_sv, second=self.last_name)
                self.assertEqual(first=user.last_name_fi, second=self.last_name)
                self.assertEqual(first=user.last_name_hu, second=self.last_name)
                self.assertEqual(first=user.last_name_th, second=self.last_name)
                self.assertEqual(first=user.last_name_el, second=self.last_name)
                self.assertEqual(first=user.last_name_ms, second=self.last_name)
                self.assertEqual(first=user.last_name_sr, second=self.last_name)
                self.assertEqual(first=user.last_name_ro, second=self.last_name)
                self.assertEqual(first=user.last_name_bn, second=self.last_name)
                self.assertEqual(first=user.last_name_ca, second=self.last_name)
                self.assertEqual(first=user.last_name_no, second=self.last_name)
                self.assertEqual(first=user.last_name_bg, second=self.last_name)
                self.assertEqual(first=user.last_name_da, second=self.last_name)
                self.assertEqual(first=user.last_name_sk, second=self.last_name)
                self.assertEqual(first=user.last_name_hi, second=self.last_name)
                self.assertEqual(first=user.last_name_et, second=self.last_name)
                self.assertEqual(first=user.last_name_hr, second=self.last_name)
                self.assertEqual(first=user.last_name_az, second=self.last_name)
                self.assertEqual(first=user.last_name_zh_yue, second=self.last_name)
                self.assertEqual(first=user.last_name_lt, second=self.last_name)
                self.assertEqual(first=user.last_name_sl, second=self.last_name)
                self.assertEqual(first=user.last_name_eu, second=self.last_name)
                self.assertEqual(first=user.last_name_hy, second=self.last_name)
                self.assertEqual(first=user.last_name_uz, second=self.last_name)
                self.assertEqual(first=user.last_name_ta, second=self.last_name)
                self.assertEqual(first=user.last_name_lv, second=self.last_name)
                self.assertEqual(first=user.username, second=self.username)
                self.assertEqual(first=user.username, second='user22')
                self.assertEqual(first=user.slug, second=self.slug)
                self.assertEqual(first=user.slug, second='user-22')
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                self.assertEqual(first=user.email_addresses.first().email, second='email@example.com')
                self.assertIs(expr1=user.email_addresses.first().is_confirmed, expr2=False)
                self.assertIs(expr1=user.email_addresses.first().is_primary, expr2=True)
                for (key, value) in self.data.items():
                    if (not (key in ['new_password1', 'date_of_birth'])):
                        self.assertEqual(first=getattr(user, key), second=value)
                self.assertEqual(first=user.date_of_birth, second=date(year=1980, month=1, day=1))

            def test_slug_gets_converted_to_username(self):
                """
                Verify a slug with dashes is kept as-is while the derived username has the dashes removed.
                """
                data = self.data.copy()
                data['slug'] = 'this-is-a-slug'
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=True)
                self.assertDictEqual(d1=form.errors, d2={})
                user = form.save()
                self.assertEqual(first=user.slug, second='this-is-a-slug')
                self.assertEqual(first=user.username, second='thisisaslug')

            def test_slug_dots_and_underscores_gets_converted_to_dashes(self):
                """
                Verify dots and underscores in the slug are converted to dashes.
                """
                data = self.data.copy()
                data['slug'] = 'this.is__a.slug'
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=True)
                self.assertDictEqual(d1=form.errors, d2={})
                user = form.save()
                self.assertEqual(first=user.slug, second='this-is-a-slug')
                self.assertEqual(first=user.username, second='thisisaslug')

            def test_slug_dashes_are_trimmed_and_double_dashes_are_converted_to_single_dashes(self):
                """
                Verify leading/trailing dashes are trimmed and repeated dashes are collapsed to a single dash.
                """
                data = self.data.copy()
                data['slug'] = '--this--is---a--slug--'
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=True)
                self.assertDictEqual(d1=form.errors, d2={})
                user = form.save()
                self.assertEqual(first=user.slug, second='this-is-a-slug')
                self.assertEqual(first=user.username, second='thisisaslug')

            def test_slug_gets_converted_to_lowercase(self):
                """
                Verify an uppercase slug is converted to lowercase.
                """
                data = self.data.copy()
                data['slug'] = 'THIS-IS-A-SLUG'
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=True)
                self.assertDictEqual(d1=form.errors, d2={})
                user = form.save()
                self.assertEqual(first=user.slug, second='this-is-a-slug')
                self.assertEqual(first=user.username, second='thisisaslug')

            def test_email_gets_converted_to_lowercase(self):
                """
                Verify an uppercase email address is converted to lowercase.
                """
                data = self.data.copy()
                data['email'] = 'EMAIL22@EXAMPLE.COM'
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=True)
                self.assertDictEqual(d1=form.errors, d2={})
                user = form.save()
                email_addresses = UserEmailAddress.objects.filter(user=user)
                email_addresses_set = {e.email for e in email_addresses}
                self.assertSetEqual(set1=email_addresses_set, set2={'email22@example.com'})

            def run_test_required_fields(self, data):
                """
                Submits the given data and asserts the form is invalid with the expected "all required fields are required" errors.

                :param data: The form data to submit.
                :type data: dict
                """
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._registration_form_all_the_required_fields_are_required_errors_dict())

            def test_required_fields_1(self):
                """
                Verify submitting an empty data dict fails with all required fields reported as required.
                """
                data = {}
                self.run_test_required_fields(data=data)

            def test_required_fields_2(self):
                """
                Verify submitting empty-string values for all required fields fails with all required fields reported as required.
                """
                data = {field_name: '' for field_name in self.required_fields}
                self.run_test_required_fields(data=data)

            def test_non_unique_confirmed_email_address(self):
                """
                Verify registering with an email address that is already confirmed by another user fails and leaves the existing user and email address unchanged.
                """
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
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                form = RegistrationForm(language_code=self.language_code, data=self.data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=False)
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
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )

            def test_non_unique_unconfirmed_email_address(self):
                """
                Verify registering with an email address that is unconfirmed and was recently added by another user fails and leaves the existing user and email address unchanged.
                """
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
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                form = RegistrationForm(language_code=self.language_code, data=self.data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._this_email_is_already_in_use_errors_dict())
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
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )

            def test_non_unique_unconfirmed_email_address_registered_6_minutes_ago(self):
                """
                Verify registering with an email address that is unconfirmed and was added by another user 6 minutes ago succeeds, deleting the old unconfirmed address.
                """
                # Unconfirmed email address is deleted if another user adds it again.
                existing_user_email = UserEmailAddressFactory(email=self.data['email'], is_confirmed=False)
                existing_user_email.date_created -= timedelta(minutes=6)
                existing_user_email.save()
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
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                form = RegistrationForm(language_code=self.language_code, data=self.data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=True)
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
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )

            def test_slug_validation_fails_with_reserved_username(self):
                """
                Verify registering with a reserved username (e.g. "webmaster") fails as already taken.
                """
                data = self.data.copy()
                data['slug'] = 'webmaster'
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._this_username_is_already_taken_errors_dict(slug_fail=True))

            def test_slug_validation_fails_with_reserved_and_too_short_username(self):
                """
                Verify registering with a reserved and too-short username fails with the minimum alphanumeric length error.
                """
                data = self.data.copy()
                data['slug'] = 'mail'
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_value_length=4))

            def test_slug_validation_fails_with_username_already_taken(self):
                """
                Verify registering with a slug whose normalized username is already taken by another user fails as already taken.
                """
                ActiveUserFactory(slug='validslug')
                data = self.data.copy()
                data['slug'] = 'valid-slug'
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._this_username_is_already_taken_errors_dict(slug_fail=True))

            def test_slug_validation_ok(self):
                """
                Verify registering with slugs of the minimum valid length succeeds and the created user can then be deleted.
                """
                slug_list = ['a' * 6, '---a--a--a--a--a--a---']
                for slug in slug_list:
                    data = self.data.copy()
                    data['slug'] = slug
                    form = RegistrationForm(language_code=self.language_code, data=data)
                    form.full_clean()
                    self.assertIs(expr1=form.is_valid(), expr2=True)
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
                """
                Verify registering with slugs whose normalized username is below the minimum length fails with the minimum alphanumeric length error.
                """
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
                    self.assertIs(expr1=form.is_valid(), expr2=False)
                    self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_value_length=username_value_length))

            def test_slug_and_username_min_length_ok(self):
                """
                Verify the default minimum slug length is 6 and running all the test slugs yields the expected success/failure counts.
                """
                self.assertEqual(first=User.settings.MIN_SLUG_LENGTH, second=6)
                test_settings = {
                    "expected_counts_tuple": (8, 0),
                }
                self.run_test_all_slugs_to_test_list(test_settings=test_settings)

            @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MIN_SLUG_LENGTH=tests_settings.OVERRIDE_USER_SETTINGS.MIN_SLUG_LENGTH))
            def test_slug_min_length_fail_username_min_length_ok(self):
                """
                With an overridden higher minimum slug length, verify running all the test slugs yields the expected success/failure counts.
                """
                self.assertEqual(first=User.settings.MIN_SLUG_LENGTH, second=60)
                test_settings = {
                    "expected_counts_tuple": (4, 4),
                }
                self.run_test_all_slugs_to_test_list(test_settings=test_settings)

            def test_slug_validation_fails_with_username_too_long(self):
                """
                Verify registering with a slug longer than the maximum allowed length fails with the maximum length error.
                """
                data = self.data.copy()
                data['slug'] = 'a' * 201
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_value_length=201))

            def test_slug_validation_fails_with_invalid_username_regex(self):
                """
                Verify registering with slugs that don't match the required username regex (e.g. starting with digits, containing spaces or symbols) fails.
                """
                slug_list = ['0' * 6, '0test1', '1234567890digits', 'aaa', 'aaa 9999', 'aaa-9999', 'aaa+9999']
                for slug in slug_list:
                    data = self.data.copy()
                    data['slug'] = slug
                    form = RegistrationForm(language_code=self.language_code, data=data)
                    form.full_clean()
                    self.assertIs(expr1=form.is_valid(), expr2=False, msg="{} is a valid slug.".format(slug))
                    self.assertDictEqual(d1=form.errors, d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True), msg='"{}" - Unexpected error messages.'.format(slug))

            def test_cannot_register_invalid_email(self):
                """
                Verify registering with an invalid email address fails with the "enter a valid email address" error.
                """
                data = self.data.copy()
                data['email'] = 'email'
                form = RegistrationForm(language_code=self.language_code, data=data)
                form.full_clean()
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._enter_a_valid_email_address_errors_dict())

            def test_invalid_date_of_birth_list_fail(self):
                """
                Verify registering with each invalid date of birth in tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST fails with the expected error.
                """
                for date_of_birth in tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST:
                    data = self.data.copy()
                    data['date_of_birth'] = date_of_birth
                    form = RegistrationForm(language_code=self.language_code, data=data)
                    form.full_clean()
                    self.assertIs(expr1=form.is_valid(), expr2=False, msg="{} is a valid date of birth.".format(date_of_birth))
                    self.assertDictEqual(d1=form.errors, d2=self._date_of_birth_errors_dict_by_date_of_birth(date_of_birth=date_of_birth), msg='"{}" - Unexpected error messages.'.format(date_of_birth))


        @only_on_sites_with_login
        class RegistrationFormWithLastNameAllMainPlusLanguagesEnglishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in English, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a English first name and last name, then computes the required fields.
                """
                # Check names in English alphabet.
                super().set_up()
                self.data.update({
                    'first_name_en': "Doron",
                    'last_name_en': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class RegistrationFormWithLastNameAllMainPlusLanguagesFrenchTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in French, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a French first name and last name, then computes the required fields.
                """
                # Check names in French alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fr': "Alizée",
                    'last_name_fr': "Jacotey",
                })
                self.first_name = "Alizée"
                self.last_name = "Jacotey"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class RegistrationFormWithLastNameAllMainPlusLanguagesGermanTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in German, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a German first name and last name, then computes the required fields.
                """
                # Check names in German alphabet.
                super().set_up()
                self.data.update({
                    'first_name_de': "Doron",
                    'last_name_de': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class RegistrationFormWithLastNameAllMainPlusLanguagesSpanishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Spanish, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Spanish first name and last name, then computes the required fields.
                """
                # Check names in Spanish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_es': "Lionel",
                    'last_name_es': "Messi",
                })
                self.first_name = "Lionel"
                self.last_name = "Messi"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class RegistrationFormWithLastNameAllMainPlusLanguagesPortugueseTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Portuguese, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Portuguese first name and last name, then computes the required fields.
                """
                # Check names in Portuguese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_pt': "Cristiano",
                    'last_name_pt': "Ronaldo",
                })
                self.first_name = "Cristiano"
                self.last_name = "Ronaldo"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class RegistrationFormWithLastNameAllMainPlusLanguagesItalianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Italian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Italian first name and last name, then computes the required fields.
                """
                # Check names in Italian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_it': "Andrea",
                    'last_name_it': "Bocelli",
                })
                self.first_name = "Andrea"
                self.last_name = "Bocelli"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class RegistrationFormWithLastNameAllMainPlusLanguagesDutchTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Dutch, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Dutch first name and last name, then computes the required fields.
                """
                # Check names in Dutch alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class RegistrationFormWithLastNameAllMainPlusLanguagesJapaneseTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Japanese, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Japanese first name and last name, then computes the required fields.
                """
                # Check names in Japanese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ja': "ドロン",
                    'last_name_ja': "マタロン",
                })
                self.first_name = "ドロン"
                self.last_name = "マタロン"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class RegistrationFormWithLastNameAllMainPlusLanguagesRussianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Russian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Russian first name and last name, then computes the required fields.
                """
                # Check names in Russian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ru': "Дорон",
                    'last_name_ru': "Маталон",
                })
                self.first_name = "Дорон"
                self.last_name = "Маталон"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class RegistrationFormWithLastNameAllMainPlusLanguagesChineseTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Chinese, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Chinese first name and last name, then computes the required fields.
                """
                # Check names in Chinese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_zh': "多伦",
                    'last_name_zh': "马塔隆",
                })
                self.first_name = "多伦"
                self.last_name = "马塔隆"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class RegistrationFormWithLastNameAllMainPlusLanguagesPolishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Polish, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Polish first name and last name, then computes the required fields.
                """
                # Check names in Polish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_pl': "Łukasz",
                    'last_name_pl': "Wójcik",
                })
                self.first_name = "Łukasz"
                self.last_name = "Wójcik"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class RegistrationFormWithLastNameAllMainPlusLanguagesPersianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Persian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Persian first name and last name, then computes the required fields.
                """
                # Check names in Persian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fa': "درون",
                    'last_name_fa': "متالون",
                })
                self.first_name = "درون"
                self.last_name = "متالون"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class RegistrationFormWithLastNameAllMainPlusLanguagesHebrewTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Hebrew, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Hebrew first name and last name, then computes the required fields.
                """
                # Check names in Hebrew alphabet.
                super().set_up()
                self.data.update({
                    'first_name_he': "דורון",
                    'last_name_he': "מטלון",
                })
                self.first_name = "דורון"
                self.last_name = "מטלון"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class RegistrationFormWithLastNameAllMainPlusLanguagesKoreanTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Korean, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Korean first name and last name, then computes the required fields.
                """
                # Check names in Korean alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ko': "도론",
                    'last_name_ko': "마탈론",
                })
                self.first_name = "도론"
                self.last_name = "마탈론"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class RegistrationFormWithLastNameAllMainPlusLanguagesArabicTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Arabic, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Arabic first name and last name, then computes the required fields.
                """
                # Check names in Arabic alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ar': "دورون",
                    'last_name_ar': "ماتالون",
                })
                self.first_name = "دورون"
                self.last_name = "ماتالون"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class RegistrationFormWithLastNameAllMainPlusLanguagesIndonesianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Indonesian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Indonesian first name and last name, then computes the required fields.
                """
                # Check names in Indonesian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_id': "Doron",
                    'last_name_id': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class RegistrationFormWithLastNameAllMainPlusLanguagesUkrainianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Ukrainian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Ukrainian first name and last name, then computes the required fields.
                """
                # Check names in Ukrainian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_uk': "Дорон",
                    'last_name_uk': "Маталон",
                })
                self.first_name = "Дорон"
                self.last_name = "Маталон"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class RegistrationFormWithLastNameAllMainPlusLanguagesTurkishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Turkish, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Turkish first name and last name, then computes the required fields.
                """
                # Check names in Turkish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_tr': "Doron",
                    'last_name_tr': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class RegistrationFormWithLastNameAllMainPlusLanguagesVietnameseTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Vietnamese, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Vietnamese first name and last name, then computes the required fields.
                """
                # Check names in Vietnamese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_vi': "Doron",
                    'last_name_vi': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class RegistrationFormWithLastNameAllMainPlusLanguagesCzechTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Czech, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Czech first name and last name, then computes the required fields.
                """
                # Check names in Czech alphabet.
                super().set_up()
                self.data.update({
                    'first_name_cs': "Doron",
                    'last_name_cs': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class RegistrationFormWithLastNameAllMainPlusLanguagesSwedishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Swedish, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Swedish first name and last name, then computes the required fields.
                """
                # Check names in Swedish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_sv': "Doron",
                    'last_name_sv': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class RegistrationFormWithLastNameAllMainPlusLanguagesFinnishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Finnish, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Finnish first name and last name, then computes the required fields.
                """
                # Check names in Finnish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fi': "Doron",
                    'last_name_fi': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class RegistrationFormWithLastNameAllMainPlusLanguagesHungarianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Hungarian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Hungarian first name and last name, then computes the required fields.
                """
                # Check names in Hungarian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_hu': "Doron",
                    'last_name_hu': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class RegistrationFormWithLastNameAllMainPlusLanguagesThaiTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Thai, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Thai first name and last name, then computes the required fields.
                """
                # Check names in Thai alphabet.
                super().set_up()
                self.data.update({
                    'first_name_th': "ดรอน",
                    'last_name_th': "มาทาลอน",
                })
                self.first_name = "ดรอน"
                self.last_name = "มาทาลอน"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class RegistrationFormWithLastNameAllMainPlusLanguagesGreekTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Greek, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Greek first name and last name, then computes the required fields.
                """
                # Check names in Greek alphabet.
                super().set_up()
                self.data.update({
                    'first_name_el': "Ντορόν",
                    'last_name_el': "Ματαλόν",
                })
                self.first_name = "Ντορόν"
                self.last_name = "Ματαλόν"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class RegistrationFormWithLastNameAllMainPlusLanguagesMalayTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Malay, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Malay first name and last name, then computes the required fields.
                """
                # Check names in Malay alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ms': "Doron",
                    'last_name_ms': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class RegistrationFormWithLastNameAllMainPlusLanguagesSerbianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Serbian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Serbian first name and last name, then computes the required fields.
                """
                # Check names in Serbian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_sr': "Дорон",
                    'last_name_sr': "Маталон",
                })
                self.first_name = "Дорон"
                self.last_name = "Маталон"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class RegistrationFormWithLastNameAllMainPlusLanguagesRomanianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Romanian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Romanian first name and last name, then computes the required fields.
                """
                # Check names in Romanian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ro': "Doron",
                    'last_name_ro': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class RegistrationFormWithLastNameAllMainPlusLanguagesBengaliTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Bengali, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Bengali first name and last name, then computes the required fields.
                """
                # Check names in Bengali alphabet.
                super().set_up()
                self.data.update({
                    'first_name_bn': "ডোরন",
                    'last_name_bn': "মাতালন",
                })
                self.first_name = "ডোরন"
                self.last_name = "মাতালন"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class RegistrationFormWithLastNameAllMainPlusLanguagesCatalanTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Catalan, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Catalan first name and last name, then computes the required fields.
                """
                # Check names in Catalan alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ca': "Doron",
                    'last_name_ca': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class RegistrationFormWithLastNameAllMainPlusLanguagesNorwegianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Norwegian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Norwegian first name and last name, then computes the required fields.
                """
                # Check names in Norwegian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_no': "Doron",
                    'last_name_no': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class RegistrationFormWithLastNameAllMainPlusLanguagesBulgarianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Bulgarian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Bulgarian first name and last name, then computes the required fields.
                """
                # Check names in Bulgarian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_bg': "Дорон",
                    'last_name_bg': "Маталон",
                })
                self.first_name = "Дорон"
                self.last_name = "Маталон"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class RegistrationFormWithLastNameAllMainPlusLanguagesDanishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Danish, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Danish first name and last name, then computes the required fields.
                """
                # Check names in Danish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_da': "Doron",
                    'last_name_da': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class RegistrationFormWithLastNameAllMainPlusLanguagesSlovakTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Slovak, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Slovak first name and last name, then computes the required fields.
                """
                # Check names in Slovak alphabet.
                super().set_up()
                self.data.update({
                    'first_name_sk': "Doron",
                    'last_name_sk': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class RegistrationFormWithLastNameAllMainPlusLanguagesHindiTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Hindi, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Hindi first name and last name, then computes the required fields.
                """
                # Check names in Hindi alphabet.
                super().set_up()
                self.data.update({
                    'first_name_hi': "डोरोन",
                    'last_name_hi': "मटालोन",
                })
                self.first_name = "डोरोन"
                self.last_name = "मटालोन"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class RegistrationFormWithLastNameAllMainPlusLanguagesEstonianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Estonian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Estonian first name and last name, then computes the required fields.
                """
                # Check names in Estonian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_et': "Doron",
                    'last_name_et': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class RegistrationFormWithLastNameAllMainPlusLanguagesCroatianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Croatian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Croatian first name and last name, then computes the required fields.
                """
                # Check names in Croatian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_hr': "Doron",
                    'last_name_hr': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class RegistrationFormWithLastNameAllMainPlusLanguagesAzerbaijaniTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Azerbaijani, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Azerbaijani first name and last name, then computes the required fields.
                """
                # Check names in Azerbaijani alphabet.
                super().set_up()
                self.data.update({
                    'first_name_az': "Doron",
                    'last_name_az': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class RegistrationFormWithLastNameAllMainPlusLanguagesCantoneseTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Cantonese, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Cantonese first name and last name, then computes the required fields.
                """
                # Check names in Cantonese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_zh_yue': "多倫",
                    'last_name_zh_yue': "馬塔倫",
                })
                self.first_name = "多倫"
                self.last_name = "馬塔倫"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class RegistrationFormWithLastNameAllMainPlusLanguagesLithuanianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Lithuanian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Lithuanian first name and last name, then computes the required fields.
                """
                # Check names in Lithuanian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_lt': "Doron",
                    'last_name_lt': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class RegistrationFormWithLastNameAllMainPlusLanguagesSlovenianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Slovenian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Slovenian first name and last name, then computes the required fields.
                """
                # Check names in Slovenian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_sl': "Doron",
                    'last_name_sl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class RegistrationFormWithLastNameAllMainPlusLanguagesBasqueTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Basque, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Basque first name and last name, then computes the required fields.
                """
                # Check names in Basque alphabet.
                super().set_up()
                self.data.update({
                    'first_name_eu': "Doron",
                    'last_name_eu': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class RegistrationFormWithLastNameAllMainPlusLanguagesArmenianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Armenian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Armenian first name and last name, then computes the required fields.
                """
                # Check names in Armenian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_hy': "Դորոն",
                    'last_name_hy': "Մատալոն",
                })
                self.first_name = "Դորոն"
                self.last_name = "Մատալոն"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class RegistrationFormWithLastNameAllMainPlusLanguagesUzbekTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Uzbek, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Uzbek first name and last name, then computes the required fields.
                """
                # Check names in Uzbek alphabet.
                super().set_up()
                self.data.update({
                    'first_name_uz': "Doron",
                    'last_name_uz': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class RegistrationFormWithLastNameAllMainPlusLanguagesTamilTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Tamil, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Tamil first name and last name, then computes the required fields.
                """
                # Check names in Tamil alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ta': "டோரோன்",
                    'last_name_ta': "மடலோன்",
                })
                self.first_name = "டோரோன்"
                self.last_name = "மடலோன்"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class RegistrationFormWithLastNameAllMainPlusLanguagesLatvianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Latvian, including a last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Latvian first name and last name, then computes the required fields.
                """
                # Check names in Latvian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_lv': "Doron",
                    'last_name_lv': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        @only_on_sites_with_login
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesEnglishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in English, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a English first name and an empty last name, then computes the required fields.
                """
                # Check names in English alphabet.
                super().set_up()
                self.data.update({
                    'first_name_en': "Doron",
                    'last_name_en': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesFrenchTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in French, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a French first name and an empty last name, then computes the required fields.
                """
                # Check names in French alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fr': "Alizée",
                    'last_name_fr': "",
                })
                self.first_name = "Alizée"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesGermanTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in German, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a German first name and an empty last name, then computes the required fields.
                """
                # Check names in German alphabet.
                super().set_up()
                self.data.update({
                    'first_name_de': "Doron",
                    'last_name_de': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesSpanishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Spanish, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Spanish first name and an empty last name, then computes the required fields.
                """
                # Check names in Spanish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_es': "Lionel",
                    'last_name_es': "",
                })
                self.first_name = "Lionel"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesPortugueseTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Portuguese, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Portuguese first name and an empty last name, then computes the required fields.
                """
                # Check names in Portuguese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_pt': "Cristiano",
                    'last_name_pt': "",
                })
                self.first_name = "Cristiano"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesItalianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Italian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Italian first name and an empty last name, then computes the required fields.
                """
                # Check names in Italian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_it': "Andrea",
                    'last_name_it': "",
                })
                self.first_name = "Andrea"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesDutchTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Dutch, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Dutch first name and an empty last name, then computes the required fields.
                """
                # Check names in Dutch alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesJapaneseTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Japanese, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Japanese first name and an empty last name, then computes the required fields.
                """
                # Check names in Japanese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ja': "ドロン",
                    'last_name_ja': "",
                })
                self.first_name = "ドロン"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesRussianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Russian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Russian first name and an empty last name, then computes the required fields.
                """
                # Check names in Russian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ru': "Дорон",
                    'last_name_ru': "",
                })
                self.first_name = "Дорон"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesChineseTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Chinese, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Chinese first name and an empty last name, then computes the required fields.
                """
                # Check names in Chinese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_zh': "多伦",
                    'last_name_zh': "",
                })
                self.first_name = "多伦"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesPolishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Polish, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Polish first name and an empty last name, then computes the required fields.
                """
                # Check names in Polish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_pl': "Łukasz",
                    'last_name_pl': "",
                })
                self.first_name = "Łukasz"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesPersianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Persian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Persian first name and an empty last name, then computes the required fields.
                """
                # Check names in Persian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fa': "درون",
                    'last_name_fa': "",
                })
                self.first_name = "درون"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesHebrewTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Hebrew, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Hebrew first name and an empty last name, then computes the required fields.
                """
                # Check names in Hebrew alphabet.
                super().set_up()
                self.data.update({
                    'first_name_he': "דורון",
                    'last_name_he': "",
                })
                self.first_name = "דורון"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesKoreanTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Korean, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Korean first name and an empty last name, then computes the required fields.
                """
                # Check names in Korean alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ko': "도론",
                    'last_name_ko': "",
                })
                self.first_name = "도론"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesArabicTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Arabic, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Arabic first name and an empty last name, then computes the required fields.
                """
                # Check names in Arabic alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ar': "دورون",
                    'last_name_ar': "",
                })
                self.first_name = "دورون"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesIndonesianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Indonesian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Indonesian first name and an empty last name, then computes the required fields.
                """
                # Check names in Indonesian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_id': "Doron",
                    'last_name_id': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesUkrainianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Ukrainian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Ukrainian first name and an empty last name, then computes the required fields.
                """
                # Check names in Ukrainian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_uk': "Дорон",
                    'last_name_uk': "",
                })
                self.first_name = "Дорон"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesTurkishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Turkish, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Turkish first name and an empty last name, then computes the required fields.
                """
                # Check names in Turkish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_tr': "Doron",
                    'last_name_tr': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesVietnameseTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Vietnamese, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Vietnamese first name and an empty last name, then computes the required fields.
                """
                # Check names in Vietnamese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_vi': "Doron",
                    'last_name_vi': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesCzechTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Czech, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Czech first name and an empty last name, then computes the required fields.
                """
                # Check names in Czech alphabet.
                super().set_up()
                self.data.update({
                    'first_name_cs': "Doron",
                    'last_name_cs': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesSwedishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Swedish, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Swedish first name and an empty last name, then computes the required fields.
                """
                # Check names in Swedish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_sv': "Doron",
                    'last_name_sv': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesFinnishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Finnish, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Finnish first name and an empty last name, then computes the required fields.
                """
                # Check names in Finnish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fi': "Doron",
                    'last_name_fi': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesHungarianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Hungarian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Hungarian first name and an empty last name, then computes the required fields.
                """
                # Check names in Hungarian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_hu': "Doron",
                    'last_name_hu': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesThaiTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Thai, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Thai first name and an empty last name, then computes the required fields.
                """
                # Check names in Thai alphabet.
                super().set_up()
                self.data.update({
                    'first_name_th': "ดรอน",
                    'last_name_th': "",
                })
                self.first_name = "ดรอน"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesGreekTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Greek, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Greek first name and an empty last name, then computes the required fields.
                """
                # Check names in Greek alphabet.
                super().set_up()
                self.data.update({
                    'first_name_el': "Ντορόν",
                    'last_name_el': "",
                })
                self.first_name = "Ντορόν"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesMalayTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Malay, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Malay first name and an empty last name, then computes the required fields.
                """
                # Check names in Malay alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ms': "Doron",
                    'last_name_ms': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesSerbianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Serbian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Serbian first name and an empty last name, then computes the required fields.
                """
                # Check names in Serbian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_sr': "Дорон",
                    'last_name_sr': "",
                })
                self.first_name = "Дорон"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesRomanianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Romanian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Romanian first name and an empty last name, then computes the required fields.
                """
                # Check names in Romanian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ro': "Doron",
                    'last_name_ro': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesBengaliTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Bengali, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Bengali first name and an empty last name, then computes the required fields.
                """
                # Check names in Bengali alphabet.
                super().set_up()
                self.data.update({
                    'first_name_bn': "ডোরন",
                    'last_name_bn': "",
                })
                self.first_name = "ডোরন"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesCatalanTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Catalan, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Catalan first name and an empty last name, then computes the required fields.
                """
                # Check names in Catalan alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ca': "Doron",
                    'last_name_ca': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesNorwegianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Norwegian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Norwegian first name and an empty last name, then computes the required fields.
                """
                # Check names in Norwegian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_no': "Doron",
                    'last_name_no': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesBulgarianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Bulgarian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Bulgarian first name and an empty last name, then computes the required fields.
                """
                # Check names in Bulgarian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_bg': "Дорон",
                    'last_name_bg': "",
                })
                self.first_name = "Дорон"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesDanishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Danish, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Danish first name and an empty last name, then computes the required fields.
                """
                # Check names in Danish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_da': "Doron",
                    'last_name_da': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesSlovakTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Slovak, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Slovak first name and an empty last name, then computes the required fields.
                """
                # Check names in Slovak alphabet.
                super().set_up()
                self.data.update({
                    'first_name_sk': "Doron",
                    'last_name_sk': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesHindiTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Hindi, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Hindi first name and an empty last name, then computes the required fields.
                """
                # Check names in Hindi alphabet.
                super().set_up()
                self.data.update({
                    'first_name_hi': "डोरोन",
                    'last_name_hi': "",
                })
                self.first_name = "डोरोन"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesEstonianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Estonian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Estonian first name and an empty last name, then computes the required fields.
                """
                # Check names in Estonian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_et': "Doron",
                    'last_name_et': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesCroatianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Croatian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Croatian first name and an empty last name, then computes the required fields.
                """
                # Check names in Croatian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_hr': "Doron",
                    'last_name_hr': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesAzerbaijaniTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Azerbaijani, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Azerbaijani first name and an empty last name, then computes the required fields.
                """
                # Check names in Azerbaijani alphabet.
                super().set_up()
                self.data.update({
                    'first_name_az': "Doron",
                    'last_name_az': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesCantoneseTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Cantonese, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Cantonese first name and an empty last name, then computes the required fields.
                """
                # Check names in Cantonese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_zh_yue': "多倫",
                    'last_name_zh_yue': "",
                })
                self.first_name = "多倫"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesLithuanianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Lithuanian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Lithuanian first name and an empty last name, then computes the required fields.
                """
                # Check names in Lithuanian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_lt': "Doron",
                    'last_name_lt': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesSlovenianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Slovenian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Slovenian first name and an empty last name, then computes the required fields.
                """
                # Check names in Slovenian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_sl': "Doron",
                    'last_name_sl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesBasqueTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Basque, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Basque first name and an empty last name, then computes the required fields.
                """
                # Check names in Basque alphabet.
                super().set_up()
                self.data.update({
                    'first_name_eu': "Doron",
                    'last_name_eu': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesArmenianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Armenian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Armenian first name and an empty last name, then computes the required fields.
                """
                # Check names in Armenian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_hy': "Դորոն",
                    'last_name_hy': "",
                })
                self.first_name = "Դորոն"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesUzbekTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Uzbek, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Uzbek first name and an empty last name, then computes the required fields.
                """
                # Check names in Uzbek alphabet.
                super().set_up()
                self.data.update({
                    'first_name_uz': "Doron",
                    'last_name_uz': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesTamilTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Tamil, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Tamil first name and an empty last name, then computes the required fields.
                """
                # Check names in Tamil alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ta': "டோரோன்",
                    'last_name_ta': "",
                })
                self.first_name = "டோரோன்"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class RegistrationFormWithoutLastNameAllMainPlusLanguagesLatvianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the registration form in Latvian, with an empty last name.
            """

            def set_up(self):
                """
                Sets up registration data with a Latvian first name and an empty last name, then computes the required fields.
                """
                # Check names in Latvian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_lv': "Doron",
                    'last_name_lv': "",
                })
                self.first_name = "Doron"
                self.last_name = ""
                self.set_up_required_fields()

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class ProfileNotificationsFormTestCaseMixin(TestCaseMixin):
            """
            Test mixin for the profile notifications form, shared between Speedy Net and Speedy Match.
            """

            def set_up(self):
                """
                Creates an active test user.
                """
                super().set_up()
                self.user = ActiveUserFactory()

            def test_has_correct_fields(self):
                """
                Placeholder that raises NotImplementedError; subclasses must override this to assert the expected form fields for their site.
                """
                raise NotImplementedError("test_has_correct_fields must be defined in classes inherited from ProfileNotificationsFormTestCaseMixin.")


        @only_on_sites_with_login
        class PasswordResetFormOnlyEnglishTestCase(SiteTestCase):
            """
            Test the password reset form's lookup of users by email address, run only once (in English) since it is language-independent.
            """

            def set_up(self):
                """
                Creates two users, each with a primary confirmed email address; the first user also gets an additional confirmed and an unconfirmed email address, and a PasswordResetForm instance is created.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()
                self.primary_email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
                self.primary_email.make_primary()
                self.confirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
                self.unconfirmed_email = UserEmailAddressFactory(user=self.user, is_confirmed=False)
                self.other_user_email = UserEmailAddressFactory(user=self.other_user, is_confirmed=True)
                self.form = PasswordResetForm()

            def test_can_reset_using_primary_email(self):
                """
                Verify the form finds the user by their primary email address.
                """
                self.assertSetEqual(set1=self.form.get_users(email=self.primary_email.email), set2={self.user})

            def test_can_reset_using_primary_email_uppercase(self):
                """
                Verify the form finds the user by their primary email address written in uppercase.
                """
                self.assertSetEqual(set1=self.form.get_users(email=self.primary_email.email.upper()), set2={self.user})

            def test_can_reset_using_confirmed_email(self):
                """
                Verify the form finds the user by a confirmed, non-primary email address.
                """
                self.assertSetEqual(set1=self.form.get_users(email=self.confirmed_email.email), set2={self.user})

            def test_can_reset_using_unconfirmed_email(self):
                """
                Verify the form finds the user by an unconfirmed email address.
                """
                self.assertSetEqual(set1=self.form.get_users(email=self.unconfirmed_email.email), set2={self.user})

            def test_can_reset_using_other_user_email(self):
                """
                Verify the form finds the other user by their own confirmed email address.
                """
                self.assertSetEqual(set1=self.form.get_users(email=self.other_user_email.email), set2={self.other_user})

            def test_cannot_reset_using_unknown_email(self):
                """
                Verify the form finds no users for an email address that doesn't belong to anyone.
                """
                self.assertSetEqual(set1=self.form.get_users(email='email@example.com'), set2=set())


        class DeactivationFormTestCaseMixin(SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Test mixin for the site profile deactivation form, covering correct and incorrect password validation.
            """

            def set_up(self):
                """
                Creates an active test user.
                """
                super().set_up()
                self.user = ActiveUserFactory()

            def test_incorrect_password(self):
                """
                Verify the form is invalid when submitted with an incorrect password.
                """
                data = {
                    'password': 'wrong password!!',
                }
                form = SiteProfileDeactivationForm(user=self.user, data=data)
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._invalid_password_errors_dict())

            def test_correct_password(self):
                """
                Verify the form is valid when submitted with the correct password.
                """
                data = {
                    'password': tests_settings.USER_PASSWORD,
                }
                form = SiteProfileDeactivationForm(user=self.user, data=data)
                self.assertIs(expr1=form.is_valid(), expr2=True)
                self.assertDictEqual(d1=form.errors, d2={})


        @only_on_sites_with_login
        class DeactivationFormAllMainLanguagesEnglishTestCase(DeactivationFormTestCaseMixin, SiteTestCase):
            """
            Test the deactivation form in English.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class DeactivationFormAllMainLanguagesFrenchTestCase(DeactivationFormTestCaseMixin, SiteTestCase):
            """
            Test the deactivation form in French.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class DeactivationFormAllMainLanguagesGermanTestCase(DeactivationFormTestCaseMixin, SiteTestCase):
            """
            Test the deactivation form in German.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class DeactivationFormAllMainLanguagesSpanishTestCase(DeactivationFormTestCaseMixin, SiteTestCase):
            """
            Test the deactivation form in Spanish.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class DeactivationFormAllMainLanguagesPortugueseTestCase(DeactivationFormTestCaseMixin, SiteTestCase):
            """
            Test the deactivation form in Portuguese.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class DeactivationFormAllMainLanguagesItalianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):
            """
            Test the deactivation form in Italian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class DeactivationFormAllMainLanguagesDutchTestCase(DeactivationFormTestCaseMixin, SiteTestCase):
            """
            Test the deactivation form in Dutch.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class DeactivationFormAllMainLanguagesJapaneseTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Japanese.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class DeactivationFormAllMainLanguagesRussianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Russian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class DeactivationFormAllMainLanguagesChineseTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Chinese.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class DeactivationFormAllMainLanguagesPolishTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Polish.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class DeactivationFormAllMainLanguagesPersianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Persian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class DeactivationFormAllMainLanguagesHebrewTestCase(DeactivationFormTestCaseMixin, SiteTestCase):
            """
            Test the deactivation form in Hebrew.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')

        # ~~~~ TODO: test ProfileForm - try to change username and get error message. ("You can't change your username.")


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class DeactivationFormAllMainLanguagesKoreanTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Korean.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class DeactivationFormAllMainLanguagesArabicTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Arabic.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class DeactivationFormAllMainLanguagesIndonesianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Indonesian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class DeactivationFormAllMainLanguagesUkrainianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Ukrainian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class DeactivationFormAllMainLanguagesTurkishTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Turkish.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class DeactivationFormAllMainLanguagesVietnameseTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Vietnamese.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class DeactivationFormAllMainLanguagesCzechTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Czech.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class DeactivationFormAllMainLanguagesSwedishTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Swedish.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class DeactivationFormAllMainLanguagesFinnishTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Finnish.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class DeactivationFormAllMainLanguagesHungarianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Hungarian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class DeactivationFormAllMainLanguagesThaiTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Thai.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class DeactivationFormAllMainLanguagesGreekTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Greek.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class DeactivationFormAllMainLanguagesMalayTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Malay.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class DeactivationFormAllMainLanguagesSerbianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Serbian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class DeactivationFormAllMainLanguagesRomanianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Romanian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class DeactivationFormAllMainLanguagesBengaliTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Bengali.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class DeactivationFormAllMainLanguagesCatalanTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Catalan.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class DeactivationFormAllMainLanguagesNorwegianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Norwegian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class DeactivationFormAllMainLanguagesBulgarianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Bulgarian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class DeactivationFormAllMainLanguagesDanishTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Danish.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class DeactivationFormAllMainLanguagesSlovakTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Slovak.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class DeactivationFormAllMainLanguagesHindiTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Hindi.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class DeactivationFormAllMainLanguagesEstonianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Estonian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class DeactivationFormAllMainLanguagesCroatianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Croatian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class DeactivationFormAllMainLanguagesAzerbaijaniTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Azerbaijani.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class DeactivationFormAllMainLanguagesCantoneseTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Cantonese.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class DeactivationFormAllMainLanguagesLithuanianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Lithuanian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class DeactivationFormAllMainLanguagesSlovenianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Slovenian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class DeactivationFormAllMainLanguagesBasqueTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Basque.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class DeactivationFormAllMainLanguagesArmenianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Armenian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class DeactivationFormAllMainLanguagesUzbekTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Uzbek.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class DeactivationFormAllMainLanguagesTamilTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Tamil.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class DeactivationFormAllMainLanguagesLatvianTestCase(DeactivationFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Test the deactivation form in Latvian.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


