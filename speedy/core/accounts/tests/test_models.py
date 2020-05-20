from datetime import datetime

from django.conf import settings as django_settings
from django.test import override_settings
from django.core.exceptions import ValidationError

from speedy.core.base.test import tests_settings
from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_sites_with_login
from speedy.core.base.test.utils import get_django_settings_class_with_override_settings
from speedy.core.accounts.test.mixins import SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin
from speedy.core.accounts.models import Entity, User, UserEmailAddress

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.utils import get_random_user_password
    from speedy.core.accounts.test.user_factories import DefaultUserFactory, InactiveUserFactory, ActiveUserFactory
    from speedy.core.accounts.test.user_email_address_factories import UserEmailAddressFactory


class EntityTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin):
    def create_one_entity(self):
        entity = Entity(slug='zzzzzz', username='zzzzzz')
        entity.save()
        self.assertEqual(first=entity.username, second='zzzzzz')
        self.assertEqual(first=entity.slug, second='zzzzzz')
        self.assertEqual(first=len(entity.id), second=15)
        return entity

    def run_test_all_slugs_to_test_list(self, test_settings):
        ok_count, model_save_failures_count = 0, 0
        for slug_dict in tests_settings.SLUGS_TO_TEST_LIST:
            entity = Entity(slug=slug_dict["slug"])
            if (slug_dict["slug_length"] >= Entity.settings.MIN_SLUG_LENGTH):
                entity.save()
                ok_count += 1
            else:
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, slug_value_length=slug_dict["slug_length"]))
                model_save_failures_count += 1
        counts_tuple = (ok_count, model_save_failures_count)
        self.assert_models_count(
            entity_count=ok_count,
            user_count=0,
            user_email_address_count=0,
            confirmed_email_address_count=0,
            unconfirmed_email_address_count=0,
        )
        self.assertEqual(first=sum(counts_tuple), second=len(tests_settings.SLUGS_TO_TEST_LIST))
        self.assertTupleEqual(tuple1=counts_tuple, tuple2=test_settings["expected_counts_tuple"])

    def test_model_settings(self):
        self.assertEqual(first=Entity.settings.MIN_USERNAME_LENGTH, second=6)
        self.assertEqual(first=Entity.settings.MAX_USERNAME_LENGTH, second=120)
        self.assertEqual(first=Entity.settings.MIN_SLUG_LENGTH, second=6)
        self.assertEqual(first=Entity.settings.MAX_SLUG_LENGTH, second=200)

    def test_cannot_create_entity_without_a_slug(self):
        entity = Entity()
        with self.assertRaises(ValidationError) as cm:
            entity.save()
        self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=Entity, slug_fail=True, username_fail=True))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._entity_slug_and_username_min_length_fail_errors_dict_by_value_length(value_length=0))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_max_length_fail_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_max_length_fail_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True))

    def test_cannot_create_entities_with_bulk_create(self):
        entity_1 = Entity(slug='zzzzzz')
        entity_2 = Entity(slug='ZZZ-ZZZ')
        with self.assertRaises(NotImplementedError) as cm:
            Entity.objects.bulk_create([entity_1, entity_2])
        self.assertEqual(first=str(cm.exception), second="bulk_create is not implemented.")

    def test_cannot_delete_entities_with_queryset_delete(self):
        with self.assertRaises(NotImplementedError) as cm:
            Entity.objects.delete()
        self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
        with self.assertRaises(NotImplementedError) as cm:
            Entity.objects.all().delete()
        self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
        with self.assertRaises(NotImplementedError) as cm:
            Entity.objects.filter(pk=1).delete()
        self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
        with self.assertRaises(NotImplementedError) as cm:
            Entity.objects.all().exclude(pk=2).delete()
        self.assertEqual(first=str(cm.exception), second="delete is not implemented.")

    def test_cannot_create_entity_with_an_invalid_id(self):
        old_entity = self.create_one_entity()
        old_entity_id = old_entity.id
        old_entity_id_as_list = list(old_entity_id)
        old_entity_id_as_list[0] = '0'
        new_entity_id = ''.join(old_entity_id_as_list)
        self.assertEqual(first=new_entity_id, second='0{}'.format(old_entity_id[1:]))
        self.assertNotEqual(first=new_entity_id, second=old_entity_id)
        new_entity = Entity(slug='yyyyyy', username='yyyyyy', id=new_entity_id)
        self.assertEqual(first=new_entity.id, second=new_entity_id)
        self.assertNotEqual(first=new_entity.id, second=old_entity.id)
        self.assertEqual(first=len(new_entity.id), second=15)
        with self.assertRaises(AssertionError) as cm:
            self.assertIn(member=new_entity.id[0], container=[str(i) for i in range(1, 10)])
        self.assertEqual(first=str(cm.exception), second="'0' not found in ['1', '2', '3', '4', '5', '6', '7', '8', '9']")
        self.assertNotIn(member=new_entity.id[0], container=[str(i) for i in range(1, 10)])
        for i in range(1, 15):
            self.assertIn(member=new_entity.id[i], container=[str(i) for i in range(10)])
        with self.assertRaises(ValidationError) as cm:
            new_entity.save()
        self.assertDictEqual(d1=dict(cm.exception), d2=self._id_contains_illegal_characters_errors_dict())

    def test_cannot_create_entity_with_reserved_username(self):
        entity = Entity(slug='webmaster')
        with self.assertRaises(ValidationError) as cm:
            entity.save()
        self.assertDictEqual(d1=dict(cm.exception), d2=self._this_username_is_already_taken_errors_dict(slug_fail=True, username_fail=True))

    def test_cannot_create_entity_with_reserved_and_too_short_username(self):
        entity = Entity(slug='mail')
        with self.assertRaises(ValidationError) as cm:
            entity.save()
        self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=4))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._this_username_is_already_taken_errors_dict(slug_fail=True, username_fail=True))

    def test_cannot_create_entity_with_existing_username(self):
        entity_1 = Entity(slug='zzzzzz')
        entity_1.save()
        entity_2 = Entity(slug='ZZZ-ZZZ')
        with self.assertRaises(ValidationError) as cm:
            entity_2.save()
        self.assertDictEqual(d1=dict(cm.exception), d2=self._this_username_is_already_taken_errors_dict(slug_fail=True, username_fail=True))

    def test_automatic_creation_of_username_and_id(self):
        entity = Entity(slug='zzzzzz')
        entity.save()
        self.assertEqual(first=entity.username, second='zzzzzz')
        self.assertEqual(first=entity.slug, second='zzzzzz')
        self.assertEqual(first=len(entity.id), second=15)

    def test_automatic_creation_of_id(self):
        entity = Entity(slug='zzzzzz', username='zzzzzz')
        entity.save()
        self.assertEqual(first=entity.username, second='zzzzzz')
        self.assertEqual(first=entity.slug, second='zzzzzz')
        self.assertEqual(first=len(entity.id), second=15)
        self.assertGreaterEqual(a=int(entity.id), b=10 ** 14)
        self.assertLess(a=int(entity.id), b=10 ** 15)
        self.assertIn(member=entity.id[0], container=[str(i) for i in range(1, 10)])
        for i in range(1, 15):
            self.assertIn(member=entity.id[i], container=[str(i) for i in range(10)])

    def test_create_2_entities_and_assert_different_ids(self):
        entity_1 = Entity(slug='zzzzzz1')
        entity_1.save()
        entity_2 = Entity(slug='ZZZ-ZZZ-2')
        entity_2.save()
        self.assertEqual(first=entity_1.username, second='zzzzzz1')
        self.assertEqual(first=entity_2.username, second='zzzzzz2')
        self.assertNotEqual(first=entity_1.username, second=entity_2.username)
        self.assertEqual(first=entity_1.slug, second='zzzzzz1')
        self.assertEqual(first=entity_2.slug, second='zzz-zzz-2')
        self.assertNotEqual(first=entity_1.slug, second=entity_2.slug)
        self.assertEqual(first=len(entity_1.id), second=15)
        self.assertEqual(first=len(entity_2.id), second=15)
        self.assertNotEqual(first=entity_1.id, second=entity_2.id)

    def test_slug_and_username_min_length_fail(self):
        entity = Entity(slug='a' * 5, username='a' * 5)
        with self.assertRaises(ValidationError) as cm:
            entity.save()
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._entity_slug_and_username_min_length_fail_errors_dict_by_value_length(value_length=5))
        self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=5))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=5))

    def test_slug_and_username_min_length_ok_1(self):
        entity = Entity(slug='a' * 6, username='a' * 6)
        entity.save()

    def test_slug_and_username_min_length_ok_2(self):
        # print("test_slug_and_username_min_length_ok_2: django_settings.ENTITY_SETTINGS.MIN_SLUG_LENGTH", django_settings.ENTITY_SETTINGS.MIN_SLUG_LENGTH)####
        # print("test_slug_and_username_min_length_ok_2: django_settings.ENTITY_SETTINGS.MAX_SLUG_LENGTH", django_settings.ENTITY_SETTINGS.MAX_SLUG_LENGTH)####
        # print("test_slug_and_username_min_length_ok_2: Entity.settings.MIN_SLUG_LENGTH", Entity.settings.MIN_SLUG_LENGTH)####
        # print("test_slug_and_username_min_length_ok_2: Entity.settings.MAX_SLUG_LENGTH", Entity.settings.MAX_SLUG_LENGTH)####
        self.assertEqual(first=Entity.settings.MIN_SLUG_LENGTH, second=6)
        test_settings = {
            "expected_counts_tuple": (8, 0),
        }
        self.run_test_all_slugs_to_test_list(test_settings=test_settings)

    @override_settings(ENTITY_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.ENTITY_SETTINGS, MIN_SLUG_LENGTH=tests_settings.OVERRIDE_ENTITY_SETTINGS.MIN_SLUG_LENGTH))
    def test_slug_min_length_fail_username_min_length_ok(self):
        self.assertEqual(first=Entity.settings.MIN_SLUG_LENGTH, second=60)
        test_settings = {
            "expected_counts_tuple": (4, 4),
        }
        self.run_test_all_slugs_to_test_list(test_settings=test_settings)

    def test_slug_and_username_max_length_fail(self):
        entity = Entity(slug='a' * 201, username='z' * 201)
        with self.assertRaises(ValidationError) as cm:
            entity.save()
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._entity_slug_and_username_max_length_fail_errors_dict_by_value_length(value_length=201))
        self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=201))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=201))

    def test_slug_max_length_ok_username_max_length_fail_1(self):
        entity = Entity(slug='b' * 200, username='b' * 200)
        with self.assertRaises(ValidationError) as cm:
            entity.save()
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._entity_username_max_length_fail_errors_dict_by_value_length(value_length=200))
        self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=200))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=200))

    def test_slug_max_length_ok_username_max_length_fail_2(self):
        entity = Entity(slug='b' * 121, username='b' * 121)
        with self.assertRaises(ValidationError) as cm:
            entity.save()
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._entity_username_max_length_fail_errors_dict_by_value_length(value_length=121))
        self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=121))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=121))

    def test_slug_max_length_fail_username_max_length_ok_with_username(self):
        entity = Entity(slug='a-' * 120, username='a' * 120)
        with self.assertRaises(ValidationError) as cm:
            entity.save()
        self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, slug_value_length=239))

    def test_slug_max_length_fail_username_max_length_ok_without_username(self):
        entity = Entity(slug='a-' * 120)
        with self.assertRaises(ValidationError) as cm:
            entity.save()
        self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, slug_value_length=239))

    def test_slug_and_username_max_length_ok(self):
        entity = Entity(slug='a' * 120 + '-' * 80, username='a' * 120)
        entity.save()

    def test_star2000_is_valid_username(self):
        entity = Entity(slug='star2000', username='star2000')
        entity.save()

    def test_come2us_is_valid_username(self):
        entity = Entity(slug='come2us', username='come2us')
        entity.save()

    def test_000000_is_invalid_username(self):
        entity = Entity(slug='0' * 6, username='0' * 6)
        with self.assertRaises(ValidationError) as cm:
            entity.save()
        self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=Entity, slug_fail=True, username_fail=True))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))

    def test_0test1_is_invalid_username(self):
        entity = Entity(slug='0-test-1', username='0test1')
        with self.assertRaises(ValidationError) as cm:
            entity.save()
        self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=Entity, slug_fail=True, username_fail=True))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))

    def test_slug_and_username_dont_match_but_valid(self):
        entity = Entity(slug='star2001', username='star2000')
        with self.assertRaises(ValidationError) as cm:
            entity.save()
        self.assertDictEqual(d1=dict(cm.exception), d2=self._slug_does_not_parse_to_username_errors_dict(model=Entity))

    def test_slug_and_username_dont_match_and_invalid(self):
        entity = Entity(slug='0-test-2', username='0test1')
        with self.assertRaises(ValidationError) as cm:
            entity.save()
        self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=Entity, slug_fail=True, username_fail=True))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._slug_does_not_parse_to_username_errors_dict(model=Entity))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._entity_username_must_start_with_4_or_more_letters_and_slug_does_not_parse_to_username_errors_dict())
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_max_length_fail_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True))
        # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_max_length_fail_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True))


# @only_on_sites_with_login # ~~~~ TODO
class EntityEnglishTestCase(EntityTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='en')


# @only_on_sites_with_login # ~~~~ TODO
@override_settings(LANGUAGE_CODE='he')
class EntityHebrewTestCase(EntityTestCaseMixin, SiteTestCase):
    def validate_all_values(self):
        super().validate_all_values()
        self.assertEqual(first=self.language_code, second='he')


if (django_settings.LOGIN_ENABLED):
    class UserTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin):
        def set_up(self):
            super().set_up()
            self.password = get_random_user_password()
            self.data = {
                'password': self.password,
                'slug': 'user-1234',
                'gender': 1,
                'date_of_birth': '1900-08-20',
            }

        def run_test_cannot_create_user_with_all_the_required_fields_number(self, number, gender_is_valid=False):
            user = User(**{field_name: (str(number) if (not (field_name in ['gender'])) else number) for field_name in self._user_all_the_required_fields_keys()})
            # user = User(**{field_name: (str(number) if (field_name in ['username', 'slug', 'date_of_birth']) else number) for field_name in self._user_all_the_required_fields_keys()}) #### TODO
            # user = User(**{field_name: str(number) for field_name in self._user_all_the_required_fields_keys()}) #### TODO
            with self.assertRaises(ValidationError) as cm:
                user.save_user_and_profile()
            self.assertDictEqual(d1=dict(cm.exception), d2=self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=number, gender_is_valid=gender_is_valid))

        def run_test_all_slugs_to_test_list(self, test_settings):
            ok_count, model_save_failures_count = 0, 0
            for slug_dict in tests_settings.SLUGS_TO_TEST_LIST:
                if (slug_dict["slug_length"] >= User.settings.MIN_SLUG_LENGTH):
                    user = DefaultUserFactory(slug=slug_dict["slug"])
                    user.save_user_and_profile()
                    ok_count += 1
                else:
                    with self.assertRaises(ValidationError) as cm:
                        user = DefaultUserFactory(slug=slug_dict["slug"])
                        user.save_user_and_profile()
                    self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_characters_errors_dict_by_value_length(model=User, slug_fail=True, slug_value_length=slug_dict["slug_length"]))
                    model_save_failures_count += 1
            counts_tuple = (ok_count, model_save_failures_count)
            self.assert_models_count(
                entity_count=ok_count,
                user_count=ok_count,
                user_email_address_count=0,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=0,
            )
            self.assertEqual(first=sum(counts_tuple), second=len(tests_settings.SLUGS_TO_TEST_LIST))
            self.assertTupleEqual(tuple1=counts_tuple, tuple2=test_settings["expected_counts_tuple"])

        def test_model_settings(self):
            self.assertEqual(first=User.settings.MIN_USERNAME_LENGTH, second=6)
            self.assertEqual(first=User.settings.MAX_USERNAME_LENGTH, second=40)
            self.assertEqual(first=User.settings.MIN_SLUG_LENGTH, second=6)
            self.assertEqual(first=User.settings.MAX_SLUG_LENGTH, second=200)
            self.assertEqual(first=User.settings.MIN_AGE_ALLOWED_IN_MODEL, second=0)
            self.assertEqual(first=User.settings.MAX_AGE_ALLOWED_IN_MODEL, second=250)
            self.assertEqual(first=User.settings.MIN_AGE_ALLOWED_IN_FORMS, second=0)
            self.assertEqual(first=User.settings.MAX_AGE_ALLOWED_IN_FORMS, second=180)
            self.assertEqual(first=User.settings.MIN_PASSWORD_LENGTH, second=8)
            self.assertEqual(first=User.settings.MAX_PASSWORD_LENGTH, second=120)
            self.assertEqual(first=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED, second=800)
            self.assertEqual(first=User.AGE_VALID_VALUES_IN_MODEL, second=range(User.settings.MIN_AGE_ALLOWED_IN_MODEL, User.settings.MAX_AGE_ALLOWED_IN_MODEL))
            self.assertEqual(first=User.AGE_VALID_VALUES_IN_MODEL, second=range(0, 250))
            self.assertEqual(first=User.AGE_VALID_VALUES_IN_FORMS, second=range(User.settings.MIN_AGE_ALLOWED_IN_FORMS, User.settings.MAX_AGE_ALLOWED_IN_FORMS))
            self.assertEqual(first=User.AGE_VALID_VALUES_IN_FORMS, second=range(0, 180))

        @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MIN_AGE_ALLOWED_IN_MODEL=tests_settings.OVERRIDE_USER_SETTINGS.MIN_AGE_ALLOWED_IN_MODEL, MAX_AGE_ALLOWED_IN_MODEL=tests_settings.OVERRIDE_USER_SETTINGS.MAX_AGE_ALLOWED_IN_MODEL, MIN_AGE_ALLOWED_IN_FORMS=tests_settings.OVERRIDE_USER_SETTINGS.MIN_AGE_ALLOWED_IN_FORMS, MAX_AGE_ALLOWED_IN_FORMS=tests_settings.OVERRIDE_USER_SETTINGS.MAX_AGE_ALLOWED_IN_FORMS))
        def test_model_settings_with_override_settings(self):
            self.assertEqual(first=User.settings.MIN_AGE_ALLOWED_IN_MODEL, second=2)
            self.assertEqual(first=User.settings.MAX_AGE_ALLOWED_IN_MODEL, second=240)
            self.assertEqual(first=User.settings.MIN_AGE_ALLOWED_IN_FORMS, second=2)
            self.assertEqual(first=User.settings.MAX_AGE_ALLOWED_IN_FORMS, second=178)
            self.assertEqual(first=User.AGE_VALID_VALUES_IN_MODEL, second=range(User.settings.MIN_AGE_ALLOWED_IN_MODEL, User.settings.MAX_AGE_ALLOWED_IN_MODEL))
            self.assertEqual(first=User.AGE_VALID_VALUES_IN_MODEL, second=range(2, 240))
            self.assertEqual(first=User.AGE_VALID_VALUES_IN_FORMS, second=range(User.settings.MIN_AGE_ALLOWED_IN_FORMS, User.settings.MAX_AGE_ALLOWED_IN_FORMS))
            self.assertEqual(first=User.AGE_VALID_VALUES_IN_FORMS, second=range(2, 178))

        def test_localizable_fields(self):
            self.assertTupleEqual(tuple1=User.LOCALIZABLE_FIELDS, tuple2=('first_name', 'last_name', 'city'))
            self.assertTupleEqual(tuple1=User.NAME_LOCALIZABLE_FIELDS, tuple2=('first_name', 'last_name'))

        def test_gender_valid_values(self):
            self.assertListEqual(list1=User.GENDER_VALID_VALUES, list2=list(range(User.GENDER_UNKNOWN + 1, User.GENDER_MAX_VALUE_PLUS_ONE)))
            self.assertListEqual(list1=User.GENDER_VALID_VALUES, list2=list(range(1, 3 + 1)))

        def test_gender_strings(self):
            self.assertEqual(first=User.GENDER_FEMALE_STRING, second='female')
            self.assertEqual(first=User.GENDER_MALE_STRING, second='male')
            self.assertEqual(first=User.GENDER_OTHER_STRING, second='other')
            self.assertListEqual(list1=User.ALL_GENDERS, list2=[User.GENDERS_DICT[gender] for gender in User.GENDER_VALID_VALUES])
            self.assertListEqual(list1=User.ALL_GENDERS, list2=[User.GENDER_FEMALE_STRING, User.GENDER_MALE_STRING, User.GENDER_OTHER_STRING])
            self.assertListEqual(list1=User.ALL_GENDERS, list2=['female', 'male', 'other'])

        def test_diet_valid_values(self):
            self.assertListEqual(list1=User.DIET_VALID_VALUES, list2=list(range(User.DIET_UNKNOWN + 1, User.DIET_MAX_VALUE_PLUS_ONE)))
            self.assertListEqual(list1=User.DIET_VALID_VALUES, list2=list(range(1, 3 + 1)))

        def test_smoking_status_valid_values(self):
            self.assertListEqual(list1=User.SMOKING_STATUS_VALID_VALUES, list2=list(range(User.SMOKING_STATUS_UNKNOWN + 1, User.SMOKING_STATUS_MAX_VALUE_PLUS_ONE)))
            self.assertListEqual(list1=User.SMOKING_STATUS_VALID_VALUES, list2=list(range(1, 3 + 1)))

        def test_relationship_status_valid_values(self):
            self.assertListEqual(list1=User.RELATIONSHIP_STATUS_VALID_VALUES, list2=list(range(User.RELATIONSHIP_STATUS_UNKNOWN + 1, User.RELATIONSHIP_STATUS_MAX_VALUE_PLUS_ONE)))
            self.assertListEqual(list1=User.RELATIONSHIP_STATUS_VALID_VALUES, list2=list(range(1, 9 + 1)))

        def test_cannot_create_user_without_all_the_required_fields(self):
            user = User()
            with self.assertRaises(ValidationError) as cm:
                user.save_user_and_profile()
            self.assertDictEqual(d1=dict(cm.exception), d2=self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None))

        def test_cannot_create_user_with_all_the_required_fields_blank(self):
            user = User(**{field_name: '' for field_name in self._user_all_the_required_fields_keys()})
            with self.assertRaises(ValidationError) as cm:
                user.save_user_and_profile()
            self.assertDictEqual(d1=dict(cm.exception), d2=self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=''))

        def test_cannot_create_user_with_all_the_required_fields_zero(self):
            self.run_test_cannot_create_user_with_all_the_required_fields_number(number=0)
            # user = User(**{field_name: 0 for field_name in self._user_all_the_required_fields_keys()})
            # with self.assertRaises(ValidationError) as cm:
            #     user.save_user_and_profile()
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None))

        def test_cannot_create_user_with_all_the_required_fields_minus_one(self):
            self.run_test_cannot_create_user_with_all_the_required_fields_number(number=-1)
            # user = User(**{field_name: -1 for field_name in self._user_all_the_required_fields_keys()})
            # with self.assertRaises(ValidationError) as cm:
            #     user.save_user_and_profile()
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None))

        def test_cannot_create_user_with_all_the_required_fields_ninety_nine(self):
            self.run_test_cannot_create_user_with_all_the_required_fields_number(number=99)
            # user = User(**{field_name: 99 for field_name in self._user_all_the_required_fields_keys()})
            # with self.assertRaises(ValidationError) as cm:
            #     user.save_user_and_profile()
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None))

        def test_cannot_create_user_with_all_the_required_fields_one(self):
            self.run_test_cannot_create_user_with_all_the_required_fields_number(number=1, gender_is_valid=True)
            # user = User(**{field_name: 0 for field_name in self._user_all_the_required_fields_keys()})
            # with self.assertRaises(ValidationError) as cm:
            #     user.save_user_and_profile()
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None))

        def test_cannot_create_user_with_empty_slug(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='')
                user.save_user_and_profile()
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._user_slug_and_username_min_length_fail_errors_dict_by_value_length(value_length=0))
            self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_max_length_fail_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_max_length_fail_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True))

        def test_cannot_create_user_with_unknown_gender(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(gender=User.GENDER_UNKNOWN)
                user.save_user_and_profile()
            self.assertDictEqual(d1=dict(cm.exception), d2=self._value_is_not_a_valid_choice_errors_dict_by_field_name_and_value(field_name='gender', value=0))

        def test_cannot_create_users_with_bulk_create(self):
            user_1 = User(slug='zzzzzz')
            user_2 = User(slug='ZZZ-ZZZ')
            with self.assertRaises(NotImplementedError) as cm:
                User.objects.bulk_create([user_1, user_2])
            self.assertEqual(first=str(cm.exception), second="bulk_create is not implemented.")

        def test_cannot_delete_users_with_queryset_delete(self):
            with self.assertRaises(NotImplementedError) as cm:
                User.objects.delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                User.objects.all().delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                User.objects.filter(pk=1).delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                User.objects.all().exclude(pk=2).delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")

        def test_cannot_create_user_with_reserved_username(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='webmaster')
                user.save_user_and_profile()
            self.assertDictEqual(d1=dict(cm.exception), d2=self._this_username_is_already_taken_errors_dict(slug_fail=True, username_fail=True))

        def test_cannot_create_user_with_reserved_and_too_short_username(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='mail')
                user.save_user_and_profile()
            self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=4))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._this_username_is_already_taken_errors_dict(slug_fail=True, username_fail=True))

        def test_admin_is_invalid_username(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='admin')
                user.save_user_and_profile()
            self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=5))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._this_username_is_already_taken_errors_dict(slug_fail=True, username_fail=True))

        def test_can_create_user_admin_with_special_username(self):
            user = DefaultUserFactory(slug='admin', special_username=True)
            user.save_user_and_profile()

        def test_can_create_user_mail_with_special_username(self):
            user = DefaultUserFactory(slug='mail', special_username=True)
            user.save_user_and_profile()

        def test_can_create_user_webmaster_with_special_username(self):
            user = DefaultUserFactory(slug='webmaster', special_username=True)
            user.save_user_and_profile()

        def test_cannot_create_user_without_a_slug_with_special_username(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='', special_username=True)
                user.save_user_and_profile()
            self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._username_is_required_error_message]})  # ~~~~ TODO: fix models! Should be 'slug' and not '__all__'.

        def test_cannot_create_user_with_a_username_and_different_slug_with_special_username(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='webmaster', username='webmaster1', special_username=True)
                user.save_user_and_profile()
            self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._slug_does_not_parse_to_username_error_message]})  # ~~~~ TODO: fix models! Should be 'slug' and not '__all__'.

        def test_cannot_create_two_users_with_the_same_username_with_special_username(self):
            user_1 = DefaultUserFactory(slug='admin', special_username=True)
            user_1.save_user_and_profile()
            with self.assertRaises(ValidationError) as cm:
                user_2 = DefaultUserFactory(slug='adm-in', special_username=True)
                user_2.save_user_and_profile()
            self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._this_username_is_already_taken_error_message], 'username': [self._this_username_is_already_taken_error_message]})  # ~~~~ TODO: fix models! Should be 'slug' and not '__all__'.

        def test_cannot_create_user_with_existing_username_1(self):
            entity = Entity(slug='zzzzzz')
            entity.save()
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='ZZZ-ZZZ')
                user.save_user_and_profile()
            self.assertDictEqual(d1=dict(cm.exception), d2=self._this_username_is_already_taken_errors_dict(slug_fail=True, username_fail=True))

        def test_cannot_create_user_with_existing_username_2(self):
            user_1 = DefaultUserFactory(slug='zzzzzz')
            user_1.save_user_and_profile()
            with self.assertRaises(ValidationError) as cm:
                user_2 = DefaultUserFactory(slug='ZZZ-ZZZ')
                user_2.save_user_and_profile()
            self.assertDictEqual(d1=dict(cm.exception), d2=self._this_username_is_already_taken_errors_dict(slug_fail=True, username_fail=True))

        def test_has_no_confirmed_email(self):
            user = DefaultUserFactory()
            UserEmailAddressFactory(user=user, is_confirmed=False)
            UserEmailAddressFactory(user=user, is_confirmed=False)
            self.assertFalse(expr=user.has_confirmed_email)

        def test_has_a_confirmed_email(self):
            user = DefaultUserFactory()
            UserEmailAddressFactory(user=user, is_confirmed=False)
            UserEmailAddressFactory(user=user, is_confirmed=True)
            self.assertTrue(expr=user.has_confirmed_email)

        def test_user_id_length(self):
            user = DefaultUserFactory()
            self.assertEqual(first=len(user.id), second=15)

        def test_user_id_number_in_range(self):
            user = DefaultUserFactory()
            self.assertGreaterEqual(a=int(user.id), b=10 ** 14)
            self.assertLess(a=int(user.id), b=10 ** 15)

        def test_slug_and_username_min_length_fail(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='a' * 5)
                user.save_user_and_profile()
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._user_slug_and_username_min_length_fail_errors_dict_by_value_length(value_length=5))
            self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=5))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=5))

        def test_slug_and_username_min_length_ok_1(self):
            user = DefaultUserFactory(slug='a' * 6)
            user.save_user_and_profile()

        def test_slug_and_username_min_length_ok_2(self):
            # print("test_slug_and_username_min_length_ok_2: django_settings.USER_SETTINGS.MIN_SLUG_LENGTH", django_settings.USER_SETTINGS.MIN_SLUG_LENGTH)####
            # print("test_slug_and_username_min_length_ok_2: django_settings.USER_SETTINGS.MAX_SLUG_LENGTH", django_settings.USER_SETTINGS.MAX_SLUG_LENGTH)####
            # print("test_slug_and_username_min_length_ok_2: User.settings.MIN_SLUG_LENGTH", User.settings.MIN_SLUG_LENGTH)####
            # print("test_slug_and_username_min_length_ok_2: User.settings.MAX_SLUG_LENGTH", User.settings.MAX_SLUG_LENGTH)####
            self.assertEqual(first=User.settings.MIN_SLUG_LENGTH, second=6)
            test_settings = {
                "expected_counts_tuple": (8, 0),
            }
            self.run_test_all_slugs_to_test_list(test_settings=test_settings)

        @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MIN_SLUG_LENGTH=tests_settings.OVERRIDE_USER_SETTINGS.MIN_SLUG_LENGTH))
        def test_slug_min_length_fail_username_min_length_ok(self):
            self.assertEqual(first=User.settings.MIN_SLUG_LENGTH, second=60)
            test_settings = {
                "expected_counts_tuple": (4, 4),
            }
            self.run_test_all_slugs_to_test_list(test_settings=test_settings)

        def test_slug_and_username_max_length_fail(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='a' * 201)
                user.save_user_and_profile()
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._user_slug_and_username_max_length_fail_errors_dict_by_value_length(value_length=201))
            self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=201))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=201))

        def test_slug_max_length_ok_username_max_length_fail_1(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='b' * 200)
                user.save_user_and_profile()
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._user_username_max_length_fail_errors_dict_by_value_length(value_length=200))
            self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=200))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=200))

        def test_slug_max_length_ok_username_max_length_fail_2(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='a' * 41)
                user.save_user_and_profile()
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._user_username_max_length_fail_errors_dict_by_value_length(value_length=41))
            self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=41))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=41))

        def test_slug_and_username_max_length_ok(self):
            user = DefaultUserFactory(slug='a' * 40)
            user.save_user_and_profile()

        def test_star2000_is_valid_username(self):
            user = DefaultUserFactory(slug='star2000', username='star2000')
            user.save_user_and_profile()

        def test_come2us_is_invalid_username(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='come2us', username='come2us')
                user.save_user_and_profile()
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._user_slug_and_username_username_must_start_with_4_or_more_letters_errors_dict())
            self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=Entity, slug_fail=True, username_fail=True))

        def test_000000_is_invalid_username(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='0' * 6, username='0' * 6)
                user.save_user_and_profile()
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._user_slug_and_username_username_must_start_with_4_or_more_letters_errors_dict())
            self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=Entity, slug_fail=True, username_fail=True))

        def test_0test1_is_invalid_username(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='0-test-1', username='0test1')
                user.save_user_and_profile()
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._user_slug_and_username_username_must_start_with_4_or_more_letters_errors_dict())
            self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=Entity, slug_fail=True, username_fail=True))

        def test_slug_and_username_dont_match_but_valid(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='star2001', username='star2000')
                user.save_user_and_profile()
            self.assertDictEqual(d1=dict(cm.exception), d2=self._slug_does_not_parse_to_username_errors_dict(model=User))

        def test_slug_and_username_dont_match_and_invalid(self):
            with self.assertRaises(ValidationError) as cm:
                user = DefaultUserFactory(slug='0-test-2', username='0test1')
                user.save_user_and_profile()
            self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=Entity, slug_fail=True, username_fail=True))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._slug_does_not_parse_to_username_errors_dict(model=User))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._user_username_must_start_with_4_or_more_letters_and_slug_does_not_parse_to_username_errors_dict())
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_max_length_fail_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True))
            # self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_max_length_fail_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True))

        def test_user_can_change_password(self):
            new_password = '8' * 8
            incorrect_new_password = '7' * 8
            user = DefaultUserFactory()
            self.assertTrue(expr=user.check_password(raw_password=tests_settings.USER_PASSWORD))
            user.set_password(raw_password=new_password)
            self.assertTrue(expr=user.check_password(raw_password=new_password))
            self.assertFalse(expr=user.check_password(raw_password=incorrect_new_password))
            self.assertFalse(expr=user.check_password(raw_password=tests_settings.USER_PASSWORD))

        def test_password_too_short_exception(self):
            new_password = '8' * 3
            user = DefaultUserFactory()
            self.assertTrue(expr=user.check_password(raw_password=tests_settings.USER_PASSWORD))
            with self.assertRaises(ValidationError) as cm:
                user.set_password(raw_password=new_password)
            self.assertListEqual(list1=list(cm.exception), list2=[self._password_too_short_error_message])
            self.assertTrue(expr=user.check_password(raw_password=tests_settings.USER_PASSWORD))
            self.assertFalse(expr=user.check_password(raw_password=new_password))

        def test_password_too_long_exception(self):
            new_password = '8' * 121
            user = DefaultUserFactory()
            self.assertTrue(expr=user.check_password(raw_password=tests_settings.USER_PASSWORD))
            with self.assertRaises(ValidationError) as cm:
                user.set_password(raw_password=new_password)
            self.assertListEqual(list1=list(cm.exception), list2=[self._password_too_long_error_message])
            self.assertTrue(expr=user.check_password(raw_password=tests_settings.USER_PASSWORD))
            self.assertFalse(expr=user.check_password(raw_password=new_password))

        def test_valid_date_of_birth_list_ok(self):
            for date_of_birth in tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST:
                data = self.data.copy()
                data['slug'] = 'user-{}'.format(date_of_birth)
                data['date_of_birth'] = date_of_birth
                user = User(**data)
                user.save_user_and_profile()
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.first_name, second=self.first_name)
                self.assertEqual(first=user.last_name, second=self.last_name)
                self.assert_user_first_and_last_name_in_all_languages(user=user)
                for (key, value) in data.items():
                    if (not (key in ['date_of_birth'])):
                        self.assertEqual(first=getattr(user, key), second=value)
                self.assertEqual(first=user.date_of_birth, second=datetime.strptime(date_of_birth, '%Y-%m-%d').date())
            self.assert_models_count(
                entity_count=len(tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST),
                user_count=len(tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST),
                user_email_address_count=0,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=0,
            )

        def test_invalid_date_of_birth_list_fail(self):
            for date_of_birth in tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST:
                data = self.data.copy()
                data['date_of_birth'] = date_of_birth
                user = User(**data)
                with self.assertRaises(ValidationError) as cm:
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._enter_a_valid_date_errors_dict())
            self.assert_models_count(
                entity_count=0,
                user_count=0,
                user_email_address_count=0,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=0,
            )

        def test_user_names_in_both_websites(self):
            for user in [DefaultUserFactory(), InactiveUserFactory(), ActiveUserFactory()]:
                self.assertEqual(first=user.full_name, second=user.get_full_name())
                self.assertEqual(first=user.full_name, second='{} {}'.format(user.first_name, user.last_name))
                self.assertEqual(first=user.short_name, second=user.get_first_name())
                self.assertEqual(first=user.short_name, second=user.get_short_name())
                self.assertEqual(first=user.short_name, second='{}'.format(user.first_name))
                self.assertEqual(first=user.full_name, second=user.speedy_net_profile.get_name())
                self.assertEqual(first=user.short_name, second=user.speedy_match_profile.get_name())
                self.assertEqual(first=str(user.first_name), second=user.speedy_match_profile.get_name())
                self.assertNotEqual(first=user.full_name, second=user.short_name)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=user.name, second=user.get_full_name())
                    self.assertEqual(first=user.name, second=user.speedy_net_profile.get_name())
                    self.assertNotEqual(first=user.name, second=user.speedy_match_profile.get_name())
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=user.name, second=user.get_first_name())
                    self.assertEqual(first=user.name, second=user.speedy_match_profile.get_name())
                    self.assertNotEqual(first=user.name, second=user.speedy_net_profile.get_name())
                else:
                    raise NotImplementedError()


    @only_on_sites_with_login
    class UserEnglishTestCase(UserTestCaseMixin, SiteTestCase):
        def set_up(self):
            super().set_up()
            self.data.update({
                'first_name_en': "Doron",
                'last_name_en': "Matalon",
            })
            self.first_name = "Doron"
            self.last_name = "Matalon"

        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='en')


    @only_on_sites_with_login
    @override_settings(LANGUAGE_CODE='he')
    class UserHebrewTestCase(UserTestCaseMixin, SiteTestCase):
        def set_up(self):
            super().set_up()
            self.data.update({
                'first_name_he': "דורון",
                'last_name_he': "מטלון",
            })
            self.first_name = "דורון"
            self.last_name = "מטלון"

        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='he')


    class UserEmailAddressTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin):
        def test_cannot_create_user_email_address_without_all_the_required_fields(self):
            user_email_address = UserEmailAddress()
            with self.assertRaises(ValidationError) as cm:
                user_email_address.save()
            self.assertDictEqual(d1=dict(cm.exception), d2=self._cannot_create_user_email_address_without_all_the_required_fields_errors_dict())
            self.assert_models_count(
                entity_count=0,
                user_count=0,
                user_email_address_count=0,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=0,
            )

        def test_cannot_create_user_email_address_with_invalid_email(self):
            email_list = ['email', 'email@example', 'email@example.', 'email@.example', 'email@example.com.', 'email@.example.com', 'email@example..com']
            user = DefaultUserFactory()
            for email in email_list:
                # print(email) ######### ~~~~ TODO
                user_email_address = UserEmailAddress(user=user, email=email)
                with self.assertRaises(ValidationError) as cm:
                    user_email_address.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._enter_a_valid_email_address_errors_dict())
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=0,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=0,
            )
            self.assert_models_count(
                entity_count=1,
                user_count=1,
                user_email_address_count=0,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=0,
            )

        def test_non_unique_confirmed_email_address(self):
            existing_user = DefaultUserFactory()
            existing_user_email = UserEmailAddressFactory(user=existing_user, email='email@example.com', is_confirmed=True)
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=1,
                user_unconfirmed_email_addresses_count=0,
            )
            user = DefaultUserFactory()
            user_email_address = UserEmailAddress(user=user, email='email@example.com')
            with self.assertRaises(ValidationError) as cm:
                user_email_address.save()
            self.assertDictEqual(d1=dict(cm.exception), d2=self._this_email_is_already_in_use_errors_dict())
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=1,
                user_unconfirmed_email_addresses_count=0,
            )
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=0,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=0,
            )
            existing_user = User.objects.get(pk=existing_user.pk)
            user = User.objects.get(pk=user.pk)
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=1,
                user_unconfirmed_email_addresses_count=0,
            )
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=0,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=0,
            )
            self.assert_models_count(
                entity_count=2,
                user_count=2,
                user_email_address_count=1,
                confirmed_email_address_count=1,
                unconfirmed_email_address_count=0,
            )

        def test_non_unique_confirmed_email_address_uppercase(self):
            existing_user = DefaultUserFactory()
            existing_user_email = UserEmailAddressFactory(user=existing_user, email='email@example.com', is_confirmed=True)
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=1,
                user_unconfirmed_email_addresses_count=0,
            )
            user = DefaultUserFactory()
            user_email_address = UserEmailAddress(user=user, email='EMAIL@EXAMPLE.COM')
            with self.assertRaises(ValidationError) as cm:
                user_email_address.save()
            self.assertDictEqual(d1=dict(cm.exception), d2=self._this_email_is_already_in_use_errors_dict())
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=1,
                user_unconfirmed_email_addresses_count=0,
            )
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=0,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=0,
            )
            existing_user = User.objects.get(pk=existing_user.pk)
            user = User.objects.get(pk=user.pk)
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=1,
                user_unconfirmed_email_addresses_count=0,
            )
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=0,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=0,
            )
            self.assert_models_count(
                entity_count=2,
                user_count=2,
                user_email_address_count=1,
                confirmed_email_address_count=1,
                unconfirmed_email_address_count=0,
            )

        def test_non_unique_unconfirmed_email_address(self):
            # Unconfirmed email address is deleted if another user adds it again.
            existing_user = DefaultUserFactory()
            existing_user_email = UserEmailAddressFactory(user=existing_user, email='email@example.com', is_confirmed=False)
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            user = DefaultUserFactory()
            user_email_address = UserEmailAddress(user=user, email='email@example.com')
            user_email_address.save()
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=0,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=0,
            )
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            existing_user = User.objects.get(pk=existing_user.pk)
            user = User.objects.get(pk=user.pk)
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=0,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=0,
            )
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            self.assert_models_count(
                entity_count=2,
                user_count=2,
                user_email_address_count=1,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=1,
            )

        def test_non_unique_unconfirmed_email_address_uppercase(self):
            # Unconfirmed email address is deleted if another user adds it again.
            existing_user = DefaultUserFactory()
            existing_user_email = UserEmailAddressFactory(user=existing_user, email='email77@example.com', is_confirmed=False)
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            user = DefaultUserFactory()
            user_email_address = UserEmailAddress(user=user, email='EMAIL77@EXAMPLE.COM')
            user_email_address.save()
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=0,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=0,
            )
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            existing_user = User.objects.get(pk=existing_user.pk)
            user = User.objects.get(pk=user.pk)
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=0,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=0,
            )
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            self.assert_models_count(
                entity_count=2,
                user_count=2,
                user_email_address_count=1,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=1,
            )

        def test_different_unconfirmed_email_addresses_uppercase(self):
            # Unconfirmed email address is deleted if another user adds it again.
            existing_user = DefaultUserFactory()
            existing_user_email = UserEmailAddressFactory(user=existing_user, email='email77@example.com', is_confirmed=False)
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            user = DefaultUserFactory()
            user_email_address = UserEmailAddress(user=user, email='EMAIL755@EXAMPLE.COM')
            user_email_address.save()
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            existing_user = User.objects.get(pk=existing_user.pk)
            user = User.objects.get(pk=user.pk)
            self.assert_user_email_addresses_count(
                user=existing_user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            self.assert_models_count(
                entity_count=2,
                user_count=2,
                user_email_address_count=2,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=2,
            )

        def test_email_gets_converted_to_lowercase_1(self):
            user = DefaultUserFactory()
            user_email_address = UserEmailAddress(user=user, email='EMAIL77@EXAMPLE.COM')
            user_email_address.save()
            self.assertEqual(first=user_email_address.email, second='email77@example.com')
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            user = User.objects.get(pk=user.pk)
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            self.assert_models_count(
                entity_count=1,
                user_count=1,
                user_email_address_count=1,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=1,
            )

        def test_email_gets_converted_to_lowercase_2(self):
            user = DefaultUserFactory()
            user_email_address = UserEmailAddressFactory(user=user, email='EMAIL75@EXAMPLE.COM')
            self.assertEqual(first=user_email_address.email, second='email75@example.com')
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            user = User.objects.get(pk=user.pk)
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            self.assert_models_count(
                entity_count=1,
                user_count=1,
                user_email_address_count=1,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=1,
            )

        def test_save_unconfirmed_email_address_5_times(self):
            user = DefaultUserFactory()
            user_email_address = UserEmailAddress(user=user, email='email75@example.com')
            for i in range(5):
                # print(i) ######### ~~~~ TODO
                # print(user_email_address.pk) ######### ~~~~ TODO
                user_email_address.save()
            self.assertEqual(first=user_email_address.email, second='email75@example.com')
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            user = User.objects.get(pk=user.pk)
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=0,
                user_unconfirmed_email_addresses_count=1,
            )
            self.assert_models_count(
                entity_count=1,
                user_count=1,
                user_email_address_count=1,
                confirmed_email_address_count=0,
                unconfirmed_email_address_count=1,
            )

        def test_save_confirmed_email_address_5_times(self):
            user = DefaultUserFactory()
            user_email_address = UserEmailAddress(user=user, email='email75@example.com', is_confirmed=True)
            for i in range(5):
                # print(i) ######### ~~~~ TODO
                # print(user_email_address.pk) ######### ~~~~ TODO
                user_email_address.save()
            self.assertEqual(first=user_email_address.email, second='email75@example.com')
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=1,
                user_unconfirmed_email_addresses_count=0,
            )
            user = User.objects.get(pk=user.pk)
            self.assert_user_email_addresses_count(
                user=user,
                user_email_addresses_count=1,
                user_confirmed_email_addresses_count=1,
                user_unconfirmed_email_addresses_count=0,
            )
            self.assert_models_count(
                entity_count=1,
                user_count=1,
                user_email_address_count=1,
                confirmed_email_address_count=1,
                unconfirmed_email_address_count=0,
            )

        def test_cannot_create_user_email_addresses_with_bulk_create(self):
            with self.assertRaises(NotImplementedError) as cm:
                UserEmailAddress.objects.bulk_create([])
            self.assertEqual(first=str(cm.exception), second="bulk_create is not implemented.")

        def test_cannot_delete_user_email_addresses_with_queryset_delete(self):
            with self.assertRaises(NotImplementedError) as cm:
                UserEmailAddress.objects.delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                UserEmailAddress.objects.all().delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                UserEmailAddress.objects.filter(pk=1).delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                UserEmailAddress.objects.all().exclude(pk=2).delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")


    @only_on_sites_with_login
    class UserEmailAddressEnglishTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='en')


    @only_on_sites_with_login
    @override_settings(LANGUAGE_CODE='he')
    class UserEmailAddressHebrewTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='he')


