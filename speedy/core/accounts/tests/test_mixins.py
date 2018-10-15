# from datetime import date
# from dateutil.relativedelta import relativedelta
#
#
# class TestsDynamicSettingsMixin(object):
#     @staticmethod
#     def _valid_date_of_birth_list():
#         return [
#             '1904-02-29',
#             '1980-01-31',
#             '1999-12-01',
#             '2000-02-29',
#             '2004-02-29',
#             '2018-10-15',
#         ]
#
#     @staticmethod
#     def _invalid_date_of_birth_list(self):
#         today = date.today()
#         return [
#             '1900-02-29',
#             '1901-02-29',
#             '1980-02-31',
#             '1980-02-99',
#             '1980-02-00',
#             '1980-02-001',
#             '1999-00-01',
#             '1999-13-01',
#             '2001-02-29',
#             '2018-10-16',
#             '2019-01-01',
#             '3000-01-01',
#             '1769-01-01',
#             '1768-01-01',
#             '1000-01-01',
#             '1-01-01',
#             str(today + relativedelta(days=1)),
#             str(today - relativedelta(years=250)),
#             str(today),
#             str(today - relativedelta(years=250) + relativedelta(days=1)),
#             'a',
#             '',
#         ]
#
#
class ErrorsMixin(object):
    # _this_field_is_required_error_message = 'This field is required.'
    # _this_field_cannot_be_null_error_message = 'This field cannot be null.'
    # _this_field_cannot_be_blank_error_message = 'This field cannot be blank.'
    # _id_contains_illegal_characters_error_message = 'id contains illegal characters.'
    # _value_must_be_valid_json_error_message = 'Value must be valid JSON.'
    # _invalid_password_error_message = 'Invalid password.'
    # _password_too_short_error_message = 'Password too short.'
    # _password_too_long_error_message = 'Password too long.'
    # _you_cant_change_your_username_error_message = "You can't change your username."
    # _this_username_is_already_taken_error_message = 'This username is already taken.'
    # _enter_a_valid_email_address_error_message = 'Enter a valid email address.'
    # _this_email_is_already_in_use_error_message = 'This email is already in use.'
    # _enter_a_valid_date_error_message = 'Enter a valid date.'
    # _please_enter_a_correct_username_and_password_error_message = 'Please enter a correct username and password. Note that both fields may be case-sensitive.'
    # _your_old_password_was_entered_incorrectly_error_message = 'Your old password was entered incorrectly. Please enter it again.'
    # _the_two_password_fields_didnt_match_error_message = "The two password fields didn't match."
    # _entity_username_must_start_with_4_or_more_letters_error_message = 'Username must start with 4 or more letters, and may contain letters, digits or dashes.'
    # _user_username_must_start_with_4_or_more_letters_error_message = 'Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'
    # _slug_does_not_parse_to_username_error_message = 'Slug does not parse to username.'

    _this_field_is_required_error_message_dict = {'en': 'This field is required.', 'he': 'יש להזין תוכן בשדה זה.'}
    _this_field_cannot_be_null_error_message_dict = {'en': 'This field cannot be null.', 'he': '___This field cannot be null.'}
    _this_field_cannot_be_blank_error_message_dict = {'en': 'This field cannot be blank.', 'he': '___This field cannot be blank.'}
    _id_contains_illegal_characters_error_message_dict = {'en': 'id contains illegal characters.', 'he': '___id contains illegal characters.'}
    _value_must_be_valid_json_error_message_dict = {'en': 'Value must be valid JSON.', 'he': '___Value must be valid JSON.'}
    _invalid_password_error_message_dict = {'en': 'Invalid password.', 'he': '___Invalid password.'}
    _password_too_short_error_message_dict = {'en': 'Password too short.', 'he': 'הסיסמה קצרה מדי.'}
    _password_too_long_error_message_dict = {'en': 'Password too long.', 'he': 'הסיסמה ארוכה מדי.'}
    _you_cant_change_your_username_error_message_dict = {'en': "You can't change your username.", 'he': '___You can\'t change your username.'}
    _this_username_is_already_taken_error_message_dict = {'en': 'This username is already taken.', 'he': 'שם המשתמש/ת הזה כבר תפוס.'}
    _enter_a_valid_email_address_error_message_dict = {'en': 'Enter a valid email address.', 'he': 'נא להזין כתובת דוא"ל חוקית'}
    _this_email_is_already_in_use_error_message_dict = {'en': 'This email is already in use.', 'he': 'הדואר האלקטרוני הזה כבר נמצא בשימוש.'}
    _enter_a_valid_date_error_message_dict = {'en': 'Enter a valid date.', 'he': 'יש להזין תאריך חוקי.'}
    _please_enter_a_correct_username_and_password_error_message_dict = {'en': 'Please enter a correct username and password. Note that both fields may be case-sensitive.', 'he': '___Please enter a correct username and password. Note that both fields may be case-sensitive.'}
    _your_old_password_was_entered_incorrectly_error_message_dict = {'en': 'Your old password was entered incorrectly. Please enter it again.', 'he': '___Your old password was entered incorrectly. Please enter it again.'}
    _the_two_password_fields_didnt_match_error_message_dict = {'en': "The two password fields didn't match.", 'he': '___The two password fields didn\'t match.'}
    _entity_username_must_start_with_4_or_more_letters_error_message_dict = {'en': 'Username must start with 4 or more letters, and may contain letters, digits or dashes.', 'he': '___Username must start with 4 or more letters, and may contain letters, digits or dashes.'}
    _user_username_must_start_with_4_or_more_letters_error_message_dict = {'en': 'Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.', 'he': '___Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'}
    _slug_does_not_parse_to_username_error_message_dict = {'en': 'Slug does not parse to username.', 'he': '___Slug does not parse to username.'}

    _ensure_this_value_has_at_least_min_length_characters_error_message_dict_by_min_length_and_value_length = {'en': 'Ensure this value has at least {min_length} characters (it has {value_length}).', 'he': 'נא לוודא שערך זה מכיל {min_length} תווים לכל הפחות (מכיל {value_length}).'}
    _ensure_this_value_has_at_most_max_length_characters_error_message_dict_by_max_length_and_value_length = {'en': 'Ensure this value has at most {max_length} characters (it has {value_length}).', 'he': 'נא לוודא שערך זה מכיל {max_length} תווים לכל היותר (מכיל {value_length}).'}

    def _registration_form_all_the_required_fields_keys(self):
        return [field_name.format(language_code=self.language_code) for field_name in ['first_name_{language_code}', 'last_name_{language_code}', 'email', 'slug', 'new_password1', 'gender', 'date_of_birth']]

    def _profile_form_all_the_required_fields_keys(self):
        return [field_name.format(language_code=self.language_code) for field_name in ['first_name_{language_code}', 'last_name_{language_code}', 'slug', 'gender', 'date_of_birth']]

    def _registration_form_all_the_required_fields_are_required_errors_dict(self):
        return {field_name: [self._this_field_is_required_error_message_dict[self.language_code]] for field_name in self._registration_form_all_the_required_fields_keys()}

    def _profile_form_all_the_required_fields_are_required_errors_dict(self):
        return {field_name: [self._this_field_is_required_error_message_dict[self.language_code]] for field_name in self._profile_form_all_the_required_fields_keys()}

    def _cannot_create_user_without_all_the_required_fields_errors_dict(self):
        return {'first_name': [self._this_field_cannot_be_blank_error_message_dict[self.language_code]], 'last_name': [self._this_field_cannot_be_blank_error_message_dict[self.language_code]], 'username': [self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=0)], 'slug': [self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=0)], 'password': [self._this_field_cannot_be_blank_error_message_dict[self.language_code]], 'gender': [self._this_field_cannot_be_null_error_message_dict[self.language_code]], 'date_of_birth': [self._this_field_cannot_be_null_error_message_dict[self.language_code]]}

    def _cannot_create_user_email_address_without_all_the_required_fields_errors_dict(self):
        return {'user': [self._this_field_cannot_be_null_error_message_dict[self.language_code]], 'email': [self._this_field_cannot_be_blank_error_message_dict[self.language_code]]}

    def _id_contains_illegal_characters_errors_dict(self):
        return {'id': [self._id_contains_illegal_characters_error_message_dict[self.language_code]]}

    def _please_enter_a_correct_username_and_password_errors_dict(self):
        return {'__all__': [self._please_enter_a_correct_username_and_password_error_message_dict[self.language_code]]}

    def _invalid_password_errors_dict(self):
        return {'password': [self._invalid_password_error_message_dict[self.language_code]]}

    def _password_too_short_errors_dict(self):
        return {'new_password1': [self._password_too_short_error_message_dict[self.language_code]]}

    def _password_too_long_errors_dict(self):
        return {'new_password1': [self._password_too_long_error_message_dict[self.language_code]]}

    def _your_old_password_was_entered_incorrectly_errors_dict(self):
        return {'old_password': [self._your_old_password_was_entered_incorrectly_error_message_dict[self.language_code]]}

    def _the_two_password_fields_didnt_match_errors_dict(self):
        return {'new_password2': [self._the_two_password_fields_didnt_match_error_message_dict[self.language_code]]}

    def _enter_a_valid_email_address_errors_dict(self):
        return {'email': [self._enter_a_valid_email_address_error_message_dict[self.language_code]]}

    def _this_email_is_already_in_use_errors_dict(self):
        return {'email': [self._this_email_is_already_in_use_error_message_dict[self.language_code]]}

    def _enter_a_valid_date_errors_dict(self):
        return {'date_of_birth': [self._enter_a_valid_date_error_message_dict[self.language_code]]}

    def _you_cant_change_your_username_errors_dict(self):
        return {'slug': [self._you_cant_change_your_username_error_message_dict[self.language_code]]}

    def _slug_this_username_is_already_taken_errors_dict(self):
        return {'slug': [self._this_username_is_already_taken_error_message_dict[self.language_code]]}

    def _slug_and_username_this_username_is_already_taken_errors_dict(self):
        return {'username': [self._this_username_is_already_taken_error_message_dict[self.language_code]], 'slug': [self._this_username_is_already_taken_error_message_dict[self.language_code]]}

    def _entity_slug_and_username_username_must_start_with_4_or_more_letters_errors_dict(self):
        return {'username': [self._entity_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]], 'slug': [self._entity_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]]}

    def _entity_username_username_must_start_with_4_or_more_letters_errors_dict(self):
        return {'username': [self._entity_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]]}

    def _entity_slug_username_must_start_with_4_or_more_letters_errors_dict(self):
        return {'slug': [self._entity_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]]}

    def _user_slug_and_username_username_must_start_with_4_or_more_letters_errors_dict(self):
        return {'username': [self._user_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]], 'slug': [self._user_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]]}

    def _user_username_username_must_start_with_4_or_more_letters_errors_dict(self):
        return {'username': [self._user_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]]}

    def _user_slug_username_must_start_with_4_or_more_letters_errors_dict(self):
        return {'slug': [self._user_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]]}

    def _slug_does_not_parse_to_username_errors_dict(self):
        return {'slug': [self._slug_does_not_parse_to_username_error_message_dict[self.language_code]]}

    def _entity_username_must_start_with_4_or_more_letters_and_slug_does_not_parse_to_username_errors_dict(self):
        return {'username': [self._entity_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]], 'slug': [self._slug_does_not_parse_to_username_error_message_dict[self.language_code]]}

    def _user_username_must_start_with_4_or_more_letters_and_slug_does_not_parse_to_username_errors_dict(self):
        return {'username': [self._user_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]], 'slug': [self._slug_does_not_parse_to_username_error_message_dict[self.language_code]]}

    # @staticmethod
    def _value_is_not_a_valid_choice_error_message_by_value(self, value):
        return 'Value {} is not a valid choice.'.format(value)

    # @staticmethod
    def _value_must_be_an_integer_error_message_by_value(self, value):
        return "'{}' value must be an integer.".format(value)

    # @staticmethod
    def _list_contains_items_it_should_contain_no_more_than_3_error_message_by_value(self, value):
        return 'List contains {} items, it should contain no more than 3.'.format(len(value))

    # @staticmethod
    def _ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(self, min_length, value_length):
        return self._ensure_this_value_has_at_least_min_length_characters_error_message_dict_by_min_length_and_value_length[self.language_code].format(min_length=min_length, value_length=value_length)

    # @staticmethod
    def _ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(self, max_length, value_length):
        return self._ensure_this_value_has_at_most_max_length_characters_error_message_dict_by_max_length_and_value_length[self.language_code].format(max_length=max_length, value_length=value_length)

    # @staticmethod
    def _this_field_cannot_be_null_errors_dict_by_field_name(self, field_name):
        return {field_name: [self._this_field_cannot_be_null_error_message_dict[self.language_code]]}

    # @staticmethod
    def _this_field_cannot_be_blank_errors_dict_by_field_name(self, field_name):
        return {field_name: [self._this_field_cannot_be_blank_error_message_dict[self.language_code]]}

    # @staticmethod
    def _value_must_be_valid_json_errors_dict_by_field_name(self, field_name):
        return {field_name: [self._value_must_be_valid_json_error_message_dict[self.language_code]]}

    # @staticmethod
    def _value_is_not_a_valid_choice_errors_dict_by_field_name_and_value(self, field_name, value):
        return {field_name: [self._value_is_not_a_valid_choice_error_message_by_value(value=value)]}

    # @staticmethod
    def _value_must_be_an_integer_errors_dict_by_field_name_and_value(self, field_name, value):
        return {field_name: [self._value_must_be_an_integer_error_message_by_value(value=value)]}

    # @staticmethod
    def _list_contains_items_it_should_contain_no_more_than_3_errors_dict_by_field_name_and_value(self, field_name, value):
        return {field_name: [self._list_contains_items_it_should_contain_no_more_than_3_error_message_by_value(value=value)]}

    # @staticmethod
    def _this_field_cannot_be_null_errors_dict_by_field_name_list(self, field_name_list):
        return {field_name_list[i]: [self._this_field_cannot_be_null_error_message_dict[self.language_code]] for i in range(len(field_name_list))}

    # @staticmethod
    def _value_must_be_an_integer_errors_dict_by_field_name_list_and_value_list(self, field_name_list, value_list):
        return {field_name_list[i]: [self._value_must_be_an_integer_error_message_by_value(value=value_list[i])] for i in range(len(field_name_list))}

    # ~~~~ TODO: simplify these functions! "slug_and_username" etc.

    # @staticmethod
    def _entity_slug_and_username_min_length_fail_errors_dict_by_value_length(self, value_length):
        return {'username': [self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)], 'slug': [self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)]}

    # @staticmethod
    def _user_slug_and_username_min_length_fail_errors_dict_by_value_length(self, value_length):
        return {'username': [self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)], 'slug': [self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)]}

    # @staticmethod
    def _entity_username_min_length_fail_errors_dict_by_value_length(self, value_length):
        return {'username': [self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)]}

    # @staticmethod
    def _user_username_min_length_fail_errors_dict_by_value_length(self, value_length):
        return {'username': [self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)]}

    # @staticmethod
    def _entity_slug_min_length_fail_errors_dict_by_value_length(self, value_length):
        return {'slug': [self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)]}

    # @staticmethod
    def _user_slug_min_length_fail_errors_dict_by_value_length(self, value_length):
        return {'slug': [self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)]}

    # @staticmethod
    def _entity_slug_and_username_max_length_fail_errors_dict_by_value_length(self, value_length):
        return {'username': [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=120, value_length=value_length)], 'slug': [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=200, value_length=value_length)]}

    # @staticmethod
    def _user_slug_and_username_max_length_fail_errors_dict_by_value_length(self, value_length):
        return {'username': [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=40, value_length=value_length)], 'slug': [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=200, value_length=value_length)]}

    # @staticmethod
    def _entity_username_max_length_fail_errors_dict_by_value_length(self, value_length):
        return {'username': [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=120, value_length=value_length)]}

    # @staticmethod
    def _user_username_max_length_fail_errors_dict_by_value_length(self, value_length):
        return {'username': [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=40, value_length=value_length)]}

    # @staticmethod
    def _entity_slug_max_length_fail_errors_dict_by_value_length(self, value_length):
        return {'slug': [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=200, value_length=value_length)]}

    # @staticmethod
    def _user_slug_max_length_fail_errors_dict_by_value_length(self, value_length):
        return {'slug': [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=200, value_length=value_length)]}

    def assert_registration_form_required_fields(self, required_fields):
        self.assertSetEqual(set1=set(self._registration_form_all_the_required_fields_are_required_errors_dict().keys()), set2=set(required_fields))
        self.assertDictEqual(d1=self._registration_form_all_the_required_fields_are_required_errors_dict(), d2={field_name: [self._this_field_is_required_error_message_dict[self.language_code]] for field_name in required_fields})

    def assert_profile_form_required_fields(self, required_fields):
        self.assertSetEqual(set1=set(self._profile_form_all_the_required_fields_are_required_errors_dict().keys()), set2=set(required_fields))
        self.assertDictEqual(d1=self._profile_form_all_the_required_fields_are_required_errors_dict(), d2={field_name: [self._this_field_is_required_error_message_dict[self.language_code]] for field_name in required_fields})


