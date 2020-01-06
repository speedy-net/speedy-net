from speedy.core.base.test.mixins import SpeedyCoreBaseLanguageMixin


class SpeedyCoreMessagesLanguageMixin(SpeedyCoreBaseLanguageMixin):
    def _ensure_this_value_has_at_most_max_length_characters_errors_dict_by_value_length(self, value_length):
        return {'text': [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=50000, value_length=value_length)]}


