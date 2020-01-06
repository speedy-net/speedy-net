class SpeedyMatchAccountsLanguageMixin(object):
    def _item_in_the_array_did_not_validate_error_message_by_index(self, index):
        return self._item_in_the_array_did_not_validate_error_message_to_format.format(index=index)

    def _active_languages_item_in_the_array_did_not_validate_value_is_not_a_valid_choice_errors_dict_by_index_and_value(self, index, value):
        return {'active_languages': ["{}{}".format(self._item_in_the_array_did_not_validate_error_message_by_index(index=index), self._value_is_not_a_valid_choice_error_message_by_value(value=value))]}

    def set_up(self):
        super().set_up()

        _a_profile_picture_is_required_error_message_dict = {'en': "A profile picture is required.", 'he': "נדרשת תמונת פרופיל."}
        _please_write_a_few_words_about_yourself_error_message_dict = {'en': "Please write a few words about yourself.", 'he': "אנא כתוב/י כמה מילים על עצמך."}
        _please_write_where_you_live_error_message_dict = {'en': "Please write where you live.", 'he': "אנא כתוב/י איפה את/ה גר/ה."}
        _do_you_have_children_how_many_error_message_dict = {'en': "Do you have children? How many?", 'he': "יש לך ילדים? כמה?"}
        _do_you_want_more_children_error_message_dict = {'en': "Do you want (more) children?", 'he': "את/ה רוצה (עוד) ילדים?"}
        _who_is_your_ideal_partner_error_message_dict = {'en': "Who is your ideal partner?", 'he': "מי בן או בת הזוג האידיאלי/ת שלך?"}
        _height_must_be_from_1_to_450_cm_error_message_dict = {'en': "Height must be from 1 to 450 cm.", 'he': 'הגובה חייב להיות בין 1 ל-450 ס"מ.'}
        _your_diet_is_required_error_message_dict = {'en': "Your diet is required.", 'he': "התזונה שלך נדרשת."}
        _your_smoking_status_is_required_error_message_dict = {'en': "Your smoking status is required.", 'he': "הרגלי העישון שלך נדרשים."}
        _your_relationship_status_is_required_error_message_dict = {'en': "Your relationship status is required.", 'he': "סטטוס מערכת היחסים שלך נדרש."}
        _gender_to_match_is_required_error_message_dict = {'en': "Gender to match is required.", 'he': "מין בן/בת הזוג שלך נדרש."}
        _minimal_age_to_match_must_be_from_0_to_180_years_error_message_dict = {'en': "Minimal age to match must be from 0 to 180 years.", 'he': "הגיל המינימלי לבן/בת הזוג חייב להיות בין 0 ל-180 שנה."}
        _maximal_age_to_match_must_be_from_0_to_180_years_error_message_dict = {'en': "Maximal age to match must be from 0 to 180 years.", 'he': "הגיל המקסימלי לבן/בת הזוג חייב להיות בין 0 ל-180 שנה."}
        _maximal_age_to_match_cant_be_less_than_minimal_age_to_match_error_message_dict = {'en': "Maximal age to match can't be less than minimal age to match.", 'he': "הגיל המקסימלי לבן/בת הזוג לא יכול להיות פחות מהגיל המינימלי לבן/בת הזוג."}
        diet_match_is_required_error_message_dict = {'en': "Diet match is required.", 'he': "התאמת התזונה נדרשת."}
        smoking_status_match_is_required_error_message_dict = {'en': "Smoking status match is required.", 'he': "התאמת הרגלי העישון נדרשת."}
        relationship_status_match_is_required_error_message_dict = {'en': "Relationship status match is required.", 'he': "התאמת סטטוס מערכת היחסים נדרשת."}
        _at_least_one_diet_match_option_should_be_5_hearts_error_message_dict = {'en': "At least one diet match option should be five hearts.", 'he': "לפחות אפשרות אחת להתאמת תזונה צריכה להיות חמישה לבבות."}
        _at_least_one_smoking_status_match_option_should_be_5_hearts_error_message_dict = {'en': "At least one smoking status match option should be five hearts.", 'he': "לפחות אפשרות אחת להתאמת הרגלי עישון צריכה להיות חמישה לבבות."}
        _at_least_one_relationship_status_match_option_should_be_5_hearts_error_message_dict = {'en': "At least one relationship status match option should be five hearts.", 'he': "לפחות אפשרות אחת להתאמת סטטוס מערכת יחסים צריכה להיות חמישה לבבות."}

        _item_in_the_array_did_not_validate_error_message_to_format_dict = {'en': "Item {index} in the array did not validate: ", 'he': "Item {index} in the array did not validate: "}

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


