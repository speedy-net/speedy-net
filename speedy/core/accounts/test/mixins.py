"""
Test mixins of the Speedy Core accounts app, with model helper methods and language specific translations used by the accounts tests.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.mixins import SpeedyCoreBaseLanguageMixin, TestCaseMixin

    from speedy.core.base.utils import to_attribute
    from speedy.core.accounts.models import Entity, User, UserEmailAddress


    class SpeedyCoreAccountsModelsMixin(TestCaseMixin):
        """
        Mixin providing assertions about entity/user/email-address counts and localized name fields for tests.
        """

        def assert_models_count(self, entity_count, user_count, user_email_address_count, confirmed_email_address_count, unconfirmed_email_address_count):
            """
            Asserts that the database contains the expected number of entities, users and user email addresses (confirmed and unconfirmed).

            :param entity_count: The expected number of Entity objects.
            :type entity_count: int
            :param user_count: The expected number of User objects.
            :type user_count: int
            :param user_email_address_count: The expected total number of UserEmailAddress objects.
            :type user_email_address_count: int
            :param confirmed_email_address_count: The expected number of confirmed UserEmailAddress objects.
            :type confirmed_email_address_count: int
            :param unconfirmed_email_address_count: The expected number of unconfirmed UserEmailAddress objects.
            :type unconfirmed_email_address_count: int
            """
            self.assertEqual(first=Entity.objects.count(), second=entity_count)
            self.assertEqual(first=User.objects.count(), second=user_count)
            self.assertEqual(first=UserEmailAddress.objects.count(), second=user_email_address_count)
            self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second=confirmed_email_address_count)
            self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=False).count(), second=unconfirmed_email_address_count)

        def assert_user_email_addresses_count(self, user, user_email_addresses_count, user_primary_email_addresses_count, user_confirmed_email_addresses_count, user_unconfirmed_email_addresses_count):
            """
            Asserts that a user's email addresses match the expected counts, and that the user's has_confirmed_email flag is consistent with the confirmed-email-addresses count.

            :param user: The user whose email addresses are checked.
            :type user: speedy.core.accounts.models.User
            :param user_email_addresses_count: The expected total number of the user's email addresses.
            :type user_email_addresses_count: int
            :param user_primary_email_addresses_count: The expected number of the user's primary email addresses.
            :type user_primary_email_addresses_count: int
            :param user_confirmed_email_addresses_count: The expected number of the user's confirmed email addresses.
            :type user_confirmed_email_addresses_count: int
            :param user_unconfirmed_email_addresses_count: The expected number of the user's unconfirmed email addresses.
            :type user_unconfirmed_email_addresses_count: int
            """
            self.assertEqual(first=user.email_addresses.count(), second=user_email_addresses_count)
            self.assertEqual(first=user.email_addresses.filter(is_primary=True).count(), second=user_primary_email_addresses_count)
            self.assertEqual(first=user.email_addresses.filter(is_confirmed=True).count(), second=user_confirmed_email_addresses_count)
            self.assertEqual(first=user.email_addresses.filter(is_confirmed=False).count(), second=user_unconfirmed_email_addresses_count)
            if (user_confirmed_email_addresses_count > 0):
                self.assertEqual(first=user.has_confirmed_email, second=True)
                self.assertEqual(first=user.email_addresses.filter(is_confirmed=True, is_primary=True).count(), second=user_primary_email_addresses_count)
            else:
                self.assertEqual(first=user.has_confirmed_email, second=False)
                self.assertEqual(first=user.email_addresses.filter(is_confirmed=True, is_primary=True).count(), second=0)

        def assert_user_first_and_last_name_in_all_languages(self, user):
            """
            Asserts that the user's first_name and last_name are identical to their localized per-language counterparts (e.g. first_name_en, first_name_fr, ...) for all the configured languages.

            :param user: The user whose localized name fields are checked.
            :type user: speedy.core.accounts.models.User
            """
            self.assertTupleEqual(tuple1=User.NAME_LOCALIZABLE_FIELDS, tuple2=('first_name', 'last_name'))
            self.assertEqual(first=user.first_name_en, second=user.first_name)
            self.assertEqual(first=user.first_name_fr, second=user.first_name)
            self.assertEqual(first=user.first_name_de, second=user.first_name)
            self.assertEqual(first=user.first_name_es, second=user.first_name)
            self.assertEqual(first=user.first_name_pt, second=user.first_name)
            self.assertEqual(first=user.first_name_it, second=user.first_name)
            self.assertEqual(first=user.first_name_nl, second=user.first_name)
            self.assertEqual(first=user.first_name_ja, second=user.first_name)
            self.assertEqual(first=user.first_name_ru, second=user.first_name)
            self.assertEqual(first=user.first_name_zh, second=user.first_name)
            self.assertEqual(first=user.first_name_pl, second=user.first_name)
            self.assertEqual(first=user.first_name_fa, second=user.first_name)
            self.assertEqual(first=user.first_name_he, second=user.first_name)
            self.assertEqual(first=user.first_name_ko, second=user.first_name)
            self.assertEqual(first=user.first_name_ar, second=user.first_name)
            self.assertEqual(first=user.first_name_id, second=user.first_name)
            self.assertEqual(first=user.first_name_uk, second=user.first_name)
            self.assertEqual(first=user.first_name_tr, second=user.first_name)
            self.assertEqual(first=user.first_name_vi, second=user.first_name)
            self.assertEqual(first=user.first_name_cs, second=user.first_name)
            self.assertEqual(first=user.first_name_sv, second=user.first_name)
            self.assertEqual(first=user.first_name_fi, second=user.first_name)
            self.assertEqual(first=user.first_name_hu, second=user.first_name)
            self.assertEqual(first=user.first_name_th, second=user.first_name)
            self.assertEqual(first=user.first_name_el, second=user.first_name)
            self.assertEqual(first=user.first_name_ms, second=user.first_name)
            self.assertEqual(first=user.first_name_sr, second=user.first_name)
            self.assertEqual(first=user.first_name_ro, second=user.first_name)
            self.assertEqual(first=user.first_name_bn, second=user.first_name)
            self.assertEqual(first=user.first_name_ca, second=user.first_name)
            self.assertEqual(first=user.first_name_no, second=user.first_name)
            self.assertEqual(first=user.first_name_bg, second=user.first_name)
            self.assertEqual(first=user.first_name_da, second=user.first_name)
            self.assertEqual(first=user.first_name_sk, second=user.first_name)
            self.assertEqual(first=user.first_name_hi, second=user.first_name)
            self.assertEqual(first=user.first_name_et, second=user.first_name)
            self.assertEqual(first=user.first_name_hr, second=user.first_name)
            self.assertEqual(first=user.first_name_az, second=user.first_name)
            self.assertEqual(first=user.first_name_zh_yue, second=user.first_name)
            self.assertEqual(first=user.first_name_lt, second=user.first_name)
            self.assertEqual(first=user.first_name_sl, second=user.first_name)
            self.assertEqual(first=user.first_name_eu, second=user.first_name)
            self.assertEqual(first=user.first_name_hy, second=user.first_name)
            self.assertEqual(first=user.first_name_uz, second=user.first_name)
            self.assertEqual(first=user.first_name_ta, second=user.first_name)
            self.assertEqual(first=user.first_name_lv, second=user.first_name)
            self.assertEqual(first=user.last_name_en, second=user.last_name)
            self.assertEqual(first=user.last_name_fr, second=user.last_name)
            self.assertEqual(first=user.last_name_de, second=user.last_name)
            self.assertEqual(first=user.last_name_es, second=user.last_name)
            self.assertEqual(first=user.last_name_pt, second=user.last_name)
            self.assertEqual(first=user.last_name_it, second=user.last_name)
            self.assertEqual(first=user.last_name_nl, second=user.last_name)
            self.assertEqual(first=user.last_name_ja, second=user.last_name)
            self.assertEqual(first=user.last_name_ru, second=user.last_name)
            self.assertEqual(first=user.last_name_zh, second=user.last_name)
            self.assertEqual(first=user.last_name_pl, second=user.last_name)
            self.assertEqual(first=user.last_name_fa, second=user.last_name)
            self.assertEqual(first=user.last_name_he, second=user.last_name)
            self.assertEqual(first=user.last_name_ko, second=user.last_name)
            self.assertEqual(first=user.last_name_ar, second=user.last_name)
            self.assertEqual(first=user.last_name_id, second=user.last_name)
            self.assertEqual(first=user.last_name_uk, second=user.last_name)
            self.assertEqual(first=user.last_name_tr, second=user.last_name)
            self.assertEqual(first=user.last_name_vi, second=user.last_name)
            self.assertEqual(first=user.last_name_cs, second=user.last_name)
            self.assertEqual(first=user.last_name_sv, second=user.last_name)
            self.assertEqual(first=user.last_name_fi, second=user.last_name)
            self.assertEqual(first=user.last_name_hu, second=user.last_name)
            self.assertEqual(first=user.last_name_th, second=user.last_name)
            self.assertEqual(first=user.last_name_el, second=user.last_name)
            self.assertEqual(first=user.last_name_ms, second=user.last_name)
            self.assertEqual(first=user.last_name_sr, second=user.last_name)
            self.assertEqual(first=user.last_name_ro, second=user.last_name)
            self.assertEqual(first=user.last_name_bn, second=user.last_name)
            self.assertEqual(first=user.last_name_ca, second=user.last_name)
            self.assertEqual(first=user.last_name_no, second=user.last_name)
            self.assertEqual(first=user.last_name_bg, second=user.last_name)
            self.assertEqual(first=user.last_name_da, second=user.last_name)
            self.assertEqual(first=user.last_name_sk, second=user.last_name)
            self.assertEqual(first=user.last_name_hi, second=user.last_name)
            self.assertEqual(first=user.last_name_et, second=user.last_name)
            self.assertEqual(first=user.last_name_hr, second=user.last_name)
            self.assertEqual(first=user.last_name_az, second=user.last_name)
            self.assertEqual(first=user.last_name_zh_yue, second=user.last_name)
            self.assertEqual(first=user.last_name_lt, second=user.last_name)
            self.assertEqual(first=user.last_name_sl, second=user.last_name)
            self.assertEqual(first=user.last_name_eu, second=user.last_name)
            self.assertEqual(first=user.last_name_hy, second=user.last_name)
            self.assertEqual(first=user.last_name_uz, second=user.last_name)
            self.assertEqual(first=user.last_name_ta, second=user.last_name)
            self.assertEqual(first=user.last_name_lv, second=user.last_name)
            field_name_localized_list = list()
            for base_field_name in User.NAME_LOCALIZABLE_FIELDS:
                for language_code, language_name in django_settings.LANGUAGES:
                    field_name_localized = to_attribute(name=base_field_name, language_code=language_code)
                    self.assertEqual(first=getattr(user, field_name_localized), second=getattr(user, base_field_name), msg="assert_user_first_and_last_name_in_all_languages::fields don't match ({field_name_localized}, {base_field_name}), user.pk={user_pk}, user.username={user_username}, user.slug={user_slug}, user.name={user_name}".format(
                        field_name_localized=field_name_localized,
                        base_field_name=base_field_name,
                        user_pk=user.pk,
                        user_username=user.username,
                        user_slug=user.slug,
                        user_name=user.name,
                    ))
                    field_name_localized_list.append(field_name_localized)
            self.assertListEqual(list1=field_name_localized_list, list2=['first_name_en', 'first_name_fr', 'first_name_de', 'first_name_es', 'first_name_pt', 'first_name_it', 'first_name_nl', 'first_name_ja', 'first_name_ru', 'first_name_zh', 'first_name_pl', 'first_name_fa', 'first_name_he', 'first_name_ko', 'first_name_ar', 'first_name_id', 'first_name_uk', 'first_name_tr', 'first_name_vi', 'first_name_cs', 'first_name_sv', 'first_name_fi', 'first_name_hu', 'first_name_th', 'first_name_el', 'first_name_ms', 'first_name_sr', 'first_name_ro', 'first_name_bn', 'first_name_ca', 'first_name_no', 'first_name_bg', 'first_name_da', 'first_name_sk', 'first_name_hi', 'first_name_et', 'first_name_hr', 'first_name_az', 'first_name_zh_yue', 'first_name_lt', 'first_name_sl', 'first_name_eu', 'first_name_hy', 'first_name_uz', 'first_name_ta', 'first_name_lv', 'last_name_en', 'last_name_fr', 'last_name_de', 'last_name_es', 'last_name_pt', 'last_name_it', 'last_name_nl', 'last_name_ja', 'last_name_ru', 'last_name_zh', 'last_name_pl', 'last_name_fa', 'last_name_he', 'last_name_ko', 'last_name_ar', 'last_name_id', 'last_name_uk', 'last_name_tr', 'last_name_vi', 'last_name_cs', 'last_name_sv', 'last_name_fi', 'last_name_hu', 'last_name_th', 'last_name_el', 'last_name_ms', 'last_name_sr', 'last_name_ro', 'last_name_bn', 'last_name_ca', 'last_name_no', 'last_name_bg', 'last_name_da', 'last_name_sk', 'last_name_hi', 'last_name_et', 'last_name_hr', 'last_name_az', 'last_name_zh_yue', 'last_name_lt', 'last_name_sl', 'last_name_eu', 'last_name_hy', 'last_name_uz', 'last_name_ta', 'last_name_lv'])


    class SpeedyCoreAccountsLanguageMixin(SpeedyCoreBaseLanguageMixin, TestCaseMixin):
        """
        Mixin providing per-language speedy.core.accounts validation error messages and errors dicts for tests, localized according to self.language_code.
        """
        _first_password_field_names = ['new_password1']
        _both_password_field_names = ['new_password1', 'new_password2']

        def _assert_model_is_entity_or_user(self, model):
            """
            Asserts that model is either Entity or User.

            :param model: The model class to check.
            :type model: type
            """
            self.assertIn(member=model, container=[Entity, User])
            if (model is Entity):
                pass
            elif (model is User):
                pass
            else:
                raise Exception("Unexpected: model={}".format(model))

        def _value_is_not_a_valid_choice_error_message_by_value(self, value):
            """
            Returns the formatted "value is not a valid choice" message for a given value.

            :param value: The invalid value.
            :return: The formatted error message.
            :rtype: str
            """
            return self._value_is_not_a_valid_choice_error_message_to_format.format(value=value)

        def _value_must_be_an_integer_error_message_by_value(self, value):
            """
            Returns the formatted "value must be an integer" message for a given value.

            :param value: The non-integer value.
            :return: The formatted error message.
            :rtype: str
            """
            return self._value_must_be_an_integer_error_message_to_format.format(value=value)

        @staticmethod
        def _get_message_to_format_by_number(message_to_format, number):
            """
            Returns the message template to use for a given number. Arabic stores a sequence of 6 templates, in the order of the gettext plural forms. Other languages whose plural form depends on the tested number store a dict of templates by number.

            :param message_to_format: A template string, a sequence of 6 templates for Arabic, or a dict of templates by number.
            :type message_to_format: str | tuple | dict
            :param number: The number which determines the plural form.
            :type number: int
            :return: The template string for this number.
            :rtype: str
            """
            if (isinstance(message_to_format, str)):
                return message_to_format
            if (isinstance(message_to_format, dict)):
                return message_to_format[number]
            if (number == 0):
                index = 0
            elif (number == 1):
                index = 1
            elif (number == 2):
                index = 2
            elif (3 <= number % 100 <= 10):
                index = 3
            elif (number % 100 >= 11):
                index = 4
            else:
                index = 5
            return message_to_format[index]

        def _username_must_contain_at_least_min_length_alphanumeric_characters_error_message_by_min_length_and_value_length(self, min_length, value_length):
            """
            Returns the formatted "username must contain at least min_length alphanumeric characters" message.

            :param min_length: The minimal required number of alphanumeric characters.
            :type min_length: int
            :param value_length: The actual length of the value.
            :type value_length: int
            :return: The formatted error message.
            :rtype: str
            """
            return self._get_message_to_format_by_number(message_to_format=self._username_must_contain_at_least_min_length_alphanumeric_characters_error_message_to_format, number=min_length).format(min_length=min_length, value_length=value_length)

        def _username_must_contain_at_most_max_length_alphanumeric_characters_error_message_by_max_length_and_value_length(self, max_length, value_length):
            """
            Returns the formatted "username must contain at most max_length alphanumeric characters" message.

            :param max_length: The maximal allowed number of alphanumeric characters.
            :type max_length: int
            :param value_length: The actual length of the value.
            :type value_length: int
            :return: The formatted error message.
            :rtype: str
            """
            return self._get_message_to_format_by_number(message_to_format=self._username_must_contain_at_most_max_length_alphanumeric_characters_error_message_to_format, number=max_length).format(max_length=max_length, value_length=value_length)

        def _username_must_contain_at_least_min_length_characters_error_message_by_min_length_and_value_length(self, min_length, value_length):
            """
            Returns the formatted "username must contain at least min_length characters" message.

            :param min_length: The minimal required number of characters.
            :type min_length: int
            :param value_length: The actual length of the value.
            :type value_length: int
            :return: The formatted error message.
            :rtype: str
            """
            return self._get_message_to_format_by_number(message_to_format=self._username_must_contain_at_least_min_length_characters_error_message_to_format, number=min_length).format(min_length=min_length, value_length=value_length)

        def _username_must_contain_at_most_max_length_characters_error_message_by_max_length_and_value_length(self, max_length, value_length):
            """
            Returns the formatted "username must contain at most max_length characters" message.

            :param max_length: The maximal allowed number of characters.
            :type max_length: int
            :param value_length: The actual length of the value.
            :type value_length: int
            :return: The formatted error message.
            :rtype: str
            """
            return self._get_message_to_format_by_number(message_to_format=self._username_must_contain_at_most_max_length_characters_error_message_to_format, number=max_length).format(max_length=max_length, value_length=value_length)

        def _a_confirmation_message_was_sent_to_email_address_success_message_by_email_address(self, email_address):
            """
            Returns the formatted "a confirmation message was sent to email_address" success message.

            :param email_address: The email address the confirmation message was sent to.
            :type email_address: str
            :return: The formatted success message.
            :rtype: str
            """
            return self._a_confirmation_message_was_sent_to_email_address_success_message_to_format.format(email_address=email_address)

        def _user_all_the_required_fields_keys(self):
            """
            Returns the list of all the required field names for creating a User, including one localized first_name field per configured language, followed by username, slug, password, gender and date_of_birth.

            :return: The list of required field names.
            :rtype: list
            """
            return [field_name.format(language_code=language_code).replace("-", "_") for field_name in ['first_name_{language_code}'] for language_code, language_name in django_settings.LANGUAGES] + ['username', 'slug', 'password', 'gender', 'date_of_birth']

        def _registration_form_all_the_required_fields_keys(self):
            """
            Returns the list of all the required field names of the registration form, with first_name localized to self.language_code.

            :return: The list of required field names.
            :rtype: list
            """
            return [field_name.format(language_code=self.language_code).replace("-", "_") for field_name in ['first_name_{language_code}', 'email', 'slug', 'new_password1', 'gender', 'date_of_birth']]

        def _profile_form_all_the_required_fields_keys(self):
            """
            Returns the list of all the required field names of the profile form, with first_name localized to self.language_code.

            :return: The list of required field names.
            :rtype: list
            """
            return [field_name.format(language_code=self.language_code).replace("-", "_") for field_name in ['first_name_{language_code}', 'slug', 'gender', 'date_of_birth']]

        def _login_form_all_the_required_fields_keys(self):
            """
            Returns the list of all the required field names of the login form (username, password).

            :return: The list of required field names.
            :rtype: list
            """
            return [field_name.format(language_code=self.language_code) for field_name in ['username', 'password']]

        def _registration_form_all_the_required_fields_are_required_errors_dict(self):
            """
            Returns the errors dict mapping each required field of the registration form to the "this field is required" error message.

            :return: The errors dict.
            :rtype: dict
            """
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=self._registration_form_all_the_required_fields_keys())

        def _profile_form_all_the_required_fields_are_required_errors_dict(self):
            """
            Returns the errors dict mapping each required field of the profile form to the "this field is required" error message.

            :return: The errors dict.
            :rtype: dict
            """
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=self._profile_form_all_the_required_fields_keys())

        def _login_form_all_the_required_fields_are_required_errors_dict(self):
            """
            Returns the errors dict mapping each required field of the login form to the "this field is required" error message.

            :return: The errors dict.
            :rtype: dict
            """
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=self._login_form_all_the_required_fields_keys())

        def _username_is_required_errors_dict(self):
            """
            Returns the errors dict for a missing username field.

            :return: The errors dict.
            :rtype: dict
            """
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=['username'])

        def _password_is_required_errors_dict(self):
            """
            Returns the errors dict for a missing password field.

            :return: The errors dict.
            :rtype: dict
            """
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=['password'])

        def _date_of_birth_is_required_errors_dict(self):
            """
            Returns the errors dict for a missing date_of_birth field.

            :return: The errors dict.
            :rtype: dict
            """
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=['date_of_birth'])

        def _enter_a_valid_date_errors_dict(self):
            """
            Returns the errors dict for an invalid date_of_birth value.

            :return: The errors dict.
            :rtype: dict
            """
            return {'date_of_birth': [self._enter_a_valid_date_error_message]}

        def _cannot_create_user_email_address_without_all_the_required_fields_errors_dict(self):
            """
            Returns the errors dict for creating a UserEmailAddress without a user (null) and without an email (blank).

            :return: The errors dict.
            :rtype: dict
            """
            return {
                'user': [self._this_field_cannot_be_null_error_message],
                'email': [self._this_field_cannot_be_blank_error_message],
            }

        def _id_contains_illegal_characters_errors_dict(self):
            """
            Returns the errors dict for an id field containing illegal characters.

            :return: The errors dict.
            :rtype: dict
            """
            return {'id': [self._id_contains_illegal_characters_error_message]}

        def _id_contains_illegal_characters_and_ensure_this_value_has_at_most_max_length_characters_errors_dict_by_max_length_and_value_length(self, max_length, value_length):
            """
            Returns the errors dict for an id field that both contains illegal characters and exceeds the maximal allowed length.

            :param max_length: The maximal allowed number of characters.
            :type max_length: int
            :param value_length: The actual length of the value.
            :type value_length: int
            :return: The errors dict.
            :rtype: dict
            """
            return {'id': [self._id_contains_illegal_characters_error_message, self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=max_length, value_length=value_length)]}

        def _please_enter_a_correct_username_and_password_errors_dict(self):
            """
            Returns the errors dict for an incorrect username/password combination at login.

            :return: The errors dict.
            :rtype: dict
            """
            return {'__all__': [self._please_enter_a_correct_username_and_password_error_message]}

        def _invalid_password_errors_dict(self):
            """
            Returns the errors dict for an invalid password field.

            :return: The errors dict.
            :rtype: dict
            """
            return {'password': [self._invalid_password_error_message]}

        def _password_too_short_errors_dict(self, field_names):
            """
            Returns the errors dict for a password that is too short, for each of the given password field names.

            :param field_names: The password field names to map to the error message.
            :type field_names: list
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name: [self._password_too_short_error_message] for field_name in field_names}

        def _password_too_long_errors_dict(self, field_names):
            """
            Returns the errors dict for a password that is too long, for each of the given password field names.

            :param field_names: The password field names to map to the error message.
            :type field_names: list
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name: [self._password_too_long_error_message] for field_name in field_names}

        def _your_password_must_contain_at_least_6_unique_characters_errors_dict(self, field_names):
            """
            Returns the errors dict for a password that doesn't contain at least 6 unique characters, for each of the given password field names.

            :param field_names: The password field names to map to the error message.
            :type field_names: list
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name: [self._your_password_must_contain_at_least_6_unique_characters_error_message] for field_name in field_names}

        def _password_too_short_and_your_password_must_contain_at_least_6_unique_characters_errors_dict(self, field_names):
            """
            Returns the errors dict for a password that is both too short and doesn't contain at least 6 unique characters, for each of the given password field names.

            :param field_names: The password field names to map to the error messages.
            :type field_names: list
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name: [self._password_too_short_error_message, self._your_password_must_contain_at_least_6_unique_characters_error_message] for field_name in field_names}

        def _password_too_long_and_your_password_must_contain_at_least_6_unique_characters_errors_dict(self, field_names):
            """
            Returns the errors dict for a password that is both too long and doesn't contain at least 6 unique characters, for each of the given password field names.

            :param field_names: The password field names to map to the error messages.
            :type field_names: list
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name: [self._password_too_long_error_message, self._your_password_must_contain_at_least_6_unique_characters_error_message] for field_name in field_names}

        def _your_old_password_was_entered_incorrectly_errors_dict(self):
            """
            Returns the errors dict for an incorrect old_password on password change.

            :return: The errors dict.
            :rtype: dict
            """
            return {'old_password': [self._your_old_password_was_entered_incorrectly_error_message]}

        def _the_two_password_fields_didnt_match_errors_dict(self):
            """
            Returns the errors dict for new_password1 and new_password2 not matching.

            :return: The errors dict.
            :rtype: dict
            """
            return {'new_password2': [self._the_two_password_fields_didnt_match_error_message]}

        def _enter_a_valid_email_address_errors_dict(self):
            """
            Returns the errors dict for an invalid email address.

            :return: The errors dict.
            :rtype: dict
            """
            return {'email': [self._enter_a_valid_email_address_error_message]}

        def _this_email_is_already_in_use_errors_dict(self):
            """
            Returns the errors dict for an email address that is already in use.

            :return: The errors dict.
            :rtype: dict
            """
            return {'email': [self._this_email_is_already_in_use_error_message]}

        def _this_username_is_already_taken_errors_dict(self, slug_fail=False, username_fail=False):
            """
            Returns the errors dict for a username/slug that is already taken. slug_fail is expected to always be True.

            :param slug_fail: Whether the slug field has this error.
            :type slug_fail: bool
            :param username_fail: Whether the username field has this error.
            :type username_fail: bool
            :return: The errors dict.
            :rtype: dict
            """
            self.assertIs(expr1=slug_fail, expr2=True)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._this_username_is_already_taken_error_message]
            if (username_fail):
                errors_dict['username'] = [self._this_username_is_already_taken_error_message]
            return errors_dict

        def _username_must_start_with_4_or_more_letters_errors_dict(self, model, slug_fail=False, username_fail=False):
            """
            Returns the errors dict for a slug and/or username of model that doesn't start with 4 or more letters.

            :param model: The model class (Entity or User) the error message is specific to.
            :type model: type
            :param slug_fail: Whether the slug field has this error.
            :type slug_fail: bool
            :param username_fail: Whether the username field has this error.
            :type username_fail: bool
            :return: The errors dict.
            :rtype: dict
            """
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                if (model is Entity):
                    errors_dict['slug'] = [self._entity_username_must_start_with_4_or_more_letters_error_message]
                elif (model is User):
                    errors_dict['slug'] = [self._user_username_must_start_with_4_or_more_letters_error_message]
                else:
                    raise NotImplementedError("Invalid model.")
            if (username_fail):
                if (model is Entity):
                    errors_dict['username'] = [self._entity_username_must_start_with_4_or_more_letters_error_message]
                elif (model is User):
                    errors_dict['username'] = [self._user_username_must_start_with_4_or_more_letters_error_message]
                else:
                    raise NotImplementedError("Invalid model.")
            return errors_dict

        def _slug_does_not_parse_to_username_errors_dict(self, model, username_fail=False):
            """
            Returns the errors dict for a slug of model that doesn't parse to a valid username.

            :param model: The model class (Entity or User) the error message is specific to.
            :type model: type
            :param username_fail: Whether the username field also has the "must start with 4 or more letters" error.
            :type username_fail: bool
            :return: The errors dict.
            :rtype: dict
            """
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {'slug': [self._slug_does_not_parse_to_username_error_message]}
            if (username_fail):
                if (model is Entity):
                    errors_dict['username'] = [self._entity_username_must_start_with_4_or_more_letters_error_message]
                elif (model is User):
                    errors_dict['username'] = [self._user_username_must_start_with_4_or_more_letters_error_message]
                else:
                    raise NotImplementedError("Invalid model.")
            return errors_dict

        def _date_of_birth_errors_dict_by_date_of_birth(self, date_of_birth):
            """
            Returns the errors dict for an empty or invalid date_of_birth value.

            :param date_of_birth: The date of birth value being validated.
            :return: The errors dict, either for a required field or for an invalid date.
            :rtype: dict
            """
            if (date_of_birth == ''):
                return self._date_of_birth_is_required_errors_dict()
            else:
                return self._enter_a_valid_date_errors_dict()

        def _you_cant_change_your_username_errors_dict_by_gender(self, gender):
            """
            Returns the errors dict for an attempt to change a username that is not allowed to change, with a gender-specific message.

            :param gender: The gender used to select the localized error message.
            :return: The errors dict.
            :rtype: dict
            """
            return {'slug': [self._you_cant_change_your_username_error_message_dict_by_gender[gender]]}

        def _cannot_create_user_without_all_the_required_fields_errors_dict_by_value(self, value, gender_is_valid=False):
            """
            Returns the errors dict for creating a User with value (None, '' or an invalid value) used for all the required fields (gender, date_of_birth, username/slug, localized first names, password).

            :param value: The value used for all the required fields (typically None, '' or an invalid gender value).
            :param gender_is_valid: Whether value is a valid gender value.
            :type gender_is_valid: bool
            :return: The errors dict.
            :rtype: dict
            """
            self.assertEqual(first=gender_is_valid, second=(value in User.GENDER_VALID_VALUES))
            if (value is None):
                str_value = ''
                gender_error_messages = [self._this_field_cannot_be_null_error_message]
            else:
                str_value = str(value)
                if (value == ''):
                    gender_error_messages = [self._value_must_be_an_integer_error_message_by_value(value=value)]
                else:
                    if (not (gender_is_valid)):
                        gender_error_messages = [self._value_is_not_a_valid_choice_error_message_by_value(value=value)]
                    else:
                        gender_error_messages = None
            slug_and_username_error_messages = [self._user_username_must_start_with_4_or_more_letters_error_message]
            date_of_birth_error_messages = [self._enter_a_valid_date_error_message]
            errors_dict = {
                'username': slug_and_username_error_messages,
                'slug': slug_and_username_error_messages,
                'date_of_birth': date_of_birth_error_messages,
            }
            if (value in [None, '']):
                self.assertEqual(first=str_value, second='')
                for language_code, language_name in django_settings.LANGUAGES:
                    if (value is None):
                        errors_dict['first_name_{language_code}'.format(language_code=language_code).replace("-", "_")] = [self._this_field_cannot_be_null_error_message]
                        # ~~~~ TODO: last name ValidationError(_('This field cannot be null.')) is not raised when User() is created without a last name - should be raised!
                        # errors_dict['last_name_{language_code}'.format(language_code=language_code).replace("-", "_")] = [self._this_field_cannot_be_null_error_message]
                    elif (value == ''):
                        errors_dict['first_name_{language_code}'.format(language_code=language_code).replace("-", "_")] = [self._this_field_cannot_be_blank_error_message]
                    else:
                        raise NotImplementedError("Invalid value.")
                errors_dict['password'] = [self._this_field_cannot_be_blank_error_message]
            else:
                self.assertNotEqual(first=str_value, second='')
            self.assertEqual(first=gender_is_valid, second=(gender_error_messages is None))
            if (not (gender_is_valid)):
                errors_dict['gender'] = gender_error_messages
            return errors_dict

        def _model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(self, model, slug_fail=False, username_fail=False, username_value_length=None):
            """
            Returns the errors dict for a slug and/or username of model that doesn't contain at least the model's minimal required number of alphanumeric characters.

            :param model: The model class (Entity or User) whose MIN_USERNAME_LENGTH setting is used.
            :type model: type
            :param slug_fail: Whether the slug field has this error.
            :type slug_fail: bool
            :param username_fail: Whether the username field has this error.
            :type username_fail: bool
            :param username_value_length: The actual length of the username/slug value.
            :type username_value_length: int
            :return: The errors dict.
            :rtype: dict
            """
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._username_must_contain_at_least_min_length_alphanumeric_characters_error_message_by_min_length_and_value_length(min_length=model.settings.MIN_USERNAME_LENGTH, value_length=username_value_length)]
            if (username_fail):
                errors_dict['username'] = [self._username_must_contain_at_least_min_length_alphanumeric_characters_error_message_by_min_length_and_value_length(min_length=model.settings.MIN_USERNAME_LENGTH, value_length=username_value_length)]
            return errors_dict

        def _model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(self, model, slug_fail=False, username_fail=False, username_value_length=None):
            """
            Returns the errors dict for a slug and/or username of model that contains more than the model's maximal allowed number of alphanumeric characters.

            :param model: The model class (Entity or User) whose MAX_USERNAME_LENGTH setting is used.
            :type model: type
            :param slug_fail: Whether the slug field has this error.
            :type slug_fail: bool
            :param username_fail: Whether the username field has this error.
            :type username_fail: bool
            :param username_value_length: The actual length of the username/slug value.
            :type username_value_length: int
            :return: The errors dict.
            :rtype: dict
            """
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._username_must_contain_at_most_max_length_alphanumeric_characters_error_message_by_max_length_and_value_length(max_length=model.settings.MAX_USERNAME_LENGTH, value_length=username_value_length)]
            if (username_fail):
                errors_dict['username'] = [self._username_must_contain_at_most_max_length_alphanumeric_characters_error_message_by_max_length_and_value_length(max_length=model.settings.MAX_USERNAME_LENGTH, value_length=username_value_length)]
            return errors_dict

        def _model_slug_or_username_username_must_contain_at_least_min_length_characters_errors_dict_by_value_length(self, model, slug_fail=False, username_fail=False, slug_value_length=None, username_value_length=None):
            """
            Returns the errors dict for a slug and/or username of model that doesn't contain at least the model's minimal required number of characters.

            :param model: The model class (Entity or User) whose MIN_SLUG_LENGTH/MIN_USERNAME_LENGTH settings are used.
            :type model: type
            :param slug_fail: Whether the slug field has this error.
            :type slug_fail: bool
            :param username_fail: Whether the username field has this error.
            :type username_fail: bool
            :param slug_value_length: The actual length of the slug value.
            :type slug_value_length: int
            :param username_value_length: The actual length of the username value.
            :type username_value_length: int
            :return: The errors dict.
            :rtype: dict
            """
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._username_must_contain_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=model.settings.MIN_SLUG_LENGTH, value_length=slug_value_length)]
            if (username_fail):
                errors_dict['username'] = [self._username_must_contain_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=model.settings.MIN_USERNAME_LENGTH, value_length=username_value_length)]
            return errors_dict

        def _model_slug_or_username_username_must_contain_at_most_max_length_characters_errors_dict_by_value_length(self, model, slug_fail=False, username_fail=False, slug_value_length=None, username_value_length=None):
            """
            Returns the errors dict for a slug and/or username of model that contains more than the model's maximal allowed number of characters.

            :param model: The model class (Entity or User) whose MAX_SLUG_LENGTH/MAX_USERNAME_LENGTH settings are used.
            :type model: type
            :param slug_fail: Whether the slug field has this error.
            :type slug_fail: bool
            :param username_fail: Whether the username field has this error.
            :type username_fail: bool
            :param slug_value_length: The actual length of the slug value.
            :type slug_value_length: int
            :param username_value_length: The actual length of the username value.
            :type username_value_length: int
            :return: The errors dict.
            :rtype: dict
            """
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._username_must_contain_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=model.settings.MAX_SLUG_LENGTH, value_length=slug_value_length)]
            if (username_fail):
                errors_dict['username'] = [self._username_must_contain_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=model.settings.MAX_USERNAME_LENGTH, value_length=username_value_length)]
            return errors_dict

        def _this_field_cannot_be_null_errors_dict_by_field_name(self, field_name):
            """
            Returns the errors dict for field_name being null.

            :param field_name: The name of the field.
            :type field_name: str
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name: [self._this_field_cannot_be_null_error_message]}

        def _this_field_cannot_be_blank_errors_dict_by_field_name(self, field_name):
            """
            Returns the errors dict for field_name being blank.

            :param field_name: The name of the field.
            :type field_name: str
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name: [self._this_field_cannot_be_blank_error_message]}

        def _value_must_be_valid_json_errors_dict_by_field_name(self, field_name):
            """
            Returns the errors dict for field_name not containing valid JSON.

            :param field_name: The name of the field.
            :type field_name: str
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name: [self._value_must_be_valid_json_error_message]}

        def _ensure_this_value_is_greater_than_or_equal_to_minus_32768_errors_dict_by_field_name(self, field_name):
            """
            Returns the errors dict for field_name's value being less than -32768.

            :param field_name: The name of the field.
            :type field_name: str
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name: [self._ensure_this_value_is_greater_than_or_equal_to_minus_32768_error_message]}

        def _ensure_this_value_is_less_than_or_equal_to_32767_errors_dict_by_field_name(self, field_name):
            """
            Returns the errors dict for field_name's value being greater than 32767.

            :param field_name: The name of the field.
            :type field_name: str
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name: [self._ensure_this_value_is_less_than_or_equal_to_32767_error_message]}

        def _value_is_not_a_valid_choice_errors_dict_by_field_name_and_value(self, field_name, value):
            """
            Returns the errors dict for field_name's value not being a valid choice.

            :param field_name: The name of the field.
            :type field_name: str
            :param value: The invalid value.
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name: [self._value_is_not_a_valid_choice_error_message_by_value(value=value)]}

        def _value_must_be_an_integer_errors_dict_by_field_name_and_value(self, field_name, value):
            """
            Returns the errors dict for field_name's value not being an integer.

            :param field_name: The name of the field.
            :type field_name: str
            :param value: The non-integer value.
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name: [self._value_must_be_an_integer_error_message_by_value(value=value)]}

        def _this_field_cannot_be_null_errors_dict_by_field_name_list(self, field_name_list):
            """
            Returns the errors dict mapping each field name in field_name_list to the "this field cannot be null" error message.

            :param field_name_list: The list of field names.
            :type field_name_list: list
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name_list[i]: [self._this_field_cannot_be_null_error_message] for i in range(len(field_name_list))}

        def _value_must_be_an_integer_errors_dict_by_field_name_list_and_value_list(self, field_name_list, value_list):
            """
            Returns the errors dict mapping each field name in field_name_list to the "value must be an integer" error message for the corresponding value in value_list.

            :param field_name_list: The list of field names.
            :type field_name_list: list
            :param value_list: The list of non-integer values, corresponding by index to field_name_list.
            :type value_list: list
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name_list[i]: [self._value_must_be_an_integer_error_message_by_value(value=value_list[i])] for i in range(len(field_name_list))}

        def _ensure_this_value_has_at_most_max_length_characters_errors_dict_by_field_name_and_max_length_and_value_length(self, field_name, max_length, value_length):
            """
            Returns the errors dict for field_name's value being longer than max_length characters.

            :param field_name: The name of the field.
            :type field_name: str
            :param max_length: The maximal allowed number of characters.
            :type max_length: int
            :param value_length: The actual length of the value.
            :type value_length: int
            :return: The errors dict.
            :rtype: dict
            """
            return {field_name: [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=max_length, value_length=value_length)]}

        def _not_null_constraint_error_message_by_column_and_relation(self, column, relation):
            """
            Returns the PostgreSQL not-null constraint violation message for a given column and relation (table) name.

            :param column: The name of the column that violated the not-null constraint.
            :type column: str
            :param relation: The name of the relation (table).
            :type relation: str
            :return: The formatted PostgreSQL error message.
            :rtype: str
            """
            return 'null value in column "{}" of relation "{}" violates not-null constraint'.format(column, relation)

        def set_up(self):
            """
            Sets up all the localized speedy.core.accounts validation error message and success message attributes used by the test cases, based on self.language_code. Builds per-language dicts of error/success message texts and assigns the entry for self.language_code to the corresponding self._xxx_error_message/self._xxx_success_message attribute.
            """
            super().set_up()

            _this_field_cannot_be_null_error_message_dict = {'en': 'This field cannot be null.', 'fr': 'Ce champ ne peut pas contenir la valeur nulle.', 'de': 'Dieses Feld darf nicht null sein.', 'es': 'Este campo no puede ser nulo.', 'pt': 'Este campo não pode ser nulo.', 'it': 'Questo campo non può essere nullo.', 'nl': 'Dit veld mag niet leeg zijn.', 'ja': 'このフィールドを null にすることはできません。', 'ru': 'Это поле не может быть нулевым.', 'zh': '此欄位不能為空。', 'pl': 'To pole nie może mieć wartości null.', 'fa': 'این فیلد نمی تواند null باشد.', 'he': 'שדה זה אינו יכול להיות ריק.', 'ko': '이 필드는 null 값을 사용할 수 없습니다.', 'ar': 'لا يمكن أن يكون هذا الحقل فارغًا.', 'id': 'Bidang ini tidak boleh nol.', 'uk': 'Це поле не може бути нульовим.', 'tr': 'Bu alan boş olamaz.', 'vi': 'Trường này không được phép để trống.', 'cs': 'Toto pole nemůže mít hodnotu null.', 'sv': 'Detta fält får inte vara null.', 'fi': 'Tämän kentän arvo ei voi olla "null".', 'hu': 'Ez a mező nem lehet null.', 'th': 'ฟิลด์นี้ต้องไม่เป็นค่า null', 'el': 'Αυτό το πεδίο δεν μπορεί να είναι null.', 'ms': 'Medan ini tidak boleh null.', 'sr': 'Ово поље не може бити null.', 'ro': 'Acest câmp nu poate fi nul.', 'bn': 'এই ফিল্ডটি শূন্য হতে পারবে না।', 'ca': 'Aquest camp no pot ser nul.', 'no': 'Dette feltet kan ikke være null.', 'bg': 'Това поле не може да бъде null.', 'da': 'Dette felt kan ikke være null.', 'sk': 'Toto pole nemôže mať hodnotu null.', 'hi': 'यह फ़ील्ड खाली नहीं हो सकता।', 'et': 'See väli ei saa olla tühi.', 'hr': 'Ovo polje ne može biti nula.', 'az': 'Bu sahə null ola bilməz.', 'zh-yue': '此欄位不能為空。', 'lt': 'Šis laukas negali būti null.', 'sl': 'To polje ne more biti null.', 'eu': 'Eremu hau ezin da null izan.', 'hy': 'Այս դաշտը չի կարող ունենալ NULL արժեք։', 'uz': "Bu maydon nolga teng bo'lmasligi kerak.", 'ta': 'இந்த புலம் காலியாக இருக்கக் கூடாது', 'lv': 'Šis lauks nevar būt null.'}
            _this_field_cannot_be_blank_error_message_dict = {'en': 'This field cannot be blank.', 'fr': 'Ce champ ne peut pas être vide.', 'de': 'Dieses Feld darf nicht leer sein.', 'es': 'Este campo no puede estar vacío.', 'pt': 'Este campo não pode ser vazio.', 'it': 'Questo campo non può essere vuoto.', 'nl': 'Dit veld kan niet leeg zijn.', 'ja': 'このフィールドを空白にすることはできません。', 'ru': 'Это поле не может быть пустым.', 'zh': '此欄位不能為空。', 'pl': 'To pole nie może być puste.', 'fa': 'این فیلد نمی تواند خالی باشد.', 'he': 'שדה זה אינו יכול להיות ריק.', 'ko': '이 필드는 빈 칸으로 둘 수 없습니다.', 'ar': 'لا يمكن أن يكون هذا الحقل فارغاً.', 'id': 'Bidang ini tidak boleh kosong.', 'uk': 'Це поле не може бути порожнім.', 'tr': 'Bu alan boş olamaz.', 'vi': 'Ô này không được để trống.', 'cs': 'Toto pole nemůže být prázdné.', 'sv': 'Detta fält får inte vara tomt.', 'fi': 'Tämä kenttä ei voi olla tyhjä.', 'hu': 'Ez a mező nem lehet üres.', 'th': 'ฟิลด์นี้ต้องไม่เว้นว่าง', 'el': 'Αυτό το πεδίο δεν μπορεί να μείνει κενό.', 'ms': 'Medan ini tidak boleh kosong.', 'sr': 'Ово поље не може бити празно.', 'ro': 'Acest câmp nu poate fi gol.', 'bn': 'এই ক্ষেত্রটি খালি রাখা যাবে না।', 'ca': 'Aquest camp no pot estar en blanc.', 'no': 'Dette feltet kan ikke være tomt.', 'bg': 'Това поле не може да бъде празно.', 'da': 'Dette felt må ikke være tomt.', 'sk': 'Toto pole nemôže byť prázdne.', 'hi': 'यह फ़ील्ड खाली नहीं हो सकता।', 'et': 'See väli ei saa olla tühi.', 'hr': 'Ovo polje ne može biti prazno.', 'az': 'Bu sahə boş ola bilməz.', 'zh-yue': '此欄位不能為空。', 'lt': 'Šis laukas negali būti tuščias.', 'sl': 'To polje ne sme biti prazno.', 'eu': 'Eremu hau ezin da hutsik egon.', 'hy': 'Այս դաշտը չի կարող լինել դատարկ։', 'uz': "Bu maydon bo'sh bo'lishi mumkin emas.", 'ta': 'இந்த புலம் வெற்று இருக்க முடியாது.', 'lv': 'Šis lauks nevar būt tukšs.'}
            _id_contains_illegal_characters_error_message_dict = {'en': 'id contains illegal characters.', 'fr': 'cette ID contient des caractères illégaux.', 'de': 'ID enthält nicht zugelassene Zeichen.', 'es': 'id contiene caracteres ilegales.', 'pt': 'id contém caracteres ilegais.', 'it': 'l’id contiene caratteri illegali.', 'nl': 'id bevat illegale tekens.', 'ja': 'id に不正な文字が含まれています。', 'ru': 'id содержит недопустимые символы.', 'zh': 'ID包含非法字元。', 'pl': 'id zawiera niedozwolone znaki.', 'fa': 'شناسه شامل کاراکترهای غیرقانونی است.', 'he': 'id מכיל תווים לא חוקיים.', 'ko': 'ID에 잘못된 문자가 있습니다.', 'ar': 'يحتوي المعرف على أحرف غير قانونية.', 'id': 'id berisi karakter ilegal.', 'uk': 'ідентифікатор містить заборонені символи.', 'tr': 'kimlik geçersiz karakterler içeriyor.', 'vi': 'ID chứa các ký tự không hợp lệ.', 'cs': 'id obsahuje nepovolené znaky.', 'sv': 'id innehåller olagliga tecken.', 'fi': 'id sisältää laittomia merkkejä.', 'hu': 'Az id illegális karaktereket tartalmaz.', 'th': 'id มีอักขระที่ไม่ได้รับอนุญาต', 'el': 'Το αναγνωριστικό περιέχει μη επιτρεπόμενους χαρακτήρες.', 'ms': 'id mengandungi aksara yang tidak dibenarkan.', 'sr': 'ид садржи недозвољене знакове.', 'ro': 'id conține caractere ilegale.', 'bn': 'আইডিতে অবৈধ অক্ষর রয়েছে।', 'ca': 'id conté caràcters il·legals.', 'no': 'ID inneholder ulovlige tegn.', 'bg': 'id съдържа незаконни знаци.', 'da': 'id indeholder ulovlige tegn.', 'sk': 'id obsahuje nepovolené znaky.', 'hi': 'आईडी में अवैध वर्ण हैं।', 'et': 'ID sisaldab lubamatuid tähemärke.', 'hr': 'id sadrži nedopuštene znakove.', 'az': 'identifikatorda icazəsiz simvollar var.', 'zh-yue': 'ID包含非法字元。', 'lt': 'id turi neleistinų simbolių.', 'sl': 'id vsebuje nedovoljene znake.', 'eu': 'id-ak legez kanpoko karaktereak ditu.', 'hy': 'id-ն պարունակում է անթույլատրելի նիշեր։', 'uz': 'idda noqonuniy belgilar mavjud.', 'ta': 'ஐடி சட்டவிரோத எழுத்துக்களைக் கொண்டுள்ளது.', 'lv': 'ID satur neatļautas rakstzīmes.'}
            _value_must_be_valid_json_error_message_dict = {'en': 'Value must be valid JSON.', 'fr': 'La valeur doit respecter la syntaxe JSON.', 'de': 'Wert muss gültiges JSON sein.', 'es': 'El valor debe ser un objeto JSON válido.', 'pt': 'O valor deve ser um JSON válido.', 'it': 'Il valore deve essere un JSON valido.', 'nl': 'Waarde moet geldige JSON zijn.', 'ja': '値は有効な JSON である必要があります。', 'ru': 'Значение должно быть действительным JSON.', 'zh': '值必須是有效的JSON格式。', 'pl': 'Wartość musi być prawidłowym kodem JSON.', 'fa': 'مقدار باید JSON معتبر باشد.', 'he': 'ערך חייב להיות JSON חוקי.', 'ko': '올바른 JSON 형식이여야 합니다.', 'ar': 'يجب أن تكون القيمة صالحة بتنسيق JSON.', 'id': 'Nilai harus berupa JSON yang valid.', 'uk': 'Значення має бути дійсним JSON.', 'tr': 'Değer geçerli bir JSON olmalıdır.', 'vi': 'Giá trị phải là JSON hợp lệ.', 'cs': 'Hodnota musí být platný JSON.', 'sv': 'Värdet måste vara giltig JSON.', 'fi': 'Arvon pitää olla kelvollista JSONia.', 'hu': 'Az értéknek érvényes JSON-nak kell lennie.', 'th': 'ค่าต้องเป็น JSON ที่ถูกต้อง', 'el': 'Η τιμή πρέπει να είναι έγκυρο JSON.', 'ms': 'Nilai mestilah JSON yang sah.', 'sr': 'Вредност мора бити важећи JSON.', 'ro': 'Valoarea trebuie să fie JSON valid.', 'bn': 'মানটি অবশ্যই বৈধ JSON হতে হবে।', 'ca': 'El valor ha de ser un JSON vàlid.', 'no': 'Verdien må være gyldig JSON.', 'bg': 'Стойността трябва да е валиден JSON.', 'da': 'Værdien skal være gyldig JSON.', 'sk': 'Hodnota musí byť platný JSON.', 'hi': 'मान वैध JSON होना चाहिए।', 'et': 'Väärtus peab olema kehtiv JSON.', 'hr': 'Vrijednost mora biti važeći JSON.', 'az': 'Dəyər düzgün JSON olmalıdır.', 'zh-yue': '值必須是有效的JSON格式。', 'lt': 'Reikšmė turi būti tinkamas JSON.', 'sl': 'Vrednost mora biti veljaven JSON.', 'eu': 'Balioak baliozko JSON izan behar du.', 'hy': 'Արժեքը պետք է լինի վավեր JSON։', 'uz': "Qiymat haqiqiy JSON bo'lishi kerak.", 'ta': 'மதிப்பு JSON ஆக இருக்க வேண்டும்.', 'lv': 'Vērtībai jābūt derīgam JSON.'}
            _invalid_password_error_message_dict = {'en': 'Invalid password.', 'fr': 'Mot de passe invalide.', 'de': 'Ungültiges Passwort.', 'es': 'Contraseña no válida.', 'pt': 'Palavra-passe inválida.', 'it': 'Password non valida.', 'nl': 'Ongeldig wachtwoord.', 'ja': 'パスワードが無効です。', 'ru': 'Неверный пароль.', 'zh': '密碼無效。', 'pl': 'Nieprawidłowe hasło.', 'fa': 'رمز عبور نامعتبر است.', 'he': 'הסיסמה לא תקינה.', 'ko': '잘못된 암호.', 'ar': 'كلمة المرور غير صالحة.', 'id': 'Kata sandi tidak valid.', 'uk': 'Недійсний пароль.', 'tr': 'Geçersiz şifre.', 'vi': 'Mật khẩu không hợp lệ.', 'cs': 'Neplatné heslo.', 'sv': 'Ogiltigt lösenord', 'fi': 'Väärä salasana.', 'hu': 'Érvénytelen jelszó.', 'th': 'รหัสผ่านไม่ถูกต้อง', 'el': 'Ο κωδικός πρόσβασης είναι λανθασμένος.', 'ms': 'Kata laluan tidak sah.', 'sr': 'Неважећа лозинка.', 'ro': 'Parolă nevalidă.', 'bn': 'ভুল পাসওয়ার্ড।', 'ca': 'Contrasenya no vàlida.', 'no': 'Ugyldig passord.', 'bg': 'Невалидна парола.', 'da': 'Ugyldig adgangskode.', 'sk': 'Neplatné heslo.', 'hi': 'अवैध पासवर्ड।', 'et': 'Vale parool.', 'hr': 'Neispravna lozinka.', 'az': 'Yanlış şifrə.', 'zh-yue': '密碼無效。', 'lt': 'Neteisingas slaptažodis.', 'sl': 'Neveljavno geslo.', 'eu': 'Pasahitz baliogabea.', 'hy': 'Անվավեր գաղտնաբառ։', 'uz': "Noto'g'ri parol.", 'ta': 'செல்லாத கடவுச்சொல்.', 'lv': 'Nederīga parole.'}
            _password_too_short_error_message_dict = {'en': 'This password is too short. It must contain at least 8 characters.', 'fr': 'Ce mot de passe est trop court. Il doit contenir au minimum 8 caractères.', 'de': 'Dieses Passwort ist zu kurz. Es muss mindestens 8 Zeichen enthalten.', 'es': 'Esta contraseña es demasiado corta. Debe contener al menos 8 caracteres.', 'pt': 'Esta palavra-passe é muito curta. Deve conter pelo menos 8 caracteres.', 'it': 'Questa password è troppo corta. Deve contenere almeno 8 caratteri.', 'nl': 'Dit wachtwoord is te kort. De minimale lengte is 8 tekens.', 'ja': 'このパスワードは短すぎます。8文字以上で入力してください。', 'ru': 'Этот пароль слишком короткий. Он должен содержать не менее 8 символов.', 'zh': '此密碼太短。必須至少包含 8 個字元。', 'pl': 'To hasło jest za krótkie. Musi zawierać co najmniej 8 znaków.', 'fa': 'این گذرواژه خیلی کوتاه است. باید حداقل 8 نویسه داشته باشد.', 'he': 'סיסמה זו קצרה מדי. היא חייבת להכיל לפחות 8 תווים.', 'ko': '비밀번호가 너무 짧습니다. 최소 8 문자를 포함해야 합니다.', 'ar': 'كلمة المرور هذه قصيرة جدًا. يجب أن تحتوي على 8 أحرف على الأقل.', 'id': 'Kata sandi ini terlalu pendek. Minimal harus berisi 8 karakter.', 'uk': 'Цей пароль занадто короткий. Він має містити принаймні 8 символів.', 'tr': 'Bu şifre çok kısa. En az 8 karakter içermelidir.', 'vi': 'Mật khẩu này quá ngắn. Nó phải chứa ít nhất 8 ký tự.', 'cs': 'Toto heslo je příliš krátké. Musí obsahovat alespoň 8 znaků.', 'sv': 'Detta lösenord är för kort. Det måste innehålla minst 8 tecken.', 'fi': 'Tämä salasana on liian lyhyt. Sen tulee sisältää ainakin 8 merkkiä.', 'hu': 'Ez a jelszó túl rövid. Legalább 8 karaktert kell tartalmaznia.', 'th': 'รหัสผ่านนี้สั้นเกินไป ต้องมีอักขระอย่างน้อย 8 ตัว', 'el': 'Αυτός ο κωδικός πρόσβασης είναι πολύ σύντομος. Πρέπει να περιέχει τουλάχιστον 8 χαρακτήρες.', 'ms': 'Kata laluan ini terlalu pendek. Ia mesti mengandungi sekurang-kurangnya 8 aksara.', 'sr': 'Ова лозинка је прекратка. Мора да садржи најмање 8 знакова.', 'ro': 'Această parolă este prea scurtă. Trebuie să conțină cel puțin 8 caractere.', 'bn': 'এই পাসওয়ার্ডটি খুব ছোট। এতে কমপক্ষে 8টি অক্ষর থাকতে হবে।', 'ca': 'Aquesta contrasenya és massa curta. Ha de contenir almenys 8 caràcters.', 'no': 'Dette passordet er for kort. Det må inneholde minst 8 tegn.', 'bg': 'Тази парола е твърде кратка. Трябва да съдържа поне 8 знака.', 'da': 'Denne adgangskode er for kort. Den skal indeholde mindst 8 tegn.', 'sk': 'Toto heslo je príliš krátke. Musí obsahovať aspoň 8 znakov.', 'hi': 'यह पासवर्ड बहुत छोटा है। इसमें कम से कम 8 वर्ण होने चाहिए।', 'et': 'See parool on liiga lühike. See peab sisaldama vähemalt 8 tähemärki.', 'hr': 'Ova lozinka je prekratka. Mora sadržavati najmanje 8 znakova.', 'az': 'Bu şifrə çox qısadır. O, ən azı 8 simvoldan ibarət olmalıdır.', 'zh-yue': '呢個密碼太短。必須至少有 8 個字符。', 'lt': 'Šis slaptažodis per trumpas. Jame turi būti bent 8 simboliai.', 'sl': 'To geslo je prekratko. Vsebovati mora vsaj 8 znakov.', 'eu': 'Pasahitz hau laburregia da. Gutxienez 8 karaktere izan behar ditu.', 'hy': 'Գաղտնաբառը շատ կարճ է։ Այն պետք է պարունակի ամենաքիչը 8 նիշ։', 'uz': "Bu parol juda qisqa. Unda kamida 8 ta belgi bo'lishi kerak.", 'ta': 'இந்த கடவுச்சொல் மிகக் குறுகியதாகும். இதில் குறைந்தது 8 எழுத்துக்கள் இருக்க வேண்டும்.', 'lv': 'Šī parole ir pārāk īsa. Tai jāsatur vismaz 8 rakstzīmes.'}
            _password_too_long_error_message_dict = {'en': 'This password is too long. It must contain at most 120 characters.', 'fr': 'Ce mot de passe est trop long. Il doit contenir au maximum 120\xa0caractères.', 'de': 'Dieses Passwort ist zu lang. Es darf höchstens 120 Zeichen enthalten.', 'es': 'Esta contraseña es demasiado larga. Debe contener como máximo 120 caracteres.', 'pt': 'Esta palavra-passe é muito longa. Ela precisa conter no máximo 120 caracteres.', 'it': 'Questa password è troppo lunga. Deve contenere al massimo 120 caratteri.', 'nl': 'Dit wachtwoord is te lang. Het mag maximaal 120 tekens bevatten.', 'ja': 'このパスワードは長すぎます。120文字以下で入力してください。', 'ru': 'Этот пароль слишком длинный. Он должен содержать не более 120 символов.', 'zh': '此密碼太長。最多只能包含 120 個字元。', 'pl': 'To hasło jest za długie. Musi zawierać najwyżej 120 znaków.', 'fa': 'این گذرواژه خیلی بلند است. باید حداکثر 120 نویسه داشته باشد.', 'he': 'סיסמה זו ארוכה מדי. היא יכולה להכיל 120 תווים לכל היותר.', 'ko': '이 암호는 너무 깁니다. 최대 120자만 포함되어야 합니다.', 'ar': 'كلمة المرور هذه طويلة جدًا. يجب أن تحتوي على 120 حرفًا على الأكثر.', 'id': 'Kata sandi ini terlalu panjang. Ini harus berisi paling banyak 120 karakter.', 'uk': 'Цей пароль задовгий. Він має містити щонайбільше 120 символів.', 'tr': 'Bu şifre çok uzun. En fazla 120 karakter içermelidir.', 'vi': 'Mật khẩu này quá dài. Nó phải chứa tối đa 120 ký tự.', 'cs': 'Toto heslo je příliš dlouhé. Musí obsahovat maximálně 120 znaků.', 'sv': 'Detta lösenord är för långt. Det får innehålla högst 120 tecken.', 'fi': 'Tämä salasana on liian pitkä. Siinä saa olla enintään 120 merkkiä.', 'hu': 'Ez a jelszó túl hosszú. Legfeljebb 120 karaktert tartalmazhat.', 'th': 'รหัสผ่านนี้ยาวเกินไป ต้องมีอักขระไม่เกิน 120 ตัว', 'el': 'Αυτός ο κωδικός πρόσβασης είναι πολύ μεγάλος. Πρέπει να περιέχει το πολύ 120 χαρακτήρες.', 'ms': 'Kata laluan ini terlalu panjang. Ia mesti mengandungi paling banyak 120 aksara.', 'sr': 'Ова лозинка је предугачка. Мора да садржи највише 120 знакова.', 'ro': 'Această parolă este prea lungă. Trebuie să conțină cel mult 120 de caractere.', 'bn': 'এই পাসওয়ার্ডটি খুব বড়। এতে সর্বোচ্চ 120টি অক্ষর থাকতে পারবে।', 'ca': 'Aquesta contrasenya és massa llarga. Ha de contenir com a màxim 120 caràcters.', 'no': 'Dette passordet er for langt. Det må inneholde maksimalt 120 tegn.', 'bg': 'Тази парола е твърде дълга. Трябва да съдържа най-много 120 знака.', 'da': 'Denne adgangskode er for lang. Den må højst indeholde 120 tegn.', 'sk': 'Toto heslo je príliš dlhé. Musí obsahovať najviac 120 znakov.', 'hi': 'यह पासवर्ड बहुत लंबा है। इसमें अधिकतम 120 वर्ण होने चाहिए।', 'et': 'See parool on liiga pikk. See peab sisaldama kuni 120 tähemärki.', 'hr': 'Ova lozinka je predugačka. Mora sadržavati najviše 120 znakova.', 'az': 'Bu şifrə çox uzundur. O, ən çox 120 simvoldan ibarət olmalıdır.', 'zh-yue': '呢個密碼太長。最多只可以有 120 個字符。', 'lt': 'Šis slaptažodis per ilgas. Jame gali būti daugiausia 120 simbolių.', 'sl': 'To geslo je predolgo. Vsebovati sme največ 120 znakov.', 'eu': 'Pasahitz hau luzeegia da. Gehienez 120 karaktere izan behar ditu.', 'hy': 'Այս գաղտնաբառը չափազանց երկար է։ Այն պետք է պարունակի առավելագույնը 120 նիշ։', 'uz': "Bu parol juda uzun. Unda ko'pi bilan 120 ta belgi bo'lishi kerak.", 'ta': 'இந்த கடவுச்சொல் மிக நீளமானது. இதில் அதிகபட்சம் 120 எழுத்துக்கள் இருக்க வேண்டும்.', 'lv': 'Šī parole ir pārāk gara. Tajā drīkst būt ne vairāk kā 120 rakstzīmju.'}
            _your_password_must_contain_at_least_6_unique_characters_error_message_dict = {'en': 'Your password must contain at least 6 unique characters.', 'fr': 'Votre mot de passe doit contenir au moins 6 caractères uniques.', 'de': 'Ihr Passwort muss mindestens 6 eindeutige Zeichen enthalten.', 'es': 'La contraseña debe contener al menos 6 caracteres únicos.', 'pt': 'Sua palavra-passe deve conter pelo menos 6 caracteres exclusivos.', 'it': 'La password deve contenere almeno 6 caratteri univoci.', 'nl': 'Je wachtwoord moet minstens 6 unieke tekens bevatten.', 'ja': 'パスワードには少なくとも 6 種類の異なる文字を含める必要があります。', 'ru': 'Ваш пароль должен содержать не менее 6 уникальных символов.', 'zh': '您的密碼必須至少包含 6 個不同的字元。', 'pl': 'Hasło musi zawierać co najmniej 6 unikalnych znaków.', 'fa': 'گذرواژه شما باید حداقل 6 نویسهٔ منحصربه\u200cفرد داشته باشد.', 'he': 'הסיסמה שלך חייבת להכיל לפחות 6 תווים ייחודיים.', 'ko': '암호에는 최소 6자의 고유 문자가 포함되어야 합니다.', 'ar': 'يجب أن تحتوي كلمة المرور الخاصة بك على 6 من الأحرف الفريدة على الأقل.', 'id': 'Kata sandi Anda harus mengandung setidaknya 6 karakter unik.', 'uk': 'Ваш пароль має містити принаймні 6 унікальних символів.', 'tr': 'Şifreniz en az 6 benzersiz karakter içermelidir.', 'vi': 'Mật khẩu của bạn phải chứa ít nhất 6 ký tự khác nhau.', 'cs': 'Vaše heslo musí obsahovat alespoň 6 jedinečných znaků.', 'sv': 'Ditt lösenord måste innehålla minst 6 unika tecken.', 'fi': 'Salasanasi tulee sisältää vähintään 6 yksilöllistä merkkiä.', 'hu': 'A jelszónak legalább 6 egyedi karaktert kell tartalmaznia.', 'th': 'รหัสผ่านของคุณต้องมีอักขระที่ไม่ซ้ำกันอย่างน้อย 6 ตัว', 'el': 'Ο κωδικός πρόσβασής σας πρέπει να περιέχει τουλάχιστον 6 μοναδικούς χαρακτήρες.', 'ms': 'Kata laluan anda mesti mengandungi sekurang-kurangnya 6 aksara unik.', 'sr': 'Ваша лозинка мора садржати најмање 6 јединствених знакова.', 'ro': 'Parola dvs. trebuie să conțină cel puțin 6 caractere unice.', 'bn': 'আপনার পাসওয়ার্ডে কমপক্ষে 6টি স্বতন্ত্র অক্ষর থাকতে হবে।', 'ca': 'La teva contrasenya ha de contenir almenys 6 caràcters únics.', 'no': 'Passordet ditt må inneholde minst 6 unike tegn.', 'bg': 'Вашата парола трябва да съдържа поне 6 уникални символа.', 'da': 'Din adgangskode skal indeholde mindst 6 unikke tegn.', 'sk': 'Vaše heslo musí obsahovať aspoň 6 jedinečných znakov.', 'hi': 'आपके पासवर्ड में कम से कम 6 अलग-अलग वर्ण होने चाहिए।', 'et': 'Teie parool peab sisaldama vähemalt 6 unikaalset tähemärki.', 'hr': 'Vaša lozinka mora sadržavati najmanje 6 jedinstvenih znakova.', 'az': 'Şifrəniz ən azı 6 fərqli simvol içərməlidir.', 'zh-yue': '你嘅密碼必須至少有 6 個獨特嘅字符。', 'lt': 'Jūsų slaptažodyje turi būti bent 6 skirtingi simboliai.', 'sl': 'Vaše geslo mora vsebovati vsaj 6 različnih znakov.', 'eu': 'Zure pasahitzak gutxienez 6 karaktere desberdin izan behar ditu.', 'hy': 'Ձեր գաղտնաբառը պետք է պարունակի առնվազն 6 եզակի նիշ։', 'uz': "Parolingizda kamida 6 ta noyob belgi bo'lishi kerak.", 'ta': 'உங்கள் கடவுச்சொல்லில் குறைந்தது 6 தனித்துவமான எழுத்துக்கள் இருக்க வேண்டும்.', 'lv': 'Jūsu parolei jāsatur vismaz 6 unikālas rakstzīmes.'}
            _this_username_is_already_taken_error_message_dict = {'en': 'This username is already taken.', 'fr': 'Ce nom d’utilisateur est déjà pris.', 'de': 'Dieser Benutzername ist bereits vergeben.', 'es': 'Este nombre de usuario ya está en uso.', 'pt': 'Este nome de utilizador já foi utilizado.', 'it': 'Questo nome utente è già stato scelto.', 'nl': 'Deze gebruikersnaam is al in gebruik.', 'ja': 'このユーザー名はすでに使用されています。', 'ru': 'Это имя пользователя уже занято.', 'zh': '該用戶名已被佔用。', 'pl': 'Ta nazwa użytkownika jest już zajęta.', 'fa': 'این نام کاربری قبلاً گرفته شده است.', 'he': 'שם המשתמש/ת הזה כבר תפוס.', 'ko': '이 사용자명은 이미 사용 중입니다.', 'ar': 'اسم المستخدم هذا مأخوذ بالفعل.', 'id': 'Nama pengguna ini sudah dipakai.', 'uk': "Це ім'я користувача вже зайняте.", 'tr': 'Bu kullanıcı adı zaten alınmış.', 'vi': 'Tên người dùng này đã được sử dụng.', 'cs': 'Toto uživatelské jméno je již obsazeno.', 'sv': 'Det här användarnamnet är redan taget.', 'fi': 'Tämä käyttäjänimi on jo varattu.', 'hu': 'Ez a felhasználónév már foglalt.', 'th': 'ชื่อผู้ใช้นี้ถูกใช้แล้ว', 'el': 'Αυτό το όνομα χρήστη χρησιμοποιείται ήδη.', 'ms': 'Nama pengguna ini telah pun diambil.', 'sr': 'Ово корисничко име је већ заузето.', 'ro': 'Acest nume de utilizator este deja folosit.', 'bn': 'এই ব্যবহারকারীর নামটি ইতিমধ্যেই নেওয়া হয়ে গেছে।', 'ca': "Aquest nom d'usuari ja està pres.", 'no': 'Dette brukernavnet er allerede tatt.', 'bg': 'Това потребителско име вече е заето.', 'da': 'Dette brugernavn er allerede taget.', 'sk': 'Toto používateľské meno je už obsadené.', 'hi': 'यह उपयोगकर्ता नाम पहले ही ले लिया है।', 'et': 'See kasutajanimi on juba hõivatud.', 'hr': 'Ovo korisničko ime je već zauzeto.', 'az': 'Bu istifadəçi adı artıq götürülüb.', 'zh-yue': '這個使用者名稱已被佔用。', 'lt': 'Šis naudotojo vardas jau užimtas.', 'sl': 'To uporabniško ime je že zasedeno.', 'eu': 'Erabiltzaile-izen hau jada hartuta dago.', 'hy': 'Այս օգտանունն արդեն օգտագործվում է։', 'uz': 'Bu foydalanuvchi nomi allaqachon band.', 'ta': 'இந்த பயனர் பெயர் ஏற்கனவே எடுக்கப்பட்டுள்ளது.', 'lv': 'Šis lietotājvārds jau ir aizņemts.'}
            _enter_a_valid_email_address_error_message_dict = {'en': 'Enter a valid email address.', 'fr': 'Saisissez une adresse de courriel valide.', 'de': 'Bitte gültige E-Mail-Adresse eingeben.', 'es': 'Introduzca una dirección de correo electrónico válida.', 'pt': 'Introduza um endereço de e-mail válido.', 'it': 'Inserisci un indirizzo email valido.', 'nl': 'Voer een geldig e-mailadres in.', 'ja': '有効な電子メール アドレスを入力してください。', 'ru': 'Введите действительный адрес электронной почты.', 'zh': '輸入有效的電子郵件地址。', 'pl': 'Wpisz prawidłowy adres e-mail.', 'fa': 'یک آدرس ایمیل معتبر وارد کنید.', 'he': 'נא להזין כתובת דואר אלקטרוני חוקית.', 'ko': '올바른 이메일 주소를 입력하세요.', 'ar': 'أدخل عنوان بريد إلكتروني صالحًا.', 'id': 'Masukkan alamat email yang valid.', 'uk': 'Введіть дійсну адресу електронної пошти.', 'tr': 'Geçerli bir e-posta adresi girin.', 'vi': 'Vui lòng nhập địa chỉ email hợp lệ.', 'cs': 'Zadejte platnou e-mailovou adresu.', 'sv': 'Fyll i en giltig e-postadress.', 'fi': 'Syötä kelvollinen sähköpostiosoite.', 'hu': 'Adjon meg egy érvényes e-mail címet.', 'th': 'ป้อนที่อยู่อีเมลที่ถูกต้อง', 'el': 'Εισάγετε μια έγκυρη διεύθυνση ηλεκτρονικού ταχυδρομείου.', 'ms': 'Masukkan alamat e-mel yang sah.', 'sr': 'Унесите важећу адресу е-поште.', 'ro': 'Introduceți o adresă de e-mail validă.', 'bn': 'একটি বৈধ ইমেল ঠিকানা লিখুন।', 'ca': 'Introduïu una adreça de correu electrònic vàlida.', 'no': 'Skriv inn en gyldig e-postadresse.', 'bg': 'Въведете валиден имейл адрес.', 'da': 'Indtast en gyldig e-mailadresse.', 'sk': 'Zadajte platnú e-mailovú adresu.', 'hi': 'एक मान्य ईईमेल पता दर्ज करें।', 'et': 'Sisestage kehtiv e-posti aadress.', 'hr': 'Unesite valjanu adresu e-pošte.', 'az': 'Düzgün e-poçt ünvanı daxil edin.', 'zh-yue': '請輸入有效的電郵地址。', 'lt': 'Įveskite teisingą el. pašto adresą.', 'sl': 'Vnesite veljaven e-poštni naslov.', 'eu': 'Sartu baliozko helbide elektroniko bat.', 'hy': 'Մուտքագրեք վավեր էլփոստի հասցե։', 'uz': 'Yaroqli elektron pochta manzilini kiriting.', 'ta': 'செல்லுபடியாகும் மின்னஞ்சல் முகவரியை உள்ளிடவும்.', 'lv': 'Ievadiet derīgu e-pasta adresi.'}
            _this_email_is_already_in_use_error_message_dict = {'en': 'This email is already in use.', 'fr': 'Cet e-mail est déjà utilisé.', 'de': 'Diese E-Mail wird bereits verwendet.', 'es': 'Este correo electrónico ya está en uso.', 'pt': 'Este e-mail já foi utilizado.', 'it': 'Questo indirizzo e-mail è già in uso.', 'nl': 'Deze email is al in gebruik.', 'ja': 'このメールはすでに使用されています。', 'ru': 'Этот адрес электронной почты уже используется.', 'zh': '該電子郵件已被使用。', 'pl': 'Ten adres e-mail jest już używany.', 'fa': 'این ایمیل در حال حاضر در حال استفاده است.', 'he': 'הדואר האלקטרוני הזה כבר נמצא בשימוש.', 'ko': '이 이메일은 이미 사용 중입니다.', 'ar': 'هذا البريد الإلكتروني قيد الاستخدام بالفعل.', 'id': 'Email ini sudah digunakan.', 'uk': 'Ця електронна адреса вже використовується.', 'tr': 'Bu e-posta zaten kullanılıyor.', 'vi': 'Địa chỉ email này hiện đang được sử dụng.', 'cs': 'Tento e-mail se již používá.', 'sv': 'Detta e-postmeddelande används redan.', 'fi': 'Tämä sähköpostiosoite on jo käytössä.', 'hu': 'Ez az e-mail cím már használatban van.', 'th': 'อีเมลนี้มีการใช้งานแล้ว', 'el': 'Αυτή η διεύθυνση ηλεκτρονικού ταχυδρομείου χρησιμοποιείται ήδη.', 'ms': 'E-mel ini sudah digunakan.', 'sr': 'Ова адреса е-поште је већ у употреби.', 'ro': 'Această adresă de e-mail este deja utilizată.', 'bn': 'এই ইমেলটি ইতিমধ্যেই ব্যবহৃত হচ্ছে।', 'ca': 'Aquest correu electrònic ja està en ús.', 'no': 'Denne e-postadressen er allerede i bruk.', 'bg': 'Този имейл адрес вече се използва.', 'da': 'Denne e-mail er allerede i brug.', 'sk': 'Tento e-mail sa už používa.', 'hi': 'यह ईमेल पहले से ही उपयोग में है।', 'et': 'See e-posti aadress on juba kasutusel.', 'hr': 'Ova adresa e-pošte već se koristi.', 'az': 'Bu e-poçt artıq istifadə olunur.', 'zh-yue': '此郵箱已被佔用。', 'lt': 'Šis el. pašto adresas jau naudojamas.', 'sl': 'Ta e-pošta je že v uporabi.', 'eu': 'Helbide elektroniko hau jada erabiltzen ari da.', 'hy': 'Այս էլփոստն արդեն օգտագործվում է։', 'uz': 'Bu elektron pochta allaqachon ishlatilmoqda.', 'ta': 'இந்த மின்னஞ்சல் ஏற்கனவே பயன்படுத்தப்படுகிறது.', 'lv': 'Šī e-pasta adrese jau tiek izmantota.'}
            _enter_a_valid_date_error_message_dict = {'en': 'Enter a valid date.', 'fr': 'Saisissez une date valide.', 'de': 'Bitte ein gültiges Datum eingeben.', 'es': 'Introduzca una fecha válida.', 'pt': 'Introduza uma data válida.', 'it': 'Inserisci una data valida.', 'nl': 'Voer een geldige datum in.', 'ja': '有効な日付を入力してください。', 'ru': 'Введите действительную дату.', 'zh': '輸入有效日期。', 'pl': 'Wprowadź prawidłową datę.', 'fa': 'تاریخ معتبری وارد کنید', 'he': 'יש להזין תאריך חוקי.', 'ko': '올바른 날짜를 입력하세요.', 'ar': 'أدخل تاريخًا صالحًا.', 'id': 'Masukkan tanggal yang valid.', 'uk': 'Введіть дійсну дату.', 'tr': 'Geçerli bir tarih girin.', 'vi': 'Nhập ngày tháng hợp lệ.', 'cs': 'Zadejte platné datum.', 'sv': 'Fyll i ett giltigt datum.', 'fi': 'Syötä oikea päivämäärä.', 'hu': 'Adjon meg egy érvényes dátumot.', 'th': 'ป้อนวันที่ที่ถูกต้อง', 'el': 'Εισάγετε μια έγκυρη ημερομηνία.', 'ms': 'Masukkan tarikh yang sah.', 'sr': 'Унесите важећи датум.', 'ro': 'Introduceți o dată validă.', 'bn': 'একটি বৈধ তারিখ লিখুন।', 'ca': 'Introduïu una data vàlida.', 'no': 'Angi en gyldig dato.', 'bg': 'Въведете валидна дата.', 'da': 'Indtast en gyldig dato.', 'sk': 'Zadajte platný dátum.', 'hi': 'एक मान्य तिथि दर्ज करें।', 'et': 'Sisestage kehtiv kuupäev.', 'hr': 'Unesite važeći datum.', 'az': 'Düzgün tarix daxil edin.', 'zh-yue': '請輸入有效日期。', 'lt': 'Įveskite tinkamą datą.', 'sl': 'Vnesite veljaven datum.', 'eu': 'Sartu baliozko data bat.', 'hy': 'Մուտքագրեք ճիշտ ամսաթիվ։', 'uz': 'Yaroqli sanani kiriting.', 'ta': 'செல்லுபடியாகும் தேதியை உள்ளிடவும்.', 'lv': 'Ievadiet derīgu datumu.'}
            _please_enter_a_correct_username_and_password_error_message_dict = {'en': 'Please enter a correct username and password. Note that both fields may be case-sensitive.', 'fr': 'Saisissez un nom d’utilisateur et un mot de passe valides. Remarquez que chacun de ces champs est sensible à la casse (différenciation des majuscules/minuscules).', 'de': 'Bitte Benutzername und Passwort eingeben. Beide Felder berücksichtigen die Groß-/Kleinschreibung.', 'es': 'Por favor, introduzca un nombre de usuario y clave correctos. Observe que ambos campos pueden ser sensibles a mayúsculas.', 'pt': 'Por favor introduza o nome do utilizador e password corretos. Tenha em atenção às maiúsculas e minúsculas.', 'it': 'Inserisci nome utente e password corretti. In entrambi i campi le maiuscole potrebbero essere significative.', 'nl': 'Voer een juiste gebruikersnaam en wachtwoord in. Let op dat beide velden hoofdlettergevoelig zijn.', 'ja': '正しいユーザー名とパスワードを入力してください。両方のフィールドでは大文字と小文字が区別される場合があることに注意してください。', 'ru': 'Пожалуйста, введите правильный имя пользователя и пароль. Обратите внимание, что оба поля могут быть чувствительны к регистру.', 'zh': '請輸入正確的使用者名稱以及密碼。請注意，這兩個欄位都區分大小寫。', 'pl': 'Wprowadź poprawną nazwę użytkownika i hasło. Pamiętaj, że w obu polach rozróżniana jest wielkość liter.', 'fa': 'لطفاً نام کاربری و گذرواژهٔ درست را وارد کنید. توجه داشته باشید که در هر دو فیلد ممکن است حروف کوچک و بزرگ تفاوت داشته باشند.', 'he': 'נא להזין שם משתמש/ת וסיסמה נכונים. נא לשים לב כי שני השדות רגישים לאותיות גדולות/קטנות.', 'ko': '올바른 사용자명와/과 비밀번호를 입력하십시오. 두 필드 모두 대문자와 소문자를 구별합니다.', 'ar': 'يرجى إدخال اسم مستخدم وكلمة مرور صحيحين. لاحظ أن كلا الحقلين قد يكونان حساسين لحالة الأحرف.', 'id': 'Masukkan nama pengguna dan kata sandi yang benar. Perhatikan bahwa kedua kolom mungkin peka huruf besar/kecil.', 'uk': 'Будь ласка, введіть правильні ім’я користувача та пароль. Зверніть увагу, що в обох полях може враховуватися регістр.', 'tr': 'Lütfen doğru kullanıcı adını ve parolayı girin. Her iki alanın da büyük/küçük harfe duyarlı olabileceğini unutmayın.', 'vi': 'Vui lòng nhập đúng tên người dùng và mật khẩu. Lưu ý rằng cả hai trường đều có thể phân biệt chữ hoa chữ thường.', 'cs': 'Zadejte prosím správné uživatelské jméno a heslo. Všimněte si, že obě pole mohou rozlišovat malá a velká písmena.', 'sv': 'Ange ett korrekt användarnamn och lösenord. Observera att båda fälten är skiftlägeskänsliga.', 'fi': 'Ole hyvä ja syötä kelvollinen käyttäjänimi ja salasana. Huomaa että kummassakin kentässä isoilla ja pienillä kirjaimilla saattaa olla merkitystä.', 'hu': 'Kérjük, adjon meg egy helyes username és jelszó párost. Vegye figyelembe, hogy mindkét mező megkülönböztetheti a kis- és nagybetűket.', 'th': 'กรุณากรอก username และรหัสผ่านที่ถูกต้อง โปรดทราบว่าทั้งสองช่องอาจคำนึงถึงตัวพิมพ์เล็กและตัวพิมพ์ใหญ่', 'el': 'Παρακαλώ εισάγετε ένα σωστό username και κωδικό πρόσβασης. Σημειώστε ότι και στα δύο πεδία μπορεί να γίνεται διάκριση μεταξύ κεφαλαίων και μικρών γραμμάτων.', 'ms': 'Sila masukkan nama pengguna dan kata laluan yang betul. Ambil perhatian bahawa kedua-dua medan mungkin sensitif huruf besar.', 'sr': 'Молимо унесите исправно корисничко име и лозинку. Имајте на уму да оба поља могу бити осетљива на велика и мала слова.', 'ro': 'Vă rugăm să introduceți o nume de utilizator și o parolă corecte. Rețineți că ambele câmpuri pot fi sensibile la majuscule.', 'bn': 'অনুগ্রহ করে একটি সঠিক username এবং পাসওয়ার্ড লিখুন। উল্লেখ্য যে, উভয় ফিল্ডই কেস-সেনসিটিভ হতে পারে।', 'ca': "Introdueix un nom d'usuari i una contrasenya correctes. Tingues en compte que tots dos camps poden distingir entre majúscules i minúscules.", 'no': 'Vennligst skriv inn riktig username og passord. Merk at begge feltene kan skille mellom store og små bokstaver.', 'bg': 'Моля, въведете правилен потребителско име и парола. Имайте предвид, че и двете полета може да са чувствителни към малки и големи букви.', 'da': 'Indtast venligst en korrekt username og adgangskode. Bemærk, at begge felter kan skelne mellem store og små bogstaver.', 'sk': 'Zadajte správne používateľské meno a heslo. Upozorňujeme, že obe polia môžu rozlišovať malé a veľké písmená.', 'hi': 'कृपया सही मान दर्ज करें username और पासवर्ड। ध्यान दें कि दोनों फ़ील्ड केस-सेंसिटिव हो सकते हैं।', 'et': 'Sisestage õige username ja parool. Pange tähele, et mõlemad väljad võivad olla tõstutundlikud.', 'hr': 'Unesite ispravan username i lozinku. Imajte na umu da oba polja mogu biti osjetljiva na velika i mala slova.', 'az': 'Lütfən, düzgün istifadəçi adı və şifrəni daxil edin. Hər iki sahənin böyük-kiçik hərflərə həssas ola biləcəyini nəzərə alın.', 'zh-yue': '請輸入正確的使用者名稱以及密碼。請注意，這兩個欄位都區分大小寫。', 'lt': 'Įveskite teisingą username ir slaptažodį. Atkreipkite dėmesį, kad abiejuose laukuose gali būti skiriamos didžiosios ir mažosios raidės.', 'sl': 'Prosimo, vnesite pravilna podatka username in geslo. Upoštevajte, da sta obe polji lahko občutljivi na velike in male črke.', 'eu': 'Mesedez, sartu username eta pasahitz zuzena. Kontuan izan bi eremuetan maiuskulak eta minuskulak bereiz daitezkeela.', 'hy': 'Մուտքագրեք ճիշտ username և գաղտնաբառ։ Երկու դաշտերն էլ կարող են տարբերակել մեծատառերը և փոքրատառերը։', 'uz': "Iltimos, to'g'ri username va parolni kiriting. Ikkala maydon ham katta-kichik harflarga sezgir bo'lishi mumkinligini unutmang.", 'ta': 'தயவுசெய்து சரியான username மற்றும் கடவுச்சொல்லை உள்ளிடவும். இரு புலங்களும் வழக்கு உணர்திறன் கொண்டதாக இருக்கலாம் என்பதை நினைவில் கொள்க.', 'lv': 'Lūdzu, ievadiet pareizu username un paroli. Ņemiet vērā, ka abos laukos tiek ņemti vērā lielie un mazie burti.'}
            _your_old_password_was_entered_incorrectly_error_message_dict = {'en': 'Your old password was entered incorrectly. Please enter it again.', 'fr': 'Votre ancien mot de passe est incorrect. Veuillez le rectifier.', 'de': 'Das alte Passwort war falsch. Bitte neu eingeben.', 'es': 'Su contraseña antigua es incorrecta. Por favor, vuelva a introducirla. ', 'pt': 'A sua palavra-passe antiga foi introduzida incorretamente. Por favor tente novamente.', 'it': 'La password attuale non è stata inserita correttamente. Riprova per favore.', 'nl': 'Uw oude wachtwoord is niet juist ingevoerd. Voer het opnieuw in.', 'ja': '元のパスワードが間違っています。もう一度入力してください。', 'ru': 'Ваш старый пароль введен неправильно. Пожалуйста, введите его снова.', 'zh': '你的舊密碼不正確。請重新輸入。', 'pl': 'Podane stare hasło jest niepoprawne. Proszę podać je jeszcze raz.', 'fa': 'گذرواژهٔ قدیمی\u200cتان اشتباه وارد شد. لطفاً دوباره وارد کنید.', 'he': 'סיסמתך הישנה הוזנה בצורה שגויה. נא להזינה שוב.', 'ko': '기존 비밀번호를 잘못 입력하셨습니다. 다시 입력해 주세요.', 'ar': 'كلمة مرورك القديمة غير صحيحة. رجاءً أدخلها مرة أخرى.', 'id': 'Sandi lama Anda yang dimasukkan salah. Masukkan sekali lagi.', 'uk': 'Старий пароль було введено неправильно. Будь ласка, введіть його знову.', 'tr': 'Eski parolanız yanlış girildi. Lütfen tekrar girin.', 'vi': 'Mật khẩu cũ không chính xác. Hãy nhập lại lần nữa', 'cs': 'Vaše současné heslo nebylo zadáno správně. Zkuste to znovu.', 'sv': 'Ditt gamla lösenord var felaktigt ifyllt. Fyll i det igen.', 'fi': 'Vanha salasana on virheellinen. Yritä uudelleen.', 'hu': 'A régi jelszó hibásan lett megadva. Írja be újra.', 'th': 'ใส่รหัสผ่านเก่าผิด กรุณาใส่รหัสผ่านอีกครั้ง', 'el': 'Το παλιό συνθηματικό σας δόθηκε λανθασμένα. Παρακαλώ δοκιμάστε ξανά.', 'ms': 'Kata laluan lama anda tidak dimasukkan dengan betul. Sila masukkan sekali lagi.', 'sr': 'Ваша стара лознка није правилно унесена. Унесите је поново.', 'ro': 'Parola veche a fost introdusă greșit. Introduceți-o din nou.', 'bn': 'আপনার পুরনো পাসওয়ার্ড ঠিকভাবে প্রবেশ করানো হয়নি। অনুগ্রহপূর্বক সঠিক পাসওয়ার্ড দিন।', 'ca': 'La vostra antiga contrasenya no és correcta. Si us plau, introduïu-la de nou.', 'no': 'Ditt gamle passord er galt. Vennligst prøv igjen.', 'bg': 'Въвели сте погрешна стара парола. Въведете я отново.  ', 'da': 'Din gamle adgangskode blev ikke indtastet korrekt. Indtast den venligst igen.', 'sk': 'Nezadali ste správne svoje staré heslo. Napíšte ho znovu, prosím.', 'hi': 'आपने पुराना शब्दकूट गलत दर्ज किया है । कृपया फिर से दर्ज करें', 'et': 'Te sisestasite oma vana parooli vigaselt. Palun sisestage see uuesti.', 'hr': 'Vaša stara lozinka je pogrešno unesena. Unesite je ponovo.', 'az': 'Köhnə şifrəni yanlış daxil etdiniz. Zəhmət olmasa bir daha yoxlayın.', 'zh-yue': '你的舊密碼不正確。請重新輸入。', 'lt': 'Blogai įvestas senas slaptažodis. Bandykite dar kartą.', 'sl': 'Vaše staro geslo ni vneseno pravilno. Poskusite znova.', 'eu': 'Zure pasahitz zaharra ez da zuzena. Idatzi ezazu berriro.', 'hy': 'Հին գաղտնաբառը սխալ է։ Մուտքագրեք նորից։', 'uz': "Sizning eski parolingiz noto'g'ri kiritilgan edi. Iltimos, qaytadan kiriting.", 'ta': 'உங்கள் பழைய கடவுச்சொல் தவறாக உள்ளிடப்பட்டது. தயவுசெய்து மீண்டும் உள்ளிடவும்.', 'lv': 'Tava iepriekšējā parole tika ievadīta nepareizi. Lūgums ievadīt to vēlreiz.'}
            _the_two_password_fields_didnt_match_error_message_dict = {'en': 'The two password fields didn’t match.', 'fr': 'Les deux mots de passe ne correspondent pas.', 'de': 'Die beiden Passwörter sind nicht identisch.', 'es': 'Los dos campos de contraseña no coinciden.', 'pt': 'As duas palavra-passe não coincidem.', 'it': 'I due campi password non corrispondono.', 'nl': 'De twee wachtwoordvelden komen niet overeen.', 'ja': '確認用パスワードが一致しません。', 'ru': 'Введенные пароли не совпадают.', 'zh': '輸入的兩個密碼不一致。', 'pl': 'Hasła w obu polach nie są zgodne.', 'fa': 'دو فیلد گذرواژه با هم مطابقت ندارند.', 'he': 'שני שדות הסיסמה אינם זהים.', 'ko': '비밀번호가 일치하지 않습니다.', 'ar': 'حقلا كلمة المرور غير متطابقين.', 'id': 'Dua bidang sandi tidak cocok.', 'uk': 'Паролі не збігаються', 'tr': 'İki parola alanı eşleşmedi.', 'vi': 'Hai trường mật khẩu không giống nhau.', 'cs': 'Hesla se neshodují.', 'sv': 'De två lösenordsfälten stämmer inte överens.', 'fi': 'Salasanakentät eivät täsmänneet.', 'hu': 'A beírt két jelszó nem egyezik.', 'th': 'ช่องรหัสผ่านทั้งสองช่องไม่ตรงกัน', 'el': 'Τα δύο πεδία κωδικών δεν ταιριάζουν.', 'ms': 'Medan kedua-dua kata laluan tidak sepadan.', 'sr': 'Два поља за лозинке се не поклапају.', 'ro': 'Cele două parole nu corespund.', 'bn': 'The two password fields didn’t match.', 'ca': 'Els dos camps de contrasenya no coincideixen.', 'no': 'De to passordfeltene er ikke like.', 'bg': 'Двете полета за паролата не съвпадат.  ', 'da': 'De to adgangskoder var ikke identiske.', 'sk': 'Heslo a jeho potvrdenie sa nezhodujú.', 'hi': 'The two password fields didn’t match.', 'et': 'Sisestatud paroolid polnud identsed.', 'hr': 'Polja lozinki se ne poklapaju.', 'az': 'Şifrə xanalarının dəyərləri eyni deyil.', 'zh-yue': '輸入的兩個密碼不一致。', 'lt': 'Šie du slaptažodžiai nesutampa.', 'sl': 'Polji za geslo se nista ujemali.', 'eu': 'Bi pasahitzak ez datoz bat.', 'hy': 'Երկու գաղտնաբառի դաշտերը չեն համընկնում։', 'uz': 'Ikkala parol maydoni bir-biriga mos kelmadi.', 'ta': 'இரண்டு கடவுச்சொல் புலங்களும் பொருந்தவில்லை.', 'lv': 'Paroles lauki nesakrita.'}
            _entity_username_must_start_with_4_or_more_letters_error_message_dict = {'en': 'Username must start with 4 or more letters, and may contain letters, digits or dashes.', 'fr': 'Le nom d’utilisateur doit commencer par 4 lettres ou plus et peut contenir des lettres, des chiffres ou des tirets.', 'de': 'Der Benutzername muss mit 4 oder mehr Buchstaben beginnen und kann Buchstaben, Ziffern oder Bindestriche enthalten.', 'es': 'El nombre de usuario debe comenzar con 4 o más letras y puede contener letras, dígitos o guiones.', 'pt': 'O nome do utilizador deve começar com 4 ou mais letras e pode conter letras, dígitos ou traços.', 'it': 'Il nome utente deve iniziare con 4 o più caratteri e può contenere lettere, cifre o trattini.', 'nl': 'De gebruikersnaam moet beginnen met 4 of meer letters en mag letters, cijfers of streepjes bevatten.', 'ja': 'ユーザー名は 4 文字以上で始まる必要があり、文字、数字、またはダッシュを含めることができます。', 'ru': 'Имя пользователя должно начинаться с 4 или более букв и может содержать буквы, цифры или тире.', 'zh': '使用者名稱必須以 4 個或更多字母開頭，並且可以包含字母、數字或連字號。', 'pl': 'Nazwa użytkownika musi zaczynać się od 4 lub więcej liter i może zawierać litery, cyfry lub myślniki.', 'fa': 'نام کاربری باید با 4 حرف یا بیشتر شروع شود و ممکن است دارای حروف، اعداد یا خط تیره باشد.', 'he': 'שם המשתמש/ת חייב להתחיל עם 4 אותיות או יותר, ויכול להכיל אותיות, ספרות או מקפים. שם המשתמש/ת חייב להיות באנגלית.', 'ko': '사용자명은 4글자 이상으로 시작되어야 하며, 글자, 숫자 또는 대시를 포함할 수 있습니다.', 'ar': 'يجب أن يبدأ اسم المستخدم بأربعة أحرف أو أكثر، ويمكن أن يحتوي على أحرف أو أرقام أو شرطات.', 'id': 'Nama pengguna harus dimulai dengan 4 huruf atau lebih, dan dapat berisi huruf, angka, atau tanda hubung.', 'uk': "Ім'я користувача має починатися з 4 або більше літер і може містити літери, цифри або тире.", 'tr': 'Kullanıcı adı 4 veya daha fazla harfle başlamalıdır ve harf, rakam veya tire içerebilir.', 'vi': 'Tên người dùng phải bắt đầu bằng 4 chữ cái trở lên và có thể chứa chữ cái, chữ số hoặc dấu gạch ngang.', 'cs': 'Uživatelské jméno musí začínat 4 nebo více písmeny a může obsahovat písmena, číslice nebo pomlčky.', 'sv': 'Username måste börja med 4 eller fler bokstäver och kan innehålla bokstäver, siffror eller bindestreck.', 'fi': 'Käyttäjätunnuksen on alettava 4 tai useammalla kirjaimella, ja se voi sisältää kirjaimia, numeroita tai väliviivoja.', 'hu': 'A felhasználónévnek 4 vagy több betűvel kell kezdődnie, és tartalmazhat betűket, számokat vagy kötőjeleket.', 'th': 'ชื่อผู้ใช้ต้องขึ้นต้นด้วยตัวอักษร 4 ตัวขึ้นไป และอาจมีตัวอักษร ตัวเลข หรือขีดกลาง', 'el': 'Το όνομα χρήστη πρέπει να ξεκινά με 4 ή περισσότερα γράμματα και μπορεί να περιέχει γράμματα, ψηφία ή παύλες.', 'ms': 'Nama pengguna mesti bermula dengan 4 atau lebih huruf dan mungkin mengandungi huruf, angka atau sempang.', 'sr': 'Корисничко име мора да почиње са 4 или више слова и може да садржи слова, цифре или цртице.', 'ro': 'Numele de utilizator trebuie să înceapă cu 4 sau mai multe litere și poate conține litere, cifre sau liniuțe.', 'bn': 'ব্যবহারকারীর নাম অবশ্যই ৪ বা তার বেশি অক্ষর দিয়ে শুরু হতে হবে এবং এতে অক্ষর, সংখ্যা বা ড্যাশ থাকতে পারে।', 'ca': "El nom d'usuari ha de començar amb 4 lletres o més i pot contenir lletres, dígits o guions.", 'no': 'Brukernavn må begynne med 4 eller flere bokstaver, og kan inneholde bokstaver, sifre eller bindestreker.', 'bg': 'Потребителското име трябва да започва с 4 или повече букви и може да съдържа букви, цифри или тирета.', 'da': 'Brugernavn skal starte med 4 eller flere bogstaver og kan indeholde bogstaver, cifre eller bindestreger.', 'sk': 'Používateľské meno musí začínať 4 alebo viacerými písmenami a môže obsahovať písmená, číslice alebo pomlčky.', 'hi': 'उपयोगकर्ता नाम 4 या अधिक अक्षरों से शुरू होना चाहिए, और इसमें अक्षर, अंक या डैश शामिल हो सकते हैं।', 'et': 'Kasutajanimi peab algama 4 või enama tähega ja võib sisaldada tähti, numbreid või sidekriipse.', 'hr': 'Korisničko ime mora započeti s 4 ili više slova, a može sadržavati slova, znamenke ili crtice.', 'az': 'İstifadəçi adı 4 və ya daha çox hərflə başlamalı və hərf, rəqəm və ya tire içərə bilər.', 'zh-yue': '使用者名稱必須以 4 個或更多字母開頭，並且可以包含字母、數字或連字號。', 'lt': 'Naudotojo vardas turi prasidėti 4 ar daugiau raidžių ir gali turėti raidžių, skaitmenų arba brūkšnelių.', 'sl': 'Uporabniško ime se mora začeti s 4 ali več črkami in lahko vsebuje črke, številke ali pomišljaje.', 'eu': 'Erabiltzaile-izenak 4 letra edo gehiagoz hasi behar du, eta letrak, digituak edo marratxoak izan ditzake.', 'hy': 'Օգտանունը պետք է սկսվի 4 կամ ավելի տառով և կարող է պարունակել տառեր, թվանշաններ կամ գծիկներ։', 'uz': "Foydalanuvchi nomi 4 yoki undan ortiq harf bilan boshlanishi kerak va harflar, raqamlar yoki tirelardan iborat bo'lishi mumkin.", 'ta': 'பயனர்பெயர் 4 அல்லது அதற்கு மேற்பட்ட எழுத்துக்களுடன் தொடங்க வேண்டும், மேலும் எழுத்துக்கள், இலக்கங்கள் அல்லது துண்டுகளைக் கொண்டிருக்கலாம்.', 'lv': 'Lietotājvārdam jāsākas ar 4 vai vairāk burtiem, un tas var saturēt burtus, ciparus vai domuzīmes.'}
            _user_username_must_start_with_4_or_more_letters_error_message_dict = {'en': 'Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.', 'fr': 'Le nom d’utilisateur doit commencer par 4 lettres ou plus, suivies d’un nombre quelconque de chiffres. Vous pouvez ajouter des tirets entre les mots.', 'de': 'Der Benutzername muss mit 4 oder mehr Buchstaben beginnen. Danach können Zahlen auftreten. Sie können Bindestriche zwischen die Wörter einfügen.', 'es': 'El nombre de usuario debe comenzar con 4 o más letras, después de las cuales puede haber cualquier número de dígitos. Puedes agregar guiones entre palabras.', 'pt': 'O nome do utilizador deve começar com 4 ou mais letras, após as quais pode haver qualquer número de dígitos. Podes adicionar traços entre as palavras.', 'it': 'Il nome utente deve iniziare con 4 o più caratteri, dopo i quali può essere inserito un numero qualsiasi di cifre. Puoi aggiungere trattini tra le parole.', 'nl': 'De gebruikersnaam moet beginnen met 4 of meer letters, met daarna een willekeurig aantal cijfers. Je kunt ook streepjes tussen woorden gebruiken.', 'ja': 'ユーザー名は 4 文字以上の文字で始まる必要があり、その後は任意の桁数にすることができます。単語の間にダッシュを追加できます。', 'ru': 'Имя пользователя должно начинаться с 4 и более букв, после которых может быть любое количество цифр. Между словами можно ставить тире.', 'zh': '使用者名稱必須以 4 個或更多字母開頭，後面可以是任意位數的數字。您可以在單字之間加上破折號。', 'pl': 'Nazwa użytkownika musi zaczynać się od 4 lub więcej liter, po których może nastąpić dowolna liczba cyfr. Możesz dodać myślniki pomiędzy wyrazami.', 'fa': 'نام کاربری باید با 4 حرف یا بیشتر شروع شود که بعد از آن می تواند هر تعداد رقم باشد. می توانید بین کلمات خط تیره اضافه کنید.', 'he': 'שם המשתמש/ת חייב להתחיל עם 4 אותיות או יותר, לאחר מכן ניתן להוסיף מספר כלשהו של ספרות. ניתן להוסיף מקפים בין מילים. שם המשתמש/ת חייב להיות באנגלית.', 'ko': '사용자명은 4글자 이상으로 시작되어야 하며, 이후 숫자가 올 수 있습니다. 단어 사이에 대시를 추가할 수 있습니다.', 'ar': 'يجب أن يبدأ اسم المستخدم بـ 4 أحرف أو أكثر، وبعد ذلك يمكن أن يكون أي عدد من الأرقام. يمكنك إضافة شرطات بين الكلمات.', 'id': 'Nama pengguna harus diawali dengan 4 huruf atau lebih, setelah itu dapat berupa sejumlah digit. Anda dapat menambahkan tanda hubung di antara kata-kata.', 'uk': "Ім'я користувача має починатися з 4 або більше літер, після яких може бути будь-яка кількість цифр. Між словами можна додавати тире.", 'tr': 'Kullanıcı adı 4 veya daha fazla harfle başlamalıdır, sonrasında herhangi bir sayıda rakam olabilir. Kelimelerin arasına tire ekleyebilirsiniz.', 'vi': 'Tên người dùng phải bắt đầu bằng 4 chữ cái trở lên, sau đó có thể là bất kỳ số lượng chữ số nào. Bạn có thể thêm dấu gạch ngang giữa các từ.', 'cs': 'Uživatelské jméno musí začínat 4 nebo více písmeny, za nimiž může být libovolný počet číslic. Mezi slova můžete přidat pomlčky.', 'sv': 'Username måste börja med 4 eller fler bokstäver, varefter det kan vara valfritt antal siffror. Du kan lägga till bindestreck mellan ord.', 'fi': 'Käyttäjätunnuksen tulee alkaa 4 tai useammalla kirjaimella, jonka jälkeen voi olla mikä tahansa määrä numeroita. Voit lisätä väliviivoja sanojen väliin.', 'hu': 'A felhasználónévnek 4 vagy több betűvel kell kezdődnie, ami után tetszőleges számú számjegy állhat. A szavak közé kötőjelet is hozzáadhat.', 'th': 'ชื่อผู้ใช้ต้องขึ้นต้นด้วยตัวอักษร 4 ตัวขึ้นไป หลังจากนั้นอาจเป็นตัวเลขจำนวนเท่าใดก็ได้ คุณสามารถเพิ่มขีดกลางระหว่างคำได้', 'el': 'Το όνομα χρήστη πρέπει να ξεκινά με 4 ή περισσότερα γράμματα, μετά τα οποία μπορεί να ακολουθεί οποιοσδήποτε αριθμός ψηφίων. Μπορείτε να προσθέσετε παύλες μεταξύ των λέξεων.', 'ms': 'Nama pengguna mesti bermula dengan 4 atau lebih huruf, selepas itu boleh menjadi sebarang nombor digit. Anda boleh menambah sempang antara perkataan.', 'sr': 'Корисничко име мора да почиње са 4 или више слова, после којих може бити било који број цифара. Можете додати цртице између речи.', 'ro': 'Numele de utilizator trebuie să înceapă cu 4 sau mai multe litere, după care poate fi orice număr de cifre. Puteți adăuga liniuțe între cuvinte.', 'bn': 'ব্যবহারকারীর নাম অবশ্যই ৪ বা তার বেশি অক্ষর দিয়ে শুরু হতে হবে, যার পরে যেকোনো সংখ্যক সংখ্যা থাকতে পারে। শব্দগুলোর মধ্যে ড্যাশ যোগ করা যাবে।', 'ca': "El nom d'usuari ha de començar amb 4 o més lletres, després de les quals pot ser qualsevol nombre de dígits. Podeu afegir guions entre paraules.", 'no': 'Brukernavnet må begynne med 4 eller flere bokstaver, hvoretter det kan være et hvilket som helst antall sifre. Du kan legge til bindestreker mellom ord.', 'bg': 'Потребителското име трябва да започва с 4 или повече букви, след които може да има произволен брой цифри. Можете да добавяте тирета между думите.', 'da': 'Brugernavn skal starte med 4 eller flere bogstaver, hvorefter der kan være et vilkårligt antal cifre. Du kan tilføje bindestreger mellem ord.', 'sk': 'Používateľské meno musí začínať 4 alebo viacerými písmenami, po ktorých môže byť ľubovoľný počet číslic. Medzi slová môžete pridať pomlčky.', 'hi': 'उपयोगकर्ता नाम की शुरुआत 4 या उससे अधिक अक्षरों से होनी चाहिए, जिसके बाद कितने भी अंक हो सकते हैं। शब्दों के बीच डैश का उपयोग किया जा सकता है।', 'et': 'Kasutajanimi peab algama vähemalt 4 tähega, mille järel võib olla mis tahes arv numbreid. Sõnade vahele saab lisada sidekriipse.', 'hr': 'Korisničko ime mora započeti s 4 ili više slova, nakon čega može biti bilo koji broj znamenki. Između riječi možete dodati crtice.', 'az': 'İstifadəçi adı 4 və ya daha çox hərflə başlamalı, sonra istənilən sayda rəqəm gələ bilər. Sözlər arasında tire əlavə edə bilərsiniz.', 'zh-yue': '使用者名稱必須以至少 4 個字母開頭，後面可以跟著任意數量的數字。單字之間可以用短橫線隔開。', 'lt': 'Naudotojo vardas turi prasidėti 4 ar daugiau raidžių, po kurių gali eiti bet koks skaitmenų skaičius. Tarp žodžių galite įterpti brūkšnelius.', 'sl': 'Uporabniško ime se mora začeti s 4 ali več črkami, nato pa lahko vsebuje poljubno število številk. Med besede lahko dodate pomišljaje.', 'eu': 'Erabiltzaile-izenak 4 letra edo gehiagoz hasi behar du; ondoren, nahi adina digitu izan ditzake. Hitz artean marratxoak gehi ditzakezu.', 'hy': 'Օգտանունը պետք է սկսվի 4 կամ ավելի տառով, որից հետո կարող է լինել ցանկացած քանակի թվանշան։ Կարող եք բառերի միջև գծիկներ ավելացնել։', 'uz': "Foydalanuvchi nomi 4 yoki undan ortiq harf bilan boshlanishi kerak, undan keyin istalgan miqdordagi raqamlar bo'lishi mumkin. So'zlar orasiga tire qo'yishingiz mumkin.", 'ta': 'பயனர்பெயர் 4 அல்லது அதற்கு மேற்பட்ட எழுத்துக்களுடன் தொடங்க வேண்டும், அதன் பிறகு எந்த எண்ணிக்கையிலான இலக்கங்களும் இருக்கலாம். நீங்கள் வார்த்தைகளுக்கு இடையில் துண்டுகளைச் சேர்க்கலாம்.', 'lv': 'Lietotājvārdam jāsākas ar 4 vai vairāk burtiem; pēc tam tajā var būt jebkāds ciparu skaits. Starp vārdiem var pievienot domuzīmes.'}
            _slug_does_not_parse_to_username_error_message_dict = {'en': 'Slug does not parse to username.', 'fr': 'Slug ne correspond pas à un nom d’utilisateur.', 'de': 'Slug wird nicht in Benutzername umgewandelt.', 'es': 'Slug no analiza el nombre de usuario.', 'pt': 'O slug não pode ser usado como nome de utilizador.', 'it': 'Lo slug non viene analizzato come nome utente.', 'nl': 'Slug parseert niet naar gebruikersnaam.', 'ja': 'Slug はユーザー名を解析しません。', 'ru': 'Slug не анализирует имя пользователя.', 'zh': 'Slug 無法解析為使用者名稱。', 'pl': 'Slug nie analizuje nazwy użytkownika.', 'fa': 'Slug به نام کاربری تجزیه نمی شود.', 'he': 'slug לא מתאים לשם המשתמש/ת.', 'ko': '슬러그는 사용자명을 구문분석하지 않습니다', 'ar': 'لا يتم تحليل Slug إلى اسم المستخدم.', 'id': 'Siput tidak menguraikan nama pengguna.', 'uk': "Slug не аналізує ім'я користувача.", 'tr': 'Slug kullanıcı adına ayrıştırılmıyor.', 'vi': 'Slug không thể được phân tích thành tên người dùng.', 'cs': 'Slug neanalyzuje uživatelské jméno.', 'sv': 'Slug tolkas inte som användarnamn.', 'fi': 'Slug ei jäsenny käyttäjänimeksi.', 'hu': 'A slug nem értelmezhető felhasználónévként.', 'th': 'Slug ไม่สามารถแปลงเป็นชื่อผู้ใช้ได้', 'el': 'Το «slug» δεν μετατρέπεται σε όνομα χρήστη.', 'ms': 'Slug tidak menghuraikan kepada nama pengguna.', 'sr': 'Slug се не може претворити у корисничко име.', 'ro': 'Slug-ul nu poate fi convertit într-un nume de utilizator.', 'bn': 'স্লাগ থেকে ব্যবহারকারীর নাম পাওয়া যায় না।', 'ca': "Slug no analitza el nom d'usuari.", 'no': 'Slug kan ikke tolkes som brukernavn.', 'bg': 'Slug не може да бъде разчетен като потребителско име.', 'da': 'Slug kan ikke fortolkes som brugernavn.', 'sk': 'Slug sa nedá spracovať na používateľské meno.', 'hi': 'स्लग को उपयोगकर्ता नाम में परिवर्तित नहीं किया जा सकता है।', 'et': 'Slug ei sõelu kasutajanimeks.', 'hr': 'Slug se ne može pretvoriti u korisničko ime.', 'az': 'Slug istifadəçi adına çevrilmir.', 'zh-yue': 'Slug 無法解析為使用者名稱。', 'lt': 'Slug nepaverčiamas į naudotojo vardą.', 'sl': 'Slug ni mogoče razčleniti v uporabniško ime.', 'eu': 'Slug-a ezin da erabiltzaile-izen gisa interpretatu.', 'hy': 'Slug-ը չի վերածվում օգտանվան։', 'uz': 'Slug foydalanuvchi nomini tahlil qilmaydi.', 'ta': 'ஸ்லக் பயனர்பெயரைப் பார்க்கவில்லை.', 'lv': 'Slugu nevar pārveidot par lietotājvārdu.'}
            _youve_already_confirmed_this_email_address_error_message_dict = {'en': "You've already confirmed this email address.", 'fr': 'Vous avez déjà confirmé cette adresse e-mail.', 'de': 'Sie haben diese E-Mail-Adresse bereits bestätigt.', 'es': 'Ya has confirmado esta dirección de correo electrónico.', 'pt': 'Tu já confirmaste esta endereço de e-mail.', 'it': 'Hai già confermato questo indirizzo e-mail.', 'nl': 'Je hebt dit e-mailadres al bevestigd.', 'ja': 'このメールアドレスはすでに確認済みです。', 'ru': 'Вы уже подтвердили этот адрес электронной почты.', 'zh': '您已確認過此電子郵件地址。', 'pl': 'Potwierdziłeś już ten adres e-mail.', 'fa': 'شما قبلاً این آدرس ایمیل را تأیید کرده اید.', 'he': 'כבר אימתת את כתובת הדואר האלקטרוני שלך.', 'ko': '이 이메일 주소를 이미 확인했습니다.', 'ar': 'لقد قمت بالفعل بتأكيد عنوان البريد الإلكتروني هذا.', 'id': 'Anda telah mengonfirmasi alamat email ini.', 'uk': 'Ви вже підтвердили цю електронну адресу.', 'tr': 'Bu e-posta adresini zaten onayladınız.', 'vi': 'Bạn đã xác nhận địa chỉ email này.', 'cs': 'Tuto e-mailovou adresu jste již potvrdili.', 'sv': 'Du har redan bekräftat den här e-postadressen.', 'fi': 'Olet jo vahvistanut tämän sähköpostiosoitteen.', 'hu': "You've already confirmed this email address.", 'th': 'คุณได้ยืนยันที่อยู่อีเมลนี้แล้ว', 'el': "You've already confirmed this email address.", 'ms': 'Anda telah pun mengesahkan alamat e-mel ini.', 'sr': "You've already confirmed this email address.", 'ro': "You've already confirmed this email address.", 'bn': "You've already confirmed this email address.", 'ca': 'Ja has confirmat aquesta adreça de correu electrònic.', 'no': "You've already confirmed this email address.", 'bg': "You've already confirmed this email address.", 'da': 'Du har allerede bekræftet denne e-mailadresse.', 'sk': "You've already confirmed this email address.", 'hi': "You've already confirmed this email address.", 'et': "You've already confirmed this email address.", 'hr': "You've already confirmed this email address.", 'az': "You've already confirmed this email address.", 'zh-yue': '您已確認過此電郵地址。', 'lt': 'Jūs jau patvirtinote šį el. pašto adresą.', 'sl': "You've already confirmed this email address.", 'eu': "You've already confirmed this email address.", 'hy': "You've already confirmed this email address.", 'uz': 'Siz allaqachon ushbu elektron pochta manzilini tasdiqlagansiz.', 'ta': "You've already confirmed this email address.", 'lv': "You've already confirmed this email address."}
            _invalid_confirmation_link_error_message_dict = {'en': 'Invalid confirmation link.', 'fr': 'Lien de confirmation invalide.', 'de': 'Ungültiger Bestätigungslink.', 'es': 'Enlace de confirmación no válido.', 'pt': 'Link de confirmação inválido.', 'it': 'Link di conferma non valido.', 'nl': 'Ongeldige bevestigingslink.', 'ja': '確認リンクが無効です。', 'ru': 'Неверная ссылка для подтверждения.', 'zh': '確認連結無效。', 'pl': 'Nieprawidłowy link potwierdzający.', 'fa': 'پیوند تایید نامعتبر است.', 'he': 'קישור אימות לא חוקי.', 'ko': '잘못된 확인 링크.', 'ar': 'رابط التأكيد غير صالح.', 'id': 'Tautan konfirmasi tidak valid.', 'uk': 'Недійсне посилання підтвердження.', 'tr': 'Geçersiz onay bağlantısı.', 'vi': 'Liên kết xác nhận không hợp lệ.', 'cs': 'Neplatný potvrzovací odkaz.', 'sv': 'Ogiltig bekräftelselänk.', 'fi': 'Virheellinen vahvistuslinkki.', 'hu': 'Érvénytelen megerősítő link.', 'th': 'ลิงก์ยืนยันไม่ถูกต้อง', 'el': 'Ο σύνδεσμος επιβεβαίωσης δεν είναι έγκυρος.', 'ms': 'Pautan pengesahan tidak sah.', 'sr': 'Неважећа веза за потврду.', 'ro': 'Link de confirmare nevalid.', 'bn': 'অবৈধ নিশ্চিতকরণ লিঙ্ক।', 'ca': 'Enllaç de confirmació no vàlid.', 'no': 'Ugyldig bekreftelseslenke.', 'bg': 'Невалидна връзка за потвърждение.', 'da': 'Ugyldigt bekræftelseslink.', 'sk': 'Neplatný potvrdzovací odkaz.', 'hi': 'अमान्य पुष्टिकरण लिंक।', 'et': 'Kehtetu kinnituslink.', 'hr': 'Nevažeća poveznica za potvrdu.', 'az': 'Yanlış təsdiq keçidi.', 'zh-yue': '確認連結無效。', 'lt': 'Neteisinga patvirtinimo nuoroda.', 'sl': 'Neveljavna potrditvena povezava.', 'eu': 'Baieztapen-esteka baliogabea.', 'hy': 'Անվավեր հաստատման հղում։', 'uz': "Tasdiqlash havolasi noto'g'ri.", 'ta': 'செல்லாத உறுதிப்படுத்தல் இணைப்பு.', 'lv': 'Nederīga apstiprinājuma saite.'}
            _username_is_required_error_message_dict = {'en': 'Username is required.', 'fr': 'Nom d’utilisateur requis.', 'de': 'Benutzername ist erforderlich.', 'es': 'Se requiere nombre de usuario.', 'pt': 'O nome de utilizador é obrigatório.', 'it': 'Il nome utente è richiesto.', 'nl': 'Gebruikersnaam is vereist.', 'ja': 'ユーザー名は必須です。', 'ru': 'Требуется имя пользователя.', 'zh': '使用者名稱是必填項。', 'pl': 'Nazwa użytkownika jest wymagana.', 'fa': 'نام کاربری مورد نیاز است.', 'he': 'שם המשתמש/ת נדרש.', 'ko': '사용자명이 필요합니다.', 'ar': 'اسم المستخدم مطلوب.', 'id': 'Nama pengguna diperlukan.', 'uk': "Потрібно ввести ім'я користувача.", 'tr': 'Kullanıcı adı gerekli.', 'vi': 'Tên người dùng là bắt buộc.', 'cs': 'Uživatelské jméno je povinné.', 'sv': 'Username är obligatoriskt.', 'fi': 'Käyttäjätunnus vaaditaan.', 'hu': 'A felhasználónév megadása kötelező.', 'th': 'จำเป็นต้องมีชื่อผู้ใช้', 'el': 'Το όνομα χρήστη είναι υποχρεωτικό.', 'ms': 'Nama pengguna diperlukan.', 'sr': 'Корисничко име је обавезно.', 'ro': 'Numele de utilizator este obligatoriu.', 'bn': 'ব্যবহারকারীর নাম আবশ্যক।', 'ca': "El nom d'usuari és obligatori.", 'no': 'Brukernavn er påkrevd.', 'bg': 'Изисква се потребителско име.', 'da': 'Brugernavn er påkrævet.', 'sk': 'Vyžaduje sa používateľské meno.', 'hi': 'उपयोगकर्ता नाम आवश्यक है।', 'et': 'Kasutajanimi on nõutav.', 'hr': 'Korisničko ime je obavezno.', 'az': 'İstifadəçi adı tələb olunur.', 'zh-yue': '使用者名稱是必填項。', 'lt': 'Naudotojo vardas yra privalomas.', 'sl': 'Uporabniško ime je obvezno.', 'eu': 'Erabiltzaile-izena beharrezkoa da.', 'hy': 'Օգտանունը պարտադիր է։', 'uz': 'Foydalanuvchi nomi talab qilinadi.', 'ta': 'பயனர் பெயர் தேவை.', 'lv': 'Lietotājvārds ir obligāts.'}
            _ensure_this_value_is_greater_than_or_equal_to_minus_32768_error_message_dict = {'en': 'Ensure this value is greater than or equal to -32768.', 'fr': 'Assurez-vous que cette valeur est supérieure ou égale à -32768.', 'de': 'Dieser Wert muss größer oder gleich -32768 sein.', 'es': 'Asegúrese de que este valor es mayor o igual a -32768.', 'pt': 'Garanta que este valor seja maior ou igual a -32768.', 'it': 'Assicurati che questo valore sia maggiore o uguale a -32768.', 'nl': 'Zorg ervoor dat deze waarde minstens -32768 is.', 'ja': 'この値は -32768 以上でなければなりません。', 'ru': 'Убедитесь, что это значение больше или равно -32768.', 'zh': '请确保该值大于或等于 -32768。', 'pl': 'Upewnij się, że ta wartość jest większa lub równa -32768.', 'fa': 'اطمینان حاصل کنید که این مقدار بزرگ\u200cتر از یا مساوی -32768 باشد.', 'he': 'יש לוודא שערך זה גדול מ או שווה ל־-32768.', 'ko': '-32768 이상의 값을 입력해 주세요.', 'ar': 'تأكد من أن هذه القيمة أكبر من أو تساوي -32768.', 'id': 'Pastikan nilai ini lebih besar dari atau sama dengan -32768.', 'uk': 'Переконайтеся, що це значення більше або дорівнює -32768.', 'tr': 'Bu değerin -32768 değerinden büyük veya ona eşit olduğundan emin olun.', 'vi': 'Hãy bảo đảm giá trị này lớn hơn hoặc bằng -32768.', 'cs': 'Zajistěte, aby tato hodnota byla větší než nebo rovna -32768.', 'sv': 'Kontrollera att detta värde är större än eller lika med -32768.', 'fi': 'Tämän luvun on oltava vähintään -32768.', 'hu': 'Bizonyosodjon meg arról, hogy az érték -32768, vagy nagyobb.', 'th': 'ค่านี้ต้องมากกว่าหรือเท่ากับ -32768', 'el': 'Βεβαιωθείτε ότι η τιμή είναι μεγαλύτερη ή ίση από -32768.', 'ms': 'Pastikan nilai ini lebih daripada atau sama dengan -32768.', 'sr': 'Ова вредност мора бити већа од -32768 или тачно толико.', 'ro': 'Asiguraţi-vă că această valoare este mai mare sau egală cu -32768 .', 'bn': 'সংখ্যাটির মান -32768 এর চেয়ে বড় বা সমান হতে হবে।', 'ca': 'Assegureu-vos que aquest valor sigui més gran o igual que -32768.', 'no': 'Verdien må være større enn eller lik -32768.', 'bg': 'Уверете се, че тази стойност е по-голяма или равна на -32768 .', 'da': 'Denne værdi skal være større end eller lig -32768.', 'sk': 'Uistite sa, že hodnota je väčšia alebo rovná -32768.', 'hi': 'सुनिश्चित करें यह मान  -32768 से बड़ा या बराबर है ।', 'et': 'Veendu, et see väärtus on suurem või võrdne kui -32768.', 'hr': 'Osigurajte da je ova vrijednost veća ili jednaka -32768.', 'az': 'Bu qiymətin -32768-(y)a/ə bərabər və ya ondan böyük olduğunu yoxlayın.', 'zh-yue': '請確保呢個值大於或等於 -32768。', 'lt': 'Įsitikinkite, kad reikšmė yra didesnė arba lygi -32768.', 'sl': 'Poskrbite, da bo ta vrednost večja ali enaka -32768.', 'eu': 'Ziurtatu balio hau -32768 baino handiagoa edo berdina dela.', 'hy': 'Համոզվեք, որ այս արժեքը մեծ է, համ հավասար -32768', 'uz': 'Ushbu qiymat -32768 dan katta yoki unga teng ekanligini tekshiring.', 'ta': 'Ensure this value is greater than or equal to -32768.', 'lv': 'Vērtībai jābūt lielākai vai vienādai ar -32768.'}
            _ensure_this_value_is_less_than_or_equal_to_32767_error_message_dict = {'en': 'Ensure this value is less than or equal to 32767.', 'fr': 'Assurez-vous que cette valeur est inférieure ou égale à 32767.', 'de': 'Dieser Wert muss kleiner oder gleich 32767 sein.', 'es': 'Asegúrese de que este valor es menor o igual a 32767.', 'pt': 'Garanta que este valor seja menor ou igual a 32767.', 'it': 'Assicurati che questo valore sia minore o uguale a 32767.', 'nl': 'Zorg ervoor dat deze waarde hoogstens 32767 is.', 'ja': 'この値は 32767 以下でなければなりません。', 'ru': 'Убедитесь, что это значение меньше или равно 32767.', 'zh': '请确保该值小于或等于 32767。', 'pl': 'Upewnij się, że ta wartość jest mniejsza lub równa 32767.', 'fa': 'اطمینان حاصل کنید که این مقدار کوچک\u200cتر از یا مساوی 32767 باشد.', 'he': 'יש לוודא שערך זה פחות מ או שווה ל־32767.', 'ko': '32767 이하의 값을 입력해 주세요.', 'ar': 'تأكد من أن هذه القيمة أصغر من أو تساوي 32767.', 'id': 'Pastikan nilai ini lebih kecil dari atau sama dengan 32767.', 'uk': 'Переконайтеся, що це значення менше або дорівнює 32767.', 'tr': 'Bu değerin 32767 değerinden küçük veya ona eşit olduğundan emin olun.', 'vi': 'Hãy bảo đảm giá trị này nhỏ hơn hoặc bằng 32767.', 'cs': 'Zajistěte, aby tato hodnota byla menší než nebo rovna 32767.', 'sv': 'Kontrollera att detta värde är mindre än eller lika med 32767.', 'fi': 'Tämän arvon on oltava enintään 32767.', 'hu': 'Bizonyosodjon meg arról, hogy az érték 32767, vagy kisebb.', 'th': 'ค่านี้ต้องน้อยกว่าหรือเท่ากับ 32767', 'el': 'Βεβαιωθείτε ότι η τιμή είναι μικρότερη ή ίση από 32767.', 'ms': 'Pastikan nilai ini kurang daripada atau sama dengan 32767.', 'sr': 'Ова вредност мора да буде мања од 32767. или тачно толико.', 'ro': 'Asiguraţi-vă că această valoare este mai mică sau egală cu 32767 .', 'bn': 'সংখ্যাটির মান 32767 এর চেয়ে ছোট বা সমান হতে হবে।', 'ca': 'Assegureu-vos que aquest valor sigui menor o igual que 32767.', 'no': 'Verdien må være mindre enn eller lik 32767.', 'bg': 'Уверете се, че тази стойност е по-малка или равна на 32767 .', 'da': 'Denne værdi skal være mindre end eller lig 32767.', 'sk': 'Uistite sa, že táto hodnota je menšia alebo rovná 32767.', 'hi': 'सुनिश्चित करें कि यह मान  32767 से कम या बराबर है ।', 'et': 'Veendu, et see väärtus on väiksem või võrdne kui 32767.', 'hr': 'Osigurajte da je ova vrijednost manja ili jednaka 32767.', 'az': 'Bu qiymətin 32767-(y)a/ə bərabər və ya ondan kiçik olduğunu yoxlayın.', 'zh-yue': '請確保呢個值小於或等於 32767。', 'lt': 'Įsitikinkite, kad reikšmė yra mažesnė arba lygi 32767.', 'sl': 'Poskrbite, da bo ta vrednost manj kot ali natanko 32767.', 'eu': 'Ziurtatu balio hau 32767 baino txikiagoa edo berdina dela.', 'hy': 'Համոզվեք, որ այս արժեքը փոքր է, կամ հավասար 32767', 'uz': 'Ushbu qiymat 32767 dan kichik yoki unga teng ekanligini tekshiring.', 'ta': 'Ensure this value is less than or equal to 32767.', 'lv': 'Šai vērtībai jabūt mazākai vai vienādai ar 32767.'}
            _value_too_long_for_type_character_varying_255_error_message_dict = {'en': 'value too long for type character varying(255)', 'fr': 'value too long for type character varying(255)', 'de': 'value too long for type character varying(255)', 'es': 'value too long for type character varying(255)', 'pt': 'value too long for type character varying(255)', 'it': 'value too long for type character varying(255)', 'nl': 'value too long for type character varying(255)', 'ja': '値が型 character varying(255) に対して長すぎます', 'ru': 'value too long for type character varying(255)', 'zh': '对于类型 character varying(255) 来说，值太长', 'pl': 'wartość jest zbyt długa dla typu character varying(255)', 'fa': 'value too long for type character varying(255)', 'he': 'value too long for type character varying(255)', 'ko': 'value too long for type character varying(255)', 'ar': 'القيمة طويلة جدًا بالنسبة للنوع character varying(255)', 'id': 'nilai terlalu panjang untuk tipe character varying(255)', 'uk': 'value too long for type character varying(255)', 'tr': 'değer, character varying(255) türü için çok uzun', 'vi': 'value too long for type character varying(255)', 'cs': 'hodnota je pro typ character varying(255) příliš dlouhá', 'sv': 'value too long for type character varying(255)', 'fi': 'value too long for type character varying(255)', 'hu': 'value too long for type character varying(255)', 'th': 'value too long for type character varying(255)', 'el': 'value too long for type character varying(255)', 'ms': 'value too long for type character varying(255)', 'sr': 'value too long for type character varying(255)', 'ro': 'value too long for type character varying(255)', 'bn': 'value too long for type character varying(255)', 'ca': 'value too long for type character varying(255)', 'no': 'value too long for type character varying(255)', 'bg': 'value too long for type character varying(255)', 'da': 'value too long for type character varying(255)', 'sk': 'value too long for type character varying(255)', 'hi': 'value too long for type character varying(255)', 'et': 'value too long for type character varying(255)', 'hr': 'value too long for type character varying(255)', 'az': 'value too long for type character varying(255)', 'zh-yue': '值對於 character varying(255) 類型嚟講太長', 'lt': 'value too long for type character varying(255)', 'sl': 'value too long for type character varying(255)', 'eu': 'value too long for type character varying(255)', 'hy': 'too long for type character varying(255) value', 'uz': 'value too long for type character varying(255)', 'ta': 'value too long for type character varying(255)', 'lv': 'value too long for type character varying(255)'}
            _superuser_must_be_equal_to_staff_error_message_dict = {'en': 'Superuser must be equal to staff.', 'fr': 'Le superutilisateur doit être égal au staff.', 'de': 'Superbenutzer muss dem Personal entsprechen', 'es': 'El superusuario debe ser igual al personal.', 'pt': 'Superuser precisa ser igual a funcionário.', 'it': 'Il superutente deve essere uguale allo staff.', 'nl': 'Supergebruiker moet gelijk zijn aan personeel.', 'ja': 'スーパーユーザーはスタッフと同等である必要があります。', 'ru': 'Суперпользователь должен быть равен персоналу.', 'zh': '超級使用者必須與員工擁有同等權限。', 'pl': 'Superużytkownik musi być równy personelowi.', 'fa': 'سوپرکاربر باید با کارکنان برابر باشد.', 'he': 'משתמש-על חייב להיות גם איש צוות.', 'ko': '슈퍼사용자는 스태프와 동일해야 합니다.', 'ar': 'يجب أن يكون المستخدم المميز مساوياً للموظفين.', 'id': 'Pengguna super harus sama dengan staf.', 'uk': 'Суперкористувач повинен бути рівним персоналу.', 'tr': 'Süper kullanıcı personele eşit olmalıdır.', 'vi': 'Người dùng quản trị phải có quyền tương đương với nhân viên.', 'cs': 'Superuživatel se musí rovnat personálu.', 'sv': 'Superanvändare måste vara lika med personal.', 'fi': 'Pääkäyttäjän on oltava yhtäläinen henkilöstöön nähden.', 'hu': 'A szuperfelhasználó értékének egyeznie kell a személyzet értékével.', 'th': 'Superuser ต้องเท่ากับ staff', 'el': 'Ο «Superuser» πρέπει να είναι ίσος με το «staff».', 'ms': 'Pengguna super mestilah sama dengan kakitangan.', 'sr': 'Суперкорисник мора бити једнак особљу.', 'ro': 'Superutilizatorul trebuie să fie egal cu personalul.', 'bn': 'সুপারইউজারকে অবশ্যই স্টাফের সমতুল্য হতে হবে।', 'ca': 'El superusuari ha de ser igual al personal.', 'no': 'Superbruker må være lik ansatt.', 'bg': 'Суперпотребителят трябва да е равен на персонала.', 'da': 'Superbruger skal være lig med personale.', 'sk': 'Superpoužívateľ sa musí rovnať členovi personálu.', 'hi': 'सुपरयूजर का पद स्टाफ के बराबर होना चाहिए।', 'et': 'Superkasutaja peab olema võrdne personaliga.', 'hr': 'Superkorisnik mora biti jednak osoblju.', 'az': 'Superistifadəçi əməkdaşa bərabər olmalıdır.', 'zh-yue': '超級使用者必須與員工擁有同等權限。', 'lt': 'Supernaudotojas turi sutapti su personalu.', 'sl': 'Superuporabnik mora biti hkrati član osebja.', 'eu': 'Supererabiltzailea staff-aren berdina izan behar da.', 'hy': 'Սուպերօգտատերը պետք է լինի նաև անձնակազմի անդամ։', 'uz': "Superuser xodimlarga teng bo'lishi kerak.", 'ta': 'சூப்பர் பயனர் ஊழியர்களுக்கு சமமாக இருக்க வேண்டும்.', 'lv': 'Superlietotājam jābūt arī personāla loceklim.'}
            _the_email_address_was_deleted_success_message_dict = {'en': 'The email address was deleted.', 'fr': 'L’adresse e-mail a été supprimée.', 'de': 'Die E-Mail-Adresse wurde gelöscht.', 'es': 'La dirección de correo electrónico fue eliminada.', 'pt': 'A direcção de e-mail foi excluída.', 'it': "L'indirizzo e-mail è stato eliminato.", 'nl': 'Het e-mailadres is verwijderd.', 'ja': 'メールアドレスが削除されました。', 'ru': 'Адрес электронной почты был удален.', 'zh': '該電子郵件地址已被刪除。', 'pl': 'Adres e-mail został usunięty.', 'fa': 'آدرس ایمیل حذف شد', 'he': 'כתובת הדואר האלקטרוני נמחקה.', 'ko': '이메일 주소가 삭제되었습니다.', 'ar': 'تم حذف عنوان البريد الإلكتروني.', 'id': 'Alamat email telah dihapus.', 'uk': 'Електронну адресу видалено.', 'tr': 'E-posta adresi silindi.', 'vi': 'Địa chỉ email đã bị xóa.', 'cs': 'E-mailová adresa byla smazána.', 'sv': 'E-postadressen raderades.', 'fi': 'Vahvistusviesti lähetettiin osoitteeseen.', 'hu': 'Az e-mail cím törölve lett.', 'th': 'ที่อยู่อีเมลถูกลบแล้ว', 'el': 'Η διεύθυνση ηλεκτρονικού ταχυδρομείου διαγράφηκε.', 'ms': 'Alamat e-mel telah dipadamkan.', 'sr': 'Адреса е-поште је избрисана.', 'ro': 'Adresa de e-mail a fost ștearsă.', 'bn': 'ইমেল ঠিকানাটি মুছে ফেলা হয়েছে।', 'ca': "S'ha suprimit l'adreça de correu electrònic.", 'no': 'E-postadressen ble slettet.', 'bg': 'Имейл адресът беше изтрит.', 'da': 'E-mailadressen blev slettet.', 'sk': 'E-mailová adresa bola vymazaná.', 'hi': 'ईईमेल पता हटा दिया गया है।', 'et': 'E-posti aadress kustutati.', 'hr': 'Adresa e-pošte je izbrisana.', 'az': 'E-poçt ünvanı silindi.', 'zh-yue': '該電郵地址已被刪除。', 'lt': 'El. pašto adresas buvo ištrintas.', 'sl': 'E-poštni naslov je bil izbrisan.', 'eu': 'Helbide elektronikoa ezabatu da.', 'hy': 'Էլփոստի հասցեն ջնջվել է։', 'uz': "Elektron pochta manzili o'chirib tashlandi.", 'ta': 'மின்னஞ்சல் முகவரி நீக்கப்பட்டது.', 'lv': 'E-pasta adrese tika dzēsta.'}
            _you_have_changed_your_primary_email_address_success_message_dict = {'en': 'You have made this email address primary.', 'fr': 'Vous avez défini cette adresse e-mail comme adresse primaire.', 'de': 'Sie haben diese E-Mail-Adresse zu Ihrer Hauptadresse gemacht.', 'es': 'Has convertido esta dirección de correo electrónico en principal.', 'pt': 'Configuraste esta endereço de e-mail como principal.', 'it': 'Questo indirizzo e-mail è diventato l’indirizzo principale.', 'nl': 'Je heb die je primaire e-mailadres gemaakt.', 'ja': 'この電子メール アドレスをプライマリに設定しました。', 'ru': 'Вы сделали этот адрес электронной почты основным.', 'zh': '您已將此電子郵件地址設為主要電子郵件地址。', 'pl': 'Ustawiłeś ten adres e-mail jako podstawowy.', 'fa': 'شما این آدرس ایمیل را اصلی کرده اید.', 'he': 'הפכת את כתובת הדואר האלקטרוני הזאת לראשית.', 'ko': '이 이메일 주소를 기본으로 설정했습니다.', 'ar': 'لقد جعلت عنوان البريد الإلكتروني هذا أساسيًا.', 'id': 'Anda telah menjadikan alamat email ini sebagai alamat utama.', 'uk': 'Ви зробили цю електронну адресу основною.', 'tr': 'Bu e-posta adresini birincil yaptınız.', 'vi': 'Bạn đã chọn địa chỉ email này làm địa chỉ email chính.', 'cs': 'Tuto e-mailovou adresu jste nastavili jako primární.', 'sv': 'Du har gjort den här e-postadressen primär.', 'fi': 'Olet määrittänyt tämän sähköpostiosoitteen ensisijaiseksi.', 'hu': 'Ezt az e-mail címet elsődlegessé tette.', 'th': 'คุณกำหนดให้ที่อยู่อีเมลนี้เป็นที่อยู่หลัก', 'el': 'Έχετε ορίσει αυτή τη διεύθυνση ηλεκτρονικού ταχυδρομείου ως κύρια.', 'ms': 'Anda telah menjadikan alamat e-mel ini utama.', 'sr': 'Ову адресу е-поште сте учинили примарном.', 'ro': 'Ați făcut această adresă de e-mail principală.', 'bn': 'আপনি এই ইমেল ঠিকানাটিকে প্রাথমিক করেছেন।', 'ca': 'Has fet que aquesta adreça de correu electrònic sigui la principal.', 'no': 'Du har gjort denne e-postadressen til primær.', 'bg': 'Направихте този имейл адрес основен.', 'da': 'Du har gjort denne e-mailadresse til den primære.', 'sk': 'Túto e-mailovú adresu ste nastavili ako primárnu.', 'hi': 'आपने इस ईमेल पते को प्राथमिक ईईमेल पता बना दिया है।', 'et': 'Olete määranud selle e-posti aadressi esmaseks.', 'hr': 'Postavili ste ovu adresu e-pošte kao primarnu.', 'az': 'Bu e-poçt ünvanını əsas etdiniz.', 'zh-yue': '您已將此電郵地址設為主要電郵地址。', 'lt': 'Nustatėte šį el. pašto adresą kaip pagrindinį.', 'sl': 'Ta e-poštni naslov ste nastavili kot primarni.', 'eu': 'Helbide elektroniko hau nagusi bihurtu duzu.', 'hy': 'Դուք այս էլփոստի հասցեն դարձրել եք հիմնականը։', 'uz': 'Siz ushbu elektron pochta manzilini asosiy qilib belgiladingiz.', 'ta': 'இந்த மின்னஞ்சல் முகவரியை முதன்மைப்படுத்தியுள்ளீர்கள்.', 'lv': 'Jūs padarījāt šo e-pasta adresi par primāro.'}
            _password_reset_on_speedy_net_subject_dict = {'en': 'Password reset on Speedy Net', 'fr': 'Réinitialisation du mot de passe sur Speedy Net', 'de': 'Passwort auf Speedy Net zurücksetzen', 'es': 'Contraseña restablecida en Speedy Net', 'pt': 'Redefinição de palavra-passe em Speedy Net', 'it': 'Password reset su Speedy Net', 'nl': 'Wachtwoordherinitialisatie voor Speedy Net', 'ja': 'Speedy Net のパスワード再設定', 'ru': 'Сброс пароля на Speedy Net', 'zh': 'Speedy Net 密码重置', 'pl': 'Reset hasła w Speedy Net', 'fa': 'بازنشانی گذرواژه در Speedy Net', 'he': 'איפוס סיסמה בספידי נט', 'ko': 'Speedy Net의 비밀번호 재설정', 'ar': 'إعادة تعيين كلمة المرور على Speedy Net', 'id': 'Setel ulang kata sandi di Speedy Net', 'uk': 'Скидання пароля у Speedy Net', 'tr': 'Speedy Net üzerinde parola sıfırlama', 'vi': 'Đặt lại mật khẩu trên Speedy Net', 'cs': 'Obnovení hesla na Speedy Net', 'sv': 'Lösenord nollställt på Speedy Net', 'fi': 'Salasanan nollaus sivustolla Speedy Net', 'hu': 'Jelszó visszaállítása a(z) Speedy Net oldalon', 'th': 'รีเซ็ตรหัสผ่านบน Speedy Net', 'el': 'Επαναφορά κωδικού πρόσβασης στο Speedy Net', 'ms': 'Tetapan semula kata laluan pada Speedy Net', 'sr': 'Ресетовање лозинке на Speedy Net', 'ro': 'Resetarea parolei pe Speedy Net', 'bn': 'Speedy Net-এ পাসওয়ার্ড রিসেট', 'ca': 'Restabliment de la contrasenya a Speedy Net', 'no': 'Tilbakestilling av passord på Speedy Net', 'bg': 'Нулиране на паролата на Speedy Net', 'da': 'Adgangskode nulstillet på Speedy Net', 'sk': 'Obnovenie hesla na Speedy Net', 'hi': 'पासवर्ड रीसेट चालू Speedy Net', 'et': 'Parool lähtestati Speedy Net', 'hr': 'Ponovno postavljanje lozinke na Speedy Net', 'az': 'Speedy Net-də şifrənin sıfırlanması', 'zh-yue': '密碼重設Speedy Net', 'lt': 'Speedy Net slaptažodžio atstatymas', 'sl': 'Ponastavitev gesla na Speedy Net', 'eu': 'Speedy Net webguneko pasahitz-berrezarpena', 'hy': 'Գաղտնաբառի փոփոխում Speedy Net կայքում', 'uz': 'Speedy Net da parolni tiklash', 'ta': 'Speedy Net இல் கடவுச்சொல் மீட்டமை', 'lv': 'Paroles atiestatīšana vietnē Speedy Net'}
            _password_reset_on_speedy_match_subject_dict = {'en': 'Password reset on Speedy Match', 'fr': 'Réinitialisation du mot de passe sur Speedy Match', 'de': 'Passwort auf Speedy Match zurücksetzen', 'es': 'Contraseña restablecida en Speedy Match', 'pt': 'Redefinição de palavra-passe em Speedy Match', 'it': 'Password reset su Speedy Match', 'nl': 'Wachtwoordherinitialisatie voor Speedy Match', 'ja': 'Speedy Match のパスワード再設定', 'ru': 'Сброс пароля на Speedy Match', 'zh': 'Speedy Match 密码重置', 'pl': 'Reset hasła w Speedy Match', 'fa': 'بازنشانی گذرواژه در Speedy Match', 'he': "איפוס סיסמה בספידי מץ'", 'ko': 'Speedy Match의 비밀번호 재설정', 'ar': 'إعادة تعيين كلمة المرور على Speedy Match', 'id': 'Setel ulang kata sandi di Speedy Match', 'uk': 'Скидання пароля у Speedy Match', 'tr': 'Speedy Match üzerinde parola sıfırlama', 'vi': 'Đặt lại mật khẩu trên Speedy Match', 'cs': 'Obnovení hesla na Speedy Match', 'sv': 'Lösenord nollställt på Speedy Match', 'fi': 'Salasanan nollaus sivustolla Speedy Match', 'hu': 'Jelszó visszaállítása a(z) Speedy Match oldalon', 'th': 'รีเซ็ตรหัสผ่านบน Speedy Match', 'el': 'Επαναφορά κωδικού πρόσβασης στο Speedy Match', 'ms': 'Tetapan semula kata laluan pada Speedy Match', 'sr': 'Ресетовање лозинке на Speedy Match', 'ro': 'Resetarea parolei pe Speedy Match', 'bn': 'Speedy Match-এ পাসওয়ার্ড রিসেট', 'ca': 'Restabliment de la contrasenya a Speedy Match', 'no': 'Tilbakestilling av passord på Speedy Match', 'bg': 'Нулиране на паролата на Speedy Match', 'da': 'Adgangskode nulstillet på Speedy Match', 'sk': 'Obnovenie hesla na Speedy Match', 'hi': 'पासवर्ड रीसेट चालू Speedy Match', 'et': 'Parool lähtestati Speedy Match', 'hr': 'Ponovno postavljanje lozinke na Speedy Match', 'az': 'Speedy Match-də şifrənin sıfırlanması', 'zh-yue': '密碼重設Speedy Match', 'lt': 'Speedy Match slaptažodžio atstatymas', 'sl': 'Ponastavitev gesla na Speedy Match', 'eu': 'Speedy Match webguneko pasahitz-berrezarpena', 'hy': 'Գաղտնաբառի փոփոխում Speedy Match կայքում', 'uz': 'Speedy Match da parolni tiklash', 'ta': 'Speedy Match இல் கடவுச்சொல் மீட்டமை', 'lv': 'Paroles atiestatīšana vietnē Speedy Match'}
            _speedy_net_deleted_user_name_dict = {'en': 'Speedy Net User', 'fr': 'Utilisateur de Speedy Net', 'de': 'Speedy Net Benutzer', 'es': 'Usuario de Speedy Net', 'pt': 'Utilizador do Speedy Net', 'it': 'Utente Speedy Net', 'nl': 'Speedy Net Gebruiker', 'ja': 'Speedy Net ユーザー', 'ru': 'Speedy Net Пользователь', 'zh': 'Speedy Net 用户', 'pl': 'Użytkownik Speedy Net', 'fa': 'کاربر Speedy Net', 'he': 'משתמש/ת ספידי נט', 'ko': 'Speedy Net 사용자', 'ar': 'مستخدم Speedy Net', 'id': 'Pengguna Speedy Net', 'uk': 'Speedy Net Користувач', 'tr': 'Speedy Net Kullanıcısı', 'vi': 'Người dùng Speedy Net', 'cs': 'Uživatel Speedy Net', 'sv': 'Speedy Net Användare', 'fi': 'Speedy Net Käyttäjä', 'hu': 'Speedy Net felhasználó', 'th': 'ผู้ใช้ Speedy Net', 'el': 'Χρήστης Speedy Net', 'ms': 'Pengguna Speedy Net', 'sr': 'Корисник Speedy Net', 'ro': 'Utilizator Speedy Net', 'bn': 'Speedy Net ব্যবহারকারী', 'ca': 'Usuari de Speedy Net', 'no': 'Speedy Net Bruker', 'bg': 'Speedy Net Потребител', 'da': 'Speedy Net Bruger', 'sk': 'Používateľ Speedy Net', 'hi': 'Speedy Net उपयोगकर्ता', 'et': 'Speedy Net Kasutaja', 'hr': 'Speedy Net korisnik', 'az': 'Speedy Net istifadəçisi', 'zh-yue': 'Speedy Net 用戶', 'lt': 'Speedy Net naudotojas', 'sl': 'Uporabnik Speedy Net', 'eu': 'Speedy Net erabiltzailea', 'hy': 'Speedy Net օգտատեր', 'uz': 'Speedy Net foydalanuvchisi', 'ta': 'Speedy Net பயனர்', 'lv': 'Speedy Net lietotājs'}
            _speedy_match_deleted_user_name_dict = {'en': 'Speedy Match User', 'fr': 'Utilisateur de Speedy Match', 'de': 'Speedy Match Benutzer', 'es': 'Usuario de Speedy Match', 'pt': 'Utilizador do Speedy Match', 'it': 'Utente Speedy Match', 'nl': 'Speedy Match Gebruiker', 'ja': 'Speedy Match ユーザー', 'ru': 'Speedy Match Пользователь', 'zh': 'Speedy Match 用户', 'pl': 'Użytkownik Speedy Match', 'fa': 'کاربر Speedy Match', 'he': "משתמש/ת ספידי מץ'", 'ko': 'Speedy Match 사용자', 'ar': 'مستخدم Speedy Match', 'id': 'Pengguna Speedy Match', 'uk': 'Speedy Match Користувач', 'tr': 'Speedy Match Kullanıcısı', 'vi': 'Người dùng Speedy Match', 'cs': 'Uživatel Speedy Match', 'sv': 'Speedy Match Användare', 'fi': 'Speedy Match Käyttäjä', 'hu': 'Speedy Match felhasználó', 'th': 'ผู้ใช้ Speedy Match', 'el': 'Χρήστης Speedy Match', 'ms': 'Pengguna Speedy Match', 'sr': 'Корисник Speedy Match', 'ro': 'Utilizator Speedy Match', 'bn': 'Speedy Match ব্যবহারকারী', 'ca': 'Usuari de Speedy Match', 'no': 'Speedy Match Bruker', 'bg': 'Speedy Match Потребител', 'da': 'Speedy Match Bruger', 'sk': 'Používateľ Speedy Match', 'hi': 'Speedy Match उपयोगकर्ता', 'et': 'Speedy Match Kasutaja', 'hr': 'Speedy Match korisnik', 'az': 'Speedy Match istifadəçisi', 'zh-yue': 'Speedy Match 用戶', 'lt': 'Speedy Match naudotojas', 'sl': 'Uporabnik Speedy Match', 'eu': 'Speedy Match erabiltzailea', 'hy': 'Speedy Match օգտատեր', 'uz': 'Speedy Match foydalanuvchisi', 'ta': 'Speedy Match பயனர்', 'lv': 'Speedy Match lietotājs'}
            _edit_profile_text_dict = {'en': 'Edit Profile', 'fr': 'Modifier profil', 'de': 'Profil bearbeiten', 'es': 'Editar perfil', 'pt': 'Editar Perfil', 'it': 'Modifica profilo', 'nl': 'Bewerk profiel', 'ja': 'プロフィールの編集', 'ru': 'Редактировать профиль', 'zh': '編輯個人資料', 'pl': 'Edytuj profil', 'fa': 'ویرایش نمایه', 'he': 'עריכת פרופיל', 'ko': '프로필 편집', 'ar': 'تحرير الملف الشخصي', 'id': 'Sunting Profil', 'uk': 'Редагувати профіль', 'tr': 'Profili Düzenle', 'vi': 'Chỉnh sửa hồ sơ', 'cs': 'Upravit profil', 'sv': 'Redigera profil', 'fi': 'Muokkaa profiilia', 'hu': 'Profil szerkesztése', 'th': 'แก้ไขโปรไฟล์', 'el': 'Επεξεργασία προφίλ', 'ms': 'Edit Profil', 'sr': 'Уреди профил', 'ro': 'Editați profilul', 'bn': 'প্রোফাইল সম্পাদনা করুন', 'ca': 'Edita el perfil', 'no': 'Rediger profil', 'bg': 'Редактиране на профил', 'da': 'Rediger profil', 'sk': 'Upraviť profil', 'hi': 'प्रोफ़ाइल संपादित करें', 'et': 'Redigeeri profiili', 'hr': 'Uredi profil', 'az': 'Profili redaktə et', 'zh-yue': '編輯個人資料', 'lt': 'Redaguoti profilį', 'sl': 'Uredi profil', 'eu': 'Editatu profila', 'hy': 'Խմբագրել պրոֆիլը', 'uz': 'Profilni tahrirlash', 'ta': 'சுயவிவரத்தை திருத்தவும்', 'lv': 'Rediģēt profilu'}

            _value_is_not_a_valid_choice_error_message_to_format_dict = {'en': 'Value {value} is not a valid choice.', 'fr': 'La valeur «\xa0{value}\xa0» n’est pas un choix valide.', 'de': 'Wert {value} ist keine gültige Option.', 'es': 'Valor {value} no es una opción válida.', 'pt': 'O valor {value} não é uma escolha válida.', 'it': 'Il valore {value} non è una scelta valida.', 'nl': 'Waarde {value} is geen geldige keuze.', 'ja': '{value} は有効な選択肢ではありません。', 'ru': 'Значения {value} нет среди допустимых вариантов.', 'zh': '數值 {value} 不是有效的選項。', 'pl': 'Wartość {value} nie jest poprawnym wyborem.', 'fa': 'مقدار {value} انتخاب معتبری نیست. ', 'he': 'ערך {value} אינו אפשרות חוקית.', 'ko': '{value} 은/는 올바른 선택사항이 아닙니다.', 'ar': 'القيمة {value} ليست خيارا صحيحاً.', 'id': 'Nilai {value} bukan pilihan yang valid.', 'uk': 'Значення {value} не є дозволеним вибором.', 'tr': '{value} değeri geçerli bir seçim değil.', 'vi': 'Giá trị {value} không phải là lựa chọn hợp lệ.', 'cs': 'Hodnota {value} není platná možnost.', 'sv': 'Värdet {value} är inget giltigt alternativ.', 'fi': 'Arvo {value} ei kelpaa.', 'hu': '{value} érték érvénytelen.', 'th': 'Value {value} is not a valid choice.', 'el': 'Η τιμή {value} δεν είναι έγκυρη επιλογή.', 'ms': 'Nilai {value} bukan pilihan yang sah.', 'sr': 'Вредност {value} није валидна.', 'ro': 'Valoarea {value} nu este o opțiune validă.', 'bn': 'Value {value} is not a valid choice.', 'ca': 'El valor {value} no és una opció vàlida.', 'no': 'Verdien {value} er ikke et gyldig valg.', 'bg': 'Стойността {value} не е валиден избор.', 'da': 'Værdien {value} er ikke et gyldigt valg.', 'sk': 'Hodnota {value} nie je platná možnosť.', 'hi': 'Value {value} is not a valid choice.', 'et': 'Väärtus {value} ei ole kehtiv valik.', 'hr': 'Vrijednost {value} nije jedna od raspoloživih opcija.', 'az': '{value} dəyəri doğru seçim deyil.', 'zh-yue': '數值 {value} 不是有效的選項。', 'lt': 'Reikšmės {value} rinktis negalima.', 'sl': 'Vrednost {value} ni veljavna izbira.', 'eu': '{value} balioa ez da baleko aukera bat.', 'hy': '{value} արժեքը չի մտնում թույլատրված տարբերակների մեջ', 'uz': "{value} qiymati to'g'ri tanlov emas.", 'ta': 'Value {value} is not a valid choice.', 'lv': 'Vērtība {value} nav derīga izvēle.'}
            _value_must_be_an_integer_error_message_to_format_dict = {'en': '“{value}” value must be an integer.', 'fr': 'La valeur «\xa0{value}\xa0» doit être un nombre entier.', 'de': 'Wert „{value}“ muss eine Ganzzahl sein.', 'es': '“{value}”: el valor debería ser un numero entero', 'pt': 'O valor “{value}” deve ser inteiro.', 'it': 'Il valore "{value}" deve essere un intero.', 'nl': 'Waarde van ‘{value}’ moet een geheel getal zijn.', 'ja': '“{value}” は整数値にしなければなりません。', 'ru': 'Значение “{value}” должно быть целым числом.', 'zh': '“{value}” 必須是整數。', 'pl': 'Wartością „{value}” musi być liczba całkowita.', 'fa': 'مقدار «{value}» باید عدد حقیقی باشد.', 'he': "הערך '{value}' חייב להיות מספר שלם.", 'ko': '"{value}" 값은 정수를 입력하여야 합니다.', 'ar': "قيمة '{value}' يجب ان تكون عدد طبيعي.", 'id': 'Nilai “{value}” harus berupa integer.', 'uk': '“{value}” value must be an integer.', 'tr': '“{value}” değeri bir tamsayı olmak zorundadır.', 'vi': '“{value}” value must be an integer.', 'cs': 'Hodnota "{value}" musí být celé číslo.', 'sv': 'Värdet "{value}" måste vara ett heltal.', 'fi': '{value}-arvo tulee olla kokonaisluku.', 'hu': 'A(z) "{value}" értékének egész számnak kell lennie.', 'th': '“{value}” value must be an integer.', 'el': "Η τιμή '{value}' πρέπει να είναι ακέραιος.", 'ms': 'Nilai "{value}" mesti dalam bentuk integer.', 'sr': 'Вредност "{value}" мора бити цео број.', 'ro': '“{value}” value must be an integer.', 'bn': '“{value}” value must be an integer.', 'ca': "El valor '{value}' ha de ser un nombre enter.", 'no': '"{value}"-verdien må være et heltall.', 'bg': 'Стойността "{value}" трябва да е цяло число.', 'da': '“{value}”-værdien skal være et heltal.', 'sk': 'Hodnota „{value}“ musí byť celé číslo.', 'hi': '“{value}” value must be an integer.', 'et': '“{value}” väärtus peab olema täisarv.', 'hr': '„{value}“ vrijednost mora biti cijeli broj.', 'az': '“{value}” dəyəri tam rəqəm olmalıdır.', 'zh-yue': '“{value}” 必須是整數。', 'lt': '“{value}” value must be an integer.', 'sl': '“{value}” vrednost mora biti celo število.', 'eu': '"{value}" zenbaki osoa izan behar da.', 'hy': '“{value}” value must be an integer.', 'uz': '"{value}" qiymati butun son bo\'lishi kerak.', 'ta': '“{value}” value must be an integer.', 'lv': '“{value}” vērtībai ir jābūt veselam skaitlim.'}
            _username_must_contain_at_least_min_length_alphanumeric_characters_error_message_to_format_dict = {'en': 'Username must contain at least {min_length} alphanumeric characters (it has {value_length}).', 'fr': 'Le nom d’utilisateur doit contenir au moins {min_length}\xa0caractères alphanumériques (il en contient {value_length}).', 'de': 'Der Benutzername muss mindestens {min_length} alphanumerische Zeichen (er hat {value_length}) enthalten.', 'es': 'El nombre de usuario debe contener al menos {min_length} caracteres alfanumérico (tiene {value_length}).', 'pt': 'O nome do utilizador deve conter pelo menos {min_length} caracteres alfanuméricos (contém {value_length}).', 'it': 'Il nome utente deve contenere almeno {min_length} caratteri alfanumerici (ha {value_length}).', 'nl': 'De gebruikersnaam moet ten minste {min_length} alfanumerieke tekens bevatten (het bevat {value_length}).', 'ja': 'ユーザー名には少なくとも {min_length} 文字の英数字が必要です（現在は {value_length} 文字です）。', 'ru': 'Имя пользователя должно содержать не менее {min_length} буквенно-цифровых символов (сейчас {value_length}).', 'zh': '使用者名稱必須至少包含 {min_length} 個英數字元（目前有 {value_length} 個）。', 'pl': 'Nazwa użytkownika musi zawierać co najmniej {min_length} znaków alfanumerycznych (obecnie ma {value_length}).', 'fa': 'نام کاربری باید حداقل {min_length} نویسهٔ الفبایی\u200cعددی داشته باشد (اکنون {value_length} نویسه دارد).', 'he': 'נא לוודא ששם המשתמש/ת מכיל {min_length} תווים אלפאנומריים לפחות (מכיל {value_length}). שם המשתמש/ת חייב להיות באנגלית.', 'ko': '사용자명에는 최소 {min_length}자의 영문자 숫자가 포함되어야 합니다 ({value_length}자).', 'ar': ('يجب أن يحتوي اسم المستخدم على {min_length} حرف أبجدي رقمي على الأقل (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على حرف أبجدي رقمي واحد على الأقل (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على حرفين أبجديين رقميين على الأقل (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على {min_length} أحرف أبجدية رقمية على الأقل (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على {min_length} حرفًا أبجديًا رقميًا على الأقل (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على {min_length} حرف أبجدي رقمي على الأقل (يحتوي على {value_length}).'), 'id': 'Nama pengguna harus mengandung setidaknya {min_length} karakter alfanumerik (memiliki {value_length}).', 'uk': 'Ім’я користувача має містити принаймні {min_length} буквено-цифрових символів (воно має {value_length}).', 'tr': 'Kullanıcı adı en az {min_length} alfanümerik karakter içermelidir ({value_length} içerir).', 'vi': 'Tên người dùng phải chứa ít nhất {min_length} ký tự chữ số (nó có {value_length}).', 'cs': 'Uživatelské jméno musí obsahovat alespoň {min_length} alfanumerických znaků (má {value_length}).', 'sv': 'Username måste innehålla minst {min_length} alfanumeriska tecken (det har {value_length}).', 'fi': 'Käyttäjätunnuksessa on oltava vähintään {min_length} aakkosnumeerista merkkiä (sillä on {value_length}).', 'hu': 'A felhasználónévnek legalább {min_length} alfanumerikus karaktert kell tartalmaznia ({value_length} van benne).', 'th': 'ชื่อผู้ใช้ต้องมีตัวอักษรหรือตัวเลขอย่างน้อย {min_length} ตัว (มี {value_length} ตัว)', 'el': 'Το όνομα χρήστη πρέπει να περιέχει τουλάχιστον {min_length} αλφαριθμητικούς χαρακτήρες (περιέχει {value_length}).', 'ms': 'Nama pengguna mesti mengandungi sekurang-kurangnya {min_length} aksara alfanumerik (ia mempunyai {value_length}).', 'sr': 'Корисничко име мора да садржи најмање {min_length} алфанумеричких знакова (има {value_length}).', 'ro': {6: 'Numele de utilizator trebuie să conțină cel puțin {min_length} caractere alfanumerice (are {value_length}).', 60: 'Numele de utilizator trebuie să conțină cel puțin {min_length} de caractere alfanumerice (are {value_length}).'}, 'bn': 'ব্যবহারকারীর নামে কমপক্ষে {min_length}টি আলফানিউমেরিক অক্ষর থাকতে হবে (এতে আছে {value_length}টি)।', 'ca': "El nom d'usuari ha de contenir almenys {min_length} caràcters alfanumèrics (té {value_length}).", 'no': 'Brukernavnet må inneholde minst {min_length} alfanumeriske tegn (det har {value_length}).', 'bg': 'Потребителското име трябва да съдържа поне {min_length} буквено-цифрови знака (има {value_length}).', 'da': 'Brugernavnet skal indeholde mindst {min_length} alfanumeriske tegn (det har {value_length}).', 'sk': 'Používateľské meno musí obsahovať aspoň {min_length} alfanumerických znakov (má {value_length}).', 'hi': 'उपयोगकर्ता नाम में कम से कम {min_length} अक्षरांकीय वर्ण होने चाहिए (इसमें {value_length} हैं)।', 'et': 'Kasutajanimi peab sisaldama vähemalt {min_length} tähtnumbrilist tähemärki (selles on {value_length}).', 'hr': 'Korisničko ime mora sadržavati najmanje {min_length} alfanumeričkih znakova (ima {value_length}).', 'az': 'İstifadəçi adı ən azı {min_length} hərf-rəqəm simvolu içərməlidir (onda {value_length} var).', 'zh-yue': '使用者名稱必須至少有 {min_length} 個英數字符(而家有 {value_length} 個)。', 'lt': {6: 'Naudotojo varde turi būti bent {min_length} raidiniai ar skaitmeniniai simboliai (jame yra {value_length}).', 60: 'Naudotojo varde turi būti bent {min_length} raidinių ar skaitmeninių simbolių (jame yra {value_length}).'}, 'sl': 'Uporabniško ime mora vsebovati vsaj {min_length} alfanumeričnih znakov (ima jih {value_length}).', 'eu': 'Erabiltzaile-izenak gutxienez {min_length} karaktere alfanumeriko izan behar ditu ({value_length} ditu).', 'hy': 'Օգտանունը պետք է պարունակի առնվազն {min_length} տառաթվային նիշ (այն ունի {value_length})։', 'uz': "Foydalanuvchi nomida kamida {min_length} ta harf-raqamli belgi bo'lishi kerak (unda {value_length} ta bor).", 'ta': 'பயனர்பெயர் குறைந்தது {min_length} எண்ணெழுத்து எழுத்துக்களைக் கொண்டிருக்க வேண்டும் (அதில் {value_length} உள்ளது).', 'lv': {6: 'Lietotājvārdam jāsatur vismaz {min_length} burtciparu rakstzīmes (tajā ir {value_length}).', 60: 'Lietotājvārdam jāsatur vismaz {min_length} burtciparu rakstzīmju (tajā ir {value_length}).'}}
            _username_must_contain_at_most_max_length_alphanumeric_characters_error_message_to_format_dict = {'en': 'Username must contain at most {max_length} alphanumeric characters (it has {value_length}).', 'fr': 'Le nom d’utilisateur doit contenir au maximum {max_length}\xa0caractères alphanumériques (il en contient {value_length}).', 'de': 'Der Benutzername darf höchstens {max_length} alphanumerische Zeichen (er hat {value_length}) enthalten.', 'es': 'El nombre de usuario debe contener como máximo {max_length} caracteres alfanumérico (tiene {value_length}).', 'pt': 'O nome do utilizador deve conter no máximo {max_length} caracteres alfanuméricos (contém {value_length}).', 'it': 'Il nome utente deve contenere al massimo {max_length} caratteri alfanumerici (ha {value_length}).', 'nl': 'De gebruikersnaam mag maximaal {max_length} alfanumerieke tekens bevatten (het bevat {value_length}).', 'ja': 'ユーザー名に使用できる英数字は最大 {max_length} 文字です（現在は {value_length} 文字です）。', 'ru': 'Имя пользователя должно содержать не более {max_length} буквенно-цифровых символов (сейчас {value_length}).', 'zh': '使用者名稱最多只能包含 {max_length} 個英數字元（目前有 {value_length} 個）。', 'pl': 'Nazwa użytkownika musi zawierać co najwyżej {max_length} znaków alfanumerycznych (obecnie ma {value_length}).', 'fa': 'نام کاربری باید حداکثر {max_length} نویسهٔ الفبایی\u200cعددی داشته باشد (اکنون {value_length} نویسه دارد).', 'he': 'נא לוודא ששם המשתמש/ת מכיל {max_length} תווים אלפאנומריים לכל היותר (מכיל {value_length}). שם המשתמש/ת חייב להיות באנגלית.', 'ko': '사용자명에는 최대 {max_length}자의 영문자 숫자가 포함되어야 합니다 ({value_length}자).', 'ar': ('يجب أن يحتوي اسم المستخدم على {max_length} حرف أبجدي رقمي على الأكثر (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على حرف أبجدي رقمي واحد على الأكثر (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على حرفين أبجديين رقميين على الأكثر (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على {max_length} أحرف أبجدية رقمية على الأكثر (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على {max_length} حرفًا أبجديًا رقميًا على الأكثر (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على {max_length} حرف أبجدي رقمي على الأكثر (يحتوي على {value_length}).'), 'id': 'Nama pengguna harus berisi paling banyak {max_length} karakter alfanumerik (memiliki {value_length}).', 'uk': 'Ім’я користувача має містити щонайбільше {max_length} буквено-цифрових символів (воно має {value_length}).', 'tr': 'Kullanıcı adı en fazla {max_length} alfanümerik karakter içermelidir ({value_length} içerir).', 'vi': 'Tên người dùng phải chứa tối đa {max_length} ký tự chữ số (nó có {value_length}).', 'cs': 'Uživatelské jméno musí obsahovat maximálně {max_length} alfanumerických znaků (má {value_length}).', 'sv': 'Username måste innehålla högst {max_length} alfanumeriska tecken (det har {value_length}).', 'fi': 'Käyttäjätunnuksessa saa olla enintään {max_length} aakkosnumeerista merkkiä (sillä on {value_length}).', 'hu': 'A felhasználónév legfeljebb {max_length} alfanumerikus karaktert tartalmazhat ({value_length} van benne).', 'th': 'ชื่อผู้ใช้ต้องมีตัวอักษรหรือตัวเลขไม่เกิน {max_length} ตัว (มี {value_length} ตัว)', 'el': 'Το όνομα χρήστη πρέπει να περιέχει το πολύ {max_length} αλφαριθμητικούς χαρακτήρες (περιέχει {value_length}).', 'ms': 'Nama pengguna mesti mengandungi paling banyak {max_length} aksara alfanumerik (ia mempunyai {value_length}).', 'sr': 'Корисничко име мора да садржи највише {max_length} алфанумеричких знакова (има {value_length}).', 'ro': 'Numele de utilizator trebuie să conțină cel mult {max_length} de caractere alfanumerice (are {value_length}).', 'bn': 'ব্যবহারকারীর নামে সর্বোচ্চ {max_length}টি আলফানিউমেরিক অক্ষর থাকতে পারবে (এতে আছে {value_length}টি)।', 'ca': "El nom d'usuari ha de contenir com a màxim {max_length} caràcters alfanumèrics (té {value_length}).", 'no': 'Brukernavnet må inneholde maksimalt {max_length} alfanumeriske tegn (det har {value_length}).', 'bg': 'Потребителското име трябва да съдържа най-много {max_length} буквено-цифрови знака (има {value_length}).', 'da': 'Brugernavnet må højst indeholde {max_length} alfanumeriske tegn (det har {value_length}).', 'sk': 'Používateľské meno musí obsahovať najviac {max_length} alfanumerických znakov (má {value_length}).', 'hi': 'उपयोगकर्ता नाम में अधिकतम {max_length} अक्षरांकीय वर्ण होने चाहिए (इसमें {value_length} हैं)।', 'et': 'Kasutajanimi peab sisaldama kuni {max_length} tähtnumbrilist tähemärki (selles on {value_length}).', 'hr': 'Korisničko ime mora sadržavati najviše {max_length} alfanumeričkih znakova (ima {value_length}).', 'az': 'İstifadəçi adı ən çox {max_length} hərf-rəqəm simvolu içərməlidir (onda {value_length} var).', 'zh-yue': '使用者名稱最多只可以有 {max_length} 個英數字符(而家有 {value_length} 個)。', 'lt': 'Naudotojo varde gali būti daugiausia {max_length} raidinių ar skaitmeninių simbolių (jame yra {value_length}).', 'sl': 'Uporabniško ime lahko vsebuje največ {max_length} alfanumeričnih znakov (ima jih {value_length}).', 'eu': 'Erabiltzaile-izenak gehienez {max_length} karaktere alfanumeriko izan behar ditu ({value_length} ditu).', 'hy': 'Օգտանունը պետք է պարունակի առավելագույնը {max_length} տառաթվային նիշ (այն ունի {value_length})։', 'uz': "Foydalanuvchi nomida ko'pi bilan {max_length} ta harf-raqamli belgi bo'lishi kerak (unda {value_length} ta bor).", 'ta': 'பயனர்பெயர் அதிகபட்சம் {max_length} எண்ணெழுத்து எழுத்துக்களைக் கொண்டிருக்க வேண்டும் (அதில் {value_length} உள்ளது).', 'lv': 'Lietotājvārdā drīkst būt ne vairāk kā {max_length} burtciparu rakstzīmju (tajā ir {value_length}).'}
            _username_must_contain_at_least_min_length_characters_error_message_to_format_dict = {'en': 'Username must contain at least {min_length} characters (it has {value_length}).', 'fr': 'Le nom d’utilisateur doit contenir au moins {min_length}\xa0caractères (il en contient {value_length}).', 'de': 'Der Benutzername muss mindestens {min_length} Zeichen (er hat {value_length}) enthalten.', 'es': 'El nombre de usuario debe contener al menos {min_length} caracteres (tiene {value_length}).', 'pt': 'O nome do utilizador deve conter pelo menos {min_length} caracteres (contém {value_length}).', 'it': 'Il nome utente deve contenere almeno {min_length} caratteri (ha {value_length}).', 'nl': 'De gebruikersnaam moet ten minste {min_length} karakter bevatten (het bevat {value_length}).', 'ja': 'ユーザー名には少なくとも {min_length} 文字が必要です（現在は {value_length} 文字です）。', 'ru': 'Имя пользователя должно содержать не менее {min_length} символов (сейчас {value_length}).', 'zh': '使用者名稱必須至少包含 {min_length} 個字元（目前有 {value_length} 個）。', 'pl': 'Nazwa użytkownika musi zawierać co najmniej {min_length} znaków (obecnie ma {value_length}).', 'fa': 'نام کاربری باید حداقل {min_length} نویسه داشته باشد (اکنون {value_length} نویسه دارد).', 'he': 'נא לוודא ששם המשתמש/ת מכיל {min_length} תווים לפחות (מכיל {value_length}).', 'ko': '사용자명에는 최소 {min_length}자의 문자가 포함되어야 합니다 ({value_length}자).', 'ar': ('يجب أن يحتوي اسم المستخدم على {min_length} حرف على الأقل (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على حرف واحد على الأقل (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على حرفين على الأقل (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على {min_length} أحرف على الأقل (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على {min_length} حرفًا على الأقل (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على {min_length} حرف على الأقل (يحتوي على {value_length}).'), 'id': 'Nama pengguna harus mengandung setidaknya {min_length} karakter (memiliki {value_length}).', 'uk': 'Ім’я користувача має містити принаймні {min_length} символів (має {value_length}).', 'tr': 'Kullanıcı adı en az {min_length} karakter içermelidir ({value_length} içerir).', 'vi': 'Tên người dùng phải chứa ít nhất {min_length} ký tự (nó có {value_length}).', 'cs': 'Uživatelské jméno musí obsahovat alespoň {min_length} znaků (má {value_length}).', 'sv': 'Username måste innehålla minst {min_length} tecken (det har {value_length}).', 'fi': 'Käyttäjätunnuksessa on oltava vähintään {min_length} merkkiä (sillä on {value_length}).', 'hu': 'A felhasználónévnek legalább {min_length} karaktert kell tartalmaznia ({value_length} van benne).', 'th': 'ชื่อผู้ใช้ต้องมีอักขระอย่างน้อย {min_length} ตัว (มี {value_length} ตัว)', 'el': 'Το όνομα χρήστη πρέπει να περιέχει τουλάχιστον {min_length} χαρακτήρες (περιέχει {value_length}).', 'ms': 'Nama pengguna mesti mengandungi sekurang-kurangnya {min_length} aksara (ia mempunyai {value_length}).', 'sr': 'Корисничко име мора да садржи најмање {min_length} знакова (има {value_length}).', 'ro': {6: 'Numele de utilizator trebuie să conțină cel puțin {min_length} caractere (are {value_length}).', 60: 'Numele de utilizator trebuie să conțină cel puțin {min_length} de caractere (are {value_length}).'}, 'bn': 'ব্যবহারকারীর নামে কমপক্ষে {min_length}টি অক্ষর থাকতে হবে (এতে আছে {value_length}টি)।', 'ca': "El nom d'usuari ha de contenir almenys {min_length} caràcters (té {value_length}).", 'no': 'Brukernavnet må inneholde minst {min_length} tegn (det har {value_length}).', 'bg': 'Потребителското име трябва да съдържа поне {min_length} знака (има {value_length}).', 'da': 'Brugernavnet skal indeholde mindst {min_length} tegn (det har {value_length}).', 'sk': 'Používateľské meno musí obsahovať aspoň {min_length} znakov (má {value_length}).', 'hi': 'उपयोगकर्ता नाम में कम से कम {min_length} वर्ण होने चाहिए (इसमें {value_length} हैं)।', 'et': 'Kasutajanimi peab sisaldama vähemalt {min_length} tähemärki (selles on {value_length}).', 'hr': 'Korisničko ime mora sadržavati najmanje {min_length} znakova (ima {value_length}).', 'az': 'İstifadəçi adı ən azı {min_length} simvol içərməlidir (onda {value_length} var).', 'zh-yue': '使用者名稱必須至少有 {min_length} 個字符(而家有 {value_length} 個)。', 'lt': {6: 'Naudotojo varde turi būti bent {min_length} simboliai (jame yra {value_length}).', 60: 'Naudotojo varde turi būti bent {min_length} simbolių (jame yra {value_length}).'}, 'sl': 'Uporabniško ime mora vsebovati vsaj {min_length} znakov (ima jih {value_length}).', 'eu': 'Erabiltzaile-izenak gutxienez {min_length} karaktere izan behar ditu ({value_length} ditu).', 'hy': 'Օգտանունը պետք է պարունակի առնվազն {min_length} նիշ (այն ունի {value_length})։', 'uz': "Foydalanuvchi nomida kamida {min_length} ta belgi bo'lishi kerak (unda {value_length} ta bor).", 'ta': 'பயனர்பெயர் குறைந்தது {min_length} எழுத்துக்களைக் கொண்டிருக்க வேண்டும் (அதில் {value_length} உள்ளது).', 'lv': {6: 'Lietotājvārdam jāsatur vismaz {min_length} rakstzīmes (tajā ir {value_length}).', 60: 'Lietotājvārdam jāsatur vismaz {min_length} rakstzīmju (tajā ir {value_length}).'}}
            _username_must_contain_at_most_max_length_characters_error_message_to_format_dict = {'en': 'Username must contain at most {max_length} characters (it has {value_length}).', 'fr': 'Le nom d’utilisateur doit contenir au maximum {max_length}\xa0caractères (il en contient {value_length}).', 'de': 'Der Benutzername darf höchstens {max_length} Zeichen (er hat {value_length}) enthalten.', 'es': 'El nombre de usuario debe contener como máximo {max_length} caracteres (tiene {value_length}).', 'pt': 'O nome do utilizador deve conter no máximo {max_length} caracteres (contém {value_length}).', 'it': 'Il nome utente deve contenere al massimo {max_length} caratteri (ha {value_length}).', 'nl': 'De gebruikersnaam mag maximaal {max_length} tekens bevatten (het bevat {value_length}).', 'ja': 'ユーザー名は最大 {max_length} 文字です（現在は {value_length} 文字です）。', 'ru': 'Имя пользователя должно содержать не более {max_length} символов (сейчас {value_length}).', 'zh': '使用者名稱最多只能包含 {max_length} 個字元（目前有 {value_length} 個）。', 'pl': 'Nazwa użytkownika może zawierać co najwyżej {max_length} znaków (obecnie ma {value_length}).', 'fa': 'نام کاربری باید حداکثر {max_length} نویسه داشته باشد (اکنون {value_length} نویسه دارد).', 'he': 'נא לוודא ששם המשתמש/ת מכיל {max_length} תווים לכל היותר (מכיל {value_length}).', 'ko': '사용자명에는 최대 {max_length}자의 문자가 포함되어야 합니다 ({value_length}자).', 'ar': ('يجب أن يحتوي اسم المستخدم على {max_length} حرف على الأكثر (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على حرف واحد على الأكثر (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على حرفين على الأكثر (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على {max_length} أحرف على الأكثر (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على {max_length} حرفًا على الأكثر (يحتوي على {value_length}).', 'يجب أن يحتوي اسم المستخدم على {max_length} حرف على الأكثر (يحتوي على {value_length}).'), 'id': 'Nama pengguna harus berisi paling banyak {max_length} karakter (memiliki {value_length}).', 'uk': 'Ім’я користувача має містити не більше {max_length} символів (воно має {value_length}).', 'tr': 'Kullanıcı adı en fazla {max_length} karakter içermelidir ({value_length} içerir).', 'vi': 'Tên người dùng phải chứa tối đa {max_length} ký tự (nó có {value_length}).', 'cs': 'Uživatelské jméno musí obsahovat maximálně {max_length} znaků (má {value_length}).', 'sv': 'Username måste innehålla minst {max_length} tecken (det har {value_length}).', 'fi': 'Käyttäjätunnuksessa saa olla enintään {max_length} merkkiä (sillä on {value_length}).', 'hu': 'A felhasználónév legfeljebb {max_length} karaktert tartalmazhat ({value_length} van benne).', 'th': 'ชื่อผู้ใช้ต้องมีอักขระไม่เกิน {max_length} ตัว (มี {value_length} ตัว)', 'el': 'Το όνομα χρήστη πρέπει να περιέχει το πολύ {max_length} χαρακτήρες (περιέχει {value_length}).', 'ms': 'Nama pengguna mesti mengandungi paling banyak {max_length} aksara (ia mempunyai {value_length}).', 'sr': 'Корисничко име мора да садржи највише {max_length} знакова (има {value_length}).', 'ro': 'Numele de utilizator trebuie să conțină cel mult {max_length} de caractere (are {value_length}).', 'bn': 'ব্যবহারকারীর নামে সর্বোচ্চ {max_length}টি অক্ষর থাকতে পারবে (এতে আছে {value_length}টি)।', 'ca': "El nom d'usuari ha de contenir com a màxim {max_length} caràcters (té {value_length}).", 'no': 'Brukernavnet må inneholde maksimalt {max_length} tegn (det har {value_length}).', 'bg': 'Потребителското име трябва да съдържа най-много {max_length} знака (има {value_length}).', 'da': 'Brugernavnet må højst indeholde {max_length} tegn (det har {value_length}).', 'sk': 'Používateľské meno musí obsahovať najviac {max_length} znakov (má {value_length}).', 'hi': 'उपयोगकर्ता नाम में अधिकतम {max_length} वर्ण होने चाहिए (इसमें {value_length} हैं)।', 'et': 'Kasutajanimi peab sisaldama kuni {max_length} tähemärki (selles on {value_length}).', 'hr': 'Korisničko ime mora sadržavati najviše {max_length} znakova (ima {value_length}).', 'az': 'İstifadəçi adı ən çox {max_length} simvol içərməlidir (onda {value_length} var).', 'zh-yue': '使用者名稱最多只可以有 {max_length} 個字符(而家有 {value_length} 個)。', 'lt': 'Naudotojo varde gali būti daugiausia {max_length} simbolių (jame yra {value_length}).', 'sl': 'Uporabniško ime lahko vsebuje največ {max_length} znakov (ima jih {value_length}).', 'eu': 'Erabiltzaile-izenak gehienez {max_length} karaktere izan behar ditu ({value_length} ditu).', 'hy': 'Օգտանունը պետք է պարունակի առավելագույնը {max_length} նիշ (այն ունի {value_length})։', 'uz': "Foydalanuvchi nomida ko'pi bilan {max_length} ta belgi bo'lishi kerak (unda {value_length} ta bor).", 'ta': 'பயனர்பெயர் அதிகபட்சம் {max_length} எழுத்துக்களைக் கொண்டிருக்க வேண்டும் (அதில் {value_length} உள்ளது).', 'lv': 'Lietotājvārdā drīkst būt ne vairāk kā {max_length} rakstzīmju (tajā ir {value_length}).'}
            _a_confirmation_message_was_sent_to_email_address_success_message_to_format_dict = {'en': 'A confirmation message was sent to {email_address}', 'fr': 'Un message de confirmation a été envoyé à {email_address}', 'de': 'Eine Bestätigungnachricht wurde gesendet an {email_address}', 'es': 'Se envió un mensaje de confirmación a {email_address}', 'pt': 'Uma mensagem de confirmação foi enviada para {email_address}', 'it': 'È stato inviato un messaggio di conferma a {email_address}', 'nl': 'Er is een bevestigingsbericht verzonden naar {email_address}', 'ja': '確認メッセージが {email_address} に送信されました', 'ru': 'Подтверждающее сообщение было отправлено на {email_address}.', 'zh': '已向...發送確認訊息{email_address}', 'pl': 'Wiadomość potwierdzająca została wysłana do {email_address}', 'fa': 'یک پیام تأیید به {email_address} ارسال شد', 'he': 'הודעת אימות נשלחה ל-\u200e{email_address}\u200e', 'ko': '확인 메시지를 {email_address}(으)로 보냈습니다', 'ar': 'تم إرسال رسالة تأكيد إلى {email_address}', 'id': 'Pesan konfirmasi telah dikirim ke {email_address}', 'uk': 'Повідомлення з підтвердженням надіслано на {email_address}', 'tr': '{email_address} adresine bir onay mesajı gönderildi', 'vi': 'Một tin nhắn xác nhận đã được gửi đến {email_address}', 'cs': 'Potvrzující zpráva byla odeslána na adresu {email_address}', 'sv': 'Ett bekräftelsemeddelande skickades till {email_address}', 'fi': 'Vahvistusviesti lähetettiin osoitteeseen {email_address}', 'hu': 'Megerősítő üzenetet küldtünk a következő címre: {email_address}', 'th': 'ข้อความยืนยันถูกส่งไปยัง {email_address}', 'el': 'Στάλθηκε ένα μήνυμα επιβεβαίωσης στη διεύθυνση {email_address}', 'ms': 'Mesej pengesahan telah dihantar ke {email_address}', 'sr': 'Порука за потврду је послата на {email_address}', 'ro': 'Un mesaj de confirmare a fost trimis la {email_address}', 'bn': '{email_address}-এ একটি নিশ্চিতকরণ বার্তা পাঠানো হয়েছে', 'ca': "S'ha enviat un missatge de confirmació a {email_address}", 'no': 'En bekreftelsesmelding ble sendt til {email_address}', 'bg': 'Изпратено е съобщение за потвърждение до {email_address}', 'da': 'En bekræftelsesmeddelelse blev sendt til {email_address}', 'sk': 'Potvrdzovacia správa bola odoslaná na {email_address}', 'hi': 'पुष्टिकरण संदेश भेजा गया {email_address}', 'et': 'Kinnitussõnum saadeti aadressile {email_address}', 'hr': 'Poruka potvrde poslana je na {email_address}', 'az': 'Təsdiq mesajı {email_address} ünvanına göndərildi.', 'zh-yue': '已向...傳送確認訊息{email_address}', 'lt': 'Patvirtinimo žinutė buvo išsiųsta adresu {email_address}', 'sl': 'Potrditveno sporočilo je bilo poslano na {email_address}', 'eu': 'Baieztapen-mezu bat bidali da {email_address} helbidera', 'hy': 'Հաստատման հաղորդագրություն է ուղարկվել {email_address} հասցեին', 'uz': 'Tasdiqlash xabari {email_address} ga yuborildi', 'ta': 'ஒரு உறுதிப்படுத்தல் செய்தி அனுப்பப்பட்டது {email_address}', 'lv': 'Apstiprinājuma ziņojums tika nosūtīts uz {email_address}'}

            _you_cant_change_your_username_error_message_dict_by_gender = {
                'en': {
                    **{gender: "You can't change your username." for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: 'Vous ne pouvez pas changer votre nom d’utilisateur.' for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Sie können Ihren Benutzernamen nicht ändern.' for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: 'No puedes cambiar tu nombre de usuario.' for gender in User.ALL_GENDERS},
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: 'Tu não podes alterar teu nome de utilizadora.',
                    User.GENDER_MALE_STRING: 'Tu não podes alterar teu nome de utilizador.',
                    User.GENDER_OTHER_STRING: 'Tu não podes alterar teu nome de utilizador.',
                },
                'it': {
                    **{gender: 'Non puoi modificare il tuo nome utente.' for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Jullie kunnen je gebruikersnaam niet wijzigen.' for gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{gender: 'ユーザー名は変更できません。' for gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{gender: 'Вы не можете изменить свое имя пользователя.' for gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{gender: '你無法更改使用者名稱。' for gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{gender: 'Nie możesz zmienić swojej nazwy użytkownika.' for gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{gender: 'شما نمی توانید نام کاربری خود را تغییر دهید.' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: 'לא ניתן לשנות שם משתמשת.',
                    User.GENDER_MALE_STRING: 'לא ניתן לשנות שם משתמש.',
                    User.GENDER_OTHER_STRING: 'לא ניתן לשנות שם משתמש/ת.',
                },
                'ko': {
                    **{gender: '사용자명은 변경할 수 없습니다.' for gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{gender: 'لا يمكنك تغيير اسم المستخدم الخاص بك.' for gender in User.ALL_GENDERS},
                },
                'id': {
                    **{gender: 'Anda tidak dapat mengubah nama pengguna Anda.' for gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{gender: "Ви не можете змінити своє ім'я користувача." for gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{gender: 'Kullanıcı adınızı değiştiremezsiniz.' for gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{gender: 'Bạn không thể thay đổi tên người dùng của mình.' for gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{gender: 'Nemůžete změnit své uživatelské jméno.' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Du kan inte ändra användarnamnet.' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Et voi vaihtaa käyttäjätunnustasi.' for gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{gender: 'A felhasználónevedet nem tudod megváltoztatni.' for gender in User.ALL_GENDERS},
                },
                'th': {
                    **{gender: 'คุณไม่สามารถเปลี่ยนชื่อผู้ใช้ของคุณได้' for gender in User.ALL_GENDERS},
                },
                'el': {
                    **{gender: 'Δεν μπορείτε να αλλάξετε το όνομα χρήστη σας.' for gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{gender: 'Anda tidak boleh menukar nama pengguna anda.' for gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{gender: 'Не можете променити своје корисничко име.' for gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{gender: 'Nu vă puteți schimba numele de utilizator.' for gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{gender: 'আপনি আপনার ব্যবহারকারীর নাম পরিবর্তন করতে পারবেন না.' for gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{gender: "No pots canviar el teu nom d'usuari." for gender in User.ALL_GENDERS},
                },
                'no': {
                    **{gender: 'Du kan ikke endre brukernavnet ditt.' for gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{gender: 'Не можете да промените потребителското си име.' for gender in User.ALL_GENDERS},
                },
                'da': {
                    **{gender: 'Du kan ikke ændre dit brugernavn.' for gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{gender: 'Používateľské meno si nemôžete zmeniť.' for gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{gender: 'आप अपना उपयोगकर्ता नाम नहीं बदल सकते.' for gender in User.ALL_GENDERS},
                },
                'et': {
                    **{gender: 'Te ei saa oma kasutajanime muuta.' for gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{gender: 'Ne možete promijeniti svoje korisničko ime.' for gender in User.ALL_GENDERS},
                },
                'az': {
                    **{gender: 'İstifadəçi adınızı dəyişə bilməzsiniz.' for gender in User.ALL_GENDERS},
                },
                'zh-yue': {
                    **{gender: '你無法更改使用者名稱。' for gender in User.ALL_GENDERS},
                },
                'lt': {
                    **{gender: 'Negalite pakeisti savo naudotojo vardo.' for gender in User.ALL_GENDERS},
                },
                'sl': {
                    **{gender: 'Svojega uporabniškega imena ne morete spremeniti.' for gender in User.ALL_GENDERS},
                },
                'eu': {
                    **{gender: 'Ezin duzu zure erabiltzaile-izena aldatu.' for gender in User.ALL_GENDERS},
                },
                'hy': {
                    **{gender: 'Դուք չեք կարող փոխել ձեր օգտանունը.' for gender in User.ALL_GENDERS},
                },
                'uz': {
                    **{gender: "Foydalanuvchi nomingizni o'zgartira olmaysiz." for gender in User.ALL_GENDERS},
                },
                'ta': {
                    **{gender: 'நீங்கள் உங்கள் பயனர்பெயரை மாற்ற முடியாது.' for gender in User.ALL_GENDERS},
                },
                'lv': {
                    **{gender: 'Jūs nevarat mainīt savu lietotājvārdu.' for gender in User.ALL_GENDERS},
                },
            }

            _youve_confirmed_your_email_address_success_message_dict_by_gender = {
                'en': {
                    **{gender: "You've confirmed your email address." for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: 'Vous avez confirmé votre adresse e-mail.' for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Sie haben Ihre E-Mail-Adresse bestätigt.' for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: 'Has confirmado tu dirección de correo electrónico.' for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: 'Tu confirmaste teu e-mail.' for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: 'Hai già confermato il tuo indirizzo e-mail.' for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Je hebt je e-mailadres bevestigd.' for gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{gender: 'メールアドレスを確認しました。' for gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{gender: 'Вы подтвердили свой адрес электронной почты.' for gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{gender: '您已確認您的電子郵件地址。' for gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{gender: 'Potwierdziłeś swój adres e-mail.' for gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{gender: 'شما آدرس ایمیل خود را تایید کرده اید.' for gender in User.ALL_GENDERS},
                },
                'he': {
                    **{gender: 'אימתת את כתובת הדואר האלקטרוני שלך.' for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: '귀하의 이메일 주소를 확인했습니다.' for gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{gender: 'لقد قمت بتأكيد عنوان بريدك الإلكتروني.' for gender in User.ALL_GENDERS},
                },
                'id': {
                    **{gender: 'Anda telah mengonfirmasi alamat email Anda.' for gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{gender: 'Ви підтвердили адресу електронної пошти.' for gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{gender: 'E-posta adresinizi onayladınız.' for gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{gender: 'Bạn đã xác nhận địa chỉ email của mình.' for gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{gender: 'Potvrdili jste svou e-mailovou adresu.' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Du har bekräftat din e-postadress.' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Olet vahvistanut sähköpostiosoitteesi.' for gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{gender: 'Megerősítette az e-mail címét.' for gender in User.ALL_GENDERS},
                },
                'th': {
                    **{gender: 'คุณได้ยืนยันที่อยู่อีเมลของคุณแล้ว' for gender in User.ALL_GENDERS},
                },
                'el': {
                    **{gender: 'Επιβεβαιώσατε τη διεύθυνση email σας.' for gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{gender: 'Anda telah mengesahkan alamat e-mel anda.' for gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{gender: 'Потврдили сте своју адресу е-поште.' for gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{gender: 'Ți-ai confirmat adresa de e-mail.' for gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{gender: 'আপনি আপনার ইমেল ঠিকানা নিশ্চিত করেছেন.' for gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{gender: 'Has confirmat la teva adreça de correu electrònic.' for gender in User.ALL_GENDERS},
                },
                'no': {
                    **{gender: 'Du har bekreftet e-postadressen din.' for gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{gender: 'Вие потвърдихте своя имейл адрес.' for gender in User.ALL_GENDERS},
                },
                'da': {
                    **{gender: 'Du har bekræftet din e-mailadresse.' for gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{gender: 'Potvrdili ste svoju e-mailovú adresu.' for gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{gender: 'आपने अपने ईमेल पते की पुष्टि कर दी है.' for gender in User.ALL_GENDERS},
                },
                'et': {
                    **{gender: 'Olete oma e-posti aadressi kinnitanud.' for gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{gender: 'Potvrdili ste svoju adresu e-pošte.' for gender in User.ALL_GENDERS},
                },
                'az': {
                    **{gender: 'E-poçt ünvanınızı təsdiqlədiniz.' for gender in User.ALL_GENDERS},
                },
                'zh-yue': {
                    **{gender: '您已確認您的電郵地址。' for gender in User.ALL_GENDERS},
                },
                'lt': {
                    **{gender: 'Patvirtinote savo el. pašto adresą.' for gender in User.ALL_GENDERS},
                },
                'sl': {
                    **{gender: 'Potrdili ste svoj e-poštni naslov.' for gender in User.ALL_GENDERS},
                },
                'eu': {
                    **{gender: 'Zure helbide elektronikoa baieztatu duzu.' for gender in User.ALL_GENDERS},
                },
                'hy': {
                    **{gender: 'Դուք հաստատել եք ձեր էլփոստի հասցեն.' for gender in User.ALL_GENDERS},
                },
                'uz': {
                    **{gender: 'Siz elektron pochta manzilingizni tasdiqladingiz.' for gender in User.ALL_GENDERS},
                },
                'ta': {
                    **{gender: 'நீங்கள் உங்கள் மின்னஞ்சல் முகவரியை உறுதிப்படுத்தியுள்ளீர்கள்.' for gender in User.ALL_GENDERS},
                },
                'lv': {
                    **{gender: 'Jūsu e-pasta adrese ir apstiprināta.' for gender in User.ALL_GENDERS},
                },
            }

            _confirm_your_email_address_on_speedy_net_subject_dict_by_gender = {
                'en': {
                    **{gender: 'Confirm your email address on Speedy Net' for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: 'Confirmez votre adresse e-mail sur Speedy Net' for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Bestätigen Sie Ihre E-Mail-Adresse auf Speedy Net' for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: 'Confirma tu dirección de correo electrónico en Speedy Net' for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: 'Confirma o teu endereço de e-mail em Speedy Net' for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: 'Confermato il tuo indirizzo e-mail su Speedy Net' for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Bevestig je e-mailadres op Speedy Net' for gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{gender: 'Speedy Net でメールアドレスを確認してください' for gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{gender: 'Подтвердите свой адрес электронной почты в Speedy Net' for gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{gender: '請在 Speedy Net 上確認您的電子郵件地址' for gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{gender: 'Potwierdź swój adres e-mail w Speedy Net' for gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{gender: 'نشانی ایمیل خود را در Speedy Net تأیید کنید' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: 'אמתי את כתובת הדואר האלקטרוני שלך בספידי נט',
                    User.GENDER_MALE_STRING: 'אמת את כתובת הדואר האלקטרוני שלך בספידי נט',
                    User.GENDER_OTHER_STRING: 'אמת/י את כתובת הדואר האלקטרוני שלך בספידי נט',
                },
                'ko': {
                    **{gender: '다음에서 이메일 주소 확인 Speedy Net' for gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{gender: 'قم بتأكيد عنوان بريدك الإلكتروني على Speedy Net' for gender in User.ALL_GENDERS},
                },
                'id': {
                    **{gender: 'Konfirmasikan alamat email Anda di Speedy Net' for gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{gender: 'Підтвердьте свою електронну адресу на Speedy Net' for gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{gender: "E-posta adresinizi Speedy Net'da doğrulayın" for gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{gender: 'Xác nhận địa chỉ email của bạn trên Speedy Net' for gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{gender: 'Potvrďte svou e-mailovou adresu na Speedy Net' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Bekräfta e-postadressen på Speedy Net' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Vahvista sähköpostiosoitteesi Speedy Net' for gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{gender: 'Erősítse meg e-mail címét a(z) Speedy Net oldalon' for gender in User.ALL_GENDERS},
                },
                'th': {
                    **{gender: 'ยืนยันที่อยู่อีเมลของคุณบน Speedy Net' for gender in User.ALL_GENDERS},
                },
                'el': {
                    **{gender: 'Επιβεβαιώστε τη διεύθυνση email σας στο Speedy Net' for gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{gender: 'Sahkan alamat e-mel anda pada Speedy Net' for gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{gender: 'Потврдите своју адресу е-поште на Speedy Net' for gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{gender: 'Confirmați-vă adresa de e-mail pe Speedy Net' for gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{gender: 'Speedy Net-এ আপনার ইমেল ঠিকানা নিশ্চিত করুন' for gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{gender: 'Confirma la teva adreça de correu electrònic a Speedy Net' for gender in User.ALL_GENDERS},
                },
                'no': {
                    **{gender: 'Bekreft e-postadressen din på Speedy Net' for gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{gender: 'Потвърдете своя имейл адрес на Speedy Net' for gender in User.ALL_GENDERS},
                },
                'da': {
                    **{gender: 'Bekræft din e-mailadresse på Speedy Net' for gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{gender: 'Potvrďte svoju e-mailovú adresu na Speedy Net' for gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{gender: 'अपना ईईमेल पता सत्यापित करें Speedy Net' for gender in User.ALL_GENDERS},
                },
                'et': {
                    **{gender: 'Kinnitage oma e-posti aadress aadressil Speedy Net' for gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{gender: 'Potvrdite svoju adresu e-pošte na Speedy Net' for gender in User.ALL_GENDERS},
                },
                'az': {
                    **{gender: 'Speedy Net-də e-poçt ünvanınızı təsdiqləyin' for gender in User.ALL_GENDERS},
                },
                'zh-yue': {
                    **{gender: '請喺 Speedy Net 度確認你嘅電郵地址' for gender in User.ALL_GENDERS},
                },
                'lt': {
                    **{gender: 'Patvirtinkite savo el. pašto adresą svetainėje Speedy Net' for gender in User.ALL_GENDERS},
                },
                'sl': {
                    **{gender: 'Potrdite svoj e-poštni naslov na Speedy Net' for gender in User.ALL_GENDERS},
                },
                'eu': {
                    **{gender: 'Baieztatu zure helbide elektronikoa Speedy Net webgunean' for gender in User.ALL_GENDERS},
                },
                'hy': {
                    **{gender: 'Հաստատեք ձեր էլփոստի հասցեն Speedy Net-ում' for gender in User.ALL_GENDERS},
                },
                'uz': {
                    **{gender: 'Speedy Net da elektron pochta manzilingizni tasdiqlang' for gender in User.ALL_GENDERS},
                },
                'ta': {
                    **{gender: 'உங்கள் மின்னஞ்சல் முகவரியை உறுதிப்படுத்தவும் Speedy Net' for gender in User.ALL_GENDERS},
                },
                'lv': {
                    **{gender: 'Apstipriniet savu e-pasta adresi vietnē Speedy Net' for gender in User.ALL_GENDERS},
                },
            }

            _confirm_your_email_address_on_speedy_match_subject_dict_by_gender = {
                'en': {
                    **{gender: 'Confirm your email address on Speedy Match' for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: 'Confirmez votre adresse e-mail sur Speedy Match' for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Bestätigen Sie Ihre E-Mail-Adresse auf Speedy Match' for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: 'Confirma tu dirección de correo electrónico en Speedy Match' for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: 'Confirma o teu endereço de e-mail em Speedy Match' for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: 'Confermato il tuo indirizzo e-mail su Speedy Match' for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Bevestig je e-mailadres op Speedy Match' for gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{gender: 'Speedy Match でメールアドレスを確認してください' for gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{gender: 'Подтвердите свой адрес электронной почты в Speedy Match' for gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{gender: '請在 Speedy Match 上確認您的電子郵件地址' for gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{gender: 'Potwierdź swój adres e-mail w Speedy Match' for gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{gender: 'نشانی ایمیل خود را در Speedy Match تأیید کنید' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "אמתי את כתובת הדואר האלקטרוני שלך בספידי מץ'",
                    User.GENDER_MALE_STRING: "אמת את כתובת הדואר האלקטרוני שלך בספידי מץ'",
                    User.GENDER_OTHER_STRING: "אמת/י את כתובת הדואר האלקטרוני שלך בספידי מץ'",
                },
                'ko': {
                    **{gender: '다음에서 이메일 주소 확인 Speedy Match' for gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{gender: 'قم بتأكيد عنوان بريدك الإلكتروني على Speedy Match' for gender in User.ALL_GENDERS},
                },
                'id': {
                    **{gender: 'Konfirmasikan alamat email Anda di Speedy Match' for gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{gender: 'Підтвердьте свою електронну адресу на Speedy Match' for gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{gender: "E-posta adresinizi Speedy Match'da doğrulayın" for gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{gender: 'Xác nhận địa chỉ email của bạn trên Speedy Match' for gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{gender: 'Potvrďte svou e-mailovou adresu na Speedy Match' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Bekräfta e-postadressen på Speedy Match' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Vahvista sähköpostiosoitteesi Speedy Match' for gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{gender: 'Erősítse meg e-mail címét a(z) Speedy Match oldalon' for gender in User.ALL_GENDERS},
                },
                'th': {
                    **{gender: 'ยืนยันที่อยู่อีเมลของคุณบน Speedy Match' for gender in User.ALL_GENDERS},
                },
                'el': {
                    **{gender: 'Επιβεβαιώστε τη διεύθυνση email σας στο Speedy Match' for gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{gender: 'Sahkan alamat e-mel anda pada Speedy Match' for gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{gender: 'Потврдите своју адресу е-поште на Speedy Match' for gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{gender: 'Confirmați-vă adresa de e-mail pe Speedy Match' for gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{gender: 'Speedy Match-এ আপনার ইমেল ঠিকানা নিশ্চিত করুন' for gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{gender: 'Confirma la teva adreça de correu electrònic a Speedy Match' for gender in User.ALL_GENDERS},
                },
                'no': {
                    **{gender: 'Bekreft e-postadressen din på Speedy Match' for gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{gender: 'Потвърдете своя имейл адрес на Speedy Match' for gender in User.ALL_GENDERS},
                },
                'da': {
                    **{gender: 'Bekræft din e-mailadresse på Speedy Match' for gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{gender: 'Potvrďte svoju e-mailovú adresu na Speedy Match' for gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{gender: 'अपना ईईमेल पता सत्यापित करें Speedy Match' for gender in User.ALL_GENDERS},
                },
                'et': {
                    **{gender: 'Kinnitage oma e-posti aadress aadressil Speedy Match' for gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{gender: 'Potvrdite svoju adresu e-pošte na Speedy Match' for gender in User.ALL_GENDERS},
                },
                'az': {
                    **{gender: 'Speedy Match-də e-poçt ünvanınızı təsdiqləyin' for gender in User.ALL_GENDERS},
                },
                'zh-yue': {
                    **{gender: '請喺 Speedy Match 度確認你嘅電郵地址' for gender in User.ALL_GENDERS},
                },
                'lt': {
                    **{gender: 'Patvirtinkite savo el. pašto adresą svetainėje Speedy Match' for gender in User.ALL_GENDERS},
                },
                'sl': {
                    **{gender: 'Potrdite svoj e-poštni naslov na Speedy Match' for gender in User.ALL_GENDERS},
                },
                'eu': {
                    **{gender: 'Baieztatu zure helbide elektronikoa Speedy Match webgunean' for gender in User.ALL_GENDERS},
                },
                'hy': {
                    **{gender: 'Հաստատեք ձեր էլփոստի հասցեն Speedy Match-ում' for gender in User.ALL_GENDERS},
                },
                'uz': {
                    **{gender: 'Speedy Match da elektron pochta manzilingizni tasdiqlang' for gender in User.ALL_GENDERS},
                },
                'ta': {
                    **{gender: 'உங்கள் மின்னஞ்சல் முகவரியை உறுதிப்படுத்தவும் Speedy Match' for gender in User.ALL_GENDERS},
                },
                'lv': {
                    **{gender: 'Apstipriniet savu e-pasta adresi vietnē Speedy Match' for gender in User.ALL_GENDERS},
                },
            }

            self._this_field_cannot_be_null_error_message = _this_field_cannot_be_null_error_message_dict[self.language_code]
            self._this_field_cannot_be_blank_error_message = _this_field_cannot_be_blank_error_message_dict[self.language_code]
            self._id_contains_illegal_characters_error_message = _id_contains_illegal_characters_error_message_dict[self.language_code]
            self._value_must_be_valid_json_error_message = _value_must_be_valid_json_error_message_dict[self.language_code]
            self._invalid_password_error_message = _invalid_password_error_message_dict[self.language_code]
            self._password_too_short_error_message = _password_too_short_error_message_dict[self.language_code]
            self._password_too_long_error_message = _password_too_long_error_message_dict[self.language_code]
            self._your_password_must_contain_at_least_6_unique_characters_error_message = _your_password_must_contain_at_least_6_unique_characters_error_message_dict[self.language_code]
            self._this_username_is_already_taken_error_message = _this_username_is_already_taken_error_message_dict[self.language_code]
            self._enter_a_valid_email_address_error_message = _enter_a_valid_email_address_error_message_dict[self.language_code]
            self._this_email_is_already_in_use_error_message = _this_email_is_already_in_use_error_message_dict[self.language_code]
            self._enter_a_valid_date_error_message = _enter_a_valid_date_error_message_dict[self.language_code]
            self._please_enter_a_correct_username_and_password_error_message = _please_enter_a_correct_username_and_password_error_message_dict[self.language_code]
            self._your_old_password_was_entered_incorrectly_error_message = _your_old_password_was_entered_incorrectly_error_message_dict[self.language_code]
            self._the_two_password_fields_didnt_match_error_message = _the_two_password_fields_didnt_match_error_message_dict[self.language_code]
            self._entity_username_must_start_with_4_or_more_letters_error_message = _entity_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]
            self._user_username_must_start_with_4_or_more_letters_error_message = _user_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]
            self._slug_does_not_parse_to_username_error_message = _slug_does_not_parse_to_username_error_message_dict[self.language_code]
            self._youve_already_confirmed_this_email_address_error_message = _youve_already_confirmed_this_email_address_error_message_dict[self.language_code]
            self._invalid_confirmation_link_error_message = _invalid_confirmation_link_error_message_dict[self.language_code]
            self._username_is_required_error_message = _username_is_required_error_message_dict[self.language_code]
            self._ensure_this_value_is_greater_than_or_equal_to_minus_32768_error_message = _ensure_this_value_is_greater_than_or_equal_to_minus_32768_error_message_dict[self.language_code]
            self._ensure_this_value_is_less_than_or_equal_to_32767_error_message = _ensure_this_value_is_less_than_or_equal_to_32767_error_message_dict[self.language_code]
            self._value_too_long_for_type_character_varying_255_error_message = _value_too_long_for_type_character_varying_255_error_message_dict[self.language_code]
            self._superuser_must_be_equal_to_staff_error_message = _superuser_must_be_equal_to_staff_error_message_dict[self.language_code]
            self._the_email_address_was_deleted_success_message = _the_email_address_was_deleted_success_message_dict[self.language_code]
            self._you_have_changed_your_primary_email_address_success_message = _you_have_changed_your_primary_email_address_success_message_dict[self.language_code]
            self._password_reset_on_speedy_net_subject = _password_reset_on_speedy_net_subject_dict[self.language_code]
            self._password_reset_on_speedy_match_subject = _password_reset_on_speedy_match_subject_dict[self.language_code]
            self._speedy_net_deleted_user_name = _speedy_net_deleted_user_name_dict[self.language_code]
            self._speedy_match_deleted_user_name = _speedy_match_deleted_user_name_dict[self.language_code]
            self._edit_profile_text = _edit_profile_text_dict[self.language_code]

            self._value_is_not_a_valid_choice_error_message_to_format = _value_is_not_a_valid_choice_error_message_to_format_dict[self.language_code]
            self._value_must_be_an_integer_error_message_to_format = _value_must_be_an_integer_error_message_to_format_dict[self.language_code]
            self._username_must_contain_at_least_min_length_alphanumeric_characters_error_message_to_format = _username_must_contain_at_least_min_length_alphanumeric_characters_error_message_to_format_dict[self.language_code]
            self._username_must_contain_at_most_max_length_alphanumeric_characters_error_message_to_format = _username_must_contain_at_most_max_length_alphanumeric_characters_error_message_to_format_dict[self.language_code]
            self._username_must_contain_at_least_min_length_characters_error_message_to_format = _username_must_contain_at_least_min_length_characters_error_message_to_format_dict[self.language_code]
            self._username_must_contain_at_most_max_length_characters_error_message_to_format = _username_must_contain_at_most_max_length_characters_error_message_to_format_dict[self.language_code]
            self._a_confirmation_message_was_sent_to_email_address_success_message_to_format = _a_confirmation_message_was_sent_to_email_address_success_message_to_format_dict[self.language_code]

            self._you_cant_change_your_username_error_message_dict_by_gender = _you_cant_change_your_username_error_message_dict_by_gender[self.language_code]
            self._youve_confirmed_your_email_address_success_message_dict_by_gender = _youve_confirmed_your_email_address_success_message_dict_by_gender[self.language_code]
            self._confirm_your_email_address_on_speedy_net_subject_dict_by_gender = _confirm_your_email_address_on_speedy_net_subject_dict_by_gender[self.language_code]
            self._confirm_your_email_address_on_speedy_match_subject_dict_by_gender = _confirm_your_email_address_on_speedy_match_subject_dict_by_gender[self.language_code]

            self.assertSetEqual(set1=set(self._you_cant_change_your_username_error_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._youve_confirmed_your_email_address_success_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._confirm_your_email_address_on_speedy_net_subject_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._confirm_your_email_address_on_speedy_match_subject_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))

            self.assertEqual(first=len(set(self._you_cant_change_your_username_error_message_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._youve_confirmed_your_email_address_success_message_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._confirm_your_email_address_on_speedy_net_subject_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._confirm_your_email_address_on_speedy_match_subject_dict_by_gender.keys())), second=3)

            self.assertEqual(first=len(set(self._user_all_the_required_fields_keys())), second=51)
            self.assertSetEqual(set1=set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None).keys()), set2=set(self._user_all_the_required_fields_keys()))
            self.assertEqual(first=len(set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None).keys())), second=51)
            self.assertEqual(first=len(set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None).keys()) - set(self._user_all_the_required_fields_keys())), second=0)
            self.assertSetEqual(set1=set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None).keys()), set2=set(self._user_all_the_required_fields_keys()) | {'first_name_en', 'first_name_he'})
            self.assertSetEqual(set1=set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value='').keys()), set2=set(self._user_all_the_required_fields_keys()))
            self.assertEqual(first=len(set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value='').keys())), second=51)
            self.assertEqual(first=len(set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value='').keys()) - set(self._user_all_the_required_fields_keys())), second=0)
            self.assertSetEqual(set1=set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value='').keys()), set2=set(self._user_all_the_required_fields_keys()) | {'first_name_en', 'first_name_he'})
            self.assertListEqual(list1=self._profile_form_all_the_required_fields_keys(), list2=[field_name for field_name in self._registration_form_all_the_required_fields_keys() if (not (field_name in ['email', 'new_password1']))])
            self.assertSetEqual(set1=set(self._registration_form_all_the_required_fields_keys()) - {'email', 'new_password1'}, set2=set(self._profile_form_all_the_required_fields_keys()))
            self.assertSetEqual(set1=set(self._profile_form_all_the_required_fields_keys()) | {'email', 'new_password1'}, set2=set(self._registration_form_all_the_required_fields_keys()))
            self.assertNotEqual(first=[to_attribute(name='first_name')], second=['first_name'])
            self.assertNotEqual(first=[to_attribute(name='first_name'), to_attribute(name='last_name')], second=['first_name', 'last_name'])
            self.assertListEqual(list1=self._user_all_the_required_fields_keys()[:len(django_settings.LANGUAGES)], list2=[to_attribute(name='first_name', language_code=language_code) for language_code, language_name in django_settings.LANGUAGES])
            self.assertListEqual(list1=self._user_all_the_required_fields_keys()[:len(django_settings.LANGUAGES)], list2=[to_attribute(name='first_name', language_code='en'), to_attribute(name='first_name', language_code='fr'), to_attribute(name='first_name', language_code='de'), to_attribute(name='first_name', language_code='es'), to_attribute(name='first_name', language_code='pt'), to_attribute(name='first_name', language_code='it'), to_attribute(name='first_name', language_code='nl'), to_attribute(name='first_name', language_code='ja'), to_attribute(name='first_name', language_code='ru'), to_attribute(name='first_name', language_code='zh'), to_attribute(name='first_name', language_code='pl'), to_attribute(name='first_name', language_code='fa'), to_attribute(name='first_name', language_code='he'), to_attribute(name='first_name', language_code='ko'), to_attribute(name='first_name', language_code='ar'), to_attribute(name='first_name', language_code='id'), to_attribute(name='first_name', language_code='uk'), to_attribute(name='first_name', language_code='tr'), to_attribute(name='first_name', language_code='vi'), to_attribute(name='first_name', language_code='cs'), to_attribute(name='first_name', language_code='sv'), to_attribute(name='first_name', language_code='fi'), to_attribute(name='first_name', language_code='hu'), to_attribute(name='first_name', language_code='th'), to_attribute(name='first_name', language_code='el'), to_attribute(name='first_name', language_code='ms'), to_attribute(name='first_name', language_code='sr'), to_attribute(name='first_name', language_code='ro'), to_attribute(name='first_name', language_code='bn'), to_attribute(name='first_name', language_code='ca'), to_attribute(name='first_name', language_code='no'), to_attribute(name='first_name', language_code='bg'), to_attribute(name='first_name', language_code='da'), to_attribute(name='first_name', language_code='sk'), to_attribute(name='first_name', language_code='hi'), to_attribute(name='first_name', language_code='et'), to_attribute(name='first_name', language_code='hr'), to_attribute(name='first_name', language_code='az'), to_attribute(name='first_name', language_code='zh-yue'), to_attribute(name='first_name', language_code='lt'), to_attribute(name='first_name', language_code='sl'), to_attribute(name='first_name', language_code='eu'), to_attribute(name='first_name', language_code='hy'), to_attribute(name='first_name', language_code='uz'), to_attribute(name='first_name', language_code='ta'), to_attribute(name='first_name', language_code='lv')])
            self.assertListEqual(list1=self._user_all_the_required_fields_keys()[:len(django_settings.LANGUAGES)], list2=['first_name_en', 'first_name_fr', 'first_name_de', 'first_name_es', 'first_name_pt', 'first_name_it', 'first_name_nl', 'first_name_ja', 'first_name_ru', 'first_name_zh', 'first_name_pl', 'first_name_fa', 'first_name_he', 'first_name_ko', 'first_name_ar', 'first_name_id', 'first_name_uk', 'first_name_tr', 'first_name_vi', 'first_name_cs', 'first_name_sv', 'first_name_fi', 'first_name_hu', 'first_name_th', 'first_name_el', 'first_name_ms', 'first_name_sr', 'first_name_ro', 'first_name_bn', 'first_name_ca', 'first_name_no', 'first_name_bg', 'first_name_da', 'first_name_sk', 'first_name_hi', 'first_name_et', 'first_name_hr', 'first_name_az', 'first_name_zh_yue', 'first_name_lt', 'first_name_sl', 'first_name_eu', 'first_name_hy', 'first_name_uz', 'first_name_ta', 'first_name_lv'])
            self.assertListEqual(list1=self._registration_form_all_the_required_fields_keys()[:1], list2=[to_attribute(name='first_name')])
            self.assertListEqual(list1=self._profile_form_all_the_required_fields_keys()[:1], list2=[to_attribute(name='first_name')])

        def assert_required_fields_and_errors_dict(self, required_fields, errors_dict):
            """
            Asserts that errors_dict's keys exactly match required_fields, and that errors_dict equals the "this field is required" errors dict built from required_fields.

            :param required_fields: The expected required field names.
            :type required_fields: list
            :param errors_dict: The actual errors dict to check.
            :type errors_dict: dict
            """
            self.assertSetEqual(set1=set(errors_dict.keys()), set2=set(required_fields))
            self.assertDictEqual(d1=errors_dict, d2=self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=required_fields))

        def assert_registration_form_required_fields(self, required_fields):
            """
            Asserts that required_fields are exactly the registration form's required fields, each mapped to a "this field is required" error.

            :param required_fields: The expected required field names.
            :type required_fields: list
            """
            self.assert_required_fields_and_errors_dict(required_fields=required_fields, errors_dict=self._registration_form_all_the_required_fields_are_required_errors_dict())

        def assert_profile_form_required_fields(self, required_fields):
            """
            Asserts that required_fields are exactly the profile form's required fields, each mapped to a "this field is required" error.

            :param required_fields: The expected required field names.
            :type required_fields: list
            """
            self.assert_required_fields_and_errors_dict(required_fields=required_fields, errors_dict=self._profile_form_all_the_required_fields_are_required_errors_dict())


