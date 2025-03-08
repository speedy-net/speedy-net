from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.mixins import SpeedyCoreBaseLanguageMixin, TestCaseMixin


    class SpeedyCoreFeedbackLanguageMixin(SpeedyCoreBaseLanguageMixin, TestCaseMixin):
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

        def _ensure_this_value_has_at_most_max_length_characters_errors_dict_by_value_length(self, value_length):
            return {'text': [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=50000, value_length=value_length)]}

        def set_up(self):
            super().set_up()

            _please_contact_us_by_email_error_message_dict = {'en': 'Please contact us by email.', 'fr': 'Veuillez nous contacter par e-mail.', 'de': "Bitte kontaktieren Sie uns per E-Mail.", 'es': "Por favor, contáctanos por correo electrónico.", 'pt': "Entre em contacto conosco por e-mail.", 'it': "Contattateci tramite e-mail.", 'nl': "Neem contact met ons op via e-mail.", 'sv': "Kontakta oss via e-post.", 'ko': "이메일로 연락해주세요.", 'fi': "Ota yhteyttä sähköpostitse.", 'he': 'אנא צרו איתנו קשר באמצעות הדואר האלקטרוני.'}
            _not_17_error_message_dict = {'en': 'Not 17.', 'fr': 'Pas 17.', 'de': "Nicht 17.", 'es': "No 17.", 'pt': "Não 17.", 'it': "Non 17.", 'nl': "Niet 17.", 'sv': "Inte 17.", 'ko': "17이 아님.", 'fi': "Ei 17.", 'he': 'לא 17.'}

            self._please_contact_us_by_email_error_message = _please_contact_us_by_email_error_message_dict[self.language_code]
            self._not_17_error_message = _not_17_error_message_dict[self.language_code]


