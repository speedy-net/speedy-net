class SpeedyMatchAccountsLanguageMixin(object):
    def set_up(self):
        super().set_up()

        _a_profile_picture_is_required_error_message_dict = {'en': 'A profile picture is required.', 'he': '_____ # ~~~~ TODO'}
        _please_write_some_text_in_this_field_error_message_dict = {'en': 'Please write some text in this field.', 'he': '_____ # ~~~~ TODO'}
        _please_write_where_you_live_error_message_dict = {'en': 'Please write where you live.', 'he': '_____ # ~~~~ TODO'}
        _do_you_have_children_how_many_error_message_dict = {'en': 'Do you have children? How many?', 'he': '_____ # ~~~~ TODO'}
        _do_you_want_more_children_error_message_dict = {'en': 'Do you want (more) children?', 'he': '_____ # ~~~~ TODO'}
        _height_must_be_from_1_to_450_cm_error_message_dict = {'en': 'Height must be from 1 to 450 cm.', 'he': 'הגובה חייב להיות בין 1 ל-450 ס"מ.___'}
        _your_diet_is_required_error_message_dict = {'en': 'Your diet is required.', 'he': '_____ # ~~~~ TODO'}
        _your_smoking_status_is_required_error_message_dict = {'en': 'Your smoking status is required.', 'he': '_____ # ~~~~ TODO'}
        _your_relationship_status_is_required_error_message_dict = {'en': 'Your relationship status is required.', 'he': '_____ # ~~~~ TODO'}
        _gender_to_match_is_required_error_message_dict = {'en': 'Gender to match is required.', 'he': '_____ # ~~~~ TODO'}
        _minimal_age_to_match_must_be_from_0_to_180_years_error_message_dict = {'en': 'Minimal age to match must be from 0 to 180 years.', 'he': '_____ # ~~~~ TODO'}
        _maximal_age_to_match_must_be_from_0_to_180_years_error_message_dict = {'en': 'Maximal age to match must be from 0 to 180 years.', 'he': '_____ # ~~~~ TODO'}
        _maximal_age_to_match_cant_be_less_than_minimal_age_to_match_error_message_dict = {'en': "Maximal age to match can't be less than minimal age to match.", 'he': '_____ # ~~~~ TODO'}
        _please_select_diet_match_error_message_dict = {'en': 'Please select diet match.', 'he': '_____ # ~~~~ TODO'}
        _please_select_smoking_status_match_error_message_dict = {'en': 'Please select smoking status match.', 'he': '_____ # ~~~~ TODO'}
        _please_select_relationship_status_match_error_message_dict = {'en': 'Please select marital status match.', 'he': '_____ # ~~~~ TODO'}
        _at_least_one_diet_match_option_should_be_5_hearts_error_message_dict = {'en': 'At least one diet match option should be five hearts.', 'he': '_____ # ~~~~ TODO'}
        _at_least_one_smoking_status_match_option_should_be_5_hearts_error_message_dict = {'en': 'At least one smoking status match option should be five hearts.', 'he': '_____ # ~~~~ TODO'}
        _at_least_one_relationship_status_match_option_should_be_5_hearts_error_message_dict = {'en': 'At least one marital status match option should be five hearts.', 'he': '_____ # ~~~~ TODO'}

        self._a_profile_picture_is_required_error_message = _a_profile_picture_is_required_error_message_dict[self.language_code]
        self._please_write_some_text_in_this_field_error_message = _please_write_some_text_in_this_field_error_message_dict[self.language_code]
        self._please_write_where_you_live_error_message = _please_write_where_you_live_error_message_dict[self.language_code]
        self._do_you_have_children_how_many_error_message = _do_you_have_children_how_many_error_message_dict[self.language_code]
        self._do_you_want_more_children_error_message = _do_you_want_more_children_error_message_dict[self.language_code]
        self._height_must_be_from_1_to_450_cm_error_message = _height_must_be_from_1_to_450_cm_error_message_dict[self.language_code]
        self._your_diet_is_required_error_message = _your_diet_is_required_error_message_dict[self.language_code]
        self._your_smoking_status_is_required_error_message = _your_smoking_status_is_required_error_message_dict[self.language_code]
        self._your_relationship_status_is_required_error_message = _your_relationship_status_is_required_error_message_dict[self.language_code]
        self._gender_to_match_is_required_error_message = _gender_to_match_is_required_error_message_dict[self.language_code]
        self._minimal_age_to_match_must_be_from_0_to_180_years_error_message = _minimal_age_to_match_must_be_from_0_to_180_years_error_message_dict[self.language_code]
        self._maximal_age_to_match_must_be_from_0_to_180_years_error_message = _maximal_age_to_match_must_be_from_0_to_180_years_error_message_dict[self.language_code]
        self._maximal_age_to_match_cant_be_less_than_minimal_age_to_match_error_message = _maximal_age_to_match_cant_be_less_than_minimal_age_to_match_error_message_dict[self.language_code]
        self._please_select_diet_match_error_message = _please_select_diet_match_error_message_dict[self.language_code]
        self._please_select_smoking_status_match_error_message = _please_select_smoking_status_match_error_message_dict[self.language_code]
        self._please_select_relationship_status_match_error_message = _please_select_relationship_status_match_error_message_dict[self.language_code]
        self._at_least_one_diet_match_option_should_be_5_hearts_error_message = _at_least_one_diet_match_option_should_be_5_hearts_error_message_dict[self.language_code]
        self._at_least_one_smoking_status_match_option_should_be_5_hearts_error_message = _at_least_one_smoking_status_match_option_should_be_5_hearts_error_message_dict[self.language_code]
        self._at_least_one_relationship_status_match_option_should_be_5_hearts_error_message = _at_least_one_relationship_status_match_option_should_be_5_hearts_error_message_dict[self.language_code]


