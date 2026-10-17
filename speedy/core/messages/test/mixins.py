"""
Mixins for the tests of the messages app of Speedy Core, for tests which run in all languages.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.mixins import SpeedyCoreBaseLanguageMixin, TestCaseMixin


    class SpeedyCoreMessagesLanguageMixin(SpeedyCoreBaseLanguageMixin, TestCaseMixin):
        """
        Language-aware mixin for messages tests, providing error message helpers and localized "you have a new message" email subjects for Speedy Net and Speedy Match.
        """

        def _ensure_this_value_has_at_most_max_length_characters_errors_dict_by_value_length(self, value_length):
            """
            Returns the expected form errors dict for the 'text' field when its value has the given length, which must exceed the field's 50000-character maximum.

            :param value_length: The length of the value that was entered in the 'text' field.
            :type value_length: int
            :return: The expected form errors dict, keyed by 'text'.
            :rtype: dict
            """
            return {'text': [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=50000, value_length=value_length)]}

        def set_up(self):
            """
            Sets up the localized "you have a new message" email subjects for Speedy Net and Speedy Match, in the current test's language, as self._you_have_a_new_message_on_speedy_net_subject and self._you_have_a_new_message_on_speedy_match_subject.
            """
            super().set_up()

            _you_have_a_new_message_on_speedy_net_subject_dict = {'en': 'You have a new message on Speedy Net', 'fr': 'Vous avez un nouveau message sur Speedy Net', 'de': 'Sie haben eine neue Mitteilung erhalten auf Speedy Net', 'es': 'Tienes un nuevo mensaje en Speedy Net', 'pt': 'Tu tens uma nova mensagem em Speedy Net', 'it': 'Hai un nuovo messaggio su Speedy Net', 'nl': 'Je hebt een nieuw bericht ingeschakeld Speedy Net', 'ja': 'Speedy Net に新しいメッセージがあります', 'ru': 'У вас новое сообщение в Speedy Net', 'zh': '您在 Speedy Net 上有一条新消息', 'pl': 'Masz nową wiadomość w Speedy Net', 'fa': 'شما یک پیام جدید در Speedy Net دارید', 'he': 'יש לך הודעה חדשה בספידי נט', 'ko': 'Speedy Net에 새 메시지가 있습니다', 'ar': 'لديك رسالة جديدة على Speedy Net', 'id': 'Anda mendapat pesan baru di Speedy Net', 'uk': 'У вас нове повідомлення на Speedy Net', 'tr': 'Speedy Net üzerinde yeni bir mesajınız var', 'vi': 'Bạn có một tin nhắn mới trên Speedy Net', 'cs': 'Máte novou zprávu na Speedy Net', 'sv': 'Du har ett nytt meddelande på Speedy Net', 'fi': 'Sinulla on uusi viesti Speedy Net', 'hu': 'Új üzenete érkezett a(z) Speedy Net oldalon', 'th': 'คุณมีข้อความใหม่บน Speedy Net', 'el': 'Έχετε ένα νέο μήνυμα στο Speedy Net', 'ms': 'Anda mempunyai mesej baharu di Speedy Net', 'sr': 'Имате нову поруку на Speedy Net', 'ro': 'Aveți un mesaj nou pe Speedy Net', 'bn': 'Speedy Net-এ আপনার একটি নতুন বার্তা আছে', 'ca': 'Tens un missatge nou a Speedy Net', 'no': 'Du har en ny melding på Speedy Net', 'bg': 'Имате ново съобщение на Speedy Net', 'da': 'Du har en ny besked på Speedy Net', 'sk': 'Máte novú správu na Speedy Net', 'hi': 'आपको एक नया संदेश मिला है Speedy Net', 'et': 'Teil on Speedy Net uus sõnum', 'hr': 'Imate novu poruku na Speedy Net', 'az': 'Speedy Net-də yeni mesajınız var', 'zh-yue': '您有一條新訊息Speedy Net', 'lt': 'Turite naują žinutę svetainėje Speedy Net', 'sl': 'Imate novo sporočilo na Speedy Net', 'eu': 'Mezu berri bat duzu Speedy Net webgunean', 'hy': 'Դուք ունեք նոր հաղորդագրություն Speedy Net-ում', 'uz': 'Sizda Speedy Net da yangi xabar bor', 'ta': 'நீங்கள் ஒரு புதிய செய்தியை உள்ள Speedy Net', 'lv': 'Jums ir jauna ziņa vietnē Speedy Net'}
            _you_have_a_new_message_on_speedy_match_subject_dict = {'en': 'You have a new message on Speedy Match', 'fr': 'Vous avez un nouveau message sur Speedy Match', 'de': 'Sie haben eine neue Mitteilung erhalten auf Speedy Match', 'es': 'Tienes un nuevo mensaje en Speedy Match', 'pt': 'Tu tens uma nova mensagem em Speedy Match', 'it': 'Hai un nuovo messaggio su Speedy Match', 'nl': 'Je hebt een nieuw bericht ingeschakeld Speedy Match', 'ja': 'Speedy Match に新しいメッセージがあります', 'ru': 'У вас новое сообщение в Speedy Match', 'zh': '您在 Speedy Match 上有一条新消息', 'pl': 'Masz nową wiadomość w Speedy Match', 'fa': 'شما یک پیام جدید در Speedy Match دارید', 'he': "יש לך הודעה חדשה בספידי מץ'", 'ko': 'Speedy Match에 새 메시지가 있습니다', 'ar': 'لديك رسالة جديدة على Speedy Match', 'id': 'Anda mendapat pesan baru di Speedy Match', 'uk': 'У вас нове повідомлення на Speedy Match', 'tr': 'Speedy Match üzerinde yeni bir mesajınız var', 'vi': 'Bạn có một tin nhắn mới trên Speedy Match', 'cs': 'Máte novou zprávu na Speedy Match', 'sv': 'Du har ett nytt meddelande på Speedy Match', 'fi': 'Sinulla on uusi viesti Speedy Match', 'hu': 'Új üzenete érkezett a(z) Speedy Match oldalon', 'th': 'คุณมีข้อความใหม่บน Speedy Match', 'el': 'Έχετε ένα νέο μήνυμα στο Speedy Match', 'ms': 'Anda mempunyai mesej baharu di Speedy Match', 'sr': 'Имате нову поруку на Speedy Match', 'ro': 'Aveți un mesaj nou pe Speedy Match', 'bn': 'Speedy Match-এ আপনার একটি নতুন বার্তা আছে', 'ca': 'Tens un missatge nou a Speedy Match', 'no': 'Du har en ny melding på Speedy Match', 'bg': 'Имате ново съобщение на Speedy Match', 'da': 'Du har en ny besked på Speedy Match', 'sk': 'Máte novú správu na Speedy Match', 'hi': 'आपको एक नया संदेश मिला है Speedy Match', 'et': 'Teil on Speedy Match uus sõnum', 'hr': 'Imate novu poruku na Speedy Match', 'az': 'Speedy Match-də yeni mesajınız var', 'zh-yue': '您有一條新訊息Speedy Match', 'lt': 'Turite naują žinutę svetainėje Speedy Match', 'sl': 'Imate novo sporočilo na Speedy Match', 'eu': 'Mezu berri bat duzu Speedy Match webgunean', 'hy': 'Դուք ունեք նոր հաղորդագրություն Speedy Match-ում', 'uz': 'Sizda Speedy Match da yangi xabar bor', 'ta': 'நீங்கள் ஒரு புதிய செய்தியை உள்ள Speedy Match', 'lv': 'Jums ir jauna ziņa vietnē Speedy Match'}

            self._you_have_a_new_message_on_speedy_net_subject = _you_have_a_new_message_on_speedy_net_subject_dict[self.language_code]
            self._you_have_a_new_message_on_speedy_match_subject = _you_have_a_new_message_on_speedy_match_subject_dict[self.language_code]


