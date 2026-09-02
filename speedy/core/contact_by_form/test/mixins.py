from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.mixins import SpeedyCoreBaseLanguageMixin, TestCaseMixin


    class SpeedyCoreFeedbackModelsMixin(TestCaseMixin):
        _not_allowed_strings = ["https://t.me/pump_upp", "https://datebest.net", "https://t.me/FeedbackFormEU"]


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

            _please_contact_us_by_email_error_message_dict = {'en': 'Please contact us by email.', 'fr': 'Veuillez nous contacter par e-mail.', 'de': 'Bitte kontaktieren Sie uns per E-Mail.', 'es': 'Por favor, contáctanos por correo electrónico.', 'pt': 'Entre em contacto conosco por e-mail.', 'it': 'Contattateci tramite e-mail.', 'nl': 'Neem contact met ons op via e-mail.', 'ja': 'メールにてご連絡ください。', 'ru': 'Пожалуйста, свяжитесь с нами по электронной почте.', 'zh': '請透過電子郵件與我們聯繫。', 'pl': 'Prosimy o kontakt e-mailowy.', 'fa': 'لطفا از طریق ایمیل با ما تماس بگیرید.', 'he': 'אנא צרו איתנו קשר באמצעות הדואר האלקטרוני.', 'ko': '이메일로 연락해주세요.', 'ar': 'يرجى الاتصال بنا عن طريق البريد الإلكتروني.', 'az': 'Lütfən, bizimlə e-poçt vasitəsilə əlaqə saxlayın.', 'id': 'Silakan hubungi kami melalui email.', 'uk': "Будь ласка, зв'яжіться з нами електронною поштою.", 'tr': 'Lütfen e-posta yoluyla bizimle iletişime geçin.', 'vi': 'Vui lòng liên hệ với chúng tôi qua email.', 'cs': 'Kontaktujte nás prosím emailem.', 'sv': 'Kontakta oss via e-post.', 'fi': 'Ota yhteyttä sähköpostitse.', 'hu': 'Kérjük, vegye fel velünk a kapcsolatot e-mailben.', 'th': 'โปรดติดต่อเราทางอีเมล', 'el': 'Επικοινωνήστε μαζί μας μέσω email.', 'ms': 'Sila hubungi kami melalui e-mel.', 'sr': 'Контактирајте нас путем е-поште.', 'ro': 'Vă rugăm să ne contactați prin e-mail.', 'bn': 'ইমেল দ্বারা আমাদের সাথে যোগাযোগ করুন.', 'ca': 'Si us plau, poseu-vos en contacte amb nosaltres per correu electrònic.', 'no': 'Vennligst kontakt oss på e-post.', 'bg': 'Моля, свържете се с нас по имейл.', 'da': 'Kontakt os venligst via e-mail.', 'sk': 'Kontaktujte nás prosím emailom.', 'hi': 'हमसे ईमेल द्वारा संपर्क करें।', 'et': 'Palun võtke meiega ühendust e-posti teel.', 'hr': 'Molimo kontaktirajte nas e-poštom.'}
            _not_17_error_message_dict = {'en': 'Not 17.', 'fr': 'Pas 17.', 'de': 'Nicht 17.', 'es': 'No 17.', 'pt': 'Não 17.', 'it': 'Non 17.', 'nl': 'Niet 17.', 'ja': '17ではありません。', 'ru': 'Не 17.', 'zh': '不是17。', 'pl': 'Nie 17.', 'fa': 'نه 17.', 'he': 'לא 17.', 'ko': '17이 아님.', 'ar': 'ليس 17.', 'az': '17 deyil.', 'id': 'Bukan 17.', 'uk': 'Не 17.', 'tr': '17 değil.', 'vi': 'Không phải 17.', 'cs': 'Ne 17.', 'sv': 'Inte 17.', 'fi': 'Ei 17.', 'hu': 'Nem 17.', 'th': 'ไม่ใช่ 17.', 'el': 'Όχι 17.', 'ms': 'Bukan 17.', 'sr': 'Не 17.', 'ro': 'Nu 17.', 'bn': '17 নয়।', 'ca': 'No 17.', 'no': 'Ikke 17.', 'bg': 'Не 17.', 'da': 'Ikke 17.', 'sk': 'Nie 17.', 'hi': '17 नहीं.', 'et': 'Mitte 17.', 'hr': 'Ne 17.'}

            self._please_contact_us_by_email_error_message = _please_contact_us_by_email_error_message_dict[self.language_code]
            self._not_17_error_message = _not_17_error_message_dict[self.language_code]


