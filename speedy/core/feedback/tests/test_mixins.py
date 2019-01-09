from speedy.core.base.tests.test_mixins import SpeedyCoreBaseLanguageMixin


class SpeedyCoreFeedbackLanguageMixin(SpeedyCoreBaseLanguageMixin):
    def _feedback_form_all_the_required_fields_keys(self, user_is_logged_in):
        if (user_is_logged_in):
            return ['text']
        else:
            return ['sender_name', 'sender_email', 'text']

    def _feedback_form_all_the_required_fields_are_required_errors_dict(self, user_is_logged_in):
        return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=self._feedback_form_all_the_required_fields_keys(user_is_logged_in=user_is_logged_in))


