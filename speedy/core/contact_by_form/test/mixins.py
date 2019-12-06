from speedy.core.base.test.mixins import SpeedyCoreBaseLanguageMixin


class SpeedyCoreFeedbackLanguageMixin(SpeedyCoreBaseLanguageMixin):
    def _feedback_form_all_the_required_fields_keys(self, user_is_logged_in):
        if (user_is_logged_in):
            return ['text']
        else:
            return ['sender_name', 'sender_email', 'text', 'no_bots']

    def _feedback_form_all_the_required_fields_are_required_errors_dict(self, user_is_logged_in):
        return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=self._feedback_form_all_the_required_fields_keys(user_is_logged_in=user_is_logged_in))

    def _feedback_form_no_bots_is_required_errors_dict(self):
        return {'no_bots': [self._this_field_is_required_error_message]}

    def _feedback_form_no_bots_is_not_17_errors_dict(self):
        return {'no_bots': [self._not_17_error_message]}

    def _please_contact_us_by_email_errors_dict(self):
        return {'text': [self._please_contact_us_by_email_error_message]}

    def set_up(self):
        super().set_up()

        _please_contact_us_by_email_error_message_dict = {'en': 'Please contact us by email.', 'he': 'אנא צרו איתנו קשר באמצעות הדואר האלקטרוני.'}
        _not_17_error_message_dict = {'en': 'Not 17.', 'he': 'לא 17.'}

        self._please_contact_us_by_email_error_message = _please_contact_us_by_email_error_message_dict[self.language_code]
        self._not_17_error_message = _not_17_error_message_dict[self.language_code]


