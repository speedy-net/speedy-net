from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.mixins import SpeedyCoreBaseLanguageMixin


    class SpeedyCoreMessagesLanguageMixin(SpeedyCoreBaseLanguageMixin):
        def _ensure_this_value_has_at_most_max_length_characters_errors_dict_by_value_length(self, value_length):
            return {'text': [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=50000, value_length=value_length)]}

        def set_up(self):
            super().set_up()

            _you_have_a_new_message_on_speedy_net_subject_dict = {'en': "You have a new message on Speedy Net", 'fr': "Vous avez un nouveau message sur Speedy Net", 'de': "Sie haben eine neue Mitteilung erhalten auf Speedy Net", 'es': "Tienes un nuevo mensaje en Speedy Net", 'pt': "Tu tens uma nova mensagem em Speedy Net", 'he': "יש לך הודעה חדשה בספידי נט"}
            _you_have_a_new_message_on_speedy_match_subject_dict = {'en': "You have a new message on Speedy Match", 'fr': "Vous avez un nouveau message sur Speedy Match", 'de': "Sie haben eine neue Mitteilung erhalten auf Speedy Match", 'es': "Tienes un nuevo mensaje en Speedy Match", 'pt': "Tu tens uma nova mensagem em Speedy Match", 'he': "יש לך הודעה חדשה בספידי מץ'"}

            self._you_have_a_new_message_on_speedy_net_subject = _you_have_a_new_message_on_speedy_net_subject_dict[self.language_code]
            self._you_have_a_new_message_on_speedy_match_subject = _you_have_a_new_message_on_speedy_match_subject_dict[self.language_code]


