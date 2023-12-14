from django.conf import settings as django_settings

if (django_settings.TESTS):
    import sys


    class SpeedyCoreBaseLanguageMixin(object):
        def _all_the_required_fields_are_required_errors_dict_by_required_fields(self, required_fields):
            return {field_name: [self._this_field_is_required_error_message] for field_name in required_fields}

        def _ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(self, max_length, value_length):
            return self._ensure_this_value_has_at_most_max_length_characters_error_message_to_format.format(max_length=max_length, value_length=value_length)

        def _exceeds_the_limit_4300_digits_for_integer_string_conversion_error_message_by_digits(self, digits):
            return self._exceeds_the_limit_4300_digits_for_integer_string_conversion_error_message_to_format.format(digits=digits)

        def set_up(self):
            super().set_up()

            _this_field_is_required_error_message_dict = {'en': 'This field is required.', 'fr': 'Ce champ est obligatoire.', 'de': "Dieses Feld ist zwingend erforderlich.", 'es': "Este campo es obligatorio.", 'pt': "Este campo é obrigatório.", 'it': "Questo campo è obbligatorio.", 'nl': "Dit veld is verplicht.", 'sv': "Detta fält måste fyllas i.", 'ko': "필수 항목입니다.", 'fi': "Tämä kenttä vaaditaan.", 'he': 'יש להזין תוכן בשדה זה.'}
            # _ensure_this_value_has_at_least_min_length_characters_error_message_to_format_dict = {'en': 'Ensure this value has at least {min_length} characters (it has {value_length}).', 'fr': "_____ # ~~~~ TODO", 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': "_____ # ~~~~ TODO"} # ~~~~ TODO
            _ensure_this_value_has_at_most_max_length_characters_error_message_to_format_dict = {'en': 'Ensure this value has at most {max_length} characters (it has {value_length}).', 'fr': 'Assurez-vous que cette valeur comporte au plus {max_length} caractères (actuellement {value_length}).', 'de': "Bitte sicherstellen, dass der Wert aus höchstens {max_length} Zeichen besteht. (Er besteht aus {value_length} Zeichen.)", 'es': "Asegúrese de que este valor tenga menos de {max_length} caracteres (tiene {value_length}).", 'pt': "Garanta que este valor tenha no máximo {max_length} caracteres (tem {value_length}).", 'it': "Assicurati che questo valore non contenga più di {max_length} caratteri (ne ha {value_length}).", 'nl': "Zorg dat deze waarde niet meer dan {max_length} tekens bevat (het zijn er nu {value_length}).", 'sv': "Säkerställ att detta värde har som mest {max_length} tecken (den har {value_length}).", 'ko': "이 값이 최대 {max_length} 개의 글자인지 확인하세요(입력값 {value_length} 자).", 'fi': "Varmista, että tämä arvo on enintään {max_length} merkkiä pitkä (tällä hetkellä {value_length}).", 'he': 'נא לוודא שערך זה מכיל {max_length} תווים לכל היותר (מכיל {value_length}).'}
            if (sys.version_info >= (3, 11)):
                _exceeds_the_limit_4300_digits_for_integer_string_conversion_error_message_to_format_dict = {'en': 'Exceeds the limit (4300 digits) for integer string conversion: value has {digits} digits; use sys.set_int_max_str_digits() to increase the limit', 'fr': "_____ # ~~~~ TODO", 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': "_____ # ~~~~ TODO"}
            else:
                _exceeds_the_limit_4300_digits_for_integer_string_conversion_error_message_to_format_dict = {'en': 'Exceeds the limit (4300) for integer string conversion: value has {digits} digits; use sys.set_int_max_str_digits() to increase the limit', 'fr': "_____ # ~~~~ TODO", 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': "_____ # ~~~~ TODO"}

            self._this_field_is_required_error_message = _this_field_is_required_error_message_dict[self.language_code]
            # self._ensure_this_value_has_at_least_min_length_characters_error_message_to_format = _ensure_this_value_has_at_least_min_length_characters_error_message_to_format_dict[self.language_code]
            self._ensure_this_value_has_at_most_max_length_characters_error_message_to_format = _ensure_this_value_has_at_most_max_length_characters_error_message_to_format_dict[self.language_code]
            self._exceeds_the_limit_4300_digits_for_integer_string_conversion_error_message_to_format = _exceeds_the_limit_4300_digits_for_integer_string_conversion_error_message_to_format_dict[self.language_code]


