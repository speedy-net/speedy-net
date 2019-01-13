class SpeedyCoreBaseLanguageMixin(object):
    def _all_the_required_fields_are_required_errors_dict_by_required_fields(self, required_fields):
        return {field_name: [self._this_field_is_required_error_message] for field_name in required_fields}

    def set_up(self):
        super().set_up()

        _this_field_is_required_error_message_dict = {'en': 'This field is required.', 'he': 'יש להזין תוכן בשדה זה.'}

        self._this_field_is_required_error_message = _this_field_is_required_error_message_dict[self.language_code]


