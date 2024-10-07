from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import itertools
        from datetime import date

        from django.test import override_settings
        from django.core.exceptions import ValidationError

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match
        from speedy.core.accounts.test.mixins import SpeedyCoreAccountsLanguageMixin
        from speedy.match.accounts.test.mixins import SpeedyMatchAccountsModelsMixin, SpeedyMatchAccountsLanguageMixin
        from speedy.core.base.test.utils import get_django_settings_class_with_override_settings

        from speedy.core.uploads.test.factories import UserImageFactory
        from speedy.core.accounts.test.user_factories import DefaultUserFactory, InactiveUserFactory, SpeedyNetInactiveUserFactory, ActiveUserFactory

        from speedy.core.base.utils import to_attribute
        from speedy.match.accounts import utils, validators
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
        from speedy.core.accounts.models import ConcurrencyError, User


        class SpeedyMatchSiteProfileTestCaseMixin(SpeedyMatchAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, SpeedyMatchAccountsLanguageMixin):
            _none_list = [None]
            _empty_string_list = [""]
            _empty_values_to_test = _none_list + _empty_string_list
            _non_int_string_values_to_test = ["Tel Aviv.", "One boy.", "Yes.", "Hi!"]
            _int_big_values_to_test = [int("-5" + "0" * 500), int("-5" + "0" * 1000), int("-5" + "0" * 2000), int("-5" + "0" * 4000), int("5" + "0" * 500), int("5" + "0" * 1000), int("5" + "0" * 2000), int("5" + "0" * 4000)]
            _valid_string_values_to_test = ["1"] + _non_int_string_values_to_test
            _valid_string_values_to_test_max_length_120 = _valid_string_values_to_test + ["a" * 60, "a" * 120]
            _too_long_string_values_to_test_max_length_120 = ["a" * 121, "b" * 200, "a" * 5000, "a" * 50000, "a" * 50001, "a" * 100000, "b" * 1000000]
            _valid_string_values_to_test_max_length_50000 = _valid_string_values_to_test + ["a" * 60, "a" * 120, "a" * 121, "b" * 200, "a" * 5000, "a" * 50000]
            _too_long_string_values_to_test_max_length_50000 = ["a" * 50001, "a" * 100000, "b" * 1000000]

            def get_default_user_doron(self):
                user = DefaultUserFactory(first_name_en="Doron", last_name_en="Matalon", slug="doron-matalon", date_of_birth=date(year=1978, month=9, day=12), gender=User.GENDER_FEMALE)
                user.diet = User.DIET_VEGAN
                user.save_user_and_profile()
                return user

            def get_active_user_jennifer(self):
                user = ActiveUserFactory(first_name_en="Jennifer", last_name_en="Connelly", slug="jennifer-connelly", date_of_birth=date(year=1978, month=9, day=12), gender=User.GENDER_FEMALE)
                user.diet = User.DIET_VEGETARIAN
                user.save_user_and_profile()
                return user

            def get_min_max_age_to_match_default_test_settings(self):
                test_settings = {
                    "field_name": 'min_max_age_to_match',
                    "expected_step": 7,
                    "expected_error_message_min_age_to_match_and_max_age_to_match_valid": self._maximal_age_to_match_cant_be_less_than_minimal_age_to_match_error_message,
                    "expected_error_message_min_age_to_match_invalid": self._minimal_age_to_match_must_be_from_0_to_180_years_error_message,
                    "expected_error_message_max_age_to_match_invalid": self._maximal_age_to_match_must_be_from_0_to_180_years_error_message,
                }
                test_settings["expected_error_messages_min_age_to_match_and_max_age_to_match_valid"] = [({'en': '["{expected_error_message_min_age_to_match_and_max_age_to_match_valid}"]', 'fr': "['{expected_error_message_min_age_to_match_and_max_age_to_match_valid}']", 'de': "['{expected_error_message_min_age_to_match_and_max_age_to_match_valid}']", 'es': "['{expected_error_message_min_age_to_match_and_max_age_to_match_valid}']", 'pt': "['{expected_error_message_min_age_to_match_and_max_age_to_match_valid}']", 'it': "['{expected_error_message_min_age_to_match_and_max_age_to_match_valid}']", 'nl': "['{expected_error_message_min_age_to_match_and_max_age_to_match_valid}']", 'sv': "['{expected_error_message_min_age_to_match_and_max_age_to_match_valid}']", 'ko': "['{expected_error_message_min_age_to_match_and_max_age_to_match_valid}']", 'fi': "['{expected_error_message_min_age_to_match_and_max_age_to_match_valid}']", 'he': "['{expected_error_message_min_age_to_match_and_max_age_to_match_valid}']"}[self.language_code]).format(expected_error_message_min_age_to_match_and_max_age_to_match_valid=test_settings["expected_error_message_min_age_to_match_and_max_age_to_match_valid"]).replace("\xa0", "\\xa0")]
                test_settings["expected_error_messages_min_age_to_match_and_max_age_to_match_invalid"] = ["['{expected_error_message_min_age_to_match_invalid}']".format(expected_error_message_min_age_to_match_invalid=test_settings["expected_error_message_min_age_to_match_invalid"]).replace("\xa0", "\\xa0"), "['{expected_error_message_max_age_to_match_invalid}']".format(expected_error_message_max_age_to_match_invalid=test_settings["expected_error_message_max_age_to_match_invalid"]).replace("\xa0", "\\xa0")]
                return test_settings

            def get_diet_match_default_test_settings(self):
                test_settings = {
                    "field_name": 'diet_match',
                    "expected_step": 8,
                    "expected_error_message_keys_and_ranks_invalid": self._diet_match_is_required_error_message,
                    "expected_error_message_max_rank_invalid": self._at_least_one_diet_match_option_should_be_5_hearts_error_message,
                }
                test_settings["expected_error_messages_keys_and_ranks_invalid"] = ["['{expected_error_message_keys_and_ranks_invalid}']".format(expected_error_message_keys_and_ranks_invalid=test_settings["expected_error_message_keys_and_ranks_invalid"]).replace("\xa0", "\\xa0")]
                test_settings["expected_error_messages_max_rank_invalid"] = ["['{expected_error_message_max_rank_invalid}']".format(expected_error_message_max_rank_invalid=test_settings["expected_error_message_max_rank_invalid"]).replace("\xa0", "\\xa0")]
                return test_settings

            def get_smoking_status_match_default_test_settings(self):
                test_settings = {
                    "field_name": 'smoking_status_match',
                    "expected_step": 8,
                    "expected_error_message_keys_and_ranks_invalid": self._smoking_status_match_is_required_error_message,
                    "expected_error_message_max_rank_invalid": self._at_least_one_smoking_status_match_option_should_be_5_hearts_error_message,
                }
                test_settings["expected_error_messages_keys_and_ranks_invalid"] = ["['{expected_error_message_keys_and_ranks_invalid}']".format(expected_error_message_keys_and_ranks_invalid=test_settings["expected_error_message_keys_and_ranks_invalid"]).replace("\xa0", "\\xa0")]
                test_settings["expected_error_messages_max_rank_invalid"] = ["['{expected_error_message_max_rank_invalid}']".format(expected_error_message_max_rank_invalid=test_settings["expected_error_message_max_rank_invalid"]).replace("\xa0", "\\xa0")]
                return test_settings

            def get_relationship_status_match_default_test_settings(self):
                test_settings = {
                    "field_name": 'relationship_status_match',
                    "expected_step": 9,
                    "expected_error_message_keys_and_ranks_invalid": self._relationship_status_match_is_required_error_message,
                    "expected_error_message_max_rank_invalid": self._at_least_one_relationship_status_match_option_should_be_5_hearts_error_message,
                }
                test_settings["expected_error_messages_keys_and_ranks_invalid"] = ["['{expected_error_message_keys_and_ranks_invalid}']".format(expected_error_message_keys_and_ranks_invalid=test_settings["expected_error_message_keys_and_ranks_invalid"]).replace("\xa0", "\\xa0")]
                test_settings["expected_error_messages_max_rank_invalid"] = ["['{expected_error_message_max_rank_invalid}']".format(expected_error_message_max_rank_invalid=test_settings["expected_error_message_max_rank_invalid"]).replace("\xa0", "\\xa0")]
                return test_settings

            def get_field_default_value(self, field_name):
                if (field_name in ['diet_match']):
                    default_value = SpeedyMatchSiteProfile.diet_match_default()
                elif (field_name in ['smoking_status_match']):
                    default_value = SpeedyMatchSiteProfile.smoking_status_match_default()
                elif (field_name in ['relationship_status_match']):
                    default_value = SpeedyMatchSiteProfile.relationship_status_match_default()
                else:
                    raise Exception("Unexpected: field_name={}".format(field_name))
                return default_value

            def validate_all_user_values(self, user):
                all_fields = [field_name.format(language_code=self.language_code) for field_name in ['profile_picture', 'profile_description_{language_code}', 'city_{language_code}', 'children_{language_code}', 'more_children_{language_code}', 'match_description_{language_code}', 'height', 'diet', 'smoking_status', 'relationship_status', 'gender_to_match', 'min_age_to_match', 'max_age_to_match', 'min_max_age_to_match', 'diet_match', 'smoking_status_match', 'relationship_status_match']]
                _all_fields = []
                for step in utils.get_steps_range():
                    fields = utils.get_step_fields_to_validate(step=step)
                    _all_fields.extend(fields)
                self.assertListEqual(list1=sorted(all_fields), list2=sorted(_all_fields))
                self.assertSetEqual(set1=set(all_fields), set2=set(_all_fields))
                for field_name in all_fields:
                    utils.validate_field(field_name=field_name, user=user)

            def assert_list_2_contains_all_elements_in_list_1(self, list_1, list_2):
                for value in list_1:
                    self.assertIn(member=value, container=list_2)

            def assert_list_2_doesnt_contain_elements_in_list_1(self, list_1, list_2):
                for value in list_1:
                    self.assertNotIn(member=value, container=list_2)

            def assert_valid_values_ok(self, values_to_test, valid_values_to_assign, valid_values_to_save, valid_values, invalid_values):
                self.assertIsNotNone(obj=values_to_test)
                self.assertIsNotNone(obj=valid_values_to_assign)
                self.assertIsNotNone(obj=valid_values_to_save)
                self.assertIsNotNone(obj=valid_values)
                self.assertIsNotNone(obj=invalid_values)
                if (isinstance(values_to_test, range)):
                    values_to_test = list(values_to_test)
                if (isinstance(valid_values_to_assign, range)):
                    valid_values_to_assign = list(valid_values_to_assign)
                if (isinstance(valid_values_to_save, range)):
                    valid_values_to_save = list(valid_values_to_save)
                if (isinstance(valid_values, range)):
                    valid_values = list(valid_values)
                if (isinstance(invalid_values, range)):
                    invalid_values = list(invalid_values)
                self.assertGreater(a=len(values_to_test), b=0)
                self.assert_list_2_contains_all_elements_in_list_1(list_1=valid_values, list_2=values_to_test)
                self.assertLess(a=len(valid_values), b=len(values_to_test))
                self.assertGreater(a=len(valid_values), b=0)
                self.assert_list_2_contains_all_elements_in_list_1(list_1=valid_values, list_2=valid_values_to_save)
                self.assertLess(a=len(valid_values), b=len(valid_values_to_save))
                self.assert_list_2_contains_all_elements_in_list_1(list_1=valid_values_to_save, list_2=values_to_test)
                self.assertLessEqual(a=len(valid_values_to_save), b=len(values_to_test))
                self.assertGreater(a=len(valid_values_to_save), b=0)
                self.assert_list_2_contains_all_elements_in_list_1(list_1=valid_values, list_2=valid_values_to_assign)
                self.assertLess(a=len(valid_values), b=len(valid_values_to_assign))
                self.assert_list_2_contains_all_elements_in_list_1(list_1=valid_values_to_assign, list_2=values_to_test)
                self.assertLessEqual(a=len(valid_values_to_assign), b=len(values_to_test))
                self.assertGreater(a=len(valid_values_to_assign), b=0)
                self.assert_list_2_contains_all_elements_in_list_1(list_1=invalid_values, list_2=values_to_test)
                self.assertLess(a=len(invalid_values), b=len(values_to_test))
                self.assertGreater(a=len(invalid_values), b=0)
                self.assertListEqual(list1=invalid_values, list2=[value for value in values_to_test if (value not in valid_values)])
                self.assertListEqual(list1=valid_values, list2=[value for value in values_to_test if (value not in invalid_values)])
                self.assert_list_2_doesnt_contain_elements_in_list_1(list_1=invalid_values, list_2=valid_values)

            def save_user_and_profile_and_assert_exceptions_for_integer(self, user, field_name, value_to_test, null, choices_only):
                if ((null is True) and (value_to_test in self._empty_string_list)):
                    with self.assertRaises(ValueError) as cm:
                        user.save_user_and_profile()
                    self.assertEqual(first=str(cm.exception), second="Field '{field_name}' expected a number but got ''.".format(field_name=field_name))
                else:
                    with self.assertRaises(ValidationError) as cm:
                        user.save_user_and_profile()
                    if ((null is False) and (value_to_test in self._none_list)):
                        self.assertDictEqual(d1=dict(cm.exception), d2=self._this_field_cannot_be_null_errors_dict_by_field_name(field_name=field_name))
                    elif (isinstance(value_to_test, int)):
                        if ((choices_only is False) and (value_to_test < -32768)):
                            self.assertDictEqual(d1=dict(cm.exception), d2=self._ensure_this_value_is_greater_than_or_equal_to_minus_32768_errors_dict_by_field_name(field_name=field_name))
                        elif ((choices_only is False) and (value_to_test >= 32768)):
                            self.assertDictEqual(d1=dict(cm.exception), d2=self._ensure_this_value_is_less_than_or_equal_to_32767_errors_dict_by_field_name(field_name=field_name))
                        else:
                            self.assertDictEqual(d1=dict(cm.exception), d2=self._value_is_not_a_valid_choice_errors_dict_by_field_name_and_value(field_name=field_name, value=value_to_test))
                    else:
                        self.assertDictEqual(d1=dict(cm.exception), d2=self._value_must_be_an_integer_errors_dict_by_field_name_and_value(field_name=field_name, value=value_to_test))

            def save_user_and_profile_and_assert_exceptions_for_string(self, user, field_name, value_to_test, max_length):
                with self.assertRaises(ValidationError) as cm:
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._ensure_this_value_has_at_most_max_length_characters_errors_dict_by_field_name_and_max_length_and_value_length(field_name=field_name, max_length=max_length, value_length=len(value_to_test)))

            def save_user_and_profile_and_assert_exceptions_for_gender_to_match(self, user, field_name, value_to_test):
                if (value_to_test is None):
                    with self.assertRaises(TypeError) as cm:
                        user.save_user_and_profile()
                    self.assertEqual(first=str(cm.exception), second="'NoneType' object is not iterable")
                else:
                    with self.assertRaises(ValidationError) as cm:
                        user.save_user_and_profile()
                    index = None
                    value = None
                    val = sorted(list(set(value_to_test)))
                    for i in range(len(val)):
                        if (index is None):
                            if (not (validators.gender_is_valid(gender=val[i]))):
                                index = i + 1
                                value = val[i]
                    self.assertDictEqual(d1=dict(cm.exception), d2=self._item_in_the_array_did_not_validate_value_is_not_a_valid_choice_errors_dict_by_field_name_and_index_and_value(field_name=field_name, index=index, value=value))

            def save_user_and_profile_and_assert_exceptions_for_jsonfield(self, user, field_name, value_to_test, blank, null):
                with self.assertRaises(ValidationError) as cm:
                    user.save_user_and_profile()
                if ((null is False) and (value_to_test in self._none_list)):
                    self.assertDictEqual(d1=dict(cm.exception), d2=self._this_field_cannot_be_null_errors_dict_by_field_name(field_name=field_name))
                elif ((blank is False) and (value_to_test in self._empty_string_list + [list(), tuple(), dict()])):
                    self.assertDictEqual(d1=dict(cm.exception), d2=self._this_field_cannot_be_blank_errors_dict_by_field_name(field_name=field_name))
                else:
                    self.assertDictEqual(d1=dict(cm.exception), d2=self._value_must_be_valid_json_errors_dict_by_field_name(field_name=field_name))

            def save_user_and_profile_and_assert_exceptions_for_integer_list(self, user, field_name_list, value_to_test, null):
                self.assertIs(expr1=(isinstance(field_name_list, (list, tuple))), expr2=True)
                self.assertIs(expr1=(isinstance(value_to_test, (list, tuple))), expr2=True)
                self.assertEqual(first=len(field_name_list), second=len(value_to_test))
                with self.assertRaises(ValidationError) as cm:
                    user.save_user_and_profile()
                if ((null is False) and (all(value_to_test[i] in self._none_list for i in range(len(value_to_test))))):
                    self.assertDictEqual(d1=dict(cm.exception), d2=self._this_field_cannot_be_null_errors_dict_by_field_name_list(field_name_list=field_name_list))
                else:
                    self.assertDictEqual(d1=dict(cm.exception), d2=self._value_must_be_an_integer_errors_dict_by_field_name_list_and_value_list(field_name_list=field_name_list, value_list=value_to_test))

            def run_test_validate_profile_and_activate_exception(self, test_settings):
                user = ActiveUserFactory()
                self.assertIn(member="field_name", container=test_settings.keys())
                field_name = test_settings["field_name"]
                expected_test_settings_keys = {"field_name", "test_invalid_values_to_assign", "test_invalid_values_to_save", "expected_step", "expected_counts_tuple"}
                if (field_name in ['min_max_age_to_match']):
                    expected_test_settings_keys.update({"test_invalid_ages", "expected_error_message_min_age_to_match_and_max_age_to_match_valid", "expected_error_message_min_age_to_match_invalid", "expected_error_message_max_age_to_match_invalid", "expected_error_messages_min_age_to_match_and_max_age_to_match_valid", "expected_error_messages_min_age_to_match_and_max_age_to_match_invalid", "expected_min_max_age_to_match_error_messages_counts_tuple"})
                elif (field_name in ['diet_match', 'smoking_status_match', 'relationship_status_match']):
                    expected_test_settings_keys.update({"test_invalid_keys", "test_invalid_ranks", "expected_error_message_keys_and_ranks_invalid", "expected_error_messages_keys_and_ranks_invalid", "expected_error_message_max_rank_invalid", "expected_error_messages_max_rank_invalid", "expected_keys_and_ranks_error_messages_counts_tuple"})
                else:
                    expected_test_settings_keys.update({"expected_error_message", "expected_error_messages"})
                self.assertSetEqual(set1=set(test_settings.keys()), set2=expected_test_settings_keys)
                ok_count, validate_profile_and_activate_failures_count, model_assign_failures_count, model_save_failures_count = 0, 0, 0, 0
                error_message_min_age_to_match_and_max_age_to_match_valid_count, error_message_min_age_to_match_and_max_age_to_match_invalid_count = 0, 0
                error_message_keys_and_ranks_invalid_count, error_message_max_rank_invalid_count = 0, 0
                can_assign_value_set, can_save_user_and_profile_set, value_is_valid_set, value_is_invalid_set = set(), set(), set(), set()
                values_to_test, valid_values_to_assign, valid_values_to_save, valid_values, invalid_values, invalid_values_with_valid_ranks = None, None, None, None, None, None
                if (field_name in ['profile_picture']):
                    valid_values = [UserImageFactory]
                    values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, 10 + 1)) + valid_values
                    valid_values_to_assign = self._none_list + valid_values
                    valid_values_to_save = valid_values_to_assign
                elif (field_name in ['city']):
                    values_to_test = self._empty_values_to_test + self._valid_string_values_to_test_max_length_120 + self._too_long_string_values_to_test_max_length_120
                    valid_values_to_save = self._empty_values_to_test + self._valid_string_values_to_test_max_length_120
                    invalid_values = self._empty_values_to_test + self._too_long_string_values_to_test_max_length_120
                    valid_values = self._valid_string_values_to_test_max_length_120
                elif (field_name in ['profile_description', 'children', 'more_children', 'match_description']):
                    values_to_test = self._empty_values_to_test + self._valid_string_values_to_test_max_length_50000 + self._too_long_string_values_to_test_max_length_50000
                    valid_values_to_save = self._empty_values_to_test + self._valid_string_values_to_test_max_length_50000
                    invalid_values = self._empty_values_to_test + self._too_long_string_values_to_test_max_length_50000
                    valid_values = self._valid_string_values_to_test_max_length_50000
                elif (field_name in ['height']):
                    values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_ALLOWED + 10 + 1)) + self._int_big_values_to_test
                    valid_values_to_save = self._none_list + [value for value in values_to_test if ((isinstance(value, int)) and (-32768 <= value < 32768))]
                    valid_values = SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES
                elif (field_name in ['diet']):
                    values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, User.DIET_MAX_VALUE_PLUS_ONE + 10)) + self._int_big_values_to_test
                    valid_values_to_save = [choice[0] for choice in User.DIET_CHOICES_WITH_DEFAULT]
                    valid_values = User.DIET_VALID_VALUES
                    self.assertListEqual(list1=valid_values_to_save, list2=[User.DIET_UNKNOWN] + valid_values)
                    self.assertListEqual(list1=valid_values_to_save, list2=[0] + valid_values)
                elif (field_name in ['smoking_status']):
                    values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, User.SMOKING_STATUS_MAX_VALUE_PLUS_ONE + 10)) + self._int_big_values_to_test
                    valid_values_to_save = [choice[0] for choice in User.SMOKING_STATUS_CHOICES_WITH_DEFAULT]
                    valid_values = User.SMOKING_STATUS_VALID_VALUES
                    self.assertListEqual(list1=valid_values_to_save, list2=[User.SMOKING_STATUS_UNKNOWN] + valid_values)
                    self.assertListEqual(list1=valid_values_to_save, list2=[0] + valid_values)
                elif (field_name in ['relationship_status']):
                    values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, User.RELATIONSHIP_STATUS_MAX_VALUE_PLUS_ONE + 10)) + self._int_big_values_to_test
                    valid_values_to_save = [choice[0] for choice in User.RELATIONSHIP_STATUS_CHOICES_WITH_DEFAULT]
                    valid_values = User.RELATIONSHIP_STATUS_VALID_VALUES
                    self.assertListEqual(list1=valid_values_to_save, list2=[User.RELATIONSHIP_STATUS_UNKNOWN] + valid_values)
                    self.assertListEqual(list1=valid_values_to_save, list2=[0] + valid_values)
                elif (field_name in ['gender_to_match']):
                    range_to_test = [User.GENDER_UNKNOWN] + User.GENDER_VALID_VALUES + [User.GENDER_MAX_VALUE_PLUS_ONE]
                    self.assertListEqual(list1=range_to_test, list2=list(range(User.GENDER_UNKNOWN, User.GENDER_MAX_VALUE_PLUS_ONE + 1)))
                    self.assertListEqual(list1=range_to_test, list2=list(range(5)))
                    self.assertSetEqual(set1=set(range_to_test) - set(User.GENDER_VALID_VALUES), set2={User.GENDER_UNKNOWN, User.GENDER_MAX_VALUE_PLUS_ONE})
                    self.assertSetEqual(set1=set(range_to_test) - set(User.GENDER_VALID_VALUES), set2={0, 4})
                    self.assert_list_2_contains_all_elements_in_list_1(list_1=User.GENDER_VALID_VALUES, list_2=range_to_test)
                    values_to_test = self._empty_values_to_test + [list(), tuple(), User.GENDER_VALID_VALUES + User.GENDER_VALID_VALUES, tuple(User.GENDER_VALID_VALUES + User.GENDER_VALID_VALUES), User.GENDER_VALID_VALUES[0:2] + User.GENDER_VALID_VALUES[0:1], User.GENDER_VALID_VALUES[0:2] + User.GENDER_VALID_VALUES[0:2]]
                    for n in range(10 + 1):
                        if (n <= len(User.GENDER_VALID_VALUES)):
                            product = list(itertools.product(*itertools.repeat(range_to_test, n)))
                            values_to_test.extend([list(item) for item in product])
                            if (n <= 1):
                                values_to_test.extend(product)
                            else:
                                product = list(itertools.product(*itertools.repeat(User.GENDER_VALID_VALUES, n)))
                                if (n == 2):
                                    values_to_test.extend(product[:5])
                                elif (n == 3):
                                    values_to_test.extend(product[3:8])
                        else:
                            values_to_test.extend([([i] + [item for j in range(10) for item in User.GENDER_VALID_VALUES])[:n] for i in range_to_test])
                    valid_values_to_save = self._empty_string_list + [gender_to_match for gender_to_match in values_to_test if ((isinstance(gender_to_match, (list, tuple))) and (len(set(gender_to_match)) <= len(User.GENDER_VALID_VALUES)) and (all(validators.gender_is_valid(gender=gender) for gender in gender_to_match)))]
                    valid_values = [gender_to_match for gender_to_match in values_to_test if ((isinstance(gender_to_match, (list, tuple))) and (len(set(gender_to_match)) > 0) and (all(validators.gender_is_valid(gender=gender) for gender in gender_to_match)))]
                    for value in [[1], [2], [3], (1,), (2,), (3,), [1, 2], [1, 3], [2, 3], (1, 2), (1, 3), [1, 2, 3], (1, 2, 3), [1, 2, 3, 1, 2, 3], (1, 2, 3, 1, 2, 3), [1, 2, 1], [1, 2, 1, 2]]:
                        for val in [value, list(value)]:
                            self.assertIn(member=val, container=values_to_test)
                            self.assertIn(member=val, container=valid_values)
                            self.assertIn(member=val, container=valid_values_to_save)
                    for value in [[], ()]:
                        for val in [value, list(value)]:
                            self.assertIn(member=val, container=values_to_test)
                            self.assertNotIn(member=val, container=valid_values)
                            self.assertIn(member=val, container=valid_values_to_save)
                    for value in [[0], [4], (0,), (4,), [0, 1], [1, 2, 0], [1, 2, 4], [4, 1, 2, 3]]:
                        for val in [value, list(value)]:
                            self.assertIn(member=val, container=values_to_test)
                            self.assertNotIn(member=val, container=valid_values)
                            self.assertNotIn(member=val, container=valid_values_to_save)
                    for value in valid_values:
                        self.assertIn(member=value, container=values_to_test)
                    invalid_values = [value for value in values_to_test if (value not in valid_values)]
                    for value in invalid_values:
                        self.assertIn(member=value, container=values_to_test)
                        self.assertNotIn(member=value, container=valid_values)
                    for value in [[i, i] for i in User.GENDER_VALID_VALUES] + [[i, i, i] for i in User.GENDER_VALID_VALUES] + [[i, i, 1] for i in User.GENDER_VALID_VALUES]:
                        self.assertIn(member=value, container=values_to_test)
                        self.assertIn(member=value, container=valid_values)
                    valid_sets_dict = {str(i): list() for i in range(1, 4)}
                    for value in [set(gender_to_match) for gender_to_match in valid_values]:
                        key = str(len(value))
                        if (value not in valid_sets_dict[key]):
                            valid_sets_dict[key].append(value)
                    valid_sets = sum([valid_sets_dict[str(i)] for i in range(1, 4)], [])
                    self.assertListEqual(list1=valid_sets, list2=[{1}, {2}, {3}, {1, 2}, {1, 3}, {2, 3}, {1, 2, 3}])
                elif (field_name in ['min_age_to_match', 'max_age_to_match']):
                    values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, SpeedyMatchSiteProfile.settings.MAX_AGE_TO_MATCH_ALLOWED + 10 + 1)) + self._int_big_values_to_test
                    valid_values_to_save = [value for value in values_to_test if ((isinstance(value, int)) and (-32768 <= value < 32768))]
                    valid_values = SpeedyMatchSiteProfile.AGE_TO_MATCH_VALID_VALUES
                elif (field_name in ['min_max_age_to_match']):
                    values_to_test_valid_ages = [(value, SpeedyMatchSiteProfile.settings.MAX_AGE_TO_MATCH_ALLOWED - value) for value in SpeedyMatchSiteProfile.AGE_TO_MATCH_VALID_VALUES]
                    self.assertIs(expr1=all((len(value) == 2) for value in values_to_test_valid_ages), expr2=True)
                    values_to_test = []
                    if (test_settings["test_invalid_values_to_save"]):
                        values_to_test.extend([(value, value) for value in self._empty_values_to_test + self._non_int_string_values_to_test])
                    if (test_settings["test_invalid_ages"]):
                        values_to_test.extend([(value, SpeedyMatchSiteProfile.settings.MAX_AGE_TO_MATCH_ALLOWED - value) for value in range(-10, SpeedyMatchSiteProfile.settings.MAX_AGE_TO_MATCH_ALLOWED + 10 + 1)])
                        self.assert_list_2_contains_all_elements_in_list_1(list_1=values_to_test_valid_ages, list_2=values_to_test)
                    else:
                        values_to_test.extend(values_to_test_valid_ages)
                    self.assertIs(expr1=all((len(value) == 2) for value in values_to_test), expr2=True)
                    if (test_settings["test_invalid_values_to_save"]):
                        valid_values_to_save = [value for value in values_to_test if (all(isinstance(value[i], int) for i in range(len(value))))]
                        valid_values = [value for value in values_to_test_valid_ages if (value[0] <= value[1])]
                    else:
                        valid_values_to_save = values_to_test
                        valid_values = [value for value in values_to_test if (value[0] <= value[1])]
                    invalid_values = [value for value in values_to_test if (value not in valid_values)]
                    self.assertListEqual(list1=valid_values, list2=[(value, 180 - value) for value in range(0, 90 + 1)])
                    self.assertEqual(first=valid_values[0], second=(0, 180))
                    self.assertEqual(first=valid_values[-1], second=(90, 90))
                    if (test_settings["test_invalid_ages"]):
                        invalid_values_valid_ages = [value for value in values_to_test_valid_ages if (value not in valid_values)]
                        self.assert_list_2_contains_all_elements_in_list_1(list_1=invalid_values_valid_ages, list_2=invalid_values)
                        self.assertListEqual(list1=invalid_values_valid_ages, list2=[(value, 180 - value) for value in range(91, 180 + 1)])
                        self.assertEqual(first=invalid_values_valid_ages[0], second=(91, 89))
                        self.assertEqual(first=invalid_values_valid_ages[-1], second=(180, 0))
                        self.assertListEqual(list1=invalid_values, list2=[(value, value) for value in self._empty_values_to_test + self._non_int_string_values_to_test] + [(value, 180 - value) for value in (list(range(-10, 0)) + list(range(91, 180 + 10 + 1)))])
                        self.assertEqual(first=invalid_values[0], second=(None, None))
                        self.assertEqual(first=invalid_values[-1], second=(190, -10))
                        self.assertListEqual(list1=invalid_values[16:-10], list2=invalid_values_valid_ages)
                        self.assertListEqual(list1=invalid_values[16:106], list2=invalid_values_valid_ages)
                    else:
                        self.assertListEqual(list1=invalid_values, list2=[(value, 180 - value) for value in range(91, 180 + 1)])
                        self.assertEqual(first=invalid_values[0], second=(91, 89))
                        self.assertEqual(first=invalid_values[-1], second=(180, 0))
                elif (field_name in ['diet_match', 'smoking_status_match', 'relationship_status_match']):
                    if (field_name in ['diet_match']):
                        all_keys = User.DIET_VALID_VALUES
                    elif (field_name in ['smoking_status_match']):
                        all_keys = User.SMOKING_STATUS_VALID_VALUES
                    elif (field_name in ['relationship_status_match']):
                        all_keys = User.RELATIONSHIP_STATUS_VALID_VALUES
                    else:
                        raise Exception("Unexpected: field_name={}".format(field_name))
                    all_keys_with_invalid_keys = ["___"] + [all_keys[0] - 1] + all_keys + [all_keys[-1] + 1]
                    if (test_settings["test_invalid_ranks"]):
                        range_to_test = [SpeedyMatchSiteProfile.RANK_VALID_VALUES[0] - 1] + SpeedyMatchSiteProfile.RANK_VALID_VALUES + [SpeedyMatchSiteProfile.RANK_VALID_VALUES[-1] + 1]
                        expected_range_to_test_list = list(range(-1, 6 + 1))
                        expected_invalid_keys_set = {-1, 6}
                    else:
                        range_to_test = SpeedyMatchSiteProfile.RANK_VALID_VALUES
                        expected_range_to_test_list = list(range(0, 5 + 1))
                        expected_invalid_keys_set = set()
                    self.assertListEqual(list1=range_to_test, list2=expected_range_to_test_list)
                    self.assertSetEqual(set1=set(range_to_test) - set(SpeedyMatchSiteProfile.RANK_VALID_VALUES), set2=expected_invalid_keys_set)
                    self.assert_list_2_contains_all_elements_in_list_1(list_1=SpeedyMatchSiteProfile.RANK_VALID_VALUES, list_2=range_to_test)
                    values_to_test, valid_values_to_save, valid_values, invalid_values_with_valid_ranks = [], [], [], []
                    if (test_settings["test_invalid_values_to_save"]):
                        values_to_test.extend(self._empty_values_to_test + [list(), tuple(), dict(), set()])
                    if (test_settings["test_invalid_keys"]):
                        for key in all_keys_with_invalid_keys:
                            value_to_test = self.get_field_default_value(field_name=field_name)
                            if (key in all_keys):
                                del value_to_test[str(key)]
                            else:
                                value_to_test[str(key)] = SpeedyMatchSiteProfile.RANK_5
                            valid_values_to_save.append(value_to_test)
                    for item in itertools.product(*itertools.repeat(range_to_test, 2)):
                        self.assertEqual(first=len(item), second=2)
                        # If both values are equal, it's enough to add value_to_test once.
                        if (item[0] == item[1]):
                            key_range = all_keys[0:1]
                        else:
                            key_range = all_keys
                        for key in key_range:
                            value_to_test = self.get_field_default_value(field_name=field_name)
                            for value_to_test_key in all_keys:
                                if (value_to_test_key == key):
                                    i = 0
                                else:
                                    i = 1
                                value_to_test[str(value_to_test_key)] = item[i]
                            valid_values_to_save.append(value_to_test)
                            all_ranks_are_valid = all(value in SpeedyMatchSiteProfile.RANK_VALID_VALUES for value in item)
                            max_rank_is_valid = (max(item) == 5)
                            self.assertEqual(first=all_ranks_are_valid, second=all(validators.rank_is_valid(rank=value) for value in item))
                            self.assertEqual(first=max_rank_is_valid, second=(max(item) == SpeedyMatchSiteProfile.RANK_5))
                            if (all_ranks_are_valid):
                                if (max_rank_is_valid):
                                    valid_values.append(value_to_test)
                                else:
                                    invalid_values_with_valid_ranks.append(value_to_test)
                    values_to_test.extend(valid_values_to_save)
                else:
                    raise Exception("Unexpected: field_name={}".format(field_name))
                if (valid_values_to_assign is None):
                    valid_values_to_assign = values_to_test
                if (invalid_values is None):
                    invalid_values = [value for value in values_to_test if (value not in valid_values)]
                self.assert_valid_values_ok(values_to_test=values_to_test, valid_values_to_assign=valid_values_to_assign, valid_values_to_save=valid_values_to_save, valid_values=valid_values, invalid_values=invalid_values)
                if (field_name in ['profile_picture']):
                    self.assertIs(expr1=test_settings["test_invalid_values_to_assign"], expr2=True)
                else:
                    self.assertIs(expr1=test_settings["test_invalid_values_to_assign"], expr2=False)
                if (test_settings["test_invalid_values_to_assign"]):
                    self.assertLess(a=len(valid_values_to_assign), b=len(values_to_test))
                else:
                    self.assertEqual(first=len(valid_values_to_assign), second=len(values_to_test))
                    self.assertListEqual(list1=valid_values_to_assign, list2=values_to_test)
                if (test_settings["test_invalid_values_to_save"]):
                    self.assertLess(a=len(valid_values_to_save), b=len(valid_values_to_assign))
                else:
                    self.assertEqual(first=len(valid_values_to_save), second=len(valid_values_to_assign))
                    self.assertListEqual(list1=valid_values_to_save, list2=valid_values_to_assign)
                if (field_name in ['diet_match', 'smoking_status_match', 'relationship_status_match']):
                    self.assertGreater(a=len(invalid_values_with_valid_ranks), b=0)
                    self.assert_list_2_contains_all_elements_in_list_1(list_1=invalid_values_with_valid_ranks, list_2=invalid_values)
                else:
                    self.assertIsNone(obj=invalid_values_with_valid_ranks)
                for value_to_test in values_to_test:
                    can_assign_value = (value_to_test in valid_values_to_assign)
                    can_save_user_and_profile = (value_to_test in valid_values_to_save)
                    value_is_valid = (value_to_test in valid_values)
                    value_is_invalid = (value_to_test in invalid_values)
                    self.assertEqual(first=value_is_valid, second=(not (value_is_invalid)))
                    can_assign_value_set.add(can_assign_value)
                    if (field_name in ['profile_picture']):
                        user.photo = None
                        if (value_to_test == UserImageFactory):
                            value_to_assign = UserImageFactory(owner=user)
                        else:
                            value_to_assign = value_to_test
                    else:
                        value_to_assign = value_to_test
                    if (not (can_assign_value)):
                        if (field_name in ['profile_picture']):
                            with self.assertRaises(ValueError) as cm:
                                user.photo = value_to_assign
                            self.assertEqual(first=str(cm.exception), second='Cannot assign "{0}{1}{0}": "User.photo" must be a "Image" instance.'.format("'" if (isinstance(value_to_assign, str)) else '', value_to_assign))
                            user.save_user_and_profile()
                            self.assertEqual(first=user.photo, second=None)
                            self.assertNotEqual(first=user.photo, second=value_to_assign)
                        else:
                            raise Exception("Unexpected: can_assign_value={}, value_to_test={}".format(can_assign_value, value_to_test))
                        model_assign_failures_count += 1
                    else:
                        if (field_name in ['profile_picture']):
                            user.photo = value_to_assign
                        elif (field_name in ['profile_description']):
                            user.speedy_match_profile.profile_description = value_to_assign
                        elif (field_name in ['city']):
                            user.city = value_to_assign
                        elif (field_name in ['children']):
                            user.speedy_match_profile.children = value_to_assign
                        elif (field_name in ['more_children']):
                            user.speedy_match_profile.more_children = value_to_assign
                        elif (field_name in ['match_description']):
                            user.speedy_match_profile.match_description = value_to_assign
                        elif (field_name in ['height']):
                            user.speedy_match_profile.height = value_to_assign
                        elif (field_name in ['diet']):
                            user.diet = value_to_assign
                        elif (field_name in ['smoking_status']):
                            user.smoking_status = value_to_assign
                        elif (field_name in ['relationship_status']):
                            user.relationship_status = value_to_assign
                        elif (field_name in ['gender_to_match']):
                            user.speedy_match_profile.gender_to_match = value_to_assign
                        elif (field_name in ['min_age_to_match']):
                            user.speedy_match_profile.min_age_to_match = value_to_assign
                        elif (field_name in ['max_age_to_match']):
                            user.speedy_match_profile.max_age_to_match = value_to_assign
                        elif (field_name in ['min_max_age_to_match']):
                            user.speedy_match_profile.min_age_to_match = value_to_assign[0]
                            user.speedy_match_profile.max_age_to_match = value_to_assign[1]
                        elif (field_name in ['diet_match']):
                            user.speedy_match_profile.diet_match = value_to_assign
                        elif (field_name in ['smoking_status_match']):
                            user.speedy_match_profile.smoking_status_match = value_to_assign
                        elif (field_name in ['relationship_status_match']):
                            user.speedy_match_profile.relationship_status_match = value_to_assign
                        can_save_user_and_profile_set.add(can_save_user_and_profile)
                        if (not (can_save_user_and_profile)):
                            if (field_name in ['height']):
                                self.save_user_and_profile_and_assert_exceptions_for_integer(user=user, field_name=field_name, value_to_test=value_to_test, null=True, choices_only=False)
                            elif (field_name in ['city']):
                                self.save_user_and_profile_and_assert_exceptions_for_string(user=user, field_name=to_attribute(name=field_name), value_to_test=value_to_test, max_length=120)
                            elif (field_name in ['profile_description', 'children', 'more_children', 'match_description']):
                                self.save_user_and_profile_and_assert_exceptions_for_string(user=user, field_name=to_attribute(name=field_name), value_to_test=value_to_test, max_length=50000)
                            elif (field_name in ['diet', 'smoking_status', 'relationship_status']):
                                self.save_user_and_profile_and_assert_exceptions_for_integer(user=user, field_name=field_name, value_to_test=value_to_test, null=False, choices_only=True)
                            elif (field_name in ['min_age_to_match', 'max_age_to_match']):
                                self.save_user_and_profile_and_assert_exceptions_for_integer(user=user, field_name=field_name, value_to_test=value_to_test, null=False, choices_only=False)
                            elif (field_name in ['min_max_age_to_match']):
                                self.save_user_and_profile_and_assert_exceptions_for_integer_list(user=user, field_name_list=['min_age_to_match', 'max_age_to_match'], value_to_test=value_to_test, null=False)
                            elif (field_name in ['gender_to_match']):
                                self.save_user_and_profile_and_assert_exceptions_for_gender_to_match(user=user, field_name=field_name, value_to_test=value_to_test)
                            elif (field_name in ['diet_match', 'smoking_status_match', 'relationship_status_match']):
                                self.save_user_and_profile_and_assert_exceptions_for_jsonfield(user=user, field_name=field_name, value_to_test=value_to_test, blank=False, null=False)
                            else:
                                raise Exception("Unexpected: can_save_user_and_profile={}, value_to_test={}".format(can_save_user_and_profile, value_to_test))
                            model_save_failures_count += 1
                        else:
                            value_is_valid_set.add(value_is_valid)
                            value_is_invalid_set.add(value_is_invalid)
                            user.save_user_and_profile()
                            step, error_messages = user.speedy_match_profile.validate_profile_and_activate()
                            if (not (value_is_valid)):
                                self.assertEqual(first=step, second=test_settings["expected_step"])
                                if (field_name in ['min_max_age_to_match']):
                                    self.assertIs(expr1=(isinstance(value_to_test, (list, tuple))), expr2=True)
                                    if (all(value_to_test[i] in SpeedyMatchSiteProfile.AGE_TO_MATCH_VALID_VALUES for i in range(2))):
                                        expected_error_messages_len = 1
                                        expected_error_messages_key = "expected_error_messages_min_age_to_match_and_max_age_to_match_valid"
                                        fields_and_error_messages = [(field_name, "expected_error_message_min_age_to_match_and_max_age_to_match_valid")]
                                        error_message_min_age_to_match_and_max_age_to_match_valid_count += 1
                                    else:
                                        self.assertIs(expr1=test_settings["test_invalid_ages"], expr2=True)
                                        expected_error_messages_len = 2
                                        expected_error_messages_key = "expected_error_messages_min_age_to_match_and_max_age_to_match_invalid"
                                        fields_and_error_messages = []
                                        for _field_name in ['min_age_to_match', 'max_age_to_match', 'min_max_age_to_match']:
                                            if (_field_name in ['min_max_age_to_match']):
                                                fields_and_error_messages.append((_field_name, None))
                                            else:
                                                fields_and_error_messages.append((_field_name, "expected_error_message_{}_invalid".format(_field_name)))
                                        error_message_min_age_to_match_and_max_age_to_match_invalid_count += 1
                                elif (field_name in ['diet_match', 'smoking_status_match', 'relationship_status_match']):
                                    if (not (value_to_test in invalid_values_with_valid_ranks)):
                                        expected_error_messages_len = 1
                                        expected_error_messages_key = "expected_error_messages_keys_and_ranks_invalid"
                                        fields_and_error_messages = [(field_name, "expected_error_message_keys_and_ranks_invalid")]
                                        error_message_keys_and_ranks_invalid_count += 1
                                    else:
                                        expected_error_messages_len = 1
                                        expected_error_messages_key = "expected_error_messages_max_rank_invalid"
                                        fields_and_error_messages = [(field_name, "expected_error_message_max_rank_invalid")]
                                        error_message_max_rank_invalid_count += 1
                                else:
                                    expected_error_messages_len = 1
                                    expected_error_messages_key = "expected_error_messages"
                                    fields_and_error_messages = [(field_name, "expected_error_message")]
                                self.assertEqual(first=len(error_messages), second=expected_error_messages_len)
                                self.assertListEqual(list1=error_messages, list2=test_settings[expected_error_messages_key])
                                for (_field_name, expected_error_message_key) in fields_and_error_messages:
                                    if (expected_error_message_key is None):
                                        utils.validate_field(field_name=_field_name, user=user)
                                    else:
                                        with self.assertRaises(ValidationError) as cm:
                                            utils.validate_field(field_name=_field_name, user=user)
                                        self.assertEqual(first=str(cm.exception.message), second=test_settings[expected_error_message_key])
                                        self.assertListEqual(list1=list(cm.exception), list2=[test_settings[expected_error_message_key]])
                                validate_profile_and_activate_failures_count += 1
                            else:
                                self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                                utils.validate_field(field_name=field_name, user=user)
                                ok_count += 1
                if (test_settings["test_invalid_values_to_assign"]):
                    self.assertSetEqual(set1=can_assign_value_set, set2={False, True})
                else:
                    self.assertSetEqual(set1=can_assign_value_set, set2={True})
                if (test_settings["test_invalid_values_to_save"]):
                    self.assertSetEqual(set1=can_save_user_and_profile_set, set2={False, True})
                else:
                    self.assertSetEqual(set1=can_save_user_and_profile_set, set2={True})
                self.assertSetEqual(set1=value_is_valid_set, set2={False, True})
                self.assertSetEqual(set1=value_is_invalid_set, set2={False, True})
                self.assertGreater(a=ok_count, b=0)
                self.assertGreater(a=validate_profile_and_activate_failures_count, b=0)
                if (test_settings["test_invalid_values_to_assign"]):
                    self.assertGreater(a=model_assign_failures_count, b=0)
                else:
                    self.assertEqual(first=model_assign_failures_count, second=0)
                if (test_settings["test_invalid_values_to_save"]):
                    self.assertGreater(a=model_save_failures_count, b=0)
                else:
                    self.assertEqual(first=model_save_failures_count, second=0)
                counts_tuple = (ok_count, validate_profile_and_activate_failures_count, model_assign_failures_count, model_save_failures_count)
                min_max_age_to_match_error_messages_counts_tuple = (error_message_min_age_to_match_and_max_age_to_match_valid_count, error_message_min_age_to_match_and_max_age_to_match_invalid_count)
                keys_and_ranks_error_messages_counts_tuple = (error_message_keys_and_ranks_invalid_count, error_message_max_rank_invalid_count)
                self.assertEqual(first=sum(counts_tuple), second=len(values_to_test))
                self.assertTupleEqual(tuple1=counts_tuple, tuple2=(len(valid_values), len(valid_values_to_save) - len(valid_values), len(values_to_test) - len(valid_values_to_assign), len(valid_values_to_assign) - len(valid_values_to_save)))
                self.assertTupleEqual(tuple1=counts_tuple, tuple2=test_settings["expected_counts_tuple"])
                if (field_name in ['min_max_age_to_match']):
                    self.assertEqual(first=sum(min_max_age_to_match_error_messages_counts_tuple), second=validate_profile_and_activate_failures_count)
                    self.assertTupleEqual(tuple1=min_max_age_to_match_error_messages_counts_tuple, tuple2=test_settings["expected_min_max_age_to_match_error_messages_counts_tuple"])
                else:
                    self.assertEqual(first=sum(min_max_age_to_match_error_messages_counts_tuple), second=0)
                    self.assertTupleEqual(tuple1=min_max_age_to_match_error_messages_counts_tuple, tuple2=(0, 0))
                if (field_name in ['diet_match', 'smoking_status_match', 'relationship_status_match']):
                    self.assertEqual(first=sum(keys_and_ranks_error_messages_counts_tuple), second=validate_profile_and_activate_failures_count)
                    self.assertTupleEqual(tuple1=keys_and_ranks_error_messages_counts_tuple, tuple2=test_settings["expected_keys_and_ranks_error_messages_counts_tuple"])
                else:
                    self.assertEqual(first=sum(keys_and_ranks_error_messages_counts_tuple), second=0)
                    self.assertTupleEqual(tuple1=keys_and_ranks_error_messages_counts_tuple, tuple2=(0, 0))

            def test_profile_property_and_class(self):
                from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile

                user = self.get_default_user_doron()
                self.assertEqual(first=user.profile, second=user.speedy_match_profile)
                self.assertEqual(first=user.profile.pk, second=user.speedy_match_profile.pk)
                self.assertEqual(first=user.profile.__class__, second=user.speedy_match_profile.__class__)
                self.assertEqual(first=user.profile.__class__, second=SpeedyMatchSiteProfile)
                self.assertEqual(first=user.profile.__class__.__name__, second="SiteProfile")
                self.assertEqual(first=user.speedy_match_profile.__class__, second=SpeedyMatchSiteProfile)
                self.assertEqual(first=user.speedy_match_profile.__class__.__name__, second="SiteProfile")
                self.assertEqual(first=user.speedy_net_profile.__class__, second=SpeedyNetSiteProfile)
                self.assertNotEqual(first=user.speedy_net_profile, second=user.profile)
                self.assertNotEqual(first=user.speedy_net_profile.__class__, second=user.profile.__class__)
                self.assertNotEqual(first=user.speedy_net_profile.__class__, second=SpeedyMatchSiteProfile)

            def test_localizable_fields(self):
                self.assertTupleEqual(tuple1=SpeedyMatchSiteProfile.LOCALIZABLE_FIELDS, tuple2=('profile_description', 'children', 'more_children', 'match_description'))

            def test_height_valid_values(self):
                self.assertEqual(first=SpeedyMatchSiteProfile.settings.MIN_HEIGHT_ALLOWED, second=1)
                self.assertEqual(first=SpeedyMatchSiteProfile.settings.MAX_HEIGHT_ALLOWED, second=450)
                self.assertEqual(first=SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES, second=range(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_ALLOWED, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_ALLOWED + 1))
                self.assertEqual(first=SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES, second=range(1, 450 + 1))

            def test_age_valid_values(self):
                self.assertEqual(first=SpeedyMatchSiteProfile.settings.MIN_AGE_TO_MATCH_ALLOWED, second=0)
                self.assertEqual(first=SpeedyMatchSiteProfile.settings.MAX_AGE_TO_MATCH_ALLOWED, second=180)
                self.assertEqual(first=SpeedyMatchSiteProfile.AGE_TO_MATCH_VALID_VALUES, second=range(SpeedyMatchSiteProfile.settings.MIN_AGE_TO_MATCH_ALLOWED, SpeedyMatchSiteProfile.settings.MAX_AGE_TO_MATCH_ALLOWED + 1))
                self.assertEqual(first=SpeedyMatchSiteProfile.AGE_TO_MATCH_VALID_VALUES, second=range(0, 180 + 1))

            @override_settings(SPEEDY_MATCH_SITE_PROFILE_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.SPEEDY_MATCH_SITE_PROFILE_SETTINGS, MIN_AGE_TO_MATCH_ALLOWED=tests_settings.OVERRIDE_SPEEDY_MATCH_SITE_PROFILE_SETTINGS.MIN_AGE_TO_MATCH_ALLOWED, MAX_AGE_TO_MATCH_ALLOWED=tests_settings.OVERRIDE_SPEEDY_MATCH_SITE_PROFILE_SETTINGS.MAX_AGE_TO_MATCH_ALLOWED))
            def test_age_valid_values_with_override_settings(self):
                self.assertEqual(first=SpeedyMatchSiteProfile.settings.MIN_AGE_TO_MATCH_ALLOWED, second=2)
                self.assertEqual(first=SpeedyMatchSiteProfile.settings.MAX_AGE_TO_MATCH_ALLOWED, second=178)
                self.assertEqual(first=SpeedyMatchSiteProfile.AGE_TO_MATCH_VALID_VALUES, second=range(SpeedyMatchSiteProfile.settings.MIN_AGE_TO_MATCH_ALLOWED, SpeedyMatchSiteProfile.settings.MAX_AGE_TO_MATCH_ALLOWED + 1))
                self.assertEqual(first=SpeedyMatchSiteProfile.AGE_TO_MATCH_VALID_VALUES, second=range(2, 178 + 1))

            def test_rank_valid_values(self):
                self.assertListEqual(list1=SpeedyMatchSiteProfile.RANK_VALID_VALUES, list2=list(range(SpeedyMatchSiteProfile.RANK_0, SpeedyMatchSiteProfile.RANK_5 + 1)))
                self.assertListEqual(list1=SpeedyMatchSiteProfile.RANK_VALID_VALUES, list2=list(range(0, 5 + 1)))

            def test_diet_match_default(self):
                diet_match = SpeedyMatchSiteProfile.diet_match_default()
                self.assertSetEqual(set1=set(diet_match.keys()), set2={str(diet) for diet in User.DIET_VALID_VALUES})
                self.assertSetEqual(set1={diet_match[key] for key in diet_match}, set2={SpeedyMatchSiteProfile.RANK_5})
                self.assertSetEqual(set1={diet_match[str(diet)] for diet in User.DIET_VALID_VALUES}, set2={SpeedyMatchSiteProfile.RANK_5})
                self.assertListEqual(list1=[diet_match[str(diet)] for diet in User.DIET_VALID_VALUES], list2=[5 for diet in User.DIET_VALID_VALUES])

            def test_smoking_status_match_default(self):
                smoking_status_match = SpeedyMatchSiteProfile.smoking_status_match_default()
                self.assertSetEqual(set1=set(smoking_status_match.keys()), set2={str(smoking_status) for smoking_status in User.SMOKING_STATUS_VALID_VALUES})
                self.assertSetEqual(set1={smoking_status_match[key] for key in smoking_status_match}, set2={SpeedyMatchSiteProfile.RANK_5})
                self.assertSetEqual(set1={smoking_status_match[str(smoking_status)] for smoking_status in User.SMOKING_STATUS_VALID_VALUES}, set2={SpeedyMatchSiteProfile.RANK_5})
                self.assertListEqual(list1=[smoking_status_match[str(smoking_status)] for smoking_status in User.SMOKING_STATUS_VALID_VALUES], list2=[5 for smoking_status in User.SMOKING_STATUS_VALID_VALUES])

            def test_relationship_status_match_default(self):
                relationship_status_match = SpeedyMatchSiteProfile.relationship_status_match_default()
                self.assertSetEqual(set1=set(relationship_status_match.keys()), set2={str(relationship_status) for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES})
                self.assertSetEqual(set1={relationship_status_match[key] for key in relationship_status_match}, set2={SpeedyMatchSiteProfile.RANK_5})
                self.assertSetEqual(set1={relationship_status_match[str(relationship_status)] for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES}, set2={SpeedyMatchSiteProfile.RANK_5})
                self.assertListEqual(list1=[relationship_status_match[str(relationship_status)] for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES], list2=[5 for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES])

            def test_get_steps_range(self):
                self.assertEqual(first=len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS), second=10)
                self.assertEqual(first=utils.get_steps_range(), second=range(1, len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)))
                self.assertEqual(first=utils.get_steps_range(), second=range(1, 10))

            def test_active_languages(self):
                p = SpeedyMatchSiteProfile(active_languages=['en', 'he', 'de'])
                self.assertListEqual(list1=p.active_languages, list2=['en', 'he', 'de'])
                self.assertEqual(first=len(p.active_languages), second=3)
                p = SpeedyMatchSiteProfile(active_languages=[])
                self.assertListEqual(list1=p.active_languages, list2=[])
                self.assertEqual(first=len(p.active_languages), second=0)

            def test_set_active_languages_1(self):
                p = SpeedyMatchSiteProfile()
                self.assertListEqual(list1=p.active_languages, list2=[])
                p._set_active_languages(languages=['en', 'he'])
                self.assertSetEqual(set1=set(p.active_languages), set2={'en', 'he'})
                self.assertEqual(first=len(p.active_languages), second=2)

            def test_set_active_languages_2(self):
                user = self.get_active_user_jennifer()
                user.speedy_match_profile._set_active_languages(languages=['en', 'fr', 'he'])
                user.save_user_and_profile()
                self.assertSetEqual(set1=set(user.speedy_match_profile.active_languages), set2={'en', 'fr', 'he'})
                self.assertEqual(first=len(user.speedy_match_profile.active_languages), second=3)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                if (self.language_code in {'en', 'fr', 'he'}):
                    self.assertEqual(first=user.speedy_match_profile.is_active, second=True)
                    self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=True)
                else:
                    self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                    self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=False)
                    active_languages = {'en', 'fr', 'he'} | {self.language_code}
                    user.speedy_match_profile._set_active_languages(languages=active_languages)
                    user.save_user_and_profile()
                    self.assertSetEqual(set1=set(user.speedy_match_profile.active_languages), set2=active_languages)
                    self.assertEqual(first=len(user.speedy_match_profile.active_languages), second=4)
                    self.assertEqual(first=user.is_active, second=True)
                    self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                    self.assertEqual(first=user.speedy_match_profile.is_active, second=True)
                    self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=True)
                    user.speedy_match_profile._set_active_languages(languages=['en', 'fr', 'he'])
                    user.save_user_and_profile()
                    self.assertSetEqual(set1=set(user.speedy_match_profile.active_languages), set2={'en', 'fr', 'he'})
                    self.assertEqual(first=len(user.speedy_match_profile.active_languages), second=3)
                    self.assertEqual(first=user.is_active, second=True)
                    self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                    self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                    self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=False)

            def test_set_active_languages_3(self):
                # Check that @cached_property user.speedy_match_profile.is_active and user.speedy_match_profile.is_active_and_valid are changed after calling user.speedy_match_profile._set_active_languages().
                user = self.get_active_user_jennifer()
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=True)
                user.speedy_match_profile._set_active_languages(languages=[])
                user.save_user_and_profile()
                self.assertSetEqual(set1=set(user.speedy_match_profile.active_languages), set2=set())
                self.assertEqual(first=len(user.speedy_match_profile.active_languages), second=0)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=False)

            def test_set_active_languages_with_duplicates(self):
                p = SpeedyMatchSiteProfile()
                self.assertListEqual(list1=p.active_languages, list2=[])
                p._set_active_languages(languages=['en', 'he', 'en', 'he'])
                self.assertSetEqual(set1=set(p.active_languages), set2={'en', 'he'})
                self.assertEqual(first=len(p.active_languages), second=2)

            def test_set_active_languages_with_typo(self):
                p = SpeedyMatchSiteProfile()
                p._set_active_languages(languages=['en', 'he', 'en', 'he1'])
                self.assertNotEqual(first=set(p.active_languages), second={'en', 'he'})
                self.assertNotEqual(first=len(p.active_languages), second=2)

            def test_set_active_languages_with_an_unsupported_language_1(self):
                user = self.get_active_user_jennifer()
                user.speedy_match_profile._set_active_languages(languages=['en', 'he', 'ab'])
                with self.assertRaises(ValidationError) as cm:
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._item_in_the_array_did_not_validate_value_is_not_a_valid_choice_errors_dict_by_field_name_and_index_and_value(field_name='active_languages', index=1, value="'ab'"))

            def test_set_active_languages_with_an_unsupported_language_2(self):
                user = self.get_active_user_jennifer()
                user.speedy_match_profile._set_active_languages(languages=['en', 'he', 'en', 'he1'])
                with self.assertRaises(ValidationError) as cm:
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._item_in_the_array_did_not_validate_value_is_not_a_valid_choice_errors_dict_by_field_name_and_index_and_value(field_name='active_languages', index=3, value="'he1'"))

            def test_set_active_languages_with_an_unsupported_language_3(self):
                user = self.get_active_user_jennifer()
                user.speedy_match_profile._set_active_languages(languages=['en', 'he', 'en1', 'he2'])
                with self.assertRaises(ValidationError) as cm:
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._item_in_the_array_did_not_validate_value_is_not_a_valid_choice_errors_dict_by_field_name_and_index_and_value(field_name='active_languages', index=2, value="'en1'"))

            def test_call_activate_directly_and_assert_exception(self):
                user = self.get_default_user_doron()
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=False)
                with self.assertRaises(NotImplementedError) as cm:
                    user.speedy_match_profile.activate()
                self.assertEqual(first=str(cm.exception), second="activate is not implemented.")
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=False)

            def test_call_deactivate_and_activate_directly_and_assert_no_exception(self):
                # Check that @cached_property user.speedy_match_profile.is_active and user.speedy_match_profile.is_active_and_valid are changed after calling user.speedy_match_profile.deactivate() and user.speedy_match_profile.validate_profile_and_activate().
                user = self.get_active_user_jennifer()
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=True)
                user.speedy_match_profile.deactivate()
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=False)
                # user.speedy_match_profile.validate_profile_and_activate(commit=False) doesn't change anything.
                step, error_messages = user.speedy_match_profile.validate_profile_and_activate(commit=False)
                self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=False)
                step, error_messages = user.speedy_match_profile.validate_profile_and_activate()
                self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=True)

            def test_call_deactivate_race_condition_profile_should_not_become_active_with_not_allowed_to_use_speedy_match(self):
                user = self.get_active_user_jennifer()
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=True)
                self.assertIs(expr1=(user.speedy_match_profile.not_allowed_to_use_speedy_match is False), expr2=True)
                user_instance_2 = User.objects.get(pk=user.pk)
                user_instance_2.speedy_match_profile.deactivate()
                self.assertEqual(first=user_instance_2.is_active, second=True)
                self.assertEqual(first=user_instance_2.speedy_match_profile.is_active, second=False)
                self.assertIs(expr1=(user_instance_2.speedy_match_profile.not_allowed_to_use_speedy_match is False), expr2=True)
                # Race condition: profile should not become active.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertIs(expr1=(user.speedy_match_profile.not_allowed_to_use_speedy_match is False), expr2=True)
                user_instance_2.speedy_match_profile.not_allowed_to_use_speedy_match = True
                user_instance_2.speedy_match_profile.save()
                self.assertEqual(first=user_instance_2.is_active, second=True)
                self.assertEqual(first=user_instance_2.speedy_match_profile.is_active, second=False)
                self.assertIs(expr1=(user_instance_2.speedy_match_profile.not_allowed_to_use_speedy_match is True), expr2=True)
                # Race condition: not_allowed_to_use_speedy_match should not change.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertIs(expr1=(user.speedy_match_profile.not_allowed_to_use_speedy_match is True), expr2=True)
                user_instance_2.speedy_match_profile.not_allowed_to_use_speedy_match = False
                user_instance_2.speedy_match_profile.save()
                self.assertEqual(first=user_instance_2.is_active, second=True)
                self.assertEqual(first=user_instance_2.speedy_match_profile.is_active, second=False)
                self.assertIs(expr1=(user_instance_2.speedy_match_profile.not_allowed_to_use_speedy_match is False), expr2=True)
                # Race condition: not_allowed_to_use_speedy_match should not change.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertIs(expr1=(user.speedy_match_profile.not_allowed_to_use_speedy_match is False), expr2=True)

            def test_call_speedy_net_deactivate_and_activate_directly_and_assert_no_exception(self):
                # Check that @cached_property user.speedy_match_profile.is_active and user.speedy_match_profile.is_active_and_valid are changed after calling user.speedy_net_profile.deactivate() and user.speedy_net_profile.activate().
                user = self.get_active_user_jennifer()
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=True)
                user.speedy_net_profile.deactivate()
                self.assertEqual(first=user.is_active, second=False)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=False)
                user.speedy_net_profile.activate()
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=True)

            def test_call_call_after_verify_email_address_directly_and_assert_no_exception(self):
                user = self.get_default_user_doron()
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=False)
                user.speedy_match_profile.call_after_verify_email_address()
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=False)

            def test_call_get_name_directly_and_assert_no_exception(self):
                user = self.get_default_user_doron()
                self.assertEqual(first=user.speedy_match_profile.get_name(), second="Doron")

            def test_call_user_name_directly_and_assert_no_exception(self):
                user = self.get_default_user_doron()
                self.assertEqual(first=user.name, second="Doron")

            def test_user_name_is_the_same_as_get_name_and_get_first_name(self):
                for user in [self.get_default_user_doron(), self.get_active_user_jennifer(), DefaultUserFactory(), InactiveUserFactory(), SpeedyNetInactiveUserFactory(), ActiveUserFactory()]:
                    self.assertEqual(first=user.name, second=user.speedy_match_profile.get_name())
                    self.assertEqual(first=user.name, second=user.get_first_name())
                    self.assertEqual(first=user.name, second='{}'.format(user.first_name))
                    self.assertNotEqual(first=user.name, second=user.get_full_name())
                    self.assertNotEqual(first=user.name, second='{} {}'.format(user.first_name, user.last_name))
                    self.assertNotEqual(first=str(user), second=user.name)

            def test_validate_profile_and_activate_ok(self):
                user = ActiveUserFactory()
                step, error_messages = user.speedy_match_profile.validate_profile_and_activate()
                self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                self.assertIn(member=user.gender, container=User.GENDER_VALID_VALUES)
                self.assertIn(member=user.diet, container=User.DIET_VALID_VALUES)
                self.assertIn(member=user.speedy_match_profile.height, container=SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES)
                self.assertIn(member=user.smoking_status, container=User.SMOKING_STATUS_VALID_VALUES)
                self.assertIn(member=user.relationship_status, container=User.RELATIONSHIP_STATUS_VALID_VALUES)
                self.assertIn(member=user.speedy_match_profile.min_age_to_match, container=SpeedyMatchSiteProfile.AGE_TO_MATCH_VALID_VALUES)
                self.assertIn(member=user.speedy_match_profile.max_age_to_match, container=SpeedyMatchSiteProfile.AGE_TO_MATCH_VALID_VALUES)
                self.assertEqual(first=user.speedy_match_profile.min_age_to_match, second=SpeedyMatchSiteProfile.settings.MIN_AGE_TO_MATCH_ALLOWED)
                self.assertEqual(first=user.speedy_match_profile.max_age_to_match, second=SpeedyMatchSiteProfile.settings.MAX_AGE_TO_MATCH_ALLOWED)
                self.validate_all_user_values(user=user)

            def test_default_user_factory_doesnt_have_confirmed_email(self):
                user = DefaultUserFactory()
                self.assertEqual(first=user.has_confirmed_email, second=False)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=False)
                self.assertEqual(first=len(user.speedy_match_profile.active_languages), second=0)

            def test_deleting_email_addresses_deactivates_user(self):
                # Check that @cached_property user.speedy_match_profile.is_active and user.speedy_match_profile.is_active_and_valid are changed after calling user_email_address.delete().
                user = ActiveUserFactory()
                self.assertEqual(first=user.has_confirmed_email, second=True)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=True)
                self.assertEqual(first=len(user.speedy_match_profile.active_languages), second=1)
                self.assertEqual(first=len(user.email_addresses.all()), second=1)
                self.assertEqual(first=len(user.email_addresses.filter(is_confirmed=True)), second=1)
                for user_email_address in user.email_addresses.filter(is_confirmed=True):
                    user_email_address.delete()
                self.assertEqual(first=len(user.email_addresses.all()), second=0)
                self.assertEqual(first=len(user.email_addresses.filter(is_confirmed=True)), second=0)
                self.assertEqual(first=user.has_confirmed_email, second=False)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=False)
                self.assertEqual(first=len(user.speedy_match_profile.active_languages), second=0)

            def test_unconfirming_email_addresses_deactivates_user(self):
                # Check that @cached_property user.speedy_match_profile.is_active and user.speedy_match_profile.is_active_and_valid are changed after changing email.is_confirmed to False.
                # After changing email.is_confirmed to True, user.speedy_match_profile.is_active doesn't change to True automatically. The user has to activate himself.
                user = ActiveUserFactory()
                self.assertEqual(first=user.has_confirmed_email, second=True)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=True)
                self.assertEqual(first=len(user.speedy_match_profile.active_languages), second=1)
                self.assertEqual(first=len(user.email_addresses.all()), second=1)
                self.assertEqual(first=len(user.email_addresses.filter(is_confirmed=True)), second=1)
                email = user.email_addresses.filter(is_confirmed=True).first()
                email.is_confirmed = False
                email.save()
                self.assertEqual(first=len(user.email_addresses.all()), second=1)
                self.assertEqual(first=len(user.email_addresses.filter(is_confirmed=True)), second=0)
                self.assertEqual(first=user.has_confirmed_email, second=False)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=False)
                self.assertEqual(first=len(user.speedy_match_profile.active_languages), second=0)
                email = user.email_addresses.filter(is_confirmed=False).first()
                email.is_confirmed = True
                email.save()
                self.assertEqual(first=len(user.email_addresses.all()), second=1)
                self.assertEqual(first=len(user.email_addresses.filter(is_confirmed=True)), second=1)
                self.assertEqual(first=user.has_confirmed_email, second=True)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=False)
                self.assertEqual(first=len(user.speedy_match_profile.active_languages), second=0)

            def test_validate_profile_and_activate_exception_on_profile_picture(self):
                test_settings = {
                    "field_name": 'profile_picture',
                    "test_invalid_values_to_assign": True,
                    "test_invalid_values_to_save": False,
                    "expected_step": 2,
                    "expected_error_message": self._a_profile_picture_is_required_error_message,
                    "expected_counts_tuple": (1, 1, 26, 0),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_profile_description(self):
                test_settings = {
                    "field_name": 'profile_description',
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "expected_step": 3,
                    "expected_error_message": self._please_write_a_few_words_about_yourself_error_message,
                    "expected_counts_tuple": (11, 2, 0, 3),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_city(self):
                test_settings = {
                    "field_name": 'city',
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "expected_step": 3,
                    "expected_error_message": self._please_write_where_you_live_error_message,
                    "expected_counts_tuple": (7, 2, 0, 7),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_children(self):
                test_settings = {
                    "field_name": 'children',
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "expected_step": 4,
                    "expected_error_message": self._do_you_have_children_how_many_error_message,
                    "expected_counts_tuple": (11, 2, 0, 3),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_more_children(self):
                test_settings = {
                    "field_name": 'more_children',
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "expected_step": 4,
                    "expected_error_message": self._do_you_want_more_children_error_message,
                    "expected_counts_tuple": (11, 2, 0, 3),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_match_description(self):
                test_settings = {
                    "field_name": 'match_description',
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "expected_step": 7,
                    "expected_error_message": self._who_is_your_ideal_partner_error_message,
                    "expected_counts_tuple": (11, 2, 0, 3),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_height(self):
                test_settings = {
                    "field_name": 'height',
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "expected_step": 3,
                    "expected_error_message": self._height_must_be_from_1_to_450_cm_error_message,
                    "expected_counts_tuple": (450, 22, 0, 13),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_diet(self):
                test_settings = {
                    "field_name": 'diet',
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "expected_step": 5,
                    "expected_error_message": self._your_diet_is_required_error_message,
                    "expected_counts_tuple": (3, 1, 0, 34),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_smoking_status(self):
                test_settings = {
                    "field_name": 'smoking_status',
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "expected_step": 5,
                    "expected_error_message": self._your_smoking_status_is_required_error_message,
                    "expected_counts_tuple": (3, 1, 0, 34),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_relationship_status(self):
                test_settings = {
                    "field_name": 'relationship_status',
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "expected_step": 6,
                    "expected_error_message": self._your_relationship_status_is_required_error_message,
                    "expected_counts_tuple": (9, 1, 0, 34),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_gender_to_match(self):
                test_settings = {
                    "field_name": 'gender_to_match',
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "expected_step": 7,
                    "expected_error_message": self._gender_to_match_is_required_error_message,
                    "expected_counts_tuple": (77, 5, 0, 133),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_min_age_to_match(self):
                test_settings = {
                    "field_name": 'min_age_to_match',
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "expected_step": 7,
                    "expected_error_message": self._minimal_age_to_match_must_be_from_0_to_180_years_error_message,
                    "expected_counts_tuple": (181, 20, 0, 14),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            @override_settings(SPEEDY_MATCH_SITE_PROFILE_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.SPEEDY_MATCH_SITE_PROFILE_SETTINGS, MIN_AGE_TO_MATCH_ALLOWED=tests_settings.OVERRIDE_SPEEDY_MATCH_SITE_PROFILE_SETTINGS.MIN_AGE_TO_MATCH_ALLOWED, MAX_AGE_TO_MATCH_ALLOWED=tests_settings.OVERRIDE_SPEEDY_MATCH_SITE_PROFILE_SETTINGS.MAX_AGE_TO_MATCH_ALLOWED))
            def test_validate_profile_and_activate_exception_on_min_age_to_match_with_override_settings(self):
                test_settings = {
                    "field_name": 'min_age_to_match',
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "expected_step": 7,
                    "expected_error_message": self._minimal_age_to_match_must_be_from_0_to_180_years_error_message,
                    "expected_counts_tuple": (177, 22, 0, 14),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_max_age_to_match(self):
                test_settings = {
                    "field_name": 'max_age_to_match',
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "expected_step": 7,
                    "expected_error_message": self._maximal_age_to_match_must_be_from_0_to_180_years_error_message,
                    "expected_counts_tuple": (181, 20, 0, 14),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            @override_settings(SPEEDY_MATCH_SITE_PROFILE_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.SPEEDY_MATCH_SITE_PROFILE_SETTINGS, MIN_AGE_TO_MATCH_ALLOWED=tests_settings.OVERRIDE_SPEEDY_MATCH_SITE_PROFILE_SETTINGS.MIN_AGE_TO_MATCH_ALLOWED, MAX_AGE_TO_MATCH_ALLOWED=tests_settings.OVERRIDE_SPEEDY_MATCH_SITE_PROFILE_SETTINGS.MAX_AGE_TO_MATCH_ALLOWED))
            def test_validate_profile_and_activate_exception_on_max_age_to_match_with_override_settings(self):
                test_settings = {
                    "field_name": 'max_age_to_match',
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "expected_step": 7,
                    "expected_error_message": self._maximal_age_to_match_must_be_from_0_to_180_years_error_message,
                    "expected_counts_tuple": (177, 22, 0, 14),
                }
                test_settings["expected_error_messages"] = ["['{expected_error_message}']".format(expected_error_message=test_settings["expected_error_message"]).replace("\xa0", "\\xa0")]
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_min_max_age_to_match_without_invalid_ages_and_invalid_values_to_save(self):
                test_settings = self.get_min_max_age_to_match_default_test_settings()
                test_settings.update({
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": False,
                    "test_invalid_ages": False,
                    "expected_counts_tuple": (91, 90, 0, 0),
                    "expected_min_max_age_to_match_error_messages_counts_tuple": (90, 0),
                })
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_min_max_age_to_match_with_invalid_ages_and_invalid_values_to_save(self):
                test_settings = self.get_min_max_age_to_match_default_test_settings()
                test_settings.update({
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "test_invalid_ages": True,
                    "expected_counts_tuple": (91, 110, 0, 6),
                    "expected_min_max_age_to_match_error_messages_counts_tuple": (90, 20),
                })
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_diet_match_with_invalid_keys_and_ranks_and_invalid_values_to_save(self):
                test_settings = self.get_diet_match_default_test_settings()
                test_settings.update({
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "test_invalid_keys": True,
                    "test_invalid_ranks": True,
                    "expected_counts_tuple": (31, 151, 0, 6),
                    "expected_keys_and_ranks_error_messages_counts_tuple": (86, 65),
                })
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_diet_match_without_invalid_keys_and_ranks_and_invalid_values_to_save(self):
                test_settings = self.get_diet_match_default_test_settings()
                test_settings.update({
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": False,
                    "test_invalid_keys": False,
                    "test_invalid_ranks": False,
                    "expected_counts_tuple": (31, 65, 0, 0),
                    "expected_keys_and_ranks_error_messages_counts_tuple": (0, 65),
                })
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_smoking_status_match_with_invalid_keys_and_ranks_and_invalid_values_to_save(self):
                test_settings = self.get_smoking_status_match_default_test_settings()
                test_settings.update({
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "test_invalid_keys": True,
                    "test_invalid_ranks": True,
                    "expected_counts_tuple": (31, 151, 0, 6),
                    "expected_keys_and_ranks_error_messages_counts_tuple": (86, 65),
                })
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_smoking_status_match_without_invalid_keys_and_ranks_and_invalid_values_to_save(self):
                test_settings = self.get_smoking_status_match_default_test_settings()
                test_settings.update({
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": False,
                    "test_invalid_keys": False,
                    "test_invalid_ranks": False,
                    "expected_counts_tuple": (31, 65, 0, 0),
                    "expected_keys_and_ranks_error_messages_counts_tuple": (0, 65),
                })
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_relationship_status_match_with_invalid_keys_and_ranks_and_invalid_values_to_save(self):
                test_settings = self.get_relationship_status_match_default_test_settings()
                test_settings.update({
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": True,
                    "test_invalid_keys": True,
                    "test_invalid_ranks": True,
                    "expected_counts_tuple": (91, 433, 0, 6),
                    "expected_keys_and_ranks_error_messages_counts_tuple": (248, 185),
                })
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)

            def test_validate_profile_and_activate_exception_on_relationship_status_match_without_invalid_keys_and_ranks_and_invalid_values_to_save(self):
                test_settings = self.get_relationship_status_match_default_test_settings()
                test_settings.update({
                    "test_invalid_values_to_assign": False,
                    "test_invalid_values_to_save": False,
                    "test_invalid_keys": False,
                    "test_invalid_ranks": False,
                    "expected_counts_tuple": (91, 185, 0, 0),
                    "expected_keys_and_ranks_error_messages_counts_tuple": (0, 185),
                })
                self.run_test_validate_profile_and_activate_exception(test_settings=test_settings)


        @only_on_speedy_match
        class SpeedyMatchSiteProfileEnglishTestCase(SpeedyMatchSiteProfileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fr')
        class SpeedyMatchSiteProfileFrenchTestCase(SpeedyMatchSiteProfileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='de')
        class SpeedyMatchSiteProfileGermanTestCase(SpeedyMatchSiteProfileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='es')
        class SpeedyMatchSiteProfileSpanishTestCase(SpeedyMatchSiteProfileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='pt')
        class SpeedyMatchSiteProfilePortugueseTestCase(SpeedyMatchSiteProfileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='it')
        class SpeedyMatchSiteProfileItalianTestCase(SpeedyMatchSiteProfileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='nl')
        class SpeedyMatchSiteProfileDutchTestCase(SpeedyMatchSiteProfileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sv')
        class SpeedyMatchSiteProfileSwedishTestCase(SpeedyMatchSiteProfileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ko')
        class SpeedyMatchSiteProfileKoreanTestCase(SpeedyMatchSiteProfileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fi')
        class SpeedyMatchSiteProfileFinnishTestCase(SpeedyMatchSiteProfileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='he')
        class SpeedyMatchSiteProfileHebrewTestCase(SpeedyMatchSiteProfileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_speedy_match
        class SpeedyMatchSiteProfileMatchOnlyEnglishTestCase(SpeedyMatchAccountsModelsMixin, SiteTestCase):
            def get_active_user_doron(self):
                user = ActiveUserFactory(first_name_en="Doron", last_name_en="Matalon", slug="doron-matalon", date_of_birth=date(year=1958, month=10, day=22), gender=User.GENDER_MALE)
                user.diet = User.DIET_VEGETARIAN
                user.smoking_status = User.SMOKING_STATUS_NOT_SMOKING
                user.relationship_status = User.RELATIONSHIP_STATUS_SINGLE
                user.speedy_match_profile.min_age_to_match = 20
                user.speedy_match_profile.max_age_to_match = 180
                user.speedy_match_profile.gender_to_match = [User.GENDER_FEMALE]
                user.save_user_and_profile()
                return user

            def get_active_user_jennifer(self):
                user = ActiveUserFactory(first_name_en="Jennifer", last_name_en="Connelly", slug="jennifer-connelly", date_of_birth=date(year=1978, month=9, day=12), gender=User.GENDER_FEMALE)
                user.diet = User.DIET_VEGAN
                user.smoking_status = User.SMOKING_STATUS_SMOKING
                user.relationship_status = User.RELATIONSHIP_STATUS_SINGLE
                user.speedy_match_profile.gender_to_match = [User.GENDER_MALE]
                user.save_user_and_profile()
                return user

            def test_user_doesnt_match_self(self):
                user = ActiveUserFactory()
                for gender in User.GENDER_VALID_VALUES:
                    user.gender = gender
                    user.speedy_match_profile.gender_to_match = User.GENDER_VALID_VALUES
                    user.save_user_and_profile()
                    rank = user.speedy_match_profile.get_matching_rank(other_profile=user.speedy_match_profile)
                    self.assertEqual(first=rank, second=0)

            def test_gender_doesnt_match_profile(self):
                user_1 = self.get_active_user_doron()
                user_2 = self.get_active_user_jennifer()
                user_1.speedy_match_profile.gender_to_match = [User.GENDER_MALE]
                user_2.speedy_match_profile.gender_to_match = [User.GENDER_MALE]
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=0)
                self.assertEqual(first=rank_2, second=0)

            def test_gender_match_profile_different_gender(self):
                user_1 = self.get_active_user_doron()
                user_2 = self.get_active_user_jennifer()
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=5)
                self.assertEqual(first=rank_2, second=5)

            def test_gender_match_profile_same_gender(self):
                user_1 = self.get_active_user_doron()
                user_2 = self.get_active_user_jennifer()
                user_1.speedy_match_profile.gender_to_match = [User.GENDER_MALE]
                user_2.gender = User.GENDER_MALE
                user_2.speedy_match_profile.gender_to_match = [User.GENDER_MALE]
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=5)
                self.assertEqual(first=rank_2, second=5)

            def test_age_doesnt_match_profile(self):
                user_1 = self.get_active_user_doron()
                user_2 = self.get_active_user_jennifer()
                user_1.speedy_match_profile.min_age_to_match = 20
                user_1.speedy_match_profile.max_age_to_match = 30
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=0)
                self.assertEqual(first=rank_2, second=0)

            def run_test_height_doesnt_match_profile(self, with_override_settings):
                user_1 = self.get_active_user_doron()
                user_2 = self.get_active_user_jennifer()
                user_1.speedy_match_profile.height = 176
                user_2.speedy_match_profile.height = 170
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=5)
                self.assertEqual(first=rank_2, second=5)
                values_to_test = [1, 5, 6, 19, 20, 59, 60, 61, 71, 72, 73, 84, 85, 86, 100, 118, 119, 120, 150, 160, 170, 180, 190, 200, 210, 219, 220, 221, 250, 320, 321, 400, 450]
                if (with_override_settings):
                    expected_rank_5_values = [height for height in values_to_test if (120 <= height <= 220)]
                    expected_rank_0_values = [height for height in values_to_test if (not (120 <= height <= 220))]
                    self.assertListEqual(list1=expected_rank_5_values, list2=[120, 150, 160, 170, 180, 190, 200, 210, 219, 220])
                    self.assertListEqual(list1=expected_rank_0_values, list2=[1, 5, 6, 19, 20, 59, 60, 61, 71, 72, 73, 84, 85, 86, 100, 118, 119, 221, 250, 320, 321, 400, 450])
                else:
                    expected_rank_5_values = [height for height in values_to_test if (85 <= height <= 320)]
                    expected_rank_0_values = [height for height in values_to_test if (not (85 <= height <= 320))]
                    self.assertListEqual(list1=expected_rank_5_values, list2=[85, 86, 100, 118, 119, 120, 150, 160, 170, 180, 190, 200, 210, 219, 220, 221, 250, 320])
                    self.assertListEqual(list1=expected_rank_0_values, list2=[1, 5, 6, 19, 20, 59, 60, 61, 71, 72, 73, 84, 321, 400, 450])
                self.assertListEqual(list1=sorted(expected_rank_5_values + expected_rank_0_values), list2=values_to_test)
                for height in values_to_test:
                    # Save both users to delete rank cache.
                    user_1.speedy_match_profile.height = height
                    user_1.save_user_and_profile()
                    user_2.save_user_and_profile()
                    if (with_override_settings):
                        expected_rank_is_5 = (120 <= height <= 220)
                    else:
                        expected_rank_is_5 = (85 <= height <= 320)
                    self.assertEqual(first=expected_rank_is_5, second=(height in expected_rank_5_values))
                    self.assertEqual(first=not (expected_rank_is_5), second=(height in expected_rank_0_values))
                    if (expected_rank_is_5):
                        expected_rank = 5
                    else:
                        expected_rank = 0
                    rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                    rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                    self.assertEqual(first=rank_1, second=expected_rank)
                    self.assertEqual(first=rank_2, second=expected_rank)

            def test_height_doesnt_match_profile(self):
                self.run_test_height_doesnt_match_profile(with_override_settings=False)

            @override_settings(SPEEDY_MATCH_SITE_PROFILE_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.SPEEDY_MATCH_SITE_PROFILE_SETTINGS, MIN_HEIGHT_TO_MATCH=tests_settings.OVERRIDE_SPEEDY_MATCH_SITE_PROFILE_SETTINGS.MIN_HEIGHT_TO_MATCH, MAX_HEIGHT_TO_MATCH=tests_settings.OVERRIDE_SPEEDY_MATCH_SITE_PROFILE_SETTINGS.MAX_HEIGHT_TO_MATCH))
            def test_height_doesnt_match_profile_with_override_settings(self):
                self.run_test_height_doesnt_match_profile(with_override_settings=True)

            def test_not_allowed_to_use_speedy_match(self):
                user_1 = self.get_active_user_doron()
                user_2 = self.get_active_user_jennifer()
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=5)
                self.assertEqual(first=rank_2, second=5)
                # Save both users to delete rank cache.
                user_1.speedy_match_profile.not_allowed_to_use_speedy_match = True
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=0)
                self.assertEqual(first=rank_2, second=0)
                # Save both users to delete rank cache.
                user_1.speedy_match_profile.not_allowed_to_use_speedy_match = False
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=0)
                self.assertEqual(first=rank_2, second=0)
                # Save both users to delete rank cache.
                step, error_messages = user_1.speedy_match_profile.validate_profile_and_activate()
                self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=5)
                self.assertEqual(first=rank_2, second=5)

            def test_smoking_status_doesnt_match_profile(self):
                user_1 = self.get_active_user_doron()
                user_2 = self.get_active_user_jennifer()
                user_1.speedy_match_profile.smoking_status_match = {str(User.SMOKING_STATUS_SMOKING): 0, str(User.SMOKING_STATUS_NOT_SMOKING): 5, str(User.SMOKING_STATUS_SMOKING_OCCASIONALLY): 0}
                user_2.smoking_status = User.SMOKING_STATUS_SMOKING
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=0)
                self.assertEqual(first=rank_2, second=0)

            def test_relationship_status_match_profile(self):
                user_1 = self.get_active_user_doron()
                user_2 = self.get_active_user_jennifer()
                user_2.speedy_match_profile.relationship_status_match[str(User.RELATIONSHIP_STATUS_MARRIED)] = SpeedyMatchSiteProfile.RANK_0
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=5)
                self.assertEqual(first=rank_2, second=5)

            def test_relationship_status_doesnt_match_profile(self):
                user_1 = self.get_active_user_doron()
                user_2 = self.get_active_user_jennifer()
                user_1.relationship_status = User.RELATIONSHIP_STATUS_MARRIED
                user_2.speedy_match_profile.relationship_status_match[str(User.RELATIONSHIP_STATUS_MARRIED)] = SpeedyMatchSiteProfile.RANK_0
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=0)
                self.assertEqual(first=rank_2, second=0)

            def test_match_profile_rank_3(self):
                user_1 = self.get_active_user_doron()
                user_2 = self.get_active_user_jennifer()
                user_1.speedy_match_profile.smoking_status_match = {str(User.SMOKING_STATUS_SMOKING): 3, str(User.SMOKING_STATUS_NOT_SMOKING): 5, str(User.SMOKING_STATUS_SMOKING_OCCASIONALLY): 4}
                user_1.speedy_match_profile.diet_match = {str(User.DIET_VEGAN): 4, str(User.DIET_VEGETARIAN): 5, str(User.DIET_CARNIST): 0}
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=3)
                self.assertEqual(first=rank_2, second=5)

            def test_match_profile_rank_4(self):
                user_1 = self.get_active_user_doron()
                user_2 = self.get_active_user_jennifer()
                user_1.speedy_match_profile.diet_match = {str(User.DIET_VEGAN): 4, str(User.DIET_VEGETARIAN): 5, str(User.DIET_CARNIST): 0}
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=4)
                self.assertEqual(first=rank_2, second=5)

            def test_match_profile_rank_1(self):
                user_1 = self.get_active_user_jennifer()
                user_2 = self.get_active_user_doron()
                user_1.speedy_match_profile.smoking_status_match = {str(User.SMOKING_STATUS_SMOKING): 3, str(User.SMOKING_STATUS_NOT_SMOKING): 5, str(User.SMOKING_STATUS_SMOKING_OCCASIONALLY): 4}
                user_1.speedy_match_profile.diet_match = {str(User.DIET_VEGAN): 4, str(User.DIET_VEGETARIAN): 5, str(User.DIET_CARNIST): 0}
                user_1.speedy_match_profile.relationship_status_match[str(User.RELATIONSHIP_STATUS_MARRIED)] = SpeedyMatchSiteProfile.RANK_1
                user_2.relationship_status = User.RELATIONSHIP_STATUS_MARRIED
                user_1.save_user_and_profile()
                user_2.save_user_and_profile()
                rank_1 = user_1.speedy_match_profile.get_matching_rank(other_profile=user_2.speedy_match_profile)
                rank_2 = user_2.speedy_match_profile.get_matching_rank(other_profile=user_1.speedy_match_profile)
                self.assertEqual(first=rank_1, second=1)
                self.assertEqual(first=rank_2, second=5)


