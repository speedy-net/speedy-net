from datetime import datetime
import itertools

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import DataError

from speedy.core.base.test import TestCase, only_on_speedy_match
from ..models import SiteProfile as SpeedyMatchSiteProfile
from speedy.match.accounts import utils
from speedy.core.accounts.models import User
from speedy.core.accounts.tests.test_factories import DefaultUserFactory, ActiveUserFactory, UserImageFactory


@only_on_speedy_match
class SpeedyMatchSiteProfileTestCase(TestCase):
    _none_list = [None]
    _empty_string_list = [""]
    _empty_values_to_test = _none_list + _empty_string_list
    _non_int_string_values_to_test = ["Tel Aviv.", "One boy.", "Yes.", "Hi!"]
    _valid_string_values_to_test = ["1"] + _non_int_string_values_to_test

    def get_default_user_1(self):
        user = DefaultUserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse-pinkman', date_of_birth=datetime(year=1978, month=9, day=12), gender=User.GENDER_FEMALE, diet=User.DIET_VEGAN)
        return user

    def get_default_user_2(self):
        user = ActiveUserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse-pinkman', date_of_birth=datetime(year=1978, month=9, day=12), gender=User.GENDER_FEMALE, diet=User.DIET_VEGETARIAN)
        return user

    def validate_all_values(self, user):
        all_fields = ['photo', 'profile_description', 'city', 'children', 'more_children', 'match_description', 'height', 'diet', 'smoking_status', 'marital_status', 'gender_to_match', 'min_age_match', 'max_age_match', 'min_max_age_to_match', 'diet_match', 'smoking_status_match', 'marital_status_match']
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

    def assert_step_and_error_messages_ok(self, step, error_messages):
        self.assertEqual(first=step, second=len(settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS))
        self.assertEqual(first=step, second=10)
        self.assertEqual(first=len(error_messages), second=0)
        self.assertListEqual(list1=error_messages, list2=[])

    def save_user_and_profile_and_assert_exceptions_for_integer(self, user, field_name, value_to_test, null):
        if ((null == True) and (value_to_test in self._empty_string_list)):
            with self.assertRaises(ValueError) as cm:
                user.save_user_and_profile()
            self.assertEqual(first=str(cm.exception), second="invalid literal for int() with base 10: ''")
        else:
            with self.assertRaises(ValidationError) as cm:
                user.save_user_and_profile()
            if ((null == False) and (value_to_test in self._none_list)):
                self.assertDictEqual(d1=dict(cm.exception), d2={field_name: ['This field cannot be null.']})
            elif (isinstance(value_to_test, int)):
                self.assertDictEqual(d1=dict(cm.exception), d2={field_name: ['Value {} is not a valid choice.'.format(value_to_test)]})
            else:
                self.assertDictEqual(d1=dict(cm.exception), d2={field_name: ["'{}' value must be an integer.".format(value_to_test)]})

    def run_test_validate_profile_and_activate_exception(self, field_name, expected_step, expected_error_message, expected_error_messages, expected_counts_tuple):
        user = ActiveUserFactory()
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        can_assign_value_set, can_save_user_and_profile_set, value_is_valid_set, value_is_invalid_set = set(), set(), set(), set()
        values_to_test, valid_values_to_assign, valid_values_to_save, valid_values, invalid_values = None, None, None, None, None
        if (field_name in ['photo']):
            valid_values = [UserImageFactory]
            values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, 10 + 1)) + valid_values
            valid_values_to_assign = self._none_list + valid_values
            valid_values_to_save = values_to_test
        elif (field_name in ['profile_description', 'city', 'children', 'more_children', 'match_description']):
            values_to_test = self._empty_values_to_test + self._valid_string_values_to_test
            valid_values_to_save = values_to_test
            invalid_values = self._empty_values_to_test
            valid_values = self._valid_string_values_to_test
        elif (field_name in ['height']):
            values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, settings.MAX_HEIGHT_ALLOWED + 10 + 1))
            valid_values_to_save = self._none_list + [value for value in values_to_test if (isinstance(value, int))]
            valid_values = SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES
        elif (field_name in ['diet']):
            values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, User.DIET_MAX_VALUE_PLUS_ONE + 10))
            valid_values_to_save = [choice[0] for choice in User.DIET_CHOICES_WITH_DEFAULT]
            valid_values = User.DIET_VALID_VALUES
            self.assertEqual(first=valid_values_to_save, second=[User.DIET_UNKNOWN] + valid_values)
            self.assertEqual(first=valid_values_to_save, second=[0] + valid_values)
        elif (field_name in ['smoking_status']):
            values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, SpeedyMatchSiteProfile.SMOKING_STATUS_MAX_VALUE_PLUS_ONE + 10))
            valid_values_to_save = [choice[0] for choice in SpeedyMatchSiteProfile.SMOKING_STATUS_CHOICES_WITH_DEFAULT]
            valid_values = SpeedyMatchSiteProfile.SMOKING_STATUS_VALID_VALUES
            self.assertEqual(first=valid_values_to_save, second=[SpeedyMatchSiteProfile.SMOKING_STATUS_UNKNOWN] + valid_values)
            self.assertEqual(first=valid_values_to_save, second=[0] + valid_values)
        elif (field_name in ['marital_status']):
            values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, SpeedyMatchSiteProfile.MARITAL_STATUS_MAX_VALUE_PLUS_ONE + 10))
            valid_values_to_save = [choice[0] for choice in SpeedyMatchSiteProfile.MARITAL_STATUS_CHOICES_WITH_DEFAULT]
            valid_values = SpeedyMatchSiteProfile.MARITAL_STATUS_VALID_VALUES
            self.assertEqual(first=valid_values_to_save, second=[SpeedyMatchSiteProfile.MARITAL_STATUS_UNKNOWN] + valid_values)
            self.assertEqual(first=valid_values_to_save, second=[0] + valid_values)
        elif (field_name in ['gender_to_match']):
            range_to_test = [User.GENDER_UNKNOWN] + User.GENDER_VALID_VALUES + [User.GENDER_MAX_VALUE_PLUS_ONE]
            self.assertEqual(first=range_to_test, second=list(range(5)))
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
            # print(len(values_to_test)) # ~~~~ TODO: remove this line!
            # print(values_to_test) # ~~~~ TODO: remove this line!
            valid_values_to_save = self._none_list + [gender_to_match for gender_to_match in values_to_test if (isinstance(gender_to_match, (list, tuple))) and (len(gender_to_match) <= len(User.GENDER_VALID_VALUES))]
            # print(len(valid_values_to_save)) # ~~~~ TODO: remove this line!
            # print(valid_values_to_save) # ~~~~ TODO: remove this line!
            valid_values = [gender_to_match for gender_to_match in values_to_test if (isinstance(gender_to_match, (list, tuple))) and (len(gender_to_match) > 0) and (len(gender_to_match) == len(set(gender_to_match))) and all(gender in User.GENDER_VALID_VALUES for gender in gender_to_match)]
            # print(len(valid_values)) # ~~~~ TODO: remove this line!
            # print(valid_values) # ~~~~ TODO: remove this line!
            for value in [[1], [2], [3], (1,), (2,), (3,), [1, 2], [1, 3], [2, 3], (1, 2), (1, 3), [1, 2, 3], (1, 2, 3)]:
                for val in [value, list(value)]:
                    self.assertIn(member=val, container=values_to_test)
                    self.assertIn(member=val, container=valid_values)
            for value in [[], (), [1, 2, 3, 1, 2, 3], (1, 2, 3, 1, 2, 3), [1, 2, 1], [1, 2, 1, 2], [0], [4], (0,), (4,), [0, 1], [1, 2, 0], [1, 2, 4], [4, 1, 2, 3]]:
                for val in [value, list(value)]:
                    self.assertIn(member=val, container=values_to_test)
                    self.assertNotIn(member=val, container=valid_values)
                    if (len(val) <= 3):
                        self.assertIn(member=val, container=valid_values_to_save)
                    else:
                        self.assertNotIn(member=val, container=valid_values_to_save)
            for value in valid_values:
                self.assertIn(member=value, container=values_to_test)
            invalid_values = [value for value in values_to_test if (value not in valid_values)]
            for value in invalid_values:
                self.assertIn(member=value, container=values_to_test)
                self.assertNotIn(member=value, container=valid_values)
            for value in [[i, i] for i in User.GENDER_VALID_VALUES] + [[i, i, i] for i in User.GENDER_VALID_VALUES] + [[i, i, 1] for i in User.GENDER_VALID_VALUES]:
                self.assertIn(member=value, container=values_to_test)
                self.assertIn(member=value, container=invalid_values)
            valid_sets = list()
            for value in [set(gender_to_match) for gender_to_match in valid_values]:
                if (value not in valid_sets):
                    valid_sets.append(value)
            # print(valid_sets) # ~~~~ TODO: remove this line!
            self.assertListEqual(list1=valid_sets, list2=[{1}, {2}, {3}, {1, 2}, {1, 3}, {2, 3}, {1, 2, 3}])
        elif (field_name in ['min_age_match', 'max_age_match']):
            values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, settings.MAX_AGE_ALLOWED + 10 + 1))
            valid_values_to_save = [value for value in values_to_test if (isinstance(value, int))]
            valid_values = SpeedyMatchSiteProfile.AGE_VALID_VALUES
        elif (field_name in ['min_max_age_to_match']):
            values_to_test = [(value, settings.MAX_AGE_ALLOWED - value) for value in SpeedyMatchSiteProfile.AGE_VALID_VALUES]
            self.assertTrue(expr=all((len(value) == 2) for value in values_to_test))
            valid_values_to_save = values_to_test
            valid_values = [value for value in values_to_test if (value[0] <= value[1])]
            invalid_values = [value for value in values_to_test if (value not in valid_values)]
            # print(values_to_test) # ~~~~ TODO: remove this line!
            # print(valid_values_to_save) # ~~~~ TODO: remove this line!
            # print(valid_values) # ~~~~ TODO: remove this line!
            # print(invalid_values) # ~~~~ TODO: remove this line!
            self.assertListEqual(list1=valid_values, list2=[(value, 180 - value) for value in range(0, 90 + 1)])
            self.assertEqual(first=valid_values[0], second=(0, 180))
            self.assertEqual(first=valid_values[-1], second=(90, 90))
            self.assertListEqual(list1=invalid_values, list2=[(value, 180 - value) for value in range(91, 180 + 1)])
            self.assertEqual(first=invalid_values[0], second=(91, 89))
            self.assertEqual(first=invalid_values[-1], second=(180, 0))
        elif (field_name in ['diet_match']):
            values_to_test = []
            valid_values_to_save = []
            valid_values = []
        elif (field_name in ['smoking_status_match']):
            values_to_test = []
            valid_values_to_save = []
            valid_values = []
        elif (field_name in ['marital_status_match']):
            values_to_test = []
            valid_values_to_save = []
            valid_values = []
        if (valid_values_to_assign is None):
            valid_values_to_assign = values_to_test
        if (invalid_values is None):
            invalid_values = [value for value in values_to_test if (value not in valid_values)]
        self.assert_valid_values_ok(values_to_test=values_to_test, valid_values_to_assign=valid_values_to_assign, valid_values_to_save=valid_values_to_save, valid_values=valid_values, invalid_values=invalid_values)
        if (field_name in ['photo', 'profile_description', 'city', 'children', 'more_children', 'match_description', 'min_max_age_to_match']):
            self.assertEqual(first=len(valid_values_to_save), second=len(values_to_test))
            self.assertListEqual(list1=valid_values_to_save, list2=values_to_test)
        else:
            self.assertLess(a=len(valid_values_to_save), b=len(values_to_test))
        if (field_name in ['photo']):
            self.assertLess(a=len(valid_values_to_assign), b=len(values_to_test))
        else:
            self.assertEqual(first=len(valid_values_to_assign), second=len(values_to_test))
            self.assertListEqual(list1=valid_values_to_assign, list2=values_to_test)
        for value_to_test in values_to_test:
            can_assign_value = (value_to_test in valid_values_to_assign)
            # if (not (field_name in ['photo'])): # ~~~~ TODO: remove this line!
            #     self.assertEqual(first=can_assign_value, second=True) # ~~~~ TODO: remove this line!
            can_save_user_and_profile = (value_to_test in valid_values_to_save)
            # if (field_name in ['photo', 'profile_description', 'city', 'children', 'more_children', 'match_description', 'min_max_age_to_match']): # ~~~~ TODO: remove this line!
            #     self.assertEqual(first=can_save_user_and_profile, second=True) # ~~~~ TODO: remove this line!
            value_is_valid = (value_to_test in valid_values)
            value_is_invalid = (value_to_test in invalid_values)
            self.assertEqual(first=value_is_valid, second=(not (value_is_invalid)))
            can_assign_value_set.add(can_assign_value)
            can_save_user_and_profile_set.add(can_save_user_and_profile)
            value_is_valid_set.add(value_is_valid)
            value_is_invalid_set.add(value_is_invalid)
            # print(value_to_test) # ~~~~ TODO: remove this line!
            if (field_name in ['photo']):
                user.photo = None
                if (value_to_test == UserImageFactory):
                    value_to_assign = UserImageFactory(owner=user)
                else:
                    value_to_assign = value_to_test
                # print(value_to_test) # ~~~~ TODO: remove this line!
                if (not (can_assign_value)):
                    with self.assertRaises(ValueError) as cm:
                        user.photo = value_to_assign
                    self.assertEqual(first=str(cm.exception), second='Cannot assign "{0}{1}{0}": "User.photo" must be a "Image" instance.'.format("'" if (isinstance(value_to_assign, str)) else '', value_to_assign))
                    user.save_user_and_profile()
                    self.assertEqual(first=user.photo, second=None)
                    self.assertNotEqual(first=user.photo, second=value_to_assign)
                    model_save_failures_count += 1
                else:
                    user.photo = value_to_assign
            elif (field_name in ['profile_description']):
                user.profile.profile_description = value_to_test
            elif (field_name in ['city']):
                user.profile.city = value_to_test
            elif (field_name in ['children']):
                user.profile.children = value_to_test
            elif (field_name in ['more_children']):
                user.profile.more_children = value_to_test
            elif (field_name in ['match_description']):
                user.profile.match_description = value_to_test
            elif (field_name in ['height']):
                user.profile.height = value_to_test
            elif (field_name in ['diet']):
                user.diet = value_to_test
            elif (field_name in ['smoking_status']):
                user.profile.smoking_status = value_to_test
            elif (field_name in ['marital_status']):
                user.profile.marital_status = value_to_test
            elif (field_name in ['gender_to_match']):
                user.profile.gender_to_match = value_to_test
            elif (field_name in ['min_age_match']):
                user.profile.min_age_match = value_to_test
            elif (field_name in ['max_age_match']):
                user.profile.max_age_match = value_to_test
            elif (field_name in ['min_max_age_to_match']):
                user.profile.min_age_match = value_to_test[0]
                user.profile.max_age_match = value_to_test[1]
            elif (field_name in ['diet_match']):
                user.profile.diet_match = value_to_test
            elif (field_name in ['smoking_status_match']):
                user.profile.smoking_status_match = value_to_test
            elif (field_name in ['marital_status_match']):
                user.profile.marital_status_match = value_to_test
            if (not (can_save_user_and_profile)):
                if (field_name in ['height']):
                    self.save_user_and_profile_and_assert_exceptions_for_integer(user=user, field_name=field_name, value_to_test=value_to_test, null=True)
                elif (field_name in ['diet', 'smoking_status', 'marital_status', 'min_age_match', 'max_age_match']):
                    self.save_user_and_profile_and_assert_exceptions_for_integer(user=user, field_name=field_name, value_to_test=value_to_test, null=False)
                elif (field_name in ['gender_to_match']):
                    if (isinstance(value_to_test, str)):
                        with self.assertRaises(DataError) as cm:
                            user.save_user_and_profile()
                        # print(str(cm.exception)) # ~~~~ TODO: remove this line!
                        self.assertIn(member='malformed array literal: ""', container=str(cm.exception))
                    else:
                        with self.assertRaises(ValidationError) as cm:
                            user.save_user_and_profile()
                        # print(str(cm.exception)) # ~~~~ TODO: remove this line!
                        # print(dict(cm.exception)) # ~~~~ TODO: remove this line!
                        self.assertDictEqual(d1=dict(cm.exception), d2={'gender_to_match': ['List contains {} items, it should contain no more than 3.'.format(len(value_to_test))]})
                else:
                    raise Exception("Unexpected: can_save_user_and_profile={}, value_to_test={}".format(can_save_user_and_profile, value_to_test))
                model_save_failures_count += 1
            else:
                user.save_user_and_profile()
                step, error_messages = user.profile.validate_profile_and_activate()
                if (not (value_is_valid)):
                    self.assertEqual(first=step, second=expected_step)
                    self.assertEqual(first=len(error_messages), second=1)
                    print(error_messages)
                    self.assertListEqual(list1=error_messages, list2=expected_error_messages)
                    with self.assertRaises(ValidationError) as cm:
                        utils.validate_field(field_name=field_name, user=user)
                    self.assertEqual(first=str(cm.exception.message), second=expected_error_message)
                    self.assertListEqual(list1=list(cm.exception), list2=[expected_error_message])
                    validate_profile_and_activate_failures_count += 1
                else:
                    self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                    utils.validate_field(field_name=field_name, user=user)
                    ok_count += 1
        if (field_name in ['photo']):
            self.assertSetEqual(set1=can_assign_value_set, set2={False, True})
        else:
            self.assertSetEqual(set1=can_assign_value_set, set2={True})
        if (field_name in ['photo', 'profile_description', 'city', 'children', 'more_children', 'match_description', 'min_max_age_to_match']):
            self.assertSetEqual(set1=can_save_user_and_profile_set, set2={True})
        else:
            self.assertSetEqual(set1=can_save_user_and_profile_set, set2={False, True})
        self.assertSetEqual(set1=value_is_valid_set, set2={False, True})
        self.assertSetEqual(set1=value_is_invalid_set, set2={False, True})
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(valid_values), len(valid_values_to_save) - len(valid_values), len(values_to_test) - len(valid_values_to_save)))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=expected_counts_tuple)

    def test_height_valid_values(self):
        self.assertEqual(first=settings.MIN_HEIGHT_ALLOWED, second=1)
        self.assertEqual(first=settings.MAX_HEIGHT_ALLOWED, second=450)
        self.assertEqual(first=SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES, second=range(settings.MIN_HEIGHT_ALLOWED, settings.MAX_HEIGHT_ALLOWED + 1))
        self.assertEqual(first=SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES, second=range(1, 450 + 1))

    def test_age_valid_values(self):
        self.assertEqual(first=settings.MIN_AGE_ALLOWED, second=0)
        self.assertEqual(first=settings.MAX_AGE_ALLOWED, second=180)
        self.assertEqual(first=SpeedyMatchSiteProfile.AGE_VALID_VALUES, second=range(settings.MIN_AGE_ALLOWED, settings.MAX_AGE_ALLOWED + 1))
        self.assertEqual(first=SpeedyMatchSiteProfile.AGE_VALID_VALUES, second=range(0, 180 + 1))

    def test_smoking_status_valid_values(self):
        self.assertListEqual(list1=SpeedyMatchSiteProfile.SMOKING_STATUS_VALID_VALUES, list2=list(range(SpeedyMatchSiteProfile.SMOKING_STATUS_UNKNOWN + 1, SpeedyMatchSiteProfile.SMOKING_STATUS_MAX_VALUE_PLUS_ONE)))
        self.assertListEqual(list1=SpeedyMatchSiteProfile.SMOKING_STATUS_VALID_VALUES, list2=list(range(1, 4)))

    def test_marital_status_valid_values(self):
        self.assertListEqual(list1=SpeedyMatchSiteProfile.MARITAL_STATUS_VALID_VALUES, list2=list(range(SpeedyMatchSiteProfile.MARITAL_STATUS_UNKNOWN + 1, SpeedyMatchSiteProfile.MARITAL_STATUS_MAX_VALUE_PLUS_ONE)))
        self.assertListEqual(list1=SpeedyMatchSiteProfile.MARITAL_STATUS_VALID_VALUES, list2=list(range(1, 9)))

    def test_get_steps_range(self):
        self.assertEqual(first=len(settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS), second=10)
        self.assertEqual(first=utils.get_steps_range(), second=range(1, len(settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)))
        self.assertEqual(first=utils.get_steps_range(), second=range(1, 10))

    def test_get_active_languages(self):
        p = SpeedyMatchSiteProfile(active_languages='en, he, de')
        self.assertListEqual(list1=p.get_active_languages(), list2=['en', 'he', 'de'])
        p = SpeedyMatchSiteProfile(active_languages='')
        self.assertListEqual(list1=p.get_active_languages(), list2=[])

    def test_set_active_languages(self):
        p = SpeedyMatchSiteProfile()
        p._set_active_languages(['en', 'he'])
        self.assertSetEqual(set1=set(p.get_active_languages()), set2={'en', 'he'})

    def test_call_activate_directly_and_assert_exception(self):
        user = self.get_default_user_1()
        self.assertEqual(first=user.profile.is_active, second=False)
        with self.assertRaises(NotImplementedError) as cm:
            user.profile.activate()
        self.assertEqual(first=str(cm.exception), second='')
        self.assertEqual(first=user.profile.is_active, second=False)

    def test_call_deactivate_directly_and_assert_no_exception(self):
        user = self.get_default_user_2()
        self.assertEqual(first=user.profile.is_active, second=True)
        user.profile.deactivate()
        self.assertEqual(first=user.profile.is_active, second=False)

    def test_call_get_name_directly_and_assert_no_exception(self):
        user = self.get_default_user_1()
        self.assertEqual(first=user.profile.get_name(), second='Jesse')

    def test_call_str_of_user_directly_and_assert_no_exception(self):
        user = self.get_default_user_1()
        self.assertEqual(first=str(user), second='Jesse')

    def test_validate_profile_and_activate_ok(self):
        user = ActiveUserFactory()
        step, error_messages = user.profile.validate_profile_and_activate()
        self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
        self.assertIn(member=user.gender, container=User.GENDER_VALID_VALUES)
        self.assertIn(member=user.diet, container=User.DIET_VALID_VALUES)
        self.assertIn(member=user.profile.height, container=SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES)
        self.assertIn(member=user.profile.smoking_status, container=SpeedyMatchSiteProfile.SMOKING_STATUS_VALID_VALUES)
        self.assertIn(member=user.profile.marital_status, container=SpeedyMatchSiteProfile.MARITAL_STATUS_VALID_VALUES)
        self.assertIn(member=user.profile.min_age_match, container=SpeedyMatchSiteProfile.AGE_VALID_VALUES)
        self.assertIn(member=user.profile.max_age_match, container=SpeedyMatchSiteProfile.AGE_VALID_VALUES)
        self.assertEqual(first=user.profile.min_age_match, second=settings.MIN_AGE_ALLOWED)
        self.assertEqual(first=user.profile.max_age_match, second=settings.MAX_AGE_ALLOWED)
        self.validate_all_values(user=user)

    def test_validate_profile_and_activate_exception_on_photo(self):
        self.run_test_validate_profile_and_activate_exception(field_name='photo', expected_step=2, expected_error_message='A profile picture is required.', expected_error_messages=["['A profile picture is required.']"], expected_counts_tuple=(1, 1, 26))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # valid_values = [UserImageFactory]
        # values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, 10 + 1)) + valid_values
        # valid_values_to_assign = self._none_list + valid_values
        # # self.assert_valid_values_ok(values_to_test=values_to_test, valid_values_to_assign=valid_values_to_assign, valid_values=valid_values)
        # for value_to_test in values_to_test:
        #     user.photo = None
        #     if (value_to_test == UserImageFactory):
        #         value_to_assign = UserImageFactory(owner=user)
        #     else:
        #         value_to_assign = value_to_test
        #     # print(value_to_test)
        #     if (not (value_to_test in valid_values_to_assign)):
        #         with self.assertRaises(ValueError) as cm:
        #             user.photo = value_to_assign
        #         self.assertEqual(first=str(cm.exception), second='Cannot assign "{0}{1}{0}": "User.photo" must be a "Image" instance.'.format("'" if (isinstance(value_to_assign, str)) else '', value_to_assign))
        #         user.save_user_and_profile()
        #         self.assertEqual(first=user.photo, second=None)
        #         self.assertNotEqual(first=user.photo, second=value_to_assign)
        #         model_save_failures_count += 1
        #     else:
        #         user.photo = value_to_assign
        #         user.save_user_and_profile()
        #         step, error_messages = user.profile.validate_profile_and_activate()
        #         if (not (value_to_test in valid_values)):
        #             self.assertEqual(first=step, second=2)
        #             self.assertEqual(first=len(error_messages), second=1)
        #             self.assertListEqual(list1=error_messages, list2=["['A profile picture is required.']"])
        #             with self.assertRaises(ValidationError) as cm:
        #                 utils.validate_field(field_name=field_name, user=user)
        #             self.assertEqual(first=str(cm.exception.message), second='A profile picture is required.')
        #             self.assertListEqual(list1=list(cm.exception), list2=['A profile picture is required.'])
        #             validate_profile_and_activate_failures_count += 1
        #         else:
        #             self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
        #             utils.validate_field(field_name=field_name, user=user)
        #             ok_count += 1
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(valid_values), len(valid_values_to_assign) - len(valid_values), len(values_to_test) - len(valid_values_to_assign)))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(1, 1, 26))

    def test_validate_profile_and_activate_exception_on_profile_description(self):
        self.run_test_validate_profile_and_activate_exception(field_name='profile_description', expected_step=3, expected_error_message='Please write some text in this field.', expected_error_messages=["['Please write some text in this field.']"], expected_counts_tuple=(5, 2, 0))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # values_to_test = self._empty_values_to_test + self._valid_string_values_to_test
        # invalid_values = self._empty_values_to_test
        # for value_to_test in values_to_test:
        #     user.profile.profile_description = value_to_test
        #     user.save_user_and_profile()
        #     step, error_messages = user.profile.validate_profile_and_activate()
        #     if (value_to_test in invalid_values):
        #         self.assertEqual(first=step, second=3)
        #         self.assertEqual(first=len(error_messages), second=1)
        #         self.assertListEqual(list1=error_messages, list2=["['Please write some text in this field.']"])
        #         with self.assertRaises(ValidationError) as cm:
        #             utils.validate_field(field_name=field_name, user=user)
        #         self.assertEqual(first=str(cm.exception.message), second='Please write some text in this field.')
        #         self.assertListEqual(list1=list(cm.exception), list2=['Please write some text in this field.'])
        #         validate_profile_and_activate_failures_count += 1
        #     else:
        #         self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
        #         utils.validate_field(field_name=field_name, user=user)
        #         ok_count += 1
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(values_to_test)- len(invalid_values), len(invalid_values), 0))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(5, 2, 0))

    def test_validate_profile_and_activate_exception_on_city(self):
        self.run_test_validate_profile_and_activate_exception(field_name='city', expected_step=3, expected_error_message='Please write where you live.', expected_error_messages=["['Please write where you live.']"], expected_counts_tuple=(5, 2, 0))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # values_to_test = self._empty_values_to_test + self._valid_string_values_to_test
        # invalid_values = self._empty_values_to_test
        # for value_to_test in values_to_test:
        #     user.profile.city = value_to_test
        #     user.save_user_and_profile()
        #     step, error_messages = user.profile.validate_profile_and_activate()
        #     if (value_to_test in invalid_values):
        #         self.assertEqual(first=step, second=3)
        #         self.assertEqual(first=len(error_messages), second=1)
        #         self.assertListEqual(list1=error_messages, list2=["['Please write where you live.']"])
        #         with self.assertRaises(ValidationError) as cm:
        #             utils.validate_field(field_name=field_name, user=user)
        #         self.assertEqual(first=str(cm.exception.message), second='Please write where you live.')
        #         self.assertListEqual(list1=list(cm.exception), list2=['Please write where you live.'])
        #         validate_profile_and_activate_failures_count += 1
        #     else:
        #         self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
        #         utils.validate_field(field_name=field_name, user=user)
        #         ok_count += 1
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(values_to_test)- len(invalid_values), len(invalid_values), 0))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(5, 2, 0))

    def test_validate_profile_and_activate_exception_on_height(self):
        self.run_test_validate_profile_and_activate_exception(field_name='height', expected_step=3, expected_error_message='Height must be from 1 to 450 cm.', expected_error_messages=["['Height must be from 1 to 450 cm.']"], expected_counts_tuple=(450, 22, 5))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, settings.MAX_HEIGHT_ALLOWED + 10 + 1))
        # valid_values_to_save = self._none_list + [value for value in values_to_test if (isinstance(value, int))]
        # valid_values = SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES
        # # self.assert_valid_values_ok(values_to_test=values_to_test, valid_values_to_save=valid_values_to_save, valid_values=valid_values)
        # for value_to_test in values_to_test:
        #     # print(value_to_test)
        #     user.profile.height = value_to_test
        #     if (not (value_to_test in valid_values_to_save)):
        #         self.save_user_and_profile_and_assert_exceptions_for_integer(user=user, field_name='height', value_to_test=value_to_test, null=True)
        #         model_save_failures_count += 1
        #     else:
        #         user.save_user_and_profile()
        #         step, error_messages = user.profile.validate_profile_and_activate()
        #         if (not (value_to_test in valid_values)):
        #             self.assertEqual(first=step, second=3)
        #             self.assertEqual(first=len(error_messages), second=1)
        #             self.assertListEqual(list1=error_messages, list2=["['Height must be from 1 to 450 cm.']"])
        #             with self.assertRaises(ValidationError) as cm:
        #                 utils.validate_field(field_name=field_name, user=user)
        #             self.assertEqual(first=str(cm.exception.message), second='Height must be from 1 to 450 cm.')
        #             self.assertListEqual(list1=list(cm.exception), list2=['Height must be from 1 to 450 cm.'])
        #             validate_profile_and_activate_failures_count += 1
        #         else:
        #             self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
        #             utils.validate_field(field_name=field_name, user=user)
        #             ok_count += 1
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(valid_values), len(valid_values_to_save) - len(valid_values), len(values_to_test) - len(valid_values_to_save)))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(450, 22, 5))

    def test_validate_profile_and_activate_exception_on_children(self):
        self.run_test_validate_profile_and_activate_exception(field_name='children', expected_step=4, expected_error_message='Do you have children? How many?', expected_error_messages=["['Do you have children? How many?']"], expected_counts_tuple=(5, 2, 0))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # values_to_test = self._empty_values_to_test + self._valid_string_values_to_test
        # invalid_values = self._empty_values_to_test
        # for value_to_test in values_to_test:
        #     user.profile.children = value_to_test
        #     user.save_user_and_profile()
        #     step, error_messages = user.profile.validate_profile_and_activate()
        #     if (value_to_test in invalid_values):
        #         self.assertEqual(first=step, second=4)
        #         self.assertEqual(first=len(error_messages), second=1)
        #         self.assertListEqual(list1=error_messages, list2=["['Do you have children? How many?']"])
        #         with self.assertRaises(ValidationError) as cm:
        #             utils.validate_field(field_name=field_name, user=user)
        #         self.assertEqual(first=str(cm.exception.message), second='Do you have children? How many?')
        #         self.assertListEqual(list1=list(cm.exception), list2=['Do you have children? How many?'])
        #         validate_profile_and_activate_failures_count += 1
        #     else:
        #         self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
        #         utils.validate_field(field_name=field_name, user=user)
        #         ok_count += 1
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(values_to_test)- len(invalid_values), len(invalid_values), 0))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(5, 2, 0))

    def test_validate_profile_and_activate_exception_on_more_children(self):
        self.run_test_validate_profile_and_activate_exception(field_name='more_children', expected_step=4, expected_error_message='Do you want (more) children?', expected_error_messages=["['Do you want (more) children?']"], expected_counts_tuple=(5, 2, 0))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # values_to_test = self._empty_values_to_test + self._valid_string_values_to_test
        # invalid_values = self._empty_values_to_test
        # for value_to_test in values_to_test:
        #     user.profile.more_children = value_to_test
        #     user.save_user_and_profile()
        #     step, error_messages = user.profile.validate_profile_and_activate()
        #     if (value_to_test in invalid_values):
        #         self.assertEqual(first=step, second=4)
        #         self.assertEqual(first=len(error_messages), second=1)
        #         self.assertListEqual(list1=error_messages, list2=["['Do you want (more) children?']"])
        #         with self.assertRaises(ValidationError) as cm:
        #             utils.validate_field(field_name=field_name, user=user)
        #         self.assertEqual(first=str(cm.exception.message), second='Do you want (more) children?')
        #         self.assertListEqual(list1=list(cm.exception), list2=['Do you want (more) children?'])
        #         validate_profile_and_activate_failures_count += 1
        #     else:
        #         self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
        #         utils.validate_field(field_name=field_name, user=user)
        #         ok_count += 1
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(values_to_test)- len(invalid_values), len(invalid_values), 0))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(5, 2, 0))

    def test_validate_profile_and_activate_exception_on_diet(self):
        self.run_test_validate_profile_and_activate_exception(field_name='diet', expected_step=5, expected_error_message='Your diet is required.', expected_error_messages=["['Your diet is required.']"], expected_counts_tuple=(3, 1, 26))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, User.DIET_MAX_VALUE_PLUS_ONE + 10))
        # valid_values_to_save = [choice[0] for choice in User.DIET_CHOICES_WITH_DEFAULT]
        # valid_values = User.DIET_VALID_VALUES
        # self.assertEqual(first=valid_values_to_save, second=[User.DIET_UNKNOWN] + valid_values)
        # self.assertEqual(first=valid_values_to_save, second=[0] + valid_values)
        # # self.assert_valid_values_ok(values_to_test=values_to_test, valid_values_to_save=valid_values_to_save, valid_values=valid_values)
        # for value_to_test in values_to_test:
        #     # print(value_to_test)
        #     user.diet = value_to_test
        #     if (not (value_to_test in valid_values_to_save)):
        #         self.save_user_and_profile_and_assert_exceptions_for_integer(user=user, field_name='diet', value_to_test=value_to_test, null=False)
        #         model_save_failures_count += 1
        #     else:
        #         user.save_user_and_profile()
        #         step, error_messages = user.profile.validate_profile_and_activate()
        #         if (not (value_to_test in valid_values)):
        #             self.assertEqual(first=step, second=5)
        #             self.assertEqual(first=len(error_messages), second=1)
        #             self.assertListEqual(list1=error_messages, list2=["['Your diet is required.']"])
        #             with self.assertRaises(ValidationError) as cm:
        #                 utils.validate_field(field_name=field_name, user=user)
        #             self.assertEqual(first=str(cm.exception.message), second='Your diet is required.')
        #             self.assertListEqual(list1=list(cm.exception), list2=['Your diet is required.'])
        #             validate_profile_and_activate_failures_count += 1
        #         else:
        #             self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
        #             utils.validate_field(field_name=field_name, user=user)
        #             ok_count += 1
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(valid_values), len(valid_values_to_save) - len(valid_values), len(values_to_test) - len(valid_values_to_save)))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(3, 1, 26))

    def test_validate_profile_and_activate_exception_on_smoking_status(self):
        self.run_test_validate_profile_and_activate_exception(field_name='smoking_status', expected_step=5, expected_error_message='Your smoking status is required.', expected_error_messages=["['Your smoking status is required.']"], expected_counts_tuple=(3, 1, 26))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, SpeedyMatchSiteProfile.SMOKING_STATUS_MAX_VALUE_PLUS_ONE + 10))
        # valid_values_to_save = [choice[0] for choice in SpeedyMatchSiteProfile.SMOKING_STATUS_CHOICES_WITH_DEFAULT]
        # valid_values = SpeedyMatchSiteProfile.SMOKING_STATUS_VALID_VALUES
        # self.assertEqual(first=valid_values_to_save, second=[SpeedyMatchSiteProfile.SMOKING_STATUS_UNKNOWN] + valid_values)
        # self.assertEqual(first=valid_values_to_save, second=[0] + valid_values)
        # # self.assert_valid_values_ok(values_to_test=values_to_test, valid_values_to_save=valid_values_to_save, valid_values=valid_values)
        # for value_to_test in values_to_test:
        #     # print(value_to_test)
        #     user.profile.smoking_status = value_to_test
        #     if (not (value_to_test in valid_values_to_save)):
        #         self.save_user_and_profile_and_assert_exceptions_for_integer(user=user, field_name='smoking_status', value_to_test=value_to_test, null=False)
        #         model_save_failures_count += 1
        #     else:
        #         user.save_user_and_profile()
        #         step, error_messages = user.profile.validate_profile_and_activate()
        #         if (not (value_to_test in valid_values)):
        #             self.assertEqual(first=step, second=5)
        #             self.assertEqual(first=len(error_messages), second=1)
        #             self.assertListEqual(list1=error_messages, list2=["['Your smoking status is required.']"])
        #             with self.assertRaises(ValidationError) as cm:
        #                 utils.validate_field(field_name=field_name, user=user)
        #             self.assertEqual(first=str(cm.exception.message), second='Your smoking status is required.')
        #             self.assertListEqual(list1=list(cm.exception), list2=['Your smoking status is required.'])
        #             validate_profile_and_activate_failures_count += 1
        #         else:
        #             self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
        #             utils.validate_field(field_name=field_name, user=user)
        #             ok_count += 1
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(valid_values), len(valid_values_to_save) - len(valid_values), len(values_to_test) - len(valid_values_to_save)))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(3, 1, 26))

    def test_validate_profile_and_activate_exception_on_marital_status(self):
        self.run_test_validate_profile_and_activate_exception(field_name='marital_status', expected_step=6, expected_error_message='Your marital status is required.', expected_error_messages=["['Your marital status is required.']"], expected_counts_tuple=(8, 1, 26))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, SpeedyMatchSiteProfile.MARITAL_STATUS_MAX_VALUE_PLUS_ONE + 10))
        # valid_values_to_save = [choice[0] for choice in SpeedyMatchSiteProfile.MARITAL_STATUS_CHOICES_WITH_DEFAULT]
        # valid_values = SpeedyMatchSiteProfile.MARITAL_STATUS_VALID_VALUES
        # self.assertEqual(first=valid_values_to_save, second=[SpeedyMatchSiteProfile.MARITAL_STATUS_UNKNOWN] + valid_values)
        # self.assertEqual(first=valid_values_to_save, second=[0] + valid_values)
        # # self.assert_valid_values_ok(values_to_test=values_to_test, valid_values_to_save=valid_values_to_save, valid_values=valid_values)
        # for value_to_test in values_to_test:
        #     # print(value_to_test)
        #     user.profile.marital_status = value_to_test
        #     if (not (value_to_test in valid_values_to_save)):
        #         self.save_user_and_profile_and_assert_exceptions_for_integer(user=user, field_name='marital_status', value_to_test=value_to_test, null=False)
        #         model_save_failures_count += 1
        #     else:
        #         user.save_user_and_profile()
        #         step, error_messages = user.profile.validate_profile_and_activate()
        #         if (not (value_to_test in valid_values)):
        #             self.assertEqual(first=step, second=6)
        #             self.assertEqual(first=len(error_messages), second=1)
        #             self.assertListEqual(list1=error_messages, list2=["['Your marital status is required.']"])
        #             with self.assertRaises(ValidationError) as cm:
        #                 utils.validate_field(field_name=field_name, user=user)
        #             self.assertEqual(first=str(cm.exception.message), second='Your marital status is required.')
        #             self.assertListEqual(list1=list(cm.exception), list2=['Your marital status is required.'])
        #             validate_profile_and_activate_failures_count += 1
        #         else:
        #             self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
        #             utils.validate_field(field_name=field_name, user=user)
        #             ok_count += 1
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(valid_values), len(valid_values_to_save) - len(valid_values), len(values_to_test) - len(valid_values_to_save)))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(8, 1, 26))

    def test_validate_profile_and_activate_exception_on_gender_to_match(self):
        self.run_test_validate_profile_and_activate_exception(field_name='gender_to_match', expected_step=7, expected_error_message='Gender to match is required.', expected_error_messages=["['Gender to match is required.']"], expected_counts_tuple=(23, 153, 39))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # range_to_test = [User.GENDER_UNKNOWN] + User.GENDER_VALID_VALUES + [User.GENDER_MAX_VALUE_PLUS_ONE]
        # self.assertEqual(first=range_to_test, second=list(range(5)))
        # values_to_test = self._empty_values_to_test + [list(), tuple(), User.GENDER_VALID_VALUES + User.GENDER_VALID_VALUES, tuple(User.GENDER_VALID_VALUES + User.GENDER_VALID_VALUES), User.GENDER_VALID_VALUES[0:2] + User.GENDER_VALID_VALUES[0:1], User.GENDER_VALID_VALUES[0:2] + User.GENDER_VALID_VALUES[0:2]]
        # for n in range(10 + 1):
        #     if (n <= len(User.GENDER_VALID_VALUES)):
        #         product = list(itertools.product(*itertools.repeat(range_to_test, n)))
        #         values_to_test.extend([list(item) for item in product])
        #         if (n <= 1):
        #             values_to_test.extend(product)
        #         else:
        #             product = list(itertools.product(*itertools.repeat(User.GENDER_VALID_VALUES, n)))
        #             if (n == 2):
        #                 values_to_test.extend(product[:5])
        #             elif (n == 3):
        #                 values_to_test.extend(product[3:8])
        #     else:
        #         values_to_test.extend([([i] + [item for j in range(10) for item in User.GENDER_VALID_VALUES])[:n] for i in range_to_test])
        # # print(len(values_to_test))
        # # print(values_to_test)
        # valid_values_to_save = self._none_list + [gender_to_match for gender_to_match in values_to_test if (isinstance(gender_to_match, (list, tuple))) and (len(gender_to_match) <= len(User.GENDER_VALID_VALUES))]
        # # print(len(valid_values_to_save))
        # # print(valid_values_to_save)
        # valid_values = [gender_to_match for gender_to_match in values_to_test if (isinstance(gender_to_match, (list, tuple))) and (len(gender_to_match) > 0) and (len(gender_to_match) == len(set(gender_to_match))) and all(gender in User.GENDER_VALID_VALUES for gender in gender_to_match)]
        # # print(len(valid_values))
        # # print(valid_values)
        # for value in [[1], [2], [3], (1,), (2,), (3,), [1, 2], [1, 3], [2, 3], (1, 2), (1, 3), [1, 2, 3], (1, 2, 3)]:
        #     for val in [value, list(value)]:
        #         self.assertIn(member=val, container=values_to_test)
        #         self.assertIn(member=val, container=valid_values)
        # for value in [[], (), [1, 2, 3, 1, 2, 3], (1, 2, 3, 1, 2, 3), [1, 2, 1], [1, 2, 1, 2], [0], [4], (0,), (4,), [0, 1], [1, 2, 0], [1, 2, 4], [4, 1, 2, 3]]:
        #     for val in [value, list(value)]:
        #         self.assertIn(member=val, container=values_to_test)
        #         self.assertNotIn(member=val, container=valid_values)
        #         if (len(val) <= 3):
        #             self.assertIn(member=val, container=valid_values_to_save)
        #         else:
        #             self.assertNotIn(member=val, container=valid_values_to_save)
        # for value in valid_values:
        #     self.assertIn(member=value, container=values_to_test)
        # invalid_values = [value for value in values_to_test if (value not in valid_values)]
        # for value in invalid_values:
        #     self.assertIn(member=value, container=values_to_test)
        #     self.assertNotIn(member=value, container=valid_values)
        # for value in [[i, i] for i in User.GENDER_VALID_VALUES] + [[i, i, i] for i in User.GENDER_VALID_VALUES] + [[i, i, 1] for i in User.GENDER_VALID_VALUES]:
        #     self.assertIn(member=value, container=values_to_test)
        #     self.assertIn(member=value, container=invalid_values)
        # valid_sets = list()
        # for value in [set(gender_to_match) for gender_to_match in valid_values]:
        #     if (value not in valid_sets):
        #         valid_sets.append(value)
        # # print(valid_sets)
        # self.assertListEqual(list1=valid_sets, list2=[{1}, {2}, {3}, {1, 2}, {1, 3}, {2, 3}, {1, 2, 3}])
        # for value_to_test in values_to_test:
        #     # print(value_to_test)
        #     user.profile.gender_to_match = value_to_test
        #     if (not (value_to_test in valid_values_to_save)):
        #         if (isinstance(value_to_test, str)):
        #             with self.assertRaises(DataError) as cm:
        #                 user.save_user_and_profile()
        #             # print(str(cm.exception))
        #             self.assertIn(member='malformed array literal: ""', container=str(cm.exception))
        #         else:
        #             with self.assertRaises(ValidationError) as cm:
        #                 user.save_user_and_profile()
        #             # print(str(cm.exception))
        #             # print(dict(cm.exception))
        #             self.assertDictEqual(d1=dict(cm.exception), d2={'gender_to_match': ['List contains {} items, it should contain no more than 3.'.format(len(value_to_test))]})
        #         model_save_failures_count += 1
        #     else:
        #         user.save_user_and_profile()
        #         step, error_messages = user.profile.validate_profile_and_activate()
        #         if (not (value_to_test in valid_values)):
        #             self.assertEqual(first=step, second=7)
        #             self.assertEqual(first=len(error_messages), second=1)
        #             self.assertListEqual(list1=error_messages, list2=["['Gender to match is required.']"])
        #             with self.assertRaises(ValidationError) as cm:
        #                 utils.validate_field(field_name=field_name, user=user)
        #             self.assertEqual(first=str(cm.exception.message), second='Gender to match is required.')
        #             self.assertListEqual(list1=list(cm.exception), list2=['Gender to match is required.'])
        #             validate_profile_and_activate_failures_count += 1
        #         else:
        #             self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
        #             utils.validate_field(field_name=field_name, user=user)
        #             ok_count += 1
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(valid_values), len(valid_values_to_save) - len(valid_values), len(values_to_test) - len(valid_values_to_save)))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(23, 153, 39))

    def test_validate_profile_and_activate_exception_on_match_description(self):
        self.run_test_validate_profile_and_activate_exception(field_name='match_description', expected_step=7, expected_error_message='Please write some text in this field.', expected_error_messages=["['Please write some text in this field.']"], expected_counts_tuple=(5, 2, 0))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # values_to_test = self._empty_values_to_test + self._valid_string_values_to_test
        # invalid_values = self._empty_values_to_test
        # for value_to_test in values_to_test:
        #     user.profile.match_description = value_to_test
        #     user.save_user_and_profile()
        #     step, error_messages = user.profile.validate_profile_and_activate()
        #     if (value_to_test in invalid_values):
        #         self.assertEqual(first=step, second=7)
        #         self.assertEqual(first=len(error_messages), second=1)
        #         self.assertListEqual(list1=error_messages, list2=["['Please write some text in this field.']"])
        #         with self.assertRaises(ValidationError) as cm:
        #             utils.validate_field(field_name=field_name, user=user)
        #         self.assertEqual(first=str(cm.exception.message), second='Please write some text in this field.')
        #         self.assertListEqual(list1=list(cm.exception), list2=['Please write some text in this field.'])
        #         validate_profile_and_activate_failures_count += 1
        #     else:
        #         self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
        #         utils.validate_field(field_name=field_name, user=user)
        #         ok_count += 1
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(values_to_test)- len(invalid_values), len(invalid_values), 0))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(5, 2, 0))

    def test_validate_profile_and_activate_exception_on_min_age_match(self):
        self.run_test_validate_profile_and_activate_exception(field_name='min_age_match', expected_step=7, expected_error_message='Minimal age to match must be from 0 to 180 years.', expected_error_messages=["['Minimal age to match must be from 0 to 180 years.']"], expected_counts_tuple=(181, 20, 6))

    def test_validate_profile_and_activate_exception_on_max_age_match(self):
        self.run_test_validate_profile_and_activate_exception(field_name='max_age_match', expected_step=7, expected_error_message='Maximal age to match must be from 0 to 180 years.', expected_error_messages=["['Maximal age to match must be from 0 to 180 years.']"], expected_counts_tuple=(181, 20, 6))

    def test_validate_profile_and_activate_exception_on_min_max_age_to_match(self):
        self.run_test_validate_profile_and_activate_exception(field_name='min_max_age_to_match', expected_step=7, expected_error_message="Maximal age to match can't be less than minimal age to match.", expected_error_messages=['["Maximal age to match can\'t be less than minimal age to match."]'], expected_counts_tuple=(91, 90, 0))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # values_to_test = [(value, settings.MAX_AGE_ALLOWED - value) for value in SpeedyMatchSiteProfile.AGE_VALID_VALUES]
        # self.assertTrue(expr=all((len(value) == 2) for value in values_to_test))
        # valid_values_to_save = values_to_test
        # valid_values = [value for value in values_to_test if (value[0] <= value[1])]
        # invalid_values = [value for value in values_to_test if (value not in valid_values)]
        # # print(values_to_test)
        # # print(valid_values_to_save)
        # # print(valid_values)
        # # print(invalid_values)
        # # self.assert_valid_values_ok(values_to_test=values_to_test, valid_values=valid_values)
        # self.assertListEqual(list1=valid_values, list2=[(value, 180 - value) for value in range(0, 90 + 1)])
        # self.assertEqual(first=valid_values[0], second=(0, 180))
        # self.assertEqual(first=valid_values[-1], second=(90, 90))
        # self.assertListEqual(list1=invalid_values, list2=[(value, 180 - value) for value in range(91, 180 + 1)])
        # self.assertEqual(first=invalid_values[0], second=(91, 89))
        # self.assertEqual(first=invalid_values[-1], second=(180, 0))
        # for value_to_test in values_to_test:
        #     # print(value_to_test)
        #     user.profile.min_age_match = value_to_test[0]
        #     user.profile.max_age_match = value_to_test[1]
        #     if (not (value_to_test in valid_values_to_save)):
        #         raise Exception("problem with valid_values_to_save, value_to_test={}".format(value_to_test))
        #     else:
        #         user.save_user_and_profile()
        #         step, error_messages = user.profile.validate_profile_and_activate()
        #         if (not (value_to_test in valid_values)):
        #             self.assertEqual(first=step, second=7)
        #             # self.assertEqual(first=len(error_messages), second=1)
        #             self.assertEqual(first=len(error_messages), second=2)
        #             # print(error_messages)
        #             # ~~~~ TODO: We don't expect error messages to appear twice.
        #             self.assertListEqual(list1=error_messages, list2=['["Maximal age to match can\'t be less than minimal age to match."]', '["Maximal age to match can\'t be less than minimal age to match."]'])
        #             with self.assertRaises(ValidationError) as cm:
        #                 utils.validate_field(field_name=field_name, user=user)
        #             self.assertEqual(first=str(cm.exception.message), second="Maximal age to match can't be less than minimal age to match.")
        #             self.assertListEqual(list1=list(cm.exception), list2=["Maximal age to match can't be less than minimal age to match."])
        #             validate_profile_and_activate_failures_count += 1
        #         else:
        #             self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
        #             utils.validate_field(field_name=field_name, user=user)
        #             ok_count += 1
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(valid_values), len(valid_values_to_save) - len(valid_values), len(values_to_test) - len(valid_values_to_save)))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(91, 90, 0))

    def test_validate_profile_and_activate_exception_on_diet_match(self):
        self.run_test_validate_profile_and_activate_exception(field_name='diet_match', expected_step=-1, expected_error_message='', expected_error_messages=[], expected_counts_tuple=(-1, -1))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # values_to_test = self._empty_values_to_test
        # for value_to_test in values_to_test:
        #     user.profile.diet_match = value_to_test
        #     user.save_user_and_profile()
        #     step, error_messages = user.profile.validate_profile_and_activate()
        #     self.assertEqual(first=step, second=7)
        #     self.assertEqual(first=len(error_messages), second=1)
        #     self.assertListEqual(list1=error_messages, list2=[1])
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(-1, -1))

    def test_validate_profile_and_activate_exception_on_smoking_status_match(self):
        self.run_test_validate_profile_and_activate_exception(field_name='smoking_status_match', expected_step=-1, expected_error_message='', expected_error_messages=[], expected_counts_tuple=(-1, -1))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # values_to_test = self._empty_values_to_test
        # for value_to_test in values_to_test:
        #     user.profile.smoking_status_match = value_to_test
        #     user.save_user_and_profile()
        #     step, error_messages = user.profile.validate_profile_and_activate()
        #     self.assertEqual(first=step, second=7)
        #     self.assertEqual(first=len(error_messages), second=1)
        #     self.assertListEqual(list1=error_messages, list2=[1])
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(-1, -1))

    def test_validate_profile_and_activate_exception_on_marital_status_match(self):
        self.run_test_validate_profile_and_activate_exception(field_name='marital_status_match', expected_step=-1, expected_error_message='', expected_error_messages=[], expected_counts_tuple=(-1, -1))
        # user = ActiveUserFactory()
        # ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        # values_to_test = self._empty_values_to_test
        # for value_to_test in values_to_test:
        #     user.profile.marital_status_match = value_to_test
        #     user.save_user_and_profile()
        #     step, error_messages = user.profile.validate_profile_and_activate()
        #     self.assertEqual(first=step, second=7)
        #     self.assertEqual(first=len(error_messages), second=1)
        #     self.assertListEqual(list1=error_messages, list2=[1])
        # self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        # self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(-1, -1))


@only_on_speedy_match
class SpeedyMatchSiteProfileMatchTestCase(TestCase):
    def get_default_user_1(self):
        user = ActiveUserFactory(first_name='Walter', last_name='White', slug='walter', date_of_birth=datetime(year=1958, month=10, day=22), gender=User.GENDER_MALE, diet=User.DIET_VEGETARIAN)
        user.profile.smoking_status = SpeedyMatchSiteProfile.SMOKING_STATUS_NO
        user.profile.marital_status = SpeedyMatchSiteProfile.MARITAL_STATUS_SINGLE
        user.profile.min_age_match = 20
        user.profile.max_age_match = 180
        user.profile.gender_to_match = [User.GENDER_FEMALE]
        user.save_user_and_profile()
        return user

    def get_default_user_2(self):
        user = ActiveUserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse-pinkman', date_of_birth=datetime(year=1978, month=9, day=12), gender=User.GENDER_FEMALE, diet=User.DIET_VEGAN)
        user.profile.smoking_status = SpeedyMatchSiteProfile.SMOKING_STATUS_YES
        user.profile.marital_status = SpeedyMatchSiteProfile.MARITAL_STATUS_SINGLE
        user.profile.gender_to_match = [User.GENDER_MALE]
        user.save_user_and_profile()
        return user

    def test_user_doesnt_match_self(self):
        user = ActiveUserFactory()
        for gender in User.GENDER_VALID_VALUES:
            user.gender = gender
            user.profile.gender_to_match = User.GENDER_VALID_VALUES
            user.save_user_and_profile()
            rank = user.profile.get_matching_rank(other_profile=user.profile)
            self.assertEqual(first=rank, second=0)

    def test_gender_doesnt_match_profile(self):
        user_1 = self.get_default_user_1()
        user_1.profile.gender_to_match = [User.GENDER_MALE]
        user_2 = self.get_default_user_2()
        user_2.profile.gender_to_match = [User.GENDER_MALE]
        rank_1 = user_1.profile.get_matching_rank(other_profile=user_2.profile)
        self.assertEqual(first=rank_1, second=0)
        rank_2 = user_2.profile.get_matching_rank(other_profile=user_1.profile)
        self.assertEqual(first=rank_2, second=0)

    def test_gender_match_profile_different_gender(self):
        user_1 = self.get_default_user_1()
        user_2 = self.get_default_user_2()
        rank_1 = user_1.profile.get_matching_rank(other_profile=user_2.profile)
        self.assertEqual(first=rank_1, second=5)
        rank_2 = user_2.profile.get_matching_rank(other_profile=user_1.profile)
        self.assertEqual(first=rank_2, second=5)

    def test_gender_match_profile_same_gender(self):
        user_1 = self.get_default_user_1()
        user_1.profile.gender_to_match = [User.GENDER_MALE]
        user_2 = self.get_default_user_2()
        user_2.gender = User.GENDER_MALE
        user_2.profile.gender_to_match = [User.GENDER_MALE]
        user_1.save_user_and_profile()
        user_2.save_user_and_profile()
        rank_1 = user_1.profile.get_matching_rank(other_profile=user_2.profile)
        self.assertEqual(first=rank_1, second=5)
        rank_2 = user_2.profile.get_matching_rank(other_profile=user_1.profile)
        self.assertEqual(first=rank_2, second=5)

    def test_age_doesnt_match_profile(self):
        user_1 = self.get_default_user_1()
        user_1.profile.min_age_match = 20
        user_1.profile.max_age_match = 30
        user_2 = self.get_default_user_2()
        rank_1 = user_1.profile.get_matching_rank(other_profile=user_2.profile)
        self.assertEqual(first=rank_1, second=0)
        rank_2 = user_2.profile.get_matching_rank(other_profile=user_1.profile)
        self.assertEqual(first=rank_2, second=0)

    def test_smoking_status_doesnt_match_profile(self):
        user_1 = self.get_default_user_1()
        user_1.profile.smoking_status_match = {str(SpeedyMatchSiteProfile.SMOKING_STATUS_YES): 0, str(SpeedyMatchSiteProfile.SMOKING_STATUS_NO): 5, str(SpeedyMatchSiteProfile.SMOKING_STATUS_SOMETIMES): 0}
        user_2 = self.get_default_user_2()
        user_2.profile.smoking_status = SpeedyMatchSiteProfile.SMOKING_STATUS_YES
        user_1.save_user_and_profile()
        user_2.save_user_and_profile()
        rank_1 = user_1.profile.get_matching_rank(other_profile=user_2.profile)
        self.assertEqual(first=rank_1, second=0)
        rank_2 = user_2.profile.get_matching_rank(other_profile=user_1.profile)
        self.assertEqual(first=rank_2, second=0)

    def test_marital_status_match_profile(self):
        user_1 = self.get_default_user_1()
        user_2 = self.get_default_user_2()
        user_2.profile.smoking_status = SpeedyMatchSiteProfile.SMOKING_STATUS_YES
        user_2.profile.marital_status_match[str(SpeedyMatchSiteProfile.MARITAL_STATUS_MARRIED)] = SpeedyMatchSiteProfile.RANK_0
        user_1.save_user_and_profile()
        user_2.save_user_and_profile()
        rank_1 = user_1.profile.get_matching_rank(other_profile=user_2.profile)
        self.assertEqual(first=rank_1, second=5)
        rank_2 = user_2.profile.get_matching_rank(other_profile=user_1.profile)
        self.assertEqual(first=rank_2, second=5)

    def test_marital_status_doesnt_match_profile(self):
        user_1 = self.get_default_user_1()
        user_1.profile.marital_status = SpeedyMatchSiteProfile.MARITAL_STATUS_MARRIED
        user_2 = self.get_default_user_2()
        user_2.profile.smoking_status = SpeedyMatchSiteProfile.SMOKING_STATUS_YES
        user_2.profile.marital_status_match[str(SpeedyMatchSiteProfile.MARITAL_STATUS_MARRIED)] = SpeedyMatchSiteProfile.RANK_0
        user_1.save_user_and_profile()
        user_2.save_user_and_profile()
        rank_1 = user_1.profile.get_matching_rank(other_profile=user_2.profile)
        self.assertEqual(first=rank_1, second=0)
        rank_2 = user_2.profile.get_matching_rank(other_profile=user_1.profile)
        self.assertEqual(first=rank_2, second=0)

    def test_match_profile_rank_3(self):
        user_1 = self.get_default_user_1()
        user_1.profile.smoking_status_match = {str(SpeedyMatchSiteProfile.SMOKING_STATUS_YES): 3, str(SpeedyMatchSiteProfile.SMOKING_STATUS_NO): 5, str(SpeedyMatchSiteProfile.SMOKING_STATUS_SOMETIMES): 4}
        user_1.profile.diet_match = {str(User.DIET_VEGAN): 4, str(User.DIET_VEGETARIAN): 5, str(User.DIET_CARNIST): 0}
        user_2 = self.get_default_user_2()
        rank_1 = user_1.profile.get_matching_rank(other_profile=user_2.profile)
        self.assertEqual(first=rank_1, second=3)
        rank_2 = user_2.profile.get_matching_rank(other_profile=user_1.profile)
        self.assertEqual(first=rank_2, second=5)

    def test_match_profile_rank_4(self):
        user_1 = self.get_default_user_1()
        user_1.profile.diet_match = {str(User.DIET_VEGAN): 4, str(User.DIET_VEGETARIAN): 5, str(User.DIET_CARNIST): 0}
        user_2 = self.get_default_user_2()
        rank_1 = user_1.profile.get_matching_rank(other_profile=user_2.profile)
        self.assertEqual(first=rank_1, second=4)
        rank_2 = user_2.profile.get_matching_rank(other_profile=user_1.profile)
        self.assertEqual(first=rank_2, second=5)

    def test_match_profile_rank_1(self):
        user_1 = self.get_default_user_2()
        user_1.profile.smoking_status_match = {str(SpeedyMatchSiteProfile.SMOKING_STATUS_YES): 3, str(SpeedyMatchSiteProfile.SMOKING_STATUS_NO): 5, str(SpeedyMatchSiteProfile.SMOKING_STATUS_SOMETIMES): 4}
        user_1.profile.diet_match = {str(User.DIET_VEGAN): 4, str(User.DIET_VEGETARIAN): 5, str(User.DIET_CARNIST): 0}
        user_1.profile.marital_status_match[str(SpeedyMatchSiteProfile.MARITAL_STATUS_MARRIED)] = SpeedyMatchSiteProfile.RANK_1
        user_2 = self.get_default_user_1()
        user_2.profile.marital_status = SpeedyMatchSiteProfile.MARITAL_STATUS_MARRIED
        rank_1 = user_1.profile.get_matching_rank(other_profile=user_2.profile)
        self.assertEqual(first=rank_1, second=1)
        rank_2 = user_2.profile.get_matching_rank(other_profile=user_1.profile)
        self.assertEqual(first=rank_2, second=5)

