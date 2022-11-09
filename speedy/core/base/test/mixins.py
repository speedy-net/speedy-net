from django.conf import settings as django_settings

if (django_settings.TESTS):
    import sys


    class SpeedyCoreBaseLanguageMixin(object):
        def _all_the_required_fields_are_required_errors_dict_by_required_fields(self, required_fields):
            return {field_name: [self._this_field_is_required_error_message] for field_name in required_fields}

        def _ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(self, max_length, value_length):
            return self._ensure_this_value_has_at_most_max_length_characters_error_message_to_format.format(max_length=max_length, value_length=value_length)

        def _exceeds_the_limit_4300_for_integer_string_conversion_error_message_by_digits(self, digits):
            return self._exceeds_the_limit_4300_for_integer_string_conversion_error_message_to_format.format(digits=digits)

        def set_up(self):
            super().set_up()

            _this_field_is_required_error_message_dict = {'en': 'This field is required.', 'he': 'יש להזין תוכן בשדה זה.'}
            # _ensure_this_value_has_at_least_min_length_characters_error_message_to_format_dict = {'en': 'Ensure this value has at least {min_length} characters (it has {value_length}).', 'he': '_____ # ~~~~ TODO'} # ~~~~ TODO
            _ensure_this_value_has_at_most_max_length_characters_error_message_to_format_dict = {'en': 'Ensure this value has at most {max_length} characters (it has {value_length}).', 'he': 'נא לוודא שערך זה מכיל {max_length} תווים לכל היותר (מכיל {value_length}).'}
            if (sys.version_info >= (3, 9)):
                _exceeds_the_limit_4300_for_integer_string_conversion_error_message_to_format_dict = {'en': 'Exceeds the limit (4300) for integer string conversion: value has {digits} digits; use sys.set_int_max_str_digits() to increase the limit', 'he': 'Exceeds the limit (4300) for integer string conversion: value has {digits} digits; use sys.set_int_max_str_digits() to increase the limit'}
            else:
                _exceeds_the_limit_4300_for_integer_string_conversion_error_message_to_format_dict = {'en': 'Exceeds the limit (4300) for integer string conversion: value has {digits} digits', 'he': 'Exceeds the limit (4300) for integer string conversion: value has {digits} digits'}

            self._this_field_is_required_error_message = _this_field_is_required_error_message_dict[self.language_code]
            # self._ensure_this_value_has_at_least_min_length_characters_error_message_to_format = _ensure_this_value_has_at_least_min_length_characters_error_message_to_format_dict[self.language_code]
            self._ensure_this_value_has_at_most_max_length_characters_error_message_to_format = _ensure_this_value_has_at_most_max_length_characters_error_message_to_format_dict[self.language_code]
            self._exceeds_the_limit_4300_for_integer_string_conversion_error_message_to_format = _exceeds_the_limit_4300_for_integer_string_conversion_error_message_to_format_dict[self.language_code]


