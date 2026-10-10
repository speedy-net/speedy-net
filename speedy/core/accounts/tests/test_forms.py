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

            Methods:
                set_up(self): Creates the base registration data dict, password and expected username/slug, and asserts no models exist yet.
                set_up_required_fields(self): Computes the set of required fields (all fields except last name for the current language) and asserts the form reports them as required.
                run_test_all_slugs_to_test_list(self, test_settings): Registers a user for each slug in tests_settings.SLUGS_TO_TEST_LIST, asserting success for long-enough slugs and failure otherwise, and checks the resulting counts.
                test_visitor_can_register(self): Verify a visitor can register and that the created entity/user and its email address have all the expected values.
                test_slug_gets_converted_to_username(self): Verify a slug with dashes is kept as-is while the derived username has the dashes removed.
                test_slug_dots_and_underscores_gets_converted_to_dashes(self): Verify dots and underscores in the slug are converted to dashes.
                test_slug_dashes_are_trimmed_and_double_dashes_are_converted_to_single_dashes(self): Verify leading/trailing dashes are trimmed and repeated dashes are collapsed to a single dash.
                test_slug_gets_converted_to_lowercase(self): Verify an uppercase slug is converted to lowercase.
                test_email_gets_converted_to_lowercase(self): Verify an uppercase email address is converted to lowercase.
                run_test_required_fields(self, data): Submits the given data and asserts the form is invalid with the expected "all required fields are required" errors.
                test_required_fields_1(self): Verify submitting an empty data dict fails with all required fields reported as required.
                test_required_fields_2(self): Verify submitting empty-string values for all required fields fails with all required fields reported as required.
                test_non_unique_confirmed_email_address(self): Verify registering with an email address that is already confirmed by another user fails and leaves the existing user and email unchanged.
                test_non_unique_unconfirmed_email_address(self): Verify registering with an email address that is unconfirmed and recently added by another user fails and leaves the existing user and email unchanged.
                test_non_unique_unconfirmed_email_address_registered_6_minutes_ago(self): Verify registering with an email address that is unconfirmed and was added by another user 6 minutes ago succeeds, deleting the old unconfirmed address.
                test_slug_validation_fails_with_reserved_username(self): Verify registering with a reserved username (e.g. "webmaster") fails as already taken.
                test_slug_validation_fails_with_reserved_and_too_short_username(self): Verify registering with a reserved and too-short username fails with the minimum alphanumeric length error.
                test_slug_validation_fails_with_username_already_taken(self): Verify registering with a slug whose normalized username is already taken by another user fails as already taken.
                test_slug_validation_ok(self): Verify registering with various slugs of the minimum valid length succeeds and the created user can then be deleted.
                test_slug_validation_fails_with_username_too_short(self): Verify registering with slugs whose normalized username is below the minimum length fails with the minimum alphanumeric length error.
                test_slug_and_username_min_length_ok(self): Verify the default minimum slug length is 6 and running all the test slugs yields the expected success/failure counts.
                test_slug_min_length_fail_username_min_length_ok(self): With an overridden higher minimum slug length, verify running all the test slugs yields the expected success/failure counts.
                test_slug_validation_fails_with_username_too_long(self): Verify registering with a slug longer than the maximum allowed length fails with the maximum length error.
                test_slug_validation_fails_with_invalid_username_regex(self): Verify registering with slugs that don't match the required username regex (e.g. starting with digits, containing spaces or symbols) fails.
                test_cannot_register_invalid_email(self): Verify registering with an invalid email address fails with the "enter a valid email address" error.
                test_invalid_date_of_birth_list_fail(self): Verify registering with each invalid date of birth in tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST fails with the expected error.
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
                self.assertEqual(first=user.first_name_sv, second=self.first_name)
                self.assertEqual(first=user.first_name_ko, second=self.first_name)
                self.assertEqual(first=user.first_name_fi, second=self.first_name)
                self.assertEqual(first=user.first_name_he, second=self.first_name)
                self.assertEqual(first=user.last_name, second=self.last_name)
                self.assertEqual(first=user.last_name_en, second=self.last_name)
                self.assertEqual(first=user.last_name_fr, second=self.last_name)
                self.assertEqual(first=user.last_name_de, second=self.last_name)
                self.assertEqual(first=user.last_name_es, second=self.last_name)
                self.assertEqual(first=user.last_name_pt, second=self.last_name)
                self.assertEqual(first=user.last_name_it, second=self.last_name)
                self.assertEqual(first=user.last_name_nl, second=self.last_name)
                self.assertEqual(first=user.last_name_sv, second=self.last_name)
                self.assertEqual(first=user.last_name_ko, second=self.last_name)
                self.assertEqual(first=user.last_name_fi, second=self.last_name)
                self.assertEqual(first=user.last_name_he, second=self.last_name)
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
        class RegistrationFormWithLastNameAllMainLanguagesEnglishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in English, including a last name.

            Methods:
                set_up(self): Sets up registration data with a English first name and last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        class RegistrationFormWithLastNameAllMainLanguagesFrenchTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in French, including a last name.

            Methods:
                set_up(self): Sets up registration data with a French first name and last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        class RegistrationFormWithLastNameAllMainLanguagesGermanTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in German, including a last name.

            Methods:
                set_up(self): Sets up registration data with a German first name and last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        class RegistrationFormWithLastNameAllMainLanguagesSpanishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Spanish, including a last name.

            Methods:
                set_up(self): Sets up registration data with a Spanish first name and last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        class RegistrationFormWithLastNameAllMainLanguagesPortugueseTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Portuguese, including a last name.

            Methods:
                set_up(self): Sets up registration data with a Portuguese first name and last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        class RegistrationFormWithLastNameAllMainLanguagesItalianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Italian, including a last name.

            Methods:
                set_up(self): Sets up registration data with a Italian first name and last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        class RegistrationFormWithLastNameAllMainLanguagesDutchTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Dutch, including a last name.

            Methods:
                set_up(self): Sets up registration data with a Dutch first name and last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        @override_settings(LANGUAGE_CODE='he')
        class RegistrationFormWithLastNameAllMainLanguagesHebrewTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Hebrew, including a last name.

            Methods:
                set_up(self): Sets up registration data with a Hebrew first name and last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        class RegistrationFormWithoutLastNameAllMainLanguagesEnglishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in English, with an empty last name.

            Methods:
                set_up(self): Sets up registration data with a English first name and an empty last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        class RegistrationFormWithoutLastNameAllMainLanguagesFrenchTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in French, with an empty last name.

            Methods:
                set_up(self): Sets up registration data with a French first name and an empty last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        class RegistrationFormWithoutLastNameAllMainLanguagesGermanTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in German, with an empty last name.

            Methods:
                set_up(self): Sets up registration data with a German first name and an empty last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        class RegistrationFormWithoutLastNameAllMainLanguagesSpanishTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Spanish, with an empty last name.

            Methods:
                set_up(self): Sets up registration data with a Spanish first name and an empty last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        class RegistrationFormWithoutLastNameAllMainLanguagesPortugueseTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Portuguese, with an empty last name.

            Methods:
                set_up(self): Sets up registration data with a Portuguese first name and an empty last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        class RegistrationFormWithoutLastNameAllMainLanguagesItalianTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Italian, with an empty last name.

            Methods:
                set_up(self): Sets up registration data with a Italian first name and an empty last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        class RegistrationFormWithoutLastNameAllMainLanguagesDutchTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Dutch, with an empty last name.

            Methods:
                set_up(self): Sets up registration data with a Dutch first name and an empty last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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
        @override_settings(LANGUAGE_CODE='he')
        class RegistrationFormWithoutLastNameAllMainLanguagesHebrewTestCase(RegistrationFormTestCaseMixin, SiteTestCase):
            """
            Test the registration form in Hebrew, with an empty last name.

            Methods:
                set_up(self): Sets up registration data with a Hebrew first name and an empty last name, then computes the required fields.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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


        class ProfileNotificationsFormTestCaseMixin(TestCaseMixin):
            """
            Test mixin for the profile notifications form, shared between Speedy Net and Speedy Match.

            Methods:
                set_up(self): Creates an active test user.
                test_has_correct_fields(self): Placeholder that must be overridden by subclasses to assert the expected form fields.
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
                raise NotImplementedError("This test is not implemented in this mixin.")


        @only_on_sites_with_login
        class PasswordResetFormOnlyEnglishTestCase(SiteTestCase):
            """
            Test the password reset form's lookup of users by email address, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates two users with primary/confirmed/unconfirmed email addresses for testing password reset lookups.
                test_can_reset_using_primary_email(self): Verify the form finds the user by their primary email address.
                test_can_reset_using_primary_email_uppercase(self): Verify the form finds the user by their primary email address in uppercase.
                test_can_reset_using_confirmed_email(self): Verify the form finds the user by a confirmed, non-primary email address.
                test_can_reset_using_unconfirmed_email(self): Verify the form finds the user by an unconfirmed email address.
                test_can_reset_using_other_user_email(self): Verify the form finds the other user by their own confirmed email address.
                test_cannot_reset_using_unknown_email(self): Verify the form finds no users for an email address that doesn't belong to anyone.
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

            Methods:
                set_up(self): Creates an active test user.
                test_incorrect_password(self): Verify the form is invalid when submitted with an incorrect password.
                test_correct_password(self): Verify the form is valid when submitted with the correct password.
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

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class DeactivationFormAllMainLanguagesHebrewTestCase(DeactivationFormTestCaseMixin, SiteTestCase):
            """
            Test the deactivation form in Hebrew.

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        # ~~~~ TODO: test ProfileForm - try to change username and get error message. ("You can't change your username.")


