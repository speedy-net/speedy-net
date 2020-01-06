class SpeedyCoreBaseLanguageMixin(object):
    def _all_the_required_fields_are_required_errors_dict_by_required_fields(self, required_fields):
        return {field_name: [self._this_field_is_required_error_message] for field_name in required_fields}

    def _ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(self, max_length, value_length):
        return self._ensure_this_value_has_at_most_max_length_characters_error_message_to_format.format(max_length=max_length, value_length=value_length)

    def set_up(self):
        super().set_up()

        _this_field_is_required_error_message_dict = {'en': 'This field is required.', 'he': 'יש להזין תוכן בשדה זה.'}
        # _ensure_this_value_has_at_least_min_length_characters_error_message_to_format_dict = {'en': 'Ensure this value has at least {min_length} characters (it has {value_length}).', 'he': '_____ # ~~~~ TODO'} # ~~~~ TODO
        _ensure_this_value_has_at_most_max_length_characters_error_message_to_format_dict = {'en': 'Ensure this value has at most {max_length} characters (it has {value_length}).', 'he': 'נא לוודא שערך זה מכיל {max_length} תווים לכל היותר (מכיל {value_length}).'}

        self._this_field_is_required_error_message = _this_field_is_required_error_message_dict[self.language_code]
        # self._ensure_this_value_has_at_least_min_length_characters_error_message_to_format = _ensure_this_value_has_at_least_min_length_characters_error_message_to_format_dict[self.language_code]
        self._ensure_this_value_has_at_most_max_length_characters_error_message_to_format = _ensure_this_value_has_at_most_max_length_characters_error_message_to_format_dict[self.language_code]


