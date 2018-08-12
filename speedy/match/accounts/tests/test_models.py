from datetime import datetime

from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError

from speedy.core.base.test import TestCase, only_on_speedy_match
from ..models import SiteProfile as SpeedyMatchSiteProfile
from speedy.match.accounts import validators
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

    def assert_step_and_error_messages_ok(self, step, error_messages):
        self.assertEqual(first=step, second=len(settings.SITE_PROFILE_FORM_FIELDS))
        self.assertEqual(first=len(error_messages), second=0)
        self.assertListEqual(list1=error_messages, list2=[])

    def test_height_valid_values(self):
        self.assertEqual(first=SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES, second=range(settings.MIN_HEIGHT_ALLOWED, settings.MAX_HEIGHT_ALLOWED + 1))
        self.assertEqual(first=SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES, second=range(1, 450 + 1))

    def test_age_valid_values(self):
        self.assertEqual(first=SpeedyMatchSiteProfile.AGE_VALID_VALUES, second=range(settings.MIN_AGE_ALLOWED, settings.MAX_AGE_ALLOWED + 1))
        self.assertEqual(first=SpeedyMatchSiteProfile.AGE_VALID_VALUES, second=range(0, 180 + 1))

    def test_smoking_status_valid_values(self):
        self.assertListEqual(list1=SpeedyMatchSiteProfile.SMOKING_STATUS_VALID_VALUES, list2=list(range(SpeedyMatchSiteProfile.SMOKING_STATUS_UNKNOWN + 1, SpeedyMatchSiteProfile.SMOKING_STATUS_MAX_VALUE_PLUS_ONE)))
        self.assertListEqual(list1=SpeedyMatchSiteProfile.SMOKING_STATUS_VALID_VALUES, list2=list(range(1, 4)))

    def test_marital_status_valid_values(self):
        self.assertListEqual(list1=SpeedyMatchSiteProfile.MARITAL_STATUS_VALID_VALUES, list2=list(range(SpeedyMatchSiteProfile.MARITAL_STATUS_UNKNOWN + 1, SpeedyMatchSiteProfile.MARITAL_STATUS_MAX_VALUE_PLUS_ONE)))
        self.assertListEqual(list1=SpeedyMatchSiteProfile.MARITAL_STATUS_VALID_VALUES, list2=list(range(1, 9)))

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
        # ~~~~ TODO: assert all values.
        self.assertIn(member=user.profile.height, container=SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES)
        self.assertIn(member=user.diet, container=User.DIET_VALID_VALUES)
        validators.validate_height(height=user.profile.height)
        validators.validate_diet(diet=user.diet)

    def test_validate_profile_and_activate_exception_on_photo(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        valid_values = [UserImageFactory]
        values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + valid_values
        valid_values_for_save = self._none_list + valid_values
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            if value_to_test == UserImageFactory:
                user.photo = UserImageFactory(owner=user)
            else:
                user.photo = value_to_test
            print(value_to_test)
            if (not (value_to_test in valid_values_for_save)):
                user.save()
                user.profile.save()
                model_save_failures_count = model_save_failures_count + 1
            else:
                user.save()
                user.profile.save()
                step, error_messages = user.profile.validate_profile_and_activate()
                if (not (value_to_test in valid_values)):
                    self.assertEqual(first=step, second=2)
                    self.assertEqual(first=len(error_messages), second=1)
                    self.assertListEqual(list1=error_messages, list2=["['A profile picture is required.']"])
                    with self.assertRaises(ValidationError) as cm:
                        validators.validate_photo(photo=user.photo)
                    self.assertEqual(first=str(cm.exception.message), second='A profile picture is required.')
                    self.assertListEqual(list1=list(cm.exception), list2=['A profile picture is required.'])
                    validate_profile_and_activate_failures_count = validate_profile_and_activate_failures_count + 1
                else:
                    self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                    validators.validate_photo(photo=user.photo)
                    ok_count = ok_count + 1
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(1, 1))

    def test_validate_profile_and_activate_exception_on_profile_description(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test + self._valid_string_values_to_test
        invalid_values = self._empty_values_to_test
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.profile.profile_description = value_to_test
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            if (value_to_test in invalid_values):
                self.assertEqual(first=step, second=3)
                self.assertEqual(first=len(error_messages), second=1)
                self.assertListEqual(list1=error_messages, list2=["['Please write some text in this field.']"])
                with self.assertRaises(ValidationError) as cm:
                    validators.validate_profile_description(profile_description=user.profile_description)
                self.assertEqual(first=str(cm.exception.message), second='Please write some text in this field.')
                self.assertListEqual(list1=list(cm.exception), list2=['Please write some text in this field.'])
                validate_profile_and_activate_failures_count = validate_profile_and_activate_failures_count + 1
            else:
                self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                validators.validate_profile_description(profile_description=user.profile_description)
                ok_count = ok_count + 1
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(self._valid_string_values_to_test), len(self._empty_values_to_test)))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(5, 2))

    def test_validate_profile_and_activate_exception_on_city(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test + self._valid_string_values_to_test
        invalid_values = self._empty_values_to_test
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.profile.city = value_to_test
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            if (value_to_test in invalid_values):
                self.assertEqual(first=step, second=3)
                self.assertEqual(first=len(error_messages), second=1)
                self.assertListEqual(list1=error_messages, list2=["['Please write where you live.']"])
                with self.assertRaises(ValidationError) as cm:
                    validators.validate_city(city=user.profile.city)
                self.assertEqual(first=str(cm.exception.message), second='Please write where you live.')
                self.assertListEqual(list1=list(cm.exception), list2=['Please write where you live.'])
                validate_profile_and_activate_failures_count = validate_profile_and_activate_failures_count + 1
            else:
                self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                validators.validate_city(city=user.profile.city)
                ok_count = ok_count + 1
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(self._valid_string_values_to_test), len(self._empty_values_to_test)))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(5, 2))

    def test_validate_profile_and_activate_exception_on_height(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, settings.MAX_HEIGHT_ALLOWED + 10 + 1))
        valid_values_for_save = self._none_list + [value for value in values_to_test if (isinstance(value, int))]
        valid_values = SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES
        for value in valid_values:
            self.assertIn(member=value, container=values_to_test)
        for value_to_test in values_to_test:
            print(value_to_test)
            user = ActiveUserFactory()
            user.profile.height = value_to_test
            if (not (value_to_test in valid_values_for_save)):
                if (value_to_test in self._empty_string_list):
                    with self.assertRaises(ValueError) as cm:
                        with transaction.atomic():
                            user.save()
                            user.profile.save()
                    print(str(cm.exception))
                    self.assertEqual(first=str(cm.exception), second="invalid literal for int() with base 10: ''")
                else:
                    with self.assertRaises(ValidationError) as cm:
                        with transaction.atomic():
                            user.save()
                            user.profile.save()
                    print(str(cm.exception))
                    print(dict(cm.exception))
                    print(list(cm.exception))
                    self.assertDictEqual(d1=dict(cm.exception), d2={'height': ["'{}' value must be an integer.".format(value_to_test)]})
                model_save_failures_count = model_save_failures_count + 1
            else:
                user.save()
                user.profile.save()
                step, error_messages = user.profile.validate_profile_and_activate()
                if (not (value_to_test in valid_values)):
                    self.assertEqual(first=step, second=3)
                    self.assertEqual(first=len(error_messages), second=1)
                    self.assertListEqual(list1=error_messages, list2=["['Height must be from 1 to 450 cm.']"])
                    with self.assertRaises(ValidationError) as cm:
                        validators.validate_height(height=user.profile.height)
                    self.assertEqual(first=str(cm.exception.message), second='Height must be from 1 to 450 cm.')
                    self.assertListEqual(list1=list(cm.exception), list2=['Height must be from 1 to 450 cm.'])
                    validate_profile_and_activate_failures_count = validate_profile_and_activate_failures_count + 1
                else:
                    self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                    validators.validate_height(height=user.profile.height)
                    ok_count = ok_count + 1
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(valid_values), len(valid_values_for_save) - len(valid_values), len(values_to_test) - len(valid_values_for_save)))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(450, 22, 5))

    def test_validate_profile_and_activate_exception_on_children(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test + self._valid_string_values_to_test
        invalid_values = self._empty_values_to_test
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.profile.children = value_to_test
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            if (value_to_test in invalid_values):
                self.assertEqual(first=step, second=4)
                self.assertEqual(first=len(error_messages), second=1)
                self.assertListEqual(list1=error_messages, list2=["['Do you have children? How many?']"])
                with self.assertRaises(ValidationError) as cm:
                    validators.validate_children(children=user.profile.children)
                self.assertEqual(first=str(cm.exception.message), second='Do you have children? How many?')
                self.assertListEqual(list1=list(cm.exception), list2=['Do you have children? How many?'])
                validate_profile_and_activate_failures_count = validate_profile_and_activate_failures_count + 1
            else:
                self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                validators.validate_children(children=user.profile.children)
                ok_count = ok_count + 1
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(self._valid_string_values_to_test), len(self._empty_values_to_test)))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(5, 2))

    def test_validate_profile_and_activate_exception_on_more_children(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test + self._valid_string_values_to_test
        invalid_values = self._empty_values_to_test
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.profile.more_children = value_to_test
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            if (value_to_test in invalid_values):
                self.assertEqual(first=step, second=4)
                self.assertEqual(first=len(error_messages), second=1)
                self.assertListEqual(list1=error_messages, list2=["['Do you want (more) children?']"])
                with self.assertRaises(ValidationError) as cm:
                    validators.validate_more_children(more_children=user.profile.more_children)
                self.assertEqual(first=str(cm.exception.message), second='Do you want (more) children?')
                self.assertListEqual(list1=list(cm.exception), list2=['Do you want (more) children?'])
                validate_profile_and_activate_failures_count = validate_profile_and_activate_failures_count + 1
            else:
                self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                validators.validate_more_children(more_children=user.profile.more_children)
                ok_count = ok_count + 1
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(self._valid_string_values_to_test), len(self._empty_values_to_test)))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(5, 2))

    def test_validate_profile_and_activate_exception_on_diet(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, User.DIET_MAX_VALUE_PLUS_ONE + 10))
        valid_values = User.DIET_VALID_VALUES
        for value in valid_values:
            self.assertIn(member=value, container=values_to_test)
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.diet = value_to_test
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            self.assertEqual(first=step, second=7)
            self.assertEqual(first=len(error_messages), second=1)
            self.assertListEqual(list1=error_messages, list2=[1])
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(-1, -1))

    def test_validate_profile_and_activate_exception_on_smoking_status(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, SpeedyMatchSiteProfile.SMOKING_STATUS_MAX_VALUE_PLUS_ONE + 10))
        valid_values = SpeedyMatchSiteProfile.SMOKING_STATUS_VALID_VALUES
        for value in valid_values:
            self.assertIn(member=value, container=values_to_test)
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.profile.smoking_status = value_to_test
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            self.assertEqual(first=step, second=7)
            self.assertEqual(first=len(error_messages), second=1)
            self.assertListEqual(list1=error_messages, list2=[1])
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(-1, -1))

    def test_validate_profile_and_activate_exception_on_marital_status(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, SpeedyMatchSiteProfile.MARITAL_STATUS_MAX_VALUE_PLUS_ONE + 10))
        valid_values = SpeedyMatchSiteProfile.MARITAL_STATUS_VALID_VALUES
        for value in valid_values:
            self.assertIn(member=value, container=values_to_test)
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.profile.marital_status = value_to_test
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            self.assertEqual(first=step, second=7)
            self.assertEqual(first=len(error_messages), second=1)
            self.assertListEqual(list1=error_messages, list2=[1])
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(-1, -1))

    def test_validate_profile_and_activate_exception_on_gender_to_match(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.profile.gender_to_match = value_to_test
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            self.assertEqual(first=step, second=7)
            self.assertEqual(first=len(error_messages), second=1)
            self.assertListEqual(list1=error_messages, list2=["['Gender to match is required.']"])
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(-1, -1))

    def test_validate_profile_and_activate_exception_on_match_description(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test + self._valid_string_values_to_test
        invalid_values = self._empty_values_to_test
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.profile.match_description = value_to_test
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            if (value_to_test in invalid_values):
                self.assertEqual(first=step, second=7)
                self.assertEqual(first=len(error_messages), second=1)
                self.assertListEqual(list1=error_messages, list2=["['Please write some text in this field.']"])
                with self.assertRaises(ValidationError) as cm:
                    validators.validate_match_description(match_description=user.profile.match_description)
                self.assertEqual(first=str(cm.exception.message), second='Please write some text in this field.')
                self.assertListEqual(list1=list(cm.exception), list2=['Please write some text in this field.'])
                validate_profile_and_activate_failures_count = validate_profile_and_activate_failures_count + 1
            else:
                self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                validators.validate_match_description(match_description=user.profile.match_description)
                ok_count = ok_count + 1
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(self._valid_string_values_to_test), len(self._empty_values_to_test)))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(5, 2))

    def test_validate_profile_and_activate_exception_on_min_age_match(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, settings.MAX_AGE_ALLOWED + 1 + 10))
        valid_values = SpeedyMatchSiteProfile.AGE_VALID_VALUES
        for value in valid_values:
            self.assertIn(member=value, container=values_to_test)
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.profile.min_age_match = value_to_test
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            if (value_to_test not in valid_values):
                self.assertEqual(first=step, second=7)
                self.assertEqual(first=len(error_messages), second=1)
                self.assertListEqual(list1=error_messages, list2=[1])
                with self.assertRaises(ValidationError) as cm:
                    validators.validate_min_age_match(min_age_match=user.profile.min_age_match)
                self.assertEqual(first=str(cm.exception.message), second='Please write some text in this field.')
                self.assertListEqual(list1=list(cm.exception), list2=['Please write some text in this field.'])
                validate_profile_and_activate_failures_count = validate_profile_and_activate_failures_count + 1
            else:
                self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                validators.validate_min_age_match(min_age_match=user.profile.min_age_match)
                ok_count = ok_count + 1
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(valid_values), len(values_to_test) - len(valid_values)))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(181, 20))

    def test_validate_profile_and_activate_exception_on_max_age_match(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test + self._non_int_string_values_to_test + list(range(-10, settings.MAX_AGE_ALLOWED + 1 + 10))
        valid_values = SpeedyMatchSiteProfile.AGE_VALID_VALUES
        for value in valid_values:
            self.assertIn(member=value, container=values_to_test)
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.profile.max_age_match = value_to_test
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            if (value_to_test not in valid_values):
                self.assertEqual(first=step, second=7)
                self.assertEqual(first=len(error_messages), second=4)
                self.assertListEqual(list1=error_messages, list2=[1])
                with self.assertRaises(ValidationError) as cm:
                    validators.validate_max_age_match(max_age_match=user.profile.max_age_match)
                self.assertEqual(first=str(cm.exception.message), second='Please write some text in this field.')
                self.assertListEqual(list1=list(cm.exception), list2=['Please write some text in this field.'])
                validate_profile_and_activate_failures_count = validate_profile_and_activate_failures_count + 1
            else:
                self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                validators.validate_max_age_match(max_age_match=user.profile.max_age_match)
                ok_count = ok_count + 1
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(valid_values), len(values_to_test) - len(valid_values)))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(181, 20))

    def test_validate_profile_and_activate_exception_on_min_max_age_to_match(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = [(i, i) for i in self._empty_values_to_test] + [(i, settings.MAX_AGE_ALLOWED + 1 - i) for i in list(range(-10, settings.MAX_AGE_ALLOWED + 1 + 10))]
        valid_values = [value for value in values_to_test if ((value[0] in SpeedyMatchSiteProfile.AGE_VALID_VALUES) and (value[1] in SpeedyMatchSiteProfile.AGE_VALID_VALUES) and (value[0] not in self._empty_values_to_test) and (value[1] not in self._empty_values_to_test) and (value[0] <= value[1]))]
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.profile.min_age_match = value_to_test[0]
            user.profile.max_age_match = value_to_test[1]
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            if (value_to_test not in valid_values):
                self.assertEqual(first=step, second=7)
                self.assertEqual(first=len(error_messages), second=1)
                self.assertListEqual(list1=error_messages, list2=[1])
                with self.assertRaises(ValidationError) as cm:
                    validators.validate_min_max_age_to_match(min_age_match=user.profile.min_age_match, max_age_match=user.profile.max_age_match)
                self.assertEqual(first=str(cm.exception.message), second='Please write some text in this field.')
                self.assertListEqual(list1=list(cm.exception), list2=['Please write some text in this field.'])
                validate_profile_and_activate_failures_count = validate_profile_and_activate_failures_count + 1
            else:
                self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                validators.validate_min_max_age_to_match(min_age_match=user.profile.min_age_match, max_age_match=user.profile.max_age_match)
                ok_count = ok_count + 1
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(len(valid_values), len(values_to_test) - len(valid_values)))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(181, 20))

    def test_validate_profile_and_activate_exception_on_diet_match(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.profile.diet_match = value_to_test
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            self.assertEqual(first=step, second=7)
            self.assertEqual(first=len(error_messages), second=1)
            self.assertListEqual(list1=error_messages, list2=[1])
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(-1, -1))

    def test_validate_profile_and_activate_exception_on_smoking_status_match(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.profile.smoking_status_match = value_to_test
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            self.assertEqual(first=step, second=7)
            self.assertEqual(first=len(error_messages), second=1)
            self.assertListEqual(list1=error_messages, list2=[1])
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(-1, -1))

    def test_validate_profile_and_activate_exception_on_marital_status_match(self):
        ok_count, validate_profile_and_activate_failures_count, model_save_failures_count = 0, 0, 0
        values_to_test = self._empty_values_to_test
        for value_to_test in values_to_test:
            user = ActiveUserFactory()
            user.profile.marital_status_match = value_to_test
            user.save()
            user.profile.save()
            step, error_messages = user.profile.validate_profile_and_activate()
            self.assertEqual(first=step, second=7)
            self.assertEqual(first=len(error_messages), second=1)
            self.assertListEqual(list1=error_messages, list2=[1])
        self.assertEqual(first=ok_count + validate_profile_and_activate_failures_count + model_save_failures_count, second=len(values_to_test))
        self.assertTupleEqual(tuple1=(ok_count, validate_profile_and_activate_failures_count, model_save_failures_count), tuple2=(-1, -1))


@only_on_speedy_match
class SpeedyMatchSiteProfileMatchTestCase(TestCase):
    def get_default_user_1(self):
        user = ActiveUserFactory(first_name='Walter', last_name='White', slug='walter', date_of_birth=datetime(year=1958, month=10, day=22), gender=User.GENDER_MALE, diet=User.DIET_VEGETARIAN)
        user.profile.smoking_status = SpeedyMatchSiteProfile.SMOKING_STATUS_NO
        user.profile.marital_status = SpeedyMatchSiteProfile.MARITAL_STATUS_SINGLE
        user.profile.min_age_match = 20
        user.profile.max_age_match = 180
        user.profile.gender_to_match = [User.GENDER_FEMALE]
        user.save()
        user.profile.save()
        return user

    def get_default_user_2(self):
        user = ActiveUserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse-pinkman', date_of_birth=datetime(year=1978, month=9, day=12), gender=User.GENDER_FEMALE, diet=User.DIET_VEGAN)
        user.profile.smoking_status = SpeedyMatchSiteProfile.SMOKING_STATUS_YES
        user.profile.marital_status = SpeedyMatchSiteProfile.MARITAL_STATUS_SINGLE
        user.profile.gender_to_match = [User.GENDER_MALE]
        user.save()
        user.profile.save()
        return user

    def test_gender_doesnt_match_profile(self):
        user_1 = self.get_default_user_1()
        user_1.profile.gender_to_match = [User.GENDER_MALE]
        user_2 = self.get_default_user_2()
        user_2.profile.gender_to_match = [User.GENDER_MALE]
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(first=rank_1, second=0)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(first=rank_2, second=0)

    def test_gender_match_profile_different_gender(self):
        user_1 = self.get_default_user_1()
        user_2 = self.get_default_user_2()
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(first=rank_1, second=5)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(first=rank_2, second=5)

    def test_gender_match_profile_same_gender(self):
        user_1 = self.get_default_user_1()
        user_1.profile.gender_to_match = [User.GENDER_MALE]
        user_2 = self.get_default_user_2()
        user_2.gender = User.GENDER_MALE
        user_2.profile.gender_to_match = [User.GENDER_MALE]
        user_2.save()
        user_2.profile.save()
        user_2._profile = user_2.get_profile()
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(first=rank_1, second=5)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(first=rank_2, second=5)

    def test_age_doesnt_match_profile(self):
        user_1 = self.get_default_user_1()
        user_1.profile.min_age_match = 20
        user_1.profile.max_age_match = 30
        user_2 = self.get_default_user_2()
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(first=rank_1, second=0)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(first=rank_2, second=0)

    def test_smoking_status_doesnt_match_profile(self):
        user_1 = self.get_default_user_1()
        user_1.profile.smoking_status_match = {str(SpeedyMatchSiteProfile.SMOKING_STATUS_YES): 0, str(SpeedyMatchSiteProfile.SMOKING_STATUS_NO): 5, str(SpeedyMatchSiteProfile.SMOKING_STATUS_SOMETIMES): 0}
        user_1.profile.save()
        user_2 = self.get_default_user_2()
        user_2.profile.smoking_status = SpeedyMatchSiteProfile.SMOKING_STATUS_YES
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(first=rank_1, second=0)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(first=rank_2, second=0)

    def test_marital_status_match_profile(self):
        user_1 = self.get_default_user_1()
        user_1.profile.save()
        user_2 = self.get_default_user_2()
        user_2.profile.smoking_status = SpeedyMatchSiteProfile.SMOKING_STATUS_YES
        user_2.profile.marital_status_match[str(SpeedyMatchSiteProfile.MARITAL_STATUS_MARRIED)] = SpeedyMatchSiteProfile.RANK_0
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(first=rank_1, second=5)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(first=rank_2, second=5)

    def test_marital_status_doesnt_match_profile(self):
        user_1 = self.get_default_user_1()
        user_1.profile.marital_status = SpeedyMatchSiteProfile.MARITAL_STATUS_MARRIED
        user_1.profile.save()
        user_2 = self.get_default_user_2()
        user_2.profile.smoking_status = SpeedyMatchSiteProfile.SMOKING_STATUS_YES
        user_2.profile.marital_status_match[str(SpeedyMatchSiteProfile.MARITAL_STATUS_MARRIED)] = SpeedyMatchSiteProfile.RANK_0
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(first=rank_1, second=0)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(first=rank_2, second=0)

    def test_match_profile_rank_3(self):
        user_1 = self.get_default_user_1()
        user_1.profile.smoking_status_match = {str(SpeedyMatchSiteProfile.SMOKING_STATUS_YES): 3, str(SpeedyMatchSiteProfile.SMOKING_STATUS_NO): 5, str(SpeedyMatchSiteProfile.SMOKING_STATUS_SOMETIMES): 4}
        user_1.profile.diet_match = {str(User.DIET_VEGAN): 4, str(User.DIET_VEGETARIAN): 5, str(User.DIET_CARNIST): 0}
        user_2 = self.get_default_user_2()
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(first=rank_1, second=3)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(first=rank_2, second=5)

    def test_match_profile_rank_4(self):
        user_1 = self.get_default_user_1()
        user_1.profile.diet_match = {str(User.DIET_VEGAN): 4, str(User.DIET_VEGETARIAN): 5, str(User.DIET_CARNIST): 0}
        user_2 = self.get_default_user_2()
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(first=rank_1, second=4)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(first=rank_2, second=5)

    def test_match_profile_rank_1(self):
        user_1 = self.get_default_user_2()
        user_1.profile.smoking_status_match = {str(SpeedyMatchSiteProfile.SMOKING_STATUS_YES): 3, str(SpeedyMatchSiteProfile.SMOKING_STATUS_NO): 5, str(SpeedyMatchSiteProfile.SMOKING_STATUS_SOMETIMES): 4}
        user_1.profile.diet_match = {str(User.DIET_VEGAN): 4, str(User.DIET_VEGETARIAN): 5, str(User.DIET_CARNIST): 0}
        user_1.profile.marital_status_match[str(SpeedyMatchSiteProfile.MARITAL_STATUS_MARRIED)] = SpeedyMatchSiteProfile.RANK_1
        user_2 = self.get_default_user_1()
        user_2.profile.marital_status = SpeedyMatchSiteProfile.MARITAL_STATUS_MARRIED
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(first=rank_1, second=1)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(first=rank_2, second=5)

