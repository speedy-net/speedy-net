from django.conf import settings as django_settings


if (django_settings.TESTS):
    class SpeedyMatchAccountsLanguageMixin(object):
        def _item_in_the_array_did_not_validate_error_message_by_index(self, index):
            return self._item_in_the_array_did_not_validate_error_message_to_format.format(index=index)

        def _item_in_the_array_did_not_validate_value_is_not_a_valid_choice_errors_dict_by_field_name_and_index_and_value(self, field_name, index, value):
            return {field_name: ["{}{}".format(self._item_in_the_array_did_not_validate_error_message_by_index(index=index), self._value_is_not_a_valid_choice_error_message_by_value(value=value))]}

        def set_up(self):
            super().set_up()

            _a_profile_picture_is_required_error_message_dict = {'en': "A profile picture is required.", 'fr': "Une photo de profil est requise.", 'he': "נדרשת תמונת פרופיל."}
            _please_write_a_few_words_about_yourself_error_message_dict = {'en': "Please write a few words about yourself.", 'fr': "Veuillez vous présenter en quelques mots.", 'he': "אנא כתוב/י כמה מילים על עצמך."}
            _please_write_where_you_live_error_message_dict = {'en': "Please write where you live.", 'fr': "Veuillez indiquer votre ville de résidence.", 'he': "אנא כתוב/י איפה את/ה גר/ה."}
            _do_you_have_children_how_many_error_message_dict = {'en': "Do you have children? How many?", 'fr': "Avez-vous des enfants\xa0? Combien\xa0?", 'he': "יש לך ילדים? כמה?"}
            _do_you_want_more_children_error_message_dict = {'en': "Do you want (more) children?", 'fr': "Voulez-vous (plus) d’enfants\xa0?", 'he': "את/ה רוצה (עוד) ילדים?"}
            _who_is_your_ideal_partner_error_message_dict = {'en': "Who is your ideal partner?", 'fr': "Qui est votre partenaire idéal\xa0?", 'he': "מי בן או בת הזוג האידיאלי/ת שלך?"}
            _height_must_be_from_1_to_450_cm_error_message_dict = {'en': "Height must be from 1 to 450 cm.", 'fr': "La hauteur doit être comprise entre 1 et 450\xa0cm.", 'he': 'הגובה חייב להיות בין 1 ל-450 ס"מ.'}
            _your_diet_is_required_error_message_dict = {'en': "Your diet is required.", 'fr': "Veuillez renseigner votre régime alimentaire.", 'he': "התזונה שלך נדרשת."}
            _your_smoking_status_is_required_error_message_dict = {'en': "Your smoking status is required.", 'fr': "Veuillez spécifier si vous êtes fumeur.", 'he': "הרגלי העישון שלך נדרשים."}
            _your_relationship_status_is_required_error_message_dict = {'en': "Your relationship status is required.", 'fr': "Veuillez spécifier si vous êtes en couple.", 'he': "סטטוס מערכת היחסים שלך נדרש."}
            _gender_to_match_is_required_error_message_dict = {'en': "Gender to match is required.", 'fr': "Veuillez renseigner le genre souhaité.", 'he': "מין בן/בת הזוג שלך נדרש."}
            _minimal_age_to_match_must_be_from_0_to_180_years_error_message_dict = {'en': "Minimal age to match must be from 0 to 180 years.", 'fr': "L’âge minimum concordant doit être compris entre 0 et 180\xa0ans.", 'he': "הגיל המינימלי לבן/בת הזוג חייב להיות בין 0 ל-180 שנה."}
            _maximal_age_to_match_must_be_from_0_to_180_years_error_message_dict = {'en': "Maximal age to match must be from 0 to 180 years.", 'fr': "L’âge maximum concordant doit être compris entre 0 et 180\xa0ans.", 'he': "הגיל המקסימלי לבן/בת הזוג חייב להיות בין 0 ל-180 שנה."}
            _maximal_age_to_match_cant_be_less_than_minimal_age_to_match_error_message_dict = {'en': "Maximal age to match can't be less than minimal age to match.", 'fr': "L’âge maximal concordant ne peut être inférieur à l’âge minimal concordant.", 'he': "הגיל המקסימלי לבן/בת הזוג לא יכול להיות פחות מהגיל המינימלי לבן/בת הזוג."}
            diet_match_is_required_error_message_dict = {'en': "Diet match is required.", 'fr': "Concordance de régimes alimentaires requise.", 'he': "התאמת התזונה נדרשת."}
            smoking_status_match_is_required_error_message_dict = {'en': "Smoking status match is required.", 'fr': "Concordance de statut de fumeur requise.", 'he': "התאמת הרגלי העישון נדרשת."}
            relationship_status_match_is_required_error_message_dict = {'en': "Relationship status match is required.", 'fr': "Concordance du statut relationnel est requise.", 'he': "התאמת סטטוס מערכת היחסים נדרשת."}
            _at_least_one_diet_match_option_should_be_5_hearts_error_message_dict = {'en': "At least one diet match option should be five hearts.", 'fr': "Au moins une option de concordance de régime alimentaire doit être de cinq cœurs.", 'he': "לפחות אפשרות אחת להתאמת תזונה צריכה להיות חמישה לבבות."}
            _at_least_one_smoking_status_match_option_should_be_5_hearts_error_message_dict = {'en': "At least one smoking status match option should be five hearts.", 'fr': "Au moins une option de concordance de statut de fumeur doit être de cinq cœurs.", 'he': "לפחות אפשרות אחת להתאמת הרגלי עישון צריכה להיות חמישה לבבות."}
            _at_least_one_relationship_status_match_option_should_be_5_hearts_error_message_dict = {'en': "At least one relationship status match option should be five hearts.", 'fr': "Au moins une option de concordance du statut relationnel doit être à cinq cœurs.", 'he': "לפחות אפשרות אחת להתאמת סטטוס מערכת יחסים צריכה להיות חמישה לבבות."}

            _item_in_the_array_did_not_validate_error_message_to_format_dict = {'en': "Item {index} in the array did not validate: ", 'fr': "Item {index} in the array did not validate: ", 'he': "Item {index} in the array did not validate: "}

            self._a_profile_picture_is_required_error_message = _a_profile_picture_is_required_error_message_dict[self.language_code]
            self._please_write_a_few_words_about_yourself_error_message = _please_write_a_few_words_about_yourself_error_message_dict[self.language_code]
            self._please_write_where_you_live_error_message = _please_write_where_you_live_error_message_dict[self.language_code]
            self._do_you_have_children_how_many_error_message = _do_you_have_children_how_many_error_message_dict[self.language_code]
            self._do_you_want_more_children_error_message = _do_you_want_more_children_error_message_dict[self.language_code]
            self._who_is_your_ideal_partner_error_message = _who_is_your_ideal_partner_error_message_dict[self.language_code]
            self._height_must_be_from_1_to_450_cm_error_message = _height_must_be_from_1_to_450_cm_error_message_dict[self.language_code]
            self._your_diet_is_required_error_message = _your_diet_is_required_error_message_dict[self.language_code]
            self._your_smoking_status_is_required_error_message = _your_smoking_status_is_required_error_message_dict[self.language_code]
            self._your_relationship_status_is_required_error_message = _your_relationship_status_is_required_error_message_dict[self.language_code]
            self._gender_to_match_is_required_error_message = _gender_to_match_is_required_error_message_dict[self.language_code]
            self._minimal_age_to_match_must_be_from_0_to_180_years_error_message = _minimal_age_to_match_must_be_from_0_to_180_years_error_message_dict[self.language_code]
            self._maximal_age_to_match_must_be_from_0_to_180_years_error_message = _maximal_age_to_match_must_be_from_0_to_180_years_error_message_dict[self.language_code]
            self._maximal_age_to_match_cant_be_less_than_minimal_age_to_match_error_message = _maximal_age_to_match_cant_be_less_than_minimal_age_to_match_error_message_dict[self.language_code]
            self.diet_match_is_required_error_message = diet_match_is_required_error_message_dict[self.language_code]
            self.smoking_status_match_is_required_error_message = smoking_status_match_is_required_error_message_dict[self.language_code]
            self.relationship_status_match_is_required_error_message = relationship_status_match_is_required_error_message_dict[self.language_code]
            self._at_least_one_diet_match_option_should_be_5_hearts_error_message = _at_least_one_diet_match_option_should_be_5_hearts_error_message_dict[self.language_code]
            self._at_least_one_smoking_status_match_option_should_be_5_hearts_error_message = _at_least_one_smoking_status_match_option_should_be_5_hearts_error_message_dict[self.language_code]
            self._at_least_one_relationship_status_match_option_should_be_5_hearts_error_message = _at_least_one_relationship_status_match_option_should_be_5_hearts_error_message_dict[self.language_code]

            self._item_in_the_array_did_not_validate_error_message_to_format = _item_in_the_array_did_not_validate_error_message_to_format_dict[self.language_code]


