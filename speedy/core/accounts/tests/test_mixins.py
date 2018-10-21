from speedy.core.accounts.models import User


class ErrorsMixin(object):
    ALL_GENDERS = [User.GENDERS_DICT[gender] for gender in User.GENDER_VALID_VALUES]

    _user_all_the_required_fields_keys = ['first_name', 'last_name', 'username', 'slug', 'password', 'gender', 'date_of_birth']

    # @staticmethod
    def _value_is_not_a_valid_choice_error_message_by_value(self, value):
        return 'Value {} is not a valid choice.'.format(value)

    # @staticmethod
    def _value_must_be_an_integer_error_message_by_value(self, value):
        return "'{}' value must be an integer.".format(value)

    # @staticmethod
    def _list_contains_items_it_should_contain_no_more_than_3_error_message_by_value(self, value):
        return 'List contains {} items, it should contain no more than 3.'.format(len(value))

    # # @staticmethod
    # def _value_has_an_invalid_date_format_error_message_by_value(self, value):
    #     return "'{}' value has an invalid date format. It must be in YYYY-MM-DD format.".format(value)
    #
    # @staticmethod
    def _ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(self, min_length, value_length):
        # ~~~~ TODO: search for this string: "_ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length" and also use normalize...
        return self._ensure_this_value_has_at_least_min_length_characters_error_message_to_format.format(min_length=min_length, value_length=value_length)

    # @staticmethod
    def _ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(self, max_length, value_length):
        # ~~~~ TODO: search for this string: "_ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length" and also use normalize...
        return self._ensure_this_value_has_at_most_max_length_characters_error_message_to_format.format(max_length=max_length, value_length=value_length)

    def _registration_form_all_the_required_fields_keys(self):
        return [field_name.format(language_code=self.language_code) for field_name in ['first_name_{language_code}', 'last_name_{language_code}', 'email', 'slug', 'new_password1', 'gender', 'date_of_birth']]

    def _profile_form_all_the_required_fields_keys(self):
        return [field_name.format(language_code=self.language_code) for field_name in ['first_name_{language_code}', 'last_name_{language_code}', 'slug', 'gender', 'date_of_birth']]

    def _all_the_required_fields_are_required_errors_dict_by_required_fields(self, required_fields):
        return {field_name: [self._this_field_is_required_error_message] for field_name in required_fields}

    def _registration_form_all_the_required_fields_are_required_errors_dict(self):
        return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=self._registration_form_all_the_required_fields_keys())

    def _profile_form_all_the_required_fields_are_required_errors_dict(self):
        return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=self._profile_form_all_the_required_fields_keys())

    def _date_of_birth_is_required_errors_dict(self):
        return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=['date_of_birth'])

    def _enter_a_valid_date_errors_dict(self):
        return {'date_of_birth': [self._enter_a_valid_date_error_message]}

    def _cannot_create_user_email_address_without_all_the_required_fields_errors_dict(self):
        return {
            'user': [self._this_field_cannot_be_null_error_message],
            'email': [self._this_field_cannot_be_blank_error_message],
        }

    def _id_contains_illegal_characters_errors_dict(self):
        return {'id': [self._id_contains_illegal_characters_error_message]}

    def _please_enter_a_correct_username_and_password_errors_dict(self):
        return {'__all__': [self._please_enter_a_correct_username_and_password_error_message]}

    def _invalid_password_errors_dict(self):
        return {'password': [self._invalid_password_error_message]}

    def _password_too_short_errors_dict(self):
        return {'new_password1': [self._password_too_short_error_message]}

    def _password_too_long_errors_dict(self):
        return {'new_password1': [self._password_too_long_error_message]}

    def _your_old_password_was_entered_incorrectly_errors_dict(self):
        return {'old_password': [self._your_old_password_was_entered_incorrectly_error_message]}

    def _the_two_password_fields_didnt_match_errors_dict(self):
        return {'new_password2': [self._the_two_password_fields_didnt_match_error_message]}

    def _enter_a_valid_email_address_errors_dict(self):
        return {'email': [self._enter_a_valid_email_address_error_message]}

    def _this_email_is_already_in_use_errors_dict(self):
        return {'email': [self._this_email_is_already_in_use_error_message]}

    def _slug_this_username_is_already_taken_errors_dict(self):
        return {'slug': [self._this_username_is_already_taken_error_message]}

    def _slug_and_username_this_username_is_already_taken_errors_dict(self):
        return {'username': [self._this_username_is_already_taken_error_message], 'slug': [self._this_username_is_already_taken_error_message]}

    def _entity_slug_and_username_username_must_start_with_4_or_more_letters_errors_dict(self):
        return {'username': [self._entity_username_must_start_with_4_or_more_letters_error_message], 'slug': [self._entity_username_must_start_with_4_or_more_letters_error_message]}

    def _entity_username_username_must_start_with_4_or_more_letters_errors_dict(self):
        return {'username': [self._entity_username_must_start_with_4_or_more_letters_error_message]}

    def _entity_slug_username_must_start_with_4_or_more_letters_errors_dict(self):
        return {'slug': [self._entity_username_must_start_with_4_or_more_letters_error_message]}

    def _user_slug_and_username_username_must_start_with_4_or_more_letters_errors_dict(self):
        return {'username': [self._user_username_must_start_with_4_or_more_letters_error_message], 'slug': [self._user_username_must_start_with_4_or_more_letters_error_message]}

    def _user_username_username_must_start_with_4_or_more_letters_errors_dict(self):
        return {'username': [self._user_username_must_start_with_4_or_more_letters_error_message]}

    def _user_slug_username_must_start_with_4_or_more_letters_errors_dict(self):
        return {'slug': [self._user_username_must_start_with_4_or_more_letters_error_message]}

    def _slug_does_not_parse_to_username_errors_dict(self):
        return {'slug': [self._slug_does_not_parse_to_username_error_message]}

    def _entity_username_must_start_with_4_or_more_letters_and_slug_does_not_parse_to_username_errors_dict(self):
        return {'username': [self._entity_username_must_start_with_4_or_more_letters_error_message], 'slug': [self._slug_does_not_parse_to_username_error_message]}

    def _user_username_must_start_with_4_or_more_letters_and_slug_does_not_parse_to_username_errors_dict(self):
        return {'username': [self._user_username_must_start_with_4_or_more_letters_error_message], 'slug': [self._slug_does_not_parse_to_username_error_message]}

    def _date_of_birth_errors_dict_by_date_of_birth(self, date_of_birth):
        if (date_of_birth == ''):
            return self._date_of_birth_is_required_errors_dict()
        else:
            return self._enter_a_valid_date_errors_dict()

    def _you_cant_change_your_username_errors_dict_by_gender(self, gender):
        return {'slug': [self._you_cant_change_your_username_error_message_dict_by_gender[gender]]}

    def _cannot_create_user_without_all_the_required_fields_errors_dict_by_value(self, value, gender_is_valid=False):
        self.assertEqual(first=gender_is_valid, second=(value in User.GENDER_VALID_VALUES))
        if (value is None):
            str_value = ''
            gender_error_messages = [self._this_field_cannot_be_null_error_message]
            date_of_birth_error_messages = [self._this_field_cannot_be_null_error_message]
        else:
            str_value = str(value)
            if (value == ''):
                gender_error_messages = [self._value_must_be_an_integer_error_message_by_value(value=value)]
            else:
                if (not (gender_is_valid)):
                    gender_error_messages = [self._value_is_not_a_valid_choice_error_message_by_value(value=value)]
                else:
                    gender_error_messages = None
            # date_of_birth_error_messages = [self._value_has_an_invalid_date_format_error_message_by_value(value=str_value)]
            date_of_birth_error_messages = [self._enter_a_valid_date_error_message]
        slug_and_username_error_messages = [self._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=len(str_value))]
        errors_dict = {
            # 'first_name': [self._this_field_cannot_be_blank_error_message],
            # 'last_name': [self._this_field_cannot_be_blank_error_message],
            'username': slug_and_username_error_messages,
            'slug': slug_and_username_error_messages,
            # 'password': [self._this_field_cannot_be_blank_error_message],
            # 'gender': gender_error_messages,
            'date_of_birth': date_of_birth_error_messages,
        }
        if (value in [None, '']):
            self.assertEqual(first=str_value, second='')
            errors_dict['first_name'] = [self._this_field_cannot_be_blank_error_message]
            errors_dict['last_name'] = [self._this_field_cannot_be_blank_error_message]
            errors_dict['password'] = [self._this_field_cannot_be_blank_error_message]
        else:
            self.assertNotEqual(first=str_value, second='')
        self.assertEqual(first=gender_is_valid, second=(gender_error_messages is None))
        if (not (gender_is_valid)):
            errors_dict['gender'] = gender_error_messages
        # if (value is None):
        #     errors_dict['gender'] = [self._this_field_cannot_be_null_error_message]
        #     errors_dict['date_of_birth'] = [self._this_field_cannot_be_null_error_message]
        # # elif (value == ''):
        # #     pass
        # else:
        #     errors_dict['gender'] = [self._value_is_not_a_valid_choice_error_message_by_value(value=value)]
        #     errors_dict['date_of_birth'] = [self._value_has_an_invalid_date_format_error_message_by_value(value=str_value)]
        return errors_dict

    # @staticmethod
    def _this_field_cannot_be_null_errors_dict_by_field_name(self, field_name):
        return {field_name: [self._this_field_cannot_be_null_error_message]}

    # @staticmethod
    def _this_field_cannot_be_blank_errors_dict_by_field_name(self, field_name):
        return {field_name: [self._this_field_cannot_be_blank_error_message]}

    # @staticmethod
    def _value_must_be_valid_json_errors_dict_by_field_name(self, field_name):
        return {field_name: [self._value_must_be_valid_json_error_message]}

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
        return {field_name_list[i]: [self._this_field_cannot_be_null_error_message] for i in range(len(field_name_list))}

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

    def setup(self):
        super().setup()

        _this_field_is_required_error_message_dict = {'en': 'This field is required.', 'he': 'יש להזין תוכן בשדה זה.'}
        _this_field_cannot_be_null_error_message_dict = {'en': 'This field cannot be null.', 'he': '___This field cannot be null.'}
        _this_field_cannot_be_blank_error_message_dict = {'en': 'This field cannot be blank.', 'he': '___This field cannot be blank.'}
        _id_contains_illegal_characters_error_message_dict = {'en': 'id contains illegal characters.', 'he': '___id contains illegal characters.'}
        _value_must_be_valid_json_error_message_dict = {'en': 'Value must be valid JSON.', 'he': '___Value must be valid JSON.'}
        _invalid_password_error_message_dict = {'en': 'Invalid password.', 'he': '___Invalid password.'}
        _password_too_short_error_message_dict = {'en': 'Password too short.', 'he': 'הסיסמה קצרה מדי.'}
        _password_too_long_error_message_dict = {'en': 'Password too long.', 'he': 'הסיסמה ארוכה מדי.'}
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

        _ensure_this_value_has_at_least_min_length_characters_error_message_to_format_dict= {'en': 'Ensure this value has at least {min_length} characters (it has {value_length}).', 'he': 'נא לוודא שערך זה מכיל {min_length} תווים לכל הפחות (מכיל {value_length}).'}
        _ensure_this_value_has_at_most_max_length_characters_error_message_to_format_dict = {'en': 'Ensure this value has at most {max_length} characters (it has {value_length}).', 'he': 'נא לוודא שערך זה מכיל {max_length} תווים לכל היותר (מכיל {value_length}).'}

        _you_cant_change_your_username_error_message_dict_by_gender = {
            'en': {gender: "You can't change your username." for gender in self.ALL_GENDERS},
            'he': {
                'female': "___לא ניתן לשנות שם משתמשת",
                'male': "___לא ניתן לשנות שם משתמש",
                'other': "___לא ניתן לשנות שם משתמש/ת",
            },
        }

        self._this_field_is_required_error_message = _this_field_is_required_error_message_dict[self.language_code]
        self._this_field_cannot_be_null_error_message = _this_field_cannot_be_null_error_message_dict[self.language_code]
        self._this_field_cannot_be_blank_error_message = _this_field_cannot_be_blank_error_message_dict[self.language_code]
        self._id_contains_illegal_characters_error_message = _id_contains_illegal_characters_error_message_dict[self.language_code]
        self._value_must_be_valid_json_error_message = _value_must_be_valid_json_error_message_dict[self.language_code]
        self._invalid_password_error_message = _invalid_password_error_message_dict[self.language_code]
        self._password_too_short_error_message = _password_too_short_error_message_dict[self.language_code]
        self._password_too_long_error_message = _password_too_long_error_message_dict[self.language_code]
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

        self._ensure_this_value_has_at_least_min_length_characters_error_message_to_format = _ensure_this_value_has_at_least_min_length_characters_error_message_to_format_dict[self.language_code]
        self._ensure_this_value_has_at_most_max_length_characters_error_message_to_format = _ensure_this_value_has_at_most_max_length_characters_error_message_to_format_dict[self.language_code]

        self._you_cant_change_your_username_error_message_dict_by_gender = _you_cant_change_your_username_error_message_dict_by_gender[self.language_code]

        self.assertListEqual(list1=self.ALL_GENDERS, list2=['female', 'male', 'other'])

        self.assertSetEqual(set1=set(self._you_cant_change_your_username_error_message_dict_by_gender.keys()), set2=set(self.ALL_GENDERS))

        self.assertSetEqual(set1=set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None).keys()), set2=set(self._user_all_the_required_fields_keys))
        self.assertListEqual(list1=self._profile_form_all_the_required_fields_keys(), list2=[field_name for field_name in self._registration_form_all_the_required_fields_keys() if (not (field_name in ['email', 'new_password1']))])
        self.assertSetEqual(set1=set(self._registration_form_all_the_required_fields_keys()) - {'email', 'new_password1'}, set2=set(self._profile_form_all_the_required_fields_keys()))
        self.assertSetEqual(set1=set(self._profile_form_all_the_required_fields_keys()) | {'email', 'new_password1'}, set2=set(self._registration_form_all_the_required_fields_keys()))

    def assert_required_fields_and_errors_dict(self, required_fields, errors_dict):
        self.assertSetEqual(set1=set(errors_dict.keys()), set2=set(required_fields))
        self.assertDictEqual(d1=errors_dict, d2=self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=required_fields))

    def assert_registration_form_required_fields(self, required_fields):
        self.assert_required_fields_and_errors_dict(required_fields=required_fields, errors_dict=self._registration_form_all_the_required_fields_are_required_errors_dict())

    def assert_profile_form_required_fields(self, required_fields):
        self.assert_required_fields_and_errors_dict(required_fields=required_fields, errors_dict=self._profile_form_all_the_required_fields_are_required_errors_dict())

    # def assert_user_all_the_required_fields(self, required_fields):
    #     self.assertSetEqual(set1=set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None).keys()), set2=set(required_fields))
