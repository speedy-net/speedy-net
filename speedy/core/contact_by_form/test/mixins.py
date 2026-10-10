"""
Mixins for the tests of the contact by form app of Speedy Core, for feedback models and for tests which run in all languages.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.mixins import SpeedyCoreBaseLanguageMixin, TestCaseMixin


    class SpeedyCoreFeedbackModelsMixin(TestCaseMixin):
        """
        Provides the list of not-allowed strings used by FeedbackForm, shared by feedback-related tests.

        Attributes:
            _not_allowed_strings (list): Strings that are not allowed to appear in feedback text (likely spam links), matching FeedbackForm._not_allowed_strings.
        """
        _not_allowed_strings = ["https://t.me/pump_upp", "https://datebest.net", "https://t.me/FeedbackFormEU"]


    class SpeedyCoreFeedbackLanguageMixin(SpeedyCoreBaseLanguageMixin, TestCaseMixin):
        """
        Provides error-dict helpers and language-specific translated error messages used by feedback form/view tests.

        Methods:
            _feedback_form_all_the_required_fields_keys(self, user_is_logged_in): Returns the list of required field keys, depending on whether the sender is logged in.
            _feedback_form_all_the_required_fields_are_required_errors_dict(self, user_is_logged_in): Returns the "this field is required" errors dict for all required fields.
            _feedback_form_no_bots_is_required_errors_dict(self): Returns the errors dict for a missing anti-bot field value.
            _feedback_form_no_bots_is_not_17_errors_dict(self): Returns the errors dict for an incorrect anti-bot field value.
            _please_contact_us_by_email_errors_dict(self): Returns the errors dict for text containing a not-allowed string.
            _ensure_this_value_has_at_most_max_length_characters_errors_dict_by_value_length(self, value_length): Returns the errors dict for text exceeding the maximum length.
            set_up(self): Sets translated error messages ("please contact us by email" and "not 17") for the current test's language.
        """
        def _feedback_form_all_the_required_fields_keys(self, user_is_logged_in):
            """
            Returns the list of required field keys for the feedback form, depending on whether the sender is logged in.

            :param user_is_logged_in: Whether the sender is an authenticated, logged-in user.
            :type user_is_logged_in: bool
            :return: The list of required field keys.
            :rtype: list
            """
            if (user_is_logged_in):
                return ['text']
            else:
                return ['sender_name', 'sender_email', 'text', 'no_bots']

        def _feedback_form_all_the_required_fields_are_required_errors_dict(self, user_is_logged_in):
            """
            Returns the "this field is required" errors dict for all required fields of the feedback form.

            :param user_is_logged_in: Whether the sender is an authenticated, logged-in user.
            :type user_is_logged_in: bool
            :return: A dict mapping each required field name to its "this field is required" error message.
            :rtype: dict
            """
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=self._feedback_form_all_the_required_fields_keys(user_is_logged_in=user_is_logged_in))

        def _feedback_form_no_bots_is_required_errors_dict(self):
            """
            Returns the errors dict for a missing (blank) anti-bot field value.

            :return: A dict mapping 'no_bots' to its "this field is required" error message.
            :rtype: dict
            """
            return {'no_bots': [self._this_field_is_required_error_message]}

        def _feedback_form_no_bots_is_not_17_errors_dict(self):
            """
            Returns the errors dict for an incorrect (not "17") anti-bot field value.

            :return: A dict mapping 'no_bots' to the "not 17" error message.
            :rtype: dict
            """
            return {'no_bots': [self._not_17_error_message]}

        def _please_contact_us_by_email_errors_dict(self):
            """
            Returns the errors dict for feedback text containing a not-allowed (spam-related) string.

            :return: A dict mapping 'text' to the "please contact us by email" error message.
            :rtype: dict
            """
            return {'text': [self._please_contact_us_by_email_error_message]}

        def _ensure_this_value_has_at_most_max_length_characters_errors_dict_by_value_length(self, value_length):
            """
            Returns the errors dict for feedback text exceeding the maximum allowed length (50000 characters).

            :param value_length: The length of the (too long) value that was submitted.
            :type value_length: int
            :return: A dict mapping 'text' to the "ensure this value has at most max_length characters" error message.
            :rtype: dict
            """
            return {'text': [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=50000, value_length=value_length)]}

        def set_up(self):
            """
            Sets the translated "please contact us by email" and "not 17" error messages for the current test's language.
            """
            super().set_up()

            _please_contact_us_by_email_error_message_dict = {'en': 'Please contact us by email.', 'fr': 'Veuillez nous contacter par e-mail.', 'de': 'Bitte kontaktieren Sie uns per E-Mail.', 'es': 'Por favor, contáctanos por correo electrónico.', 'pt': 'Entre em contacto conosco por e-mail.', 'it': 'Contattateci tramite e-mail.', 'nl': 'Neem contact met ons op via e-mail.', 'ja': 'メールにてご連絡ください。', 'ru': 'Пожалуйста, свяжитесь с нами по электронной почте.', 'zh': '請透過電子郵件與我們聯繫。', 'pl': 'Prosimy o kontakt e-mailowy.', 'fa': 'لطفا از طریق ایمیل با ما تماس بگیرید.', 'he': 'אנא צרו איתנו קשר באמצעות הדואר האלקטרוני.', 'ko': '이메일로 연락해주세요.', 'ar': 'يرجى الاتصال بنا عن طريق البريد الإلكتروني.', 'id': 'Silakan hubungi kami melalui email.', 'uk': "Будь ласка, зв'яжіться з нами електронною поштою.", 'tr': 'Lütfen e-posta yoluyla bizimle iletişime geçin.', 'vi': 'Vui lòng liên hệ với chúng tôi qua email.', 'cs': 'Kontaktujte nás prosím emailem.', 'sv': 'Kontakta oss via e-post.', 'fi': 'Ota yhteyttä sähköpostitse.', 'hu': 'Kérjük, vegye fel velünk a kapcsolatot e-mailben.', 'th': 'โปรดติดต่อเราทางอีเมล', 'el': 'Επικοινωνήστε μαζί μας μέσω email.', 'ms': 'Sila hubungi kami melalui e-mel.', 'sr': 'Контактирајте нас путем е-поште.', 'ro': 'Vă rugăm să ne contactați prin e-mail.', 'bn': 'ইমেল দ্বারা আমাদের সাথে যোগাযোগ করুন.', 'ca': 'Si us plau, poseu-vos en contacte amb nosaltres per correu electrònic.', 'no': 'Vennligst kontakt oss på e-post.', 'bg': 'Моля, свържете се с нас по имейл.', 'da': 'Kontakt os venligst via e-mail.', 'sk': 'Kontaktujte nás prosím emailom.', 'hi': 'हमसे ईमेल द्वारा संपर्क करें।', 'et': 'Palun võtke meiega ühendust e-posti teel.', 'hr': 'Molimo kontaktirajte nas e-poštom.', 'az': 'Lütfən, bizimlə e-poçt vasitəsilə əlaqə saxlayın.', 'zh-yue': '請透過電郵與我們聯繫。', 'lt': 'Susisiekite su mumis el. paštu.', 'sl': 'Prosimo, kontaktirajte nas po e-pošti.', 'eu': 'Mesedez, jarri gurekin harremanetan posta elektronikoz.', 'hy': 'Խնդրում ենք կապվել մեզ հետ էլփոստով.', 'uz': "Iltimos, biz bilan elektron pochta orqali bog'laning.", 'ta': 'தயவுசெய்து மின்னஞ்சல் மூலம் எங்களை தொடர்பு கொள்ளவும்.', 'lv': 'Lūdzu, sazinieties ar mums pa e-pastu.'}
            _not_17_error_message_dict = {'en': 'Not 17.', 'fr': 'Pas 17.', 'de': 'Nicht 17.', 'es': 'No 17.', 'pt': 'Não 17.', 'it': 'Non 17.', 'nl': 'Niet 17.', 'ja': '17ではありません。', 'ru': 'Не 17.', 'zh': '不是17。', 'pl': 'Nie 17.', 'fa': 'نه 17.', 'he': 'לא 17.', 'ko': '17이 아님.', 'ar': 'ليس 17.', 'id': 'Bukan 17.', 'uk': 'Не 17.', 'tr': '17 değil.', 'vi': 'Không phải 17.', 'cs': 'Ne 17.', 'sv': 'Inte 17.', 'fi': 'Ei 17.', 'hu': 'Nem 17.', 'th': 'ไม่ใช่ 17.', 'el': 'Όχι 17.', 'ms': 'Bukan 17.', 'sr': 'Не 17.', 'ro': 'Nu 17.', 'bn': '17 নয়।', 'ca': 'No 17.', 'no': 'Ikke 17.', 'bg': 'Не 17.', 'da': 'Ikke 17.', 'sk': 'Nie 17.', 'hi': '17 नहीं.', 'et': 'Mitte 17.', 'hr': 'Ne 17.', 'az': '17 deyil.', 'zh-yue': '不是17歲。', 'lt': 'Ne 17.', 'sl': 'Ni 17.', 'eu': 'Ez da 17.', 'hy': '17 չէ.', 'uz': '17 emas.', 'ta': '17 இல்லை.', 'lv': 'Tas nav 17.'}

            self._please_contact_us_by_email_error_message = _please_contact_us_by_email_error_message_dict[self.language_code]
            self._not_17_error_message = _not_17_error_message_dict[self.language_code]


