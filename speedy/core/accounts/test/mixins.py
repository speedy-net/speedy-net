from django.conf import settings as django_settings

if (django_settings.TESTS):
    from django.db import connection

    from speedy.core.base.test.mixins import SpeedyCoreBaseLanguageMixin

    from speedy.core.base.utils import to_attribute
    from speedy.core.accounts.models import Entity, User, UserEmailAddress


    class SpeedyCoreAccountsModelsMixin(object):
        def assert_models_count(self, entity_count, user_count, user_email_address_count, confirmed_email_address_count, unconfirmed_email_address_count):
            self.assertEqual(first=Entity.objects.count(), second=entity_count)
            self.assertEqual(first=User.objects.count(), second=user_count)
            self.assertEqual(first=UserEmailAddress.objects.count(), second=user_email_address_count)
            self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second=confirmed_email_address_count)
            self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=False).count(), second=unconfirmed_email_address_count)

        def assert_user_email_addresses_count(self, user, user_email_addresses_count, user_primary_email_addresses_count, user_confirmed_email_addresses_count, user_unconfirmed_email_addresses_count):
            self.assertEqual(first=user.email_addresses.count(), second=user_email_addresses_count)
            self.assertEqual(first=user.email_addresses.filter(is_primary=True).count(), second=user_primary_email_addresses_count)
            self.assertEqual(first=user.email_addresses.filter(is_confirmed=True).count(), second=user_confirmed_email_addresses_count)
            self.assertEqual(first=user.email_addresses.filter(is_confirmed=False).count(), second=user_unconfirmed_email_addresses_count)
            if (user_confirmed_email_addresses_count > 0):
                self.assertEqual(first=user.has_confirmed_email, second=True)
                self.assertEqual(first=user.email_addresses.filter(is_confirmed=True, is_primary=True).count(), second=user_primary_email_addresses_count)
            else:
                self.assertEqual(first=user.has_confirmed_email, second=False)
                self.assertEqual(first=user.email_addresses.filter(is_confirmed=True, is_primary=True).count(), second=0)

        def assert_user_first_and_last_name_in_all_languages(self, user):
            self.assertTupleEqual(tuple1=User.NAME_LOCALIZABLE_FIELDS, tuple2=('first_name', 'last_name'))
            self.assertEqual(first=user.first_name_en, second=user.first_name)
            self.assertEqual(first=user.first_name_fr, second=user.first_name)
            self.assertEqual(first=user.first_name_de, second=user.first_name)
            self.assertEqual(first=user.first_name_es, second=user.first_name)
            self.assertEqual(first=user.first_name_pt, second=user.first_name)
            self.assertEqual(first=user.first_name_it, second=user.first_name)
            self.assertEqual(first=user.first_name_nl, second=user.first_name)
            self.assertEqual(first=user.first_name_sv, second=user.first_name)
            self.assertEqual(first=user.first_name_ko, second=user.first_name)
            self.assertEqual(first=user.first_name_fi, second=user.first_name)
            self.assertEqual(first=user.first_name_he, second=user.first_name)
            self.assertEqual(first=user.last_name_en, second=user.last_name)
            self.assertEqual(first=user.last_name_fr, second=user.last_name)
            self.assertEqual(first=user.last_name_de, second=user.last_name)
            self.assertEqual(first=user.last_name_es, second=user.last_name)
            self.assertEqual(first=user.last_name_pt, second=user.last_name)
            self.assertEqual(first=user.last_name_it, second=user.last_name)
            self.assertEqual(first=user.last_name_nl, second=user.last_name)
            self.assertEqual(first=user.last_name_sv, second=user.last_name)
            self.assertEqual(first=user.last_name_ko, second=user.last_name)
            self.assertEqual(first=user.last_name_fi, second=user.last_name)
            self.assertEqual(first=user.last_name_he, second=user.last_name)
            field_name_localized_list = list()
            for base_field_name in User.NAME_LOCALIZABLE_FIELDS:
                for language_code, language_name in django_settings.LANGUAGES:
                    field_name_localized = to_attribute(name=base_field_name, language_code=language_code)
                    self.assertEqual(first=getattr(user, field_name_localized), second=getattr(user, base_field_name), msg="assert_user_first_and_last_name_in_all_languages::fields don't match ({field_name_localized}, {base_field_name}), user.pk={user_pk}, user.username={user_username}, user.slug={user_slug}, user.name={user_name}".format(
                        field_name_localized=field_name_localized,
                        base_field_name=base_field_name,
                        user_pk=user.pk,
                        user_username=user.username,
                        user_slug=user.slug,
                        user_name=user.name,
                    ))
                    field_name_localized_list.append(field_name_localized)
            self.assertListEqual(list1=field_name_localized_list, list2=['first_name_en', 'first_name_fr', 'first_name_de', 'first_name_es', 'first_name_pt', 'first_name_it', 'first_name_nl', 'first_name_sv', 'first_name_ko', 'first_name_fi', 'first_name_he', 'last_name_en', 'last_name_fr', 'last_name_de', 'last_name_es', 'last_name_pt', 'last_name_it', 'last_name_nl', 'last_name_sv', 'last_name_ko', 'last_name_fi', 'last_name_he'])


    class SpeedyCoreAccountsLanguageMixin(SpeedyCoreBaseLanguageMixin):
        _first_password_field_names = ['new_password1']
        _both_password_field_names = ['new_password1', 'new_password2']

        def _assert_model_is_entity_or_user(self, model):
            self.assertIn(member=model, container=[Entity, User])
            if (model is Entity):
                pass
            elif (model is User):
                pass
            else:
                raise Exception("Unexpected: model={}".format(model))

        def _value_is_not_a_valid_choice_error_message_by_value(self, value):
            return self._value_is_not_a_valid_choice_error_message_to_format.format(value=value)

        def _value_must_be_an_integer_error_message_by_value(self, value):
            return self._value_must_be_an_integer_error_message_to_format.format(value=value)

        def _username_must_contain_at_least_min_length_alphanumeric_characters_error_message_by_min_length_and_value_length(self, min_length, value_length):
            return self._username_must_contain_at_least_min_length_alphanumeric_characters_error_message_to_format.format(min_length=min_length, value_length=value_length)

        def _username_must_contain_at_most_max_length_alphanumeric_characters_error_message_by_max_length_and_value_length(self, max_length, value_length):
            return self._username_must_contain_at_most_max_length_alphanumeric_characters_error_message_to_format.format(max_length=max_length, value_length=value_length)

        def _username_must_contain_at_least_min_length_characters_error_message_by_min_length_and_value_length(self, min_length, value_length):
            return self._username_must_contain_at_least_min_length_characters_error_message_to_format.format(min_length=min_length, value_length=value_length)

        def _username_must_contain_at_most_max_length_characters_error_message_by_max_length_and_value_length(self, max_length, value_length):
            return self._username_must_contain_at_most_max_length_characters_error_message_to_format.format(max_length=max_length, value_length=value_length)

        def _a_confirmation_message_was_sent_to_email_address_error_message_by_email_address(self, email_address):
            return self._a_confirmation_message_was_sent_to_email_address_error_message_to_format.format(email_address=email_address)

        def _user_all_the_required_fields_keys(self):
            return [field_name.format(language_code=language_code) for field_name in ['first_name_{language_code}'] for language_code, language_name in django_settings.LANGUAGES] + ['username', 'slug', 'password', 'gender', 'date_of_birth']

        def _registration_form_all_the_required_fields_keys(self):
            return [field_name.format(language_code=self.language_code) for field_name in ['first_name_{language_code}', 'email', 'slug', 'new_password1', 'gender', 'date_of_birth']]

        def _profile_form_all_the_required_fields_keys(self):
            return [field_name.format(language_code=self.language_code) for field_name in ['first_name_{language_code}', 'slug', 'gender', 'date_of_birth']]

        def _registration_form_all_the_required_fields_are_required_errors_dict(self):
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=self._registration_form_all_the_required_fields_keys())

        def _profile_form_all_the_required_fields_are_required_errors_dict(self):
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=self._profile_form_all_the_required_fields_keys())

        def _date_of_birth_is_required_errors_dict(self):
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=['date_of_birth'])

        def _enter_a_valid_date_errors_dict(self):
            return {'date_of_birth': [self._enter_a_valid_date_error_message]}

        def _cannot_create_user_email_address_without_all_the_required_fields_errors_dict(self):
            return {
                'user': [self._this_field_cannot_be_null_error_message],
                'email': [self._this_field_cannot_be_blank_error_message],
            }

        def _id_contains_illegal_characters_errors_dict(self):
            return {'id': [self._id_contains_illegal_characters_error_message]}

        def _please_enter_a_correct_username_and_password_errors_dict(self):
            return {'__all__': [self._please_enter_a_correct_username_and_password_error_message]}

        def _invalid_password_errors_dict(self):
            return {'password': [self._invalid_password_error_message]}

        def _password_too_short_errors_dict(self, field_names):
            return {field_name: [self._password_too_short_error_message] for field_name in field_names}

        def _password_too_long_errors_dict(self, field_names):
            return {field_name: [self._password_too_long_error_message] for field_name in field_names}

        def _your_old_password_was_entered_incorrectly_errors_dict(self):
            return {'old_password': [self._your_old_password_was_entered_incorrectly_error_message]}

        def _the_two_password_fields_didnt_match_errors_dict(self):
            return {'new_password2': [self._the_two_password_fields_didnt_match_error_message]}

        def _enter_a_valid_email_address_errors_dict(self):
            return {'email': [self._enter_a_valid_email_address_error_message]}

        def _this_email_is_already_in_use_errors_dict(self):
            return {'email': [self._this_email_is_already_in_use_error_message]}

        def _this_username_is_already_taken_errors_dict(self, slug_fail=False, username_fail=False):
            self.assertIs(expr1=slug_fail, expr2=True)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._this_username_is_already_taken_error_message]
            if (username_fail):
                errors_dict['username'] = [self._this_username_is_already_taken_error_message]
            return errors_dict

        def _username_must_start_with_4_or_more_letters_errors_dict(self, model, slug_fail=False, username_fail=False):
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                if (model is Entity):
                    errors_dict['slug'] = [self._entity_username_must_start_with_4_or_more_letters_error_message]
                elif (model is User):
                    errors_dict['slug'] = [self._user_username_must_start_with_4_or_more_letters_error_message]
            if (username_fail):
                if (model is Entity):
                    errors_dict['username'] = [self._entity_username_must_start_with_4_or_more_letters_error_message]
                elif (model is User):
                    errors_dict['username'] = [self._user_username_must_start_with_4_or_more_letters_error_message]
            return errors_dict

        def _slug_does_not_parse_to_username_errors_dict(self, model, username_fail=False):
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {'slug': [self._slug_does_not_parse_to_username_error_message]}
            if (username_fail):
                if (model is Entity):
                    errors_dict['username'] = [self._entity_username_must_start_with_4_or_more_letters_error_message]
                elif (model is User):
                    errors_dict['username'] = [self._user_username_must_start_with_4_or_more_letters_error_message]
            return errors_dict

        def _date_of_birth_errors_dict_by_date_of_birth(self, date_of_birth):
            if (date_of_birth == ''):
                return self._date_of_birth_is_required_errors_dict()
            else:
                return self._enter_a_valid_date_errors_dict()

        def _you_cant_change_your_username_errors_dict_by_gender(self, gender):
            return {'slug': [self._you_cant_change_your_username_error_message_dict_by_gender[gender]]}

        def _cannot_create_user_without_all_the_required_fields_errors_dict_by_value(self, value, gender_is_valid=False):
            self.assertEqual(first=gender_is_valid, second=(value in User.GENDER_VALID_VALUES))
            if (value is None):
                str_value = ''
                gender_error_messages = [self._this_field_cannot_be_null_error_message]
            else:
                str_value = str(value)
                if (value == ''):
                    gender_error_messages = [self._value_must_be_an_integer_error_message_by_value(value=value)]
                else:
                    if (not (gender_is_valid)):
                        gender_error_messages = [self._value_is_not_a_valid_choice_error_message_by_value(value=value)]
                    else:
                        gender_error_messages = None
            slug_and_username_error_messages = [self._user_username_must_start_with_4_or_more_letters_error_message]
            date_of_birth_error_messages = [self._enter_a_valid_date_error_message]
            errors_dict = {
                'username': slug_and_username_error_messages,
                'slug': slug_and_username_error_messages,
                'date_of_birth': date_of_birth_error_messages,
            }
            if (value in [None, '']):
                self.assertEqual(first=str_value, second='')
                for language_code, language_name in django_settings.LANGUAGES:
                    if (value is None):
                        errors_dict['first_name_{language_code}'.format(language_code=language_code)] = [self._this_field_cannot_be_null_error_message]
                        # ~~~~ TODO: last name ValidationError(_('This field cannot be null.')) is not raised when User() is created without a last name - should be raised!
                        # errors_dict['last_name_{language_code}'.format(language_code=language_code)] = [self._this_field_cannot_be_null_error_message]
                    elif (value == ''):
                        errors_dict['first_name_{language_code}'.format(language_code=language_code)] = [self._this_field_cannot_be_blank_error_message]
                    else:
                        raise NotImplementedError()
                errors_dict['password'] = [self._this_field_cannot_be_blank_error_message]
            else:
                self.assertNotEqual(first=str_value, second='')
            self.assertEqual(first=gender_is_valid, second=(gender_error_messages is None))
            if (not (gender_is_valid)):
                errors_dict['gender'] = gender_error_messages
            return errors_dict

        def _model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(self, model, slug_fail=False, username_fail=False, username_value_length=None):
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._username_must_contain_at_least_min_length_alphanumeric_characters_error_message_by_min_length_and_value_length(min_length=model.settings.MIN_USERNAME_LENGTH, value_length=username_value_length)]
            if (username_fail):
                errors_dict['username'] = [self._username_must_contain_at_least_min_length_alphanumeric_characters_error_message_by_min_length_and_value_length(min_length=model.settings.MIN_USERNAME_LENGTH, value_length=username_value_length)]
            return errors_dict

        def _model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(self, model, slug_fail=False, username_fail=False, username_value_length=None):
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._username_must_contain_at_most_max_length_alphanumeric_characters_error_message_by_max_length_and_value_length(max_length=model.settings.MAX_USERNAME_LENGTH, value_length=username_value_length)]
            if (username_fail):
                errors_dict['username'] = [self._username_must_contain_at_most_max_length_alphanumeric_characters_error_message_by_max_length_and_value_length(max_length=model.settings.MAX_USERNAME_LENGTH, value_length=username_value_length)]
            return errors_dict

        def _model_slug_or_username_username_must_contain_at_least_min_length_characters_errors_dict_by_value_length(self, model, slug_fail=False, username_fail=False, slug_value_length=None, username_value_length=None):
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._username_must_contain_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=model.settings.MIN_SLUG_LENGTH, value_length=slug_value_length)]
            if (username_fail):
                errors_dict['username'] = [self._username_must_contain_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=model.settings.MIN_USERNAME_LENGTH, value_length=username_value_length)]
            return errors_dict

        def _model_slug_or_username_username_must_contain_at_most_max_length_characters_errors_dict_by_value_length(self, model, slug_fail=False, username_fail=False, slug_value_length=None, username_value_length=None):
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._username_must_contain_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=model.settings.MAX_SLUG_LENGTH, value_length=slug_value_length)]
            if (username_fail):
                errors_dict['username'] = [self._username_must_contain_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=model.settings.MAX_USERNAME_LENGTH, value_length=username_value_length)]
            return errors_dict

        def _this_field_cannot_be_null_errors_dict_by_field_name(self, field_name):
            return {field_name: [self._this_field_cannot_be_null_error_message]}

        def _this_field_cannot_be_blank_errors_dict_by_field_name(self, field_name):
            return {field_name: [self._this_field_cannot_be_blank_error_message]}

        def _value_must_be_valid_json_errors_dict_by_field_name(self, field_name):
            return {field_name: [self._value_must_be_valid_json_error_message]}

        def _ensure_this_value_is_greater_than_or_equal_to_minus_32768_errors_dict_by_field_name(self, field_name):
            return {field_name: [self._ensure_this_value_is_greater_than_or_equal_to_minus_32768_error_message]}

        def _ensure_this_value_is_less_than_or_equal_to_32767_errors_dict_by_field_name(self, field_name):
            return {field_name: [self._ensure_this_value_is_less_than_or_equal_to_32767_error_message]}

        def _value_is_not_a_valid_choice_errors_dict_by_field_name_and_value(self, field_name, value):
            return {field_name: [self._value_is_not_a_valid_choice_error_message_by_value(value=value)]}

        def _value_must_be_an_integer_errors_dict_by_field_name_and_value(self, field_name, value):
            return {field_name: [self._value_must_be_an_integer_error_message_by_value(value=value)]}

        def _this_field_cannot_be_null_errors_dict_by_field_name_list(self, field_name_list):
            return {field_name_list[i]: [self._this_field_cannot_be_null_error_message] for i in range(len(field_name_list))}

        def _value_must_be_an_integer_errors_dict_by_field_name_list_and_value_list(self, field_name_list, value_list):
            return {field_name_list[i]: [self._value_must_be_an_integer_error_message_by_value(value=value_list[i])] for i in range(len(field_name_list))}

        def _ensure_this_value_has_at_most_max_length_characters_errors_dict_by_field_name_and_max_length_and_value_length(self, field_name, max_length, value_length):
            return {field_name: [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=max_length, value_length=value_length)]}

        def _not_null_constraint_error_message_by_column_and_relation(self, column, relation):
            postgresql_version = connection.cursor().connection.server_version
            if (postgresql_version < 130000):
                # msg = 'null value in column "{}" violates not-null constraint'
                raise NotImplementedError("postgresql version must be at least 13.0.")
            else:
                msg = 'null value in column "{}" of relation "{}" violates not-null constraint'
            return msg.format(column, relation)

        def set_up(self):
            super().set_up()

            _this_field_cannot_be_null_error_message_dict = {'en': 'This field cannot be null.', 'fr': 'Ce champ ne peut pas contenir la valeur nulle.', 'de': "Dieses Feld darf nicht null sein.", 'es': "Este campo no puede ser nulo.", 'pt': "Este campo não pode ser nulo.", 'it': "Questo campo non può essere nullo.", 'nl': "Dit veld mag niet leeg zijn.", 'sv': "Detta fält får inte vara null.", 'ko': "이 필드는 null 값을 사용할 수 없습니다.", 'fi': "Tämän kentän arvo ei voi olla \"null\".", 'he': 'שדה זה אינו יכול להיות ריק.'}
            _this_field_cannot_be_blank_error_message_dict = {'en': 'This field cannot be blank.', 'fr': 'Ce champ ne peut pas être vide.', 'de': "Dieses Feld darf nicht leer sein.", 'es': "Este campo no puede estar vacío.", 'pt': "Este campo não pode ser vazio.", 'it': "Questo campo non può essere vuoto.", 'nl': "Dit veld kan niet leeg zijn.", 'sv': "Detta fält får inte vara tomt.", 'ko': "이 필드는 빈 칸으로 둘 수 없습니다.", 'fi': "Tämä kenttä ei voi olla tyhjä.", 'he': 'שדה זה אינו יכול להיות ריק.'}
            _id_contains_illegal_characters_error_message_dict = {'en': 'id contains illegal characters.', 'fr': 'cette ID contient des caractères illégaux.', 'de': "ID enthält nicht zugelassene Zeichen.", 'es': "id contiene caracteres ilegales.", 'pt': "id contém caracteres ilegais.", 'it': "l’id contiene caratteri illegali.", 'nl': "id bevat illegale tekens.", 'sv': "id innehåller olagliga tecken.", 'ko': "ID에 잘못된 문자가 있습니다.", 'fi': "id sisältää laittomia merkkejä.", 'he': 'id מכיל תווים לא חוקיים.'}
            _value_must_be_valid_json_error_message_dict = {'en': 'Value must be valid JSON.', 'fr': 'La valeur doit respecter la syntaxe JSON.', 'de': "Wert muss gültiges JSON sein.", 'es': "El valor debe ser un objeto JSON válido.", 'pt': "O valor deve ser um JSON válido.", 'it': "Il valore deve essere un JSON valido.", 'nl': "Waarde moet geldige JSON zijn.", 'sv': "Värdet måste vara giltig JSON.", 'ko': "올바른 JSON 형식이여야 합니다.", 'fi': "Arvon pitää olla kelvollista JSONia.", 'he': 'ערך חייב להיות JSON חוקי.'}
            _invalid_password_error_message_dict = {'en': 'Invalid password.', 'fr': 'Mot de passe invalide.', 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': 'הסיסמה לא תקינה.'}
            _password_too_short_error_message_dict = {'en': 'This password is too short. It must contain at least 8 characters.', 'fr': 'Ce mot de passe est trop court. Il doit contenir au minimum 8 caractères.', 'de': "Dieses Passwort ist zu kurz. Es muss mindestens 8 Zeichen enthalten.", 'es': "Esta contraseña es demasiado corta. Debe contener al menos 8 caracteres.", 'pt': "Esta palavra-passe é muito curta. Deve conter pelo menos 8 caracteres.", 'it': "Questa password è troppo corta. Deve contenere almeno 8 caratteri.", 'nl': "Dit wachtwoord is te kort. De minimale lengte is 8 tekens.", 'sv': "Detta lösenord är för kort. Det måste innehålla minst 8 tecken.", 'ko': "비밀번호가 너무 짧습니다. 최소 8 문자를 포함해야 합니다.", 'fi': "Tämä salasana on liian lyhyt. Sen tulee sisältää ainakin 8 merkkiä.", 'he': 'סיסמה זו קצרה מדי. היא חייבת להכיל לפחות 8 תווים.'}
            _password_too_long_error_message_dict = {'en': 'This password is too long. It must contain at most 120 characters.', 'fr': 'Ce mot de passe est trop long. Il doit contenir au maximum 120\xa0caractères.', 'de': "Dieses Passwort ist zu lang. Es darf höchstens 120 Zeichen enthalten.", 'es': "Esta contraseña es demasiado larga. Debe contener como máximo 120 caracteres.", 'pt': "Esta palavra-passe é muito longa. Ela precisa conter no máximo 120 caracteres.", 'it': "Questa password è troppo lunga. Deve contenere al massimo 120 caratteri.", 'nl': "Dit wachtwoord is te lang. Het mag maximaal 120 tekens bevatten.", 'sv': "Detta lösenord är för långt. Det får innehålla högst 120 tecken.", 'ko': "이 암호는 너무 깁니다. 최대 120자만 포함되어야 합니다.", 'fi': "Tämä salasana on liian pitkä. Siinä saa olla enintään 120 merkkiä.", 'he': 'סיסמה זו ארוכה מדי. היא יכולה להכיל 120 תווים לכל היותר.'}
            _this_username_is_already_taken_error_message_dict = {'en': 'This username is already taken.', 'fr': 'Ce nom d’utilisateur est déjà pris.', 'de': "Dieser Benutzername ist bereits vergeben.", 'es': "Este nombre de usuario ya está en uso.", 'pt': "Este nome de utilizador já foi utilizado.", 'it': "Questo nome utente è già stato scelto.", 'nl': "Deze gebruikersnaam is al in gebruik.", 'sv': "Det här användarnamnet är redan taget.", 'ko': "이 사용자명은 이미 사용 중입니다.", 'fi': "Tämä käyttäjänimi on jo varattu.", 'he': 'שם המשתמש/ת הזה כבר תפוס.'}
            _enter_a_valid_email_address_error_message_dict = {'en': 'Enter a valid email address.', 'fr': 'Saisissez une adresse de courriel valide.', 'de': "Bitte gültige E-Mail-Adresse eingeben.", 'es': "Introduzca una dirección de correo electrónico válida.", 'pt': "Introduza um endereço de e-mail válido.", 'it': "Inserisci un indirizzo email valido.", 'nl': "Voer een geldig e-mailadres in.", 'sv': "Fyll i en giltig e-postadress.", 'ko': "올바른 이메일 주소를 입력하세요.", 'fi': "Syötä kelvollinen sähköpostiosoite.", 'he': 'נא להזין כתובת דואר אלקטרוני חוקית.'}
            _this_email_is_already_in_use_error_message_dict = {'en': 'This email is already in use.', 'fr': 'Cet e-mail est déjà utilisé.', 'de': "Diese E-Mail wird bereits verwendet.", 'es': "Este correo electrónico ya está en uso.", 'pt': "Este e-mail já foi utilizado.", 'it': "Questo indirizzo e-mail è già in uso.", 'nl': "Deze email is al in gebruik.", 'sv': "Detta e-postmeddelande används redan.", 'ko': "이 이메일은 이미 사용 중입니다.", 'fi': "Tämä sähköpostiosoite on jo käytössä.", 'he': 'הדואר האלקטרוני הזה כבר נמצא בשימוש.'}
            _enter_a_valid_date_error_message_dict = {'en': 'Enter a valid date.', 'fr': 'Saisissez une date valide.', 'de': "Bitte ein gültiges Datum eingeben.", 'es': "Introduzca una fecha válida.", 'pt': "Introduza uma data válida.", 'it': "Inserisci una data valida.", 'nl': "Voer een geldige datum in.", 'sv': "Fyll i ett giltigt datum.", 'ko': "올바른 날짜를 입력하세요.", 'fi': "Syötä oikea päivämäärä.", 'he': 'יש להזין תאריך חוקי.'}
            _please_enter_a_correct_username_and_password_error_message_dict = {'en': 'Please enter a correct username and password. Note that both fields may be case-sensitive.', 'fr': 'Veuillez saisir un nom d’utilisateur et un mot de passe corrects. Attention, les deux champs peuvent être sensibles à la casse.', 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': 'נא להזין שם משתמש/ת וסיסמה נכונים. נא לשים לב כי שני השדות רגישים לאותיות גדולות/קטנות.'}
            _your_old_password_was_entered_incorrectly_error_message_dict = {'en': 'Your old password was entered incorrectly. Please enter it again.', 'fr': 'Votre ancien mot de passe est incorrect. Veuillez le rectifier.', 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': 'סיסמתך הישנה הוזנה בצורה שגויה. נא להזינה שוב.'}
            _the_two_password_fields_didnt_match_error_message_dict = {'en': "The two password fields didn’t match.", 'fr': "Les deux mots de passe ne correspondent pas.", 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': 'שני שדות הסיסמה אינם זהים.'}
            _entity_username_must_start_with_4_or_more_letters_error_message_dict = {'en': 'Username must start with 4 or more letters, and may contain letters, digits or dashes.', 'fr': 'Le nom d’utilisateur doit commencer par 4 lettres ou plus et peut contenir des lettres, des chiffres ou des tirets.', 'de': "Der Benutzername muss mit 4 oder mehr Buchstaben beginnen und kann Buchstaben, Ziffern oder Bindestriche enthalten.", 'es': "El nombre de usuario debe comenzar con 4 o más letras y puede contener letras, dígitos o guiones.", 'pt': "O nome do utilizador deve começar com 4 ou mais letras e pode conter letras, dígitos ou traços.", 'it': "Il nome utente deve iniziare con 4 o più caratteri e può contenere lettere, cifre o trattini.", 'nl': "De gebruikersnaam moet beginnen met 4 of meer letters en mag letters, cijfers of streepjes bevatten.", 'sv': "Username måste börja med 4 eller fler bokstäver och kan innehålla bokstäver, siffror eller bindestreck.", 'ko': "사용자명은 4글자 이상으로 시작되어야 하며, 글자, 숫자 또는 대시를 포함할 수 있습니다.", 'fi': "Käyttäjätunnuksen on alettava 4 tai useammalla kirjaimella, ja se voi sisältää kirjaimia, numeroita tai väliviivoja.", 'he': 'שם המשתמש/ת חייב להתחיל עם 4 אותיות או יותר, ויכול להכיל אותיות, ספרות או מקפים. שם המשתמש/ת חייב להיות באנגלית.'}
            _user_username_must_start_with_4_or_more_letters_error_message_dict = {'en': 'Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.', 'fr': 'Le nom d’utilisateur doit commencer par 4 lettres ou plus, suivies d’un nombre quelconque de chiffres. Vous pouvez ajouter des tirets entre les mots.', 'de': "Der Benutzername muss mit 4 oder mehr Buchstaben beginnen. Danach können Zahlen auftreten. Sie können Bindestriche zwischen die Wörter einfügen.", 'es': "El nombre de usuario debe comenzar con 4 o más letras, después de las cuales puede haber cualquier número de dígitos. Puedes agregar guiones entre palabras.", 'pt': "O nome do utilizador deve começar com 4 ou mais letras, após as quais pode haver qualquer número de dígitos. Podes adicionar traços entre as palavras.", 'it': "Il nome utente deve iniziare con 4 o più caratteri, dopo i quali può essere inserito un numero qualsiasi di cifre. Puoi aggiungere trattini tra le parole.", 'nl': "De gebruikersnaam moet beginnen met 4 of meer letters, met daarna een  een willekeurig aantal cijfers. Je kunt ook streepjes tussen woorden gebruiken.", 'sv': "Username måste börja med 4 eller fler bokstäver, varefter det kan vara valfritt antal siffror. Du kan lägga till bindestreck mellan ord.", 'ko': "사용자명은 4글자 이상으로 시작되어야 하며, 이후 숫자가 올 수 있습니다. 단어 사이에 대시를 추가할 수 있습니다.", 'fi': "Käyttäjätunnuksen tulee alkaa 4 tai useammalla kirjaimella, jonka jälkeen voi olla mikä tahansa määrä numeroita. Voit lisätä väliviivoja sanojen väliin.", 'he': 'שם המשתמש/ת חייב להתחיל עם 4 אותיות או יותר, לאחר מכן ניתן להוסיף מספר כלשהו של ספרות. ניתן להוסיף מקפים בין מילים. שם המשתמש/ת חייב להיות באנגלית.'}
            _slug_does_not_parse_to_username_error_message_dict = {'en': 'Slug does not parse to username.', 'fr': 'Slug ne correspond pas à un nom d’utilisateur.', 'de': "Slug wird nicht in Benutzername umgewandelt.", 'es': "Slug no analiza el nombre de usuario.", 'pt': "O slug não pode ser usado como nome de utilizador.", 'it': "Lo slug non viene analizzato come nome utente.", 'nl': "Slug parseert niet naar gebruikersnaam.", 'sv': "Slug tolkas inte som användarnamn.", 'ko': "슬러그는 사용자명을 구문분석하지 않습니다", 'fi': "Slug ei jäsenny käyttäjänimeksi.", 'he': 'slug לא מתאים לשם המשתמש/ת.'}
            _youve_already_confirmed_this_email_address_error_message_dict = {'en': "You've already confirmed this email address.", 'fr': "Vous avez déjà confirmé cette adresse e-mail.", 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': 'כבר אימתת את כתובת הדואר האלקטרוני שלך.'}
            _invalid_confirmation_link_error_message_dict = {'en': "Invalid confirmation link.", 'fr': "Lien de confirmation invalide.", 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': 'קישור אימות לא חוקי.'}
            _youve_confirmed_your_email_address_message_dict = {'en': "You've confirmed your email address.", 'fr': "Vous avez confirmé votre adresse e-mail.", 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': 'אימתת את כתובת הדואר האלקטרוני שלך.'}
            _the_email_address_was_deleted_error_message_dict = {'en': 'The email address was deleted.', 'fr': 'L’adresse e-mail a été supprimée.', 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': 'כתובת הדואר האלקטרוני נמחקה.'}
            _you_have_changed_your_primary_email_address_error_message_dict = {'en': 'You have made this email address primary.', 'fr': 'Vous avez défini cette adresse e-mail comme adresse primaire.', 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': 'הפכת את כתובת הדואר האלקטרוני הזאת לראשית.'}
            _username_is_required_error_message_dict = {'en': 'Username is required.', 'fr': 'Nom d’utilisateur requis.', 'de': "Benutzername ist erforderlich.", 'es': "Se requiere nombre de usuario.", 'pt': "O nome de utilizador é obrigatório.", 'it': "Il nome utente è richiesto.", 'nl': "Gebruikersnaam is vereist.", 'sv': "Username är obligatoriskt.", 'ko': "사용자명이 필요합니다.", 'fi': "Käyttäjätunnus vaaditaan.", 'he': 'שם המשתמש/ת נדרש.'}
            _password_reset_on_speedy_net_subject_dict = {'en': "Password reset on Speedy Net", 'fr': "Réinitialisation du mot de passe sur Speedy Net", 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': "איפוס סיסמה בספידי נט"}
            _password_reset_on_speedy_match_subject_dict = {'en': "Password reset on Speedy Match", 'fr': "Réinitialisation du mot de passe sur Speedy Match", 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': "איפוס סיסמה בספידי מץ'"}
            _ensure_this_value_is_greater_than_or_equal_to_minus_32768_error_message_dict = {'en': 'Ensure this value is greater than or equal to -32768.', 'fr': 'Assurez-vous que cette valeur est supérieure ou égale à -32768.', 'de': "Dieser Wert muss größer oder gleich -32768 sein.", 'es': "Asegúrese de que este valor es mayor o igual a -32768.", 'pt': "Garanta que este valor seja maior ou igual a -32768.", 'it': "Assicurati che questo valore sia maggiore o uguale a -32768.", 'nl': "Zorg ervoor dat deze waarde minstens -32768 is.", 'sv': "Kontrollera att detta värde är större än eller lika med -32768.", 'ko': "-32768 이상의 값을 입력해 주세요.", 'fi': "Tämän luvun on oltava vähintään -32768.", 'he': 'יש לוודא שהערך גדול מ או שווה ל־-32768.'}
            _ensure_this_value_is_less_than_or_equal_to_32767_error_message_dict = {'en': 'Ensure this value is less than or equal to 32767.', 'fr': 'Assurez-vous que cette valeur est inférieure ou égale à 32767.', 'de': "Dieser Wert muss kleiner oder gleich 32767 sein.", 'es': "Asegúrese de que este valor es menor o igual a 32767.", 'pt': "Garanta que este valor seja menor ou igual a 32767.", 'it': "Assicurati che questo valore sia minore o uguale a 32767.", 'nl': "Zorg ervoor dat deze waarde hoogstens 32767 is.", 'sv': "Kontrollera att detta värde är mindre än eller lika med 32767.", 'ko': "32767 이하의 값을 입력해 주세요.", 'fi': "Tämän arvon on oltava enintään 32767.", 'he': 'יש לוודא שערך זה פחות מ או שווה ל־32767 .'}
            _value_too_long_for_type_character_varying_255_error_message_dict = {'en': 'value too long for type character varying(255)', 'fr': 'value too long for type character varying(255)', 'de': 'value too long for type character varying(255)', 'es': 'value too long for type character varying(255)', 'pt': 'value too long for type character varying(255)', 'it': 'value too long for type character varying(255)', 'nl': 'value too long for type character varying(255)', 'sv': 'value too long for type character varying(255)', 'ko': 'value too long for type character varying(255)', 'fi': 'value too long for type character varying(255)', 'he': 'value too long for type character varying(255)'}

            _value_is_not_a_valid_choice_error_message_to_format_dict = {'en': 'Value {value} is not a valid choice.', 'fr': 'La valeur «\xa0{value}\xa0» n’est pas un choix valide.', 'de': "Wert {value} ist keine gültige Option.", 'es': "Valor {value} no es una opción válida.", 'pt': "O valor {value} não é uma escolha válida.", 'it': "Il valore {value} non è una scelta valida.", 'nl': "Waarde {value} is geen geldige keuze.", 'sv': "Värdet {value} är inget giltigt alternativ.", 'ko': "{value} 은/는 올바른 선택사항이 아닙니다.", 'fi': "Arvo {value} ei kelpaa.", 'he': 'ערך {value} אינו אפשרות חוקית.'}
            _value_must_be_an_integer_error_message_to_format_dict = {'en': "“{value}” value must be an integer.", 'fr': "La valeur «\xa0{value}\xa0» doit être un nombre entier.", 'de': "Wert „{value}“ muss eine Ganzzahl sein.", 'es': "“{value}”: el valor debería ser un numero entero", 'pt': "O valor “{value}” deve ser inteiro.", 'it': "Il valore \"{value}\" deve essere un intero.", 'nl': "Waarde van ‘{value}’ moet een geheel getal zijn.", 'sv': "Värdet \"{value}\" måste vara ett heltal.", 'ko': "\"{value}\" 값은 정수를 입력하여야 합니다.", 'fi': "{value}-arvo tulee olla kokonaisluku.", 'he': "הערך '{value}' חייב להיות מספר שלם."}
            _username_must_contain_at_least_min_length_alphanumeric_characters_error_message_to_format_dict = {'en': 'Username must contain at least {min_length} alphanumeric characters (it has {value_length}).', 'fr': 'Le nom d’utilisateur doit contenir au moins {min_length}\xa0caractères alphanumériques (il en contient {value_length}).', 'de': "Der Benutzername muss mindestens {min_length} alphanumerische Zeichen (er hat {value_length}) enthalten.", 'es': "El nombre de usuario debe contener al menos {min_length} caracteres alfanumérico (tiene {value_length}).", 'pt': "O nome do utilizador deve conter pelo menos {min_length} caracteres alfanuméricos (contém {value_length}).", 'it': "Il nome utente deve contenere almeno {min_length} caratteri alfanumerici (ha {value_length}).", 'nl': "De gebruikersnaam moet ten minste {min_length} alfanumerieke tekens bevatten (het bevat {value_length}).", 'sv': "Username måste innehålla minst {min_length} alfanumeriska tecken (det har {value_length}).", 'ko': "사용자명에는 최소 {min_length}자의 영문자 숫자가 포함되어야 합니다 ({value_length}자).", 'fi': "Käyttäjätunnuksessa on oltava vähintään {min_length} aakkosnumeerista merkkiä (sillä on {value_length}).", 'he': 'נא לוודא ששם המשתמש/ת מכיל {min_length} תווים אלפאנומריים לפחות (מכיל {value_length}). שם המשתמש/ת חייב להיות באנגלית.'}
            _username_must_contain_at_most_max_length_alphanumeric_characters_error_message_to_format_dict = {'en': 'Username must contain at most {max_length} alphanumeric characters (it has {value_length}).', 'fr': 'Le nom d’utilisateur doit contenir au maximum {max_length}\xa0caractères alphanumériques (il en contient {value_length}).', 'de': "Der Benutzername darf höchstens {max_length} alphanumerische Zeichen (er hat {value_length}) enthalten.", 'es': "El nombre de usuario debe contener como máximo {max_length} caracteres alfanumérico (tiene {value_length}).", 'pt': "O nome do utilizador deve conter no máximo {max_length} caracteres alfanuméricos (contém {value_length}).", 'it': "Il nome utente deve contenere al massimo {max_length} caratteri alfanumerici (ha {value_length}).", 'nl': "De gebruikersnaam mag maximaal {max_length} alfanumerieke tekens bevatten (het bevat {value_length}).", 'sv': "Username måste innehålla högst {max_length} alfanumeriska tecken (det har {value_length}).", 'ko': "사용자명에는 최대 {max_length}자의 영문자 숫자가 포함되어야 합니다 ({value_length}자).", 'fi': "Käyttäjätunnuksessa saa olla enintään {max_length} aakkosnumeerista merkkiä (sillä on {value_length}).", 'he': 'נא לוודא ששם המשתמש/ת מכיל {max_length} תווים אלפאנומריים לכל היותר (מכיל {value_length}). שם המשתמש/ת חייב להיות באנגלית.'}
            _username_must_contain_at_least_min_length_characters_error_message_to_format_dict = {'en': 'Username must contain at least {min_length} characters (it has {value_length}).', 'fr': 'Le nom d’utilisateur doit contenir au moins {min_length}\xa0caractères (il en contient {value_length}).', 'de': "Der Benutzername muss mindestens {min_length} Zeichen (er hat {value_length}) enthalten.", 'es': "El nombre de usuario debe contener al menos {min_length} caracteres (tiene {value_length}).", 'pt': "O nome do utilizador deve conter pelo menos {min_length} caracteres (contém {value_length}).", 'it': "Il nome utente deve contenere almeno {min_length} caratteri (ha {value_length}).", 'nl': "De gebruikersnaam moet ten minste {min_length} karakter bevatten (het bevat {value_length}).", 'sv': "Username måste innehålla minst {min_length} tecken (det har {value_length}).", 'ko': "사용자명에는 최소 {min_length}자의 문자가 포함되어야 합니다 ({value_length}자).", 'fi': "Käyttäjätunnuksessa on oltava vähintään {min_length} merkkiä (sillä on {value_length}).", 'he': 'נא לוודא ששם המשתמש/ת מכיל {min_length} תווים לפחות (מכיל {value_length}).'}
            _username_must_contain_at_most_max_length_characters_error_message_to_format_dict = {'en': 'Username must contain at most {max_length} characters (it has {value_length}).', 'fr': 'Le nom d’utilisateur doit contenir au maximum {max_length}\xa0caractères (il en contient {value_length}).', 'de': "Der Benutzername darf höchstens {max_length} Zeichen (er hat {value_length}) enthalten.", 'es': "El nombre de usuario debe contener como máximo {max_length} caracteres (tiene {value_length}).", 'pt': "O nome do utilizador deve conter no máximo {max_length} caracteres (contém {value_length}).", 'it': "Il nome utente deve contenere al massimo {max_length} caratteri (ha {value_length}).", 'nl': "De gebruikersnaam mag maximaal {max_length} tekens bevatten (het bevat {value_length}).", 'sv': "Username måste innehålla minst {max_length} tecken (det har {value_length}).", 'ko': "사용자명에는 최대 {max_length}자의 문자가 포함되어야 합니다 ({value_length}자).", 'fi': "Käyttäjätunnuksessa saa olla enintään {max_length} merkkiä (sillä on {value_length}).", 'he': 'נא לוודא ששם המשתמש/ת מכיל {max_length} תווים לכל היותר (מכיל {value_length}).'}
            _a_confirmation_message_was_sent_to_email_address_error_message_to_format_dict = {'en': 'A confirmation message was sent to {email_address}', 'fr': 'Un message de confirmation a été envoyé à {email_address}', 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': 'הודעת אימות נשלחה ל-‎{email_address}‎'}

            _you_cant_change_your_username_error_message_dict_by_gender = {
                'en': {
                    **{gender: "You can't change your username." for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: "Vous ne pouvez pas changer votre nom d’utilisateur." for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "לא ניתן לשנות שם משתמשת.",
                    User.GENDER_MALE_STRING: "לא ניתן לשנות שם משתמש.",
                    User.GENDER_OTHER_STRING: "לא ניתן לשנות שם משתמש/ת.",
                },
            }
            _confirm_your_email_address_on_speedy_net_subject_dict_by_gender = {
                'en': {
                    **{gender: "Confirm your email address on Speedy Net" for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: "Confirmez votre adresse e-mail sur Speedy Net" for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "אמתי את כתובת הדואר האלקטרוני שלך בספידי נט",
                    User.GENDER_MALE_STRING: "אמת את כתובת הדואר האלקטרוני שלך בספידי נט",
                    User.GENDER_OTHER_STRING: "אמת/י את כתובת הדואר האלקטרוני שלך בספידי נט",
                },
            }
            _confirm_your_email_address_on_speedy_match_subject_dict_by_gender = {
                'en': {
                    **{gender: "Confirm your email address on Speedy Match" for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: "Confirmez votre adresse e-mail sur Speedy Match" for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "אמתי את כתובת הדואר האלקטרוני שלך בספידי מץ'",
                    User.GENDER_MALE_STRING: "אמת את כתובת הדואר האלקטרוני שלך בספידי מץ'",
                    User.GENDER_OTHER_STRING: "אמת/י את כתובת הדואר האלקטרוני שלך בספידי מץ'",
                },
            }

            self._this_field_cannot_be_null_error_message = _this_field_cannot_be_null_error_message_dict[self.language_code]
            self._this_field_cannot_be_blank_error_message = _this_field_cannot_be_blank_error_message_dict[self.language_code]
            self._id_contains_illegal_characters_error_message = _id_contains_illegal_characters_error_message_dict[self.language_code]
            self._value_must_be_valid_json_error_message = _value_must_be_valid_json_error_message_dict[self.language_code]
            self._invalid_password_error_message = _invalid_password_error_message_dict[self.language_code]
            self._password_too_short_error_message = _password_too_short_error_message_dict[self.language_code]
            self._password_too_long_error_message = _password_too_long_error_message_dict[self.language_code]
            self._this_username_is_already_taken_error_message = _this_username_is_already_taken_error_message_dict[self.language_code]
            self._enter_a_valid_email_address_error_message = _enter_a_valid_email_address_error_message_dict[self.language_code]
            self._this_email_is_already_in_use_error_message = _this_email_is_already_in_use_error_message_dict[self.language_code]
            self._enter_a_valid_date_error_message = _enter_a_valid_date_error_message_dict[self.language_code]
            self._please_enter_a_correct_username_and_password_error_message = _please_enter_a_correct_username_and_password_error_message_dict[self.language_code]
            self._your_old_password_was_entered_incorrectly_error_message = _your_old_password_was_entered_incorrectly_error_message_dict[self.language_code]
            self._the_two_password_fields_didnt_match_error_message = _the_two_password_fields_didnt_match_error_message_dict[self.language_code]
            self._entity_username_must_start_with_4_or_more_letters_error_message = _entity_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]
            self._user_username_must_start_with_4_or_more_letters_error_message = _user_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]
            self._slug_does_not_parse_to_username_error_message = _slug_does_not_parse_to_username_error_message_dict[self.language_code]
            self._youve_already_confirmed_this_email_address_error_message = _youve_already_confirmed_this_email_address_error_message_dict[self.language_code]
            self._invalid_confirmation_link_error_message = _invalid_confirmation_link_error_message_dict[self.language_code]
            self._youve_confirmed_your_email_address_message = _youve_confirmed_your_email_address_message_dict[self.language_code]
            self._the_email_address_was_deleted_error_message = _the_email_address_was_deleted_error_message_dict[self.language_code]
            self._you_have_changed_your_primary_email_address_error_message = _you_have_changed_your_primary_email_address_error_message_dict[self.language_code]
            self._username_is_required_error_message = _username_is_required_error_message_dict[self.language_code]
            self._password_reset_on_speedy_net_subject = _password_reset_on_speedy_net_subject_dict[self.language_code]
            self._password_reset_on_speedy_match_subject = _password_reset_on_speedy_match_subject_dict[self.language_code]
            self._ensure_this_value_is_greater_than_or_equal_to_minus_32768_error_message = _ensure_this_value_is_greater_than_or_equal_to_minus_32768_error_message_dict[self.language_code]
            self._ensure_this_value_is_less_than_or_equal_to_32767_error_message = _ensure_this_value_is_less_than_or_equal_to_32767_error_message_dict[self.language_code]
            self._value_too_long_for_type_character_varying_255_error_message = _value_too_long_for_type_character_varying_255_error_message_dict[self.language_code]

            self._value_is_not_a_valid_choice_error_message_to_format = _value_is_not_a_valid_choice_error_message_to_format_dict[self.language_code]
            self._value_must_be_an_integer_error_message_to_format = _value_must_be_an_integer_error_message_to_format_dict[self.language_code]
            self._username_must_contain_at_least_min_length_alphanumeric_characters_error_message_to_format = _username_must_contain_at_least_min_length_alphanumeric_characters_error_message_to_format_dict[self.language_code]
            self._username_must_contain_at_most_max_length_alphanumeric_characters_error_message_to_format = _username_must_contain_at_most_max_length_alphanumeric_characters_error_message_to_format_dict[self.language_code]
            self._username_must_contain_at_least_min_length_characters_error_message_to_format = _username_must_contain_at_least_min_length_characters_error_message_to_format_dict[self.language_code]
            self._username_must_contain_at_most_max_length_characters_error_message_to_format = _username_must_contain_at_most_max_length_characters_error_message_to_format_dict[self.language_code]
            self._a_confirmation_message_was_sent_to_email_address_error_message_to_format = _a_confirmation_message_was_sent_to_email_address_error_message_to_format_dict[self.language_code]

            self._you_cant_change_your_username_error_message_dict_by_gender = _you_cant_change_your_username_error_message_dict_by_gender[self.language_code]
            self._confirm_your_email_address_on_speedy_net_subject_dict_by_gender = _confirm_your_email_address_on_speedy_net_subject_dict_by_gender[self.language_code]
            self._confirm_your_email_address_on_speedy_match_subject_dict_by_gender = _confirm_your_email_address_on_speedy_match_subject_dict_by_gender[self.language_code]

            self.assertSetEqual(set1=set(self._you_cant_change_your_username_error_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._confirm_your_email_address_on_speedy_net_subject_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._confirm_your_email_address_on_speedy_match_subject_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))

            self.assertEqual(first=len(set(self._you_cant_change_your_username_error_message_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._confirm_your_email_address_on_speedy_net_subject_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._confirm_your_email_address_on_speedy_match_subject_dict_by_gender.keys())), second=3)

            self.assertEqual(first=len(set(self._user_all_the_required_fields_keys())), second=16)
            self.assertEqual(first=set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None).keys()), second=set(self._user_all_the_required_fields_keys()))
            self.assertEqual(first=len(set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None).keys())), second=16)
            self.assertEqual(first=len(set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None).keys()) - set(self._user_all_the_required_fields_keys())), second=0)
            self.assertSetEqual(set1=set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None).keys()), set2=set(self._user_all_the_required_fields_keys()) | {'first_name_en', 'first_name_he'})
            self.assertEqual(first=set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value='').keys()), second=set(self._user_all_the_required_fields_keys()))
            self.assertEqual(first=len(set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value='').keys())), second=16)
            self.assertEqual(first=len(set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value='').keys()) - set(self._user_all_the_required_fields_keys())), second=0)
            self.assertSetEqual(set1=set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value='').keys()), set2=set(self._user_all_the_required_fields_keys()) | {'first_name_en', 'first_name_he'})
            self.assertListEqual(list1=self._profile_form_all_the_required_fields_keys(), list2=[field_name for field_name in self._registration_form_all_the_required_fields_keys() if (not (field_name in ['email', 'new_password1']))])
            self.assertSetEqual(set1=set(self._registration_form_all_the_required_fields_keys()) - {'email', 'new_password1'}, set2=set(self._profile_form_all_the_required_fields_keys()))
            self.assertSetEqual(set1=set(self._profile_form_all_the_required_fields_keys()) | {'email', 'new_password1'}, set2=set(self._registration_form_all_the_required_fields_keys()))
            self.assertNotEqual(first=[to_attribute(name='first_name')], second=['first_name'])
            self.assertNotEqual(first=[to_attribute(name='first_name'), to_attribute(name='last_name')], second=['first_name', 'last_name'])
            self.assertListEqual(list1=self._user_all_the_required_fields_keys()[:len(django_settings.LANGUAGES)], list2=[to_attribute(name='first_name', language_code=language_code) for language_code, language_name in django_settings.LANGUAGES])
            self.assertListEqual(list1=self._user_all_the_required_fields_keys()[:len(django_settings.LANGUAGES)], list2=[to_attribute(name='first_name', language_code='en'), to_attribute(name='first_name', language_code='fr'), to_attribute(name='first_name', language_code='de'), to_attribute(name='first_name', language_code='es'), to_attribute(name='first_name', language_code='pt'), to_attribute(name='first_name', language_code='it'), to_attribute(name='first_name', language_code='nl'), to_attribute(name='first_name', language_code='sv'), to_attribute(name='first_name', language_code='ko'), to_attribute(name='first_name', language_code='fi'), to_attribute(name='first_name', language_code='he')])
            self.assertListEqual(list1=self._user_all_the_required_fields_keys()[:len(django_settings.LANGUAGES)], list2=['first_name_en', 'first_name_fr', 'first_name_de', 'first_name_es', 'first_name_pt', 'first_name_it', 'first_name_nl', 'first_name_sv', 'first_name_ko', 'first_name_fi', 'first_name_he'])
            self.assertListEqual(list1=self._registration_form_all_the_required_fields_keys()[:1], list2=[to_attribute(name='first_name')])
            self.assertListEqual(list1=self._profile_form_all_the_required_fields_keys()[:1], list2=[to_attribute(name='first_name')])

        def assert_required_fields_and_errors_dict(self, required_fields, errors_dict):
            self.assertSetEqual(set1=set(errors_dict.keys()), set2=set(required_fields))
            self.assertDictEqual(d1=errors_dict, d2=self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=required_fields))

        def assert_registration_form_required_fields(self, required_fields):
            self.assert_required_fields_and_errors_dict(required_fields=required_fields, errors_dict=self._registration_form_all_the_required_fields_are_required_errors_dict())

        def assert_profile_form_required_fields(self, required_fields):
            self.assert_required_fields_and_errors_dict(required_fields=required_fields, errors_dict=self._profile_form_all_the_required_fields_are_required_errors_dict())


