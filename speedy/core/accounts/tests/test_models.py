from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import random
        from time import sleep
        from datetime import datetime, timedelta

        from dateutil.relativedelta import relativedelta

        from django.test import override_settings
        from django.db.utils import DataError, IntegrityError
        from django.core.exceptions import ValidationError
        from django.utils.timezone import now

        from speedy.core.base.test.utils import get_random_user_password

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.base.test.utils import get_django_settings_class_with_override_settings
        from speedy.core.accounts.test.mixins import SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin
        from speedy.core.accounts.test.user_factories import DefaultUserFactory, InactiveUserFactory, SpeedyNetInactiveUserFactory, ActiveUserFactory
        from speedy.core.accounts.test.user_email_address_factories import UserEmailAddressFactory

        from speedy.core.accounts.models import ConcurrencyError, Entity, ReservedUsername, User, UserEmailAddress
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

        from speedy.match.accounts.test.mixins import SpeedyMatchAccountsModelsMixin, SpeedyMatchAccountsLanguageMixin


        class EntityTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the Entity model's validations and behavior, such as slug/username/id generation, length limits and reserved usernames.
            """
            def create_one_entity(self):
                """
                Creates and saves one Entity with a fixed slug and username, and asserts its username, slug and id are set correctly.

                :return: The created entity.
                :rtype: speedy.core.accounts.models.Entity
                """
                entity = Entity(slug='zzzzzz', username='zzzzzz')
                entity.save()
                self.assertEqual(first=entity.username, second='zzzzzz')
                self.assertEqual(first=entity.slug, second='zzzzzz')
                self.assertEqual(first=len(entity.id), second=15)
                return entity

            def run_test_all_slugs_to_test_list(self, test_settings):
                """
                Attempts to save an entity for each slug in tests_settings.SLUGS_TO_TEST_LIST, counts successes and failures according to the current MIN_SLUG_LENGTH setting, and asserts the resulting counts and model counts match the expected values.

                :param test_settings: A dict containing the key "expected_counts_tuple", a tuple of (ok_count, model_save_failures_count) expected for the current settings.
                :type test_settings: dict
                """
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
                """
                Asserts the Entity model's username and slug length settings have the expected default values.
                """
                self.assertEqual(first=Entity.settings.MIN_USERNAME_LENGTH, second=6)
                self.assertEqual(first=Entity.settings.MAX_USERNAME_LENGTH, second=120)
                self.assertEqual(first=Entity.settings.MIN_SLUG_LENGTH, second=6)
                self.assertEqual(first=Entity.settings.MAX_SLUG_LENGTH, second=200)

            def test_cannot_create_entity_without_a_slug(self):
                """
                Asserts that saving an Entity without a slug raises a ValidationError because the username doesn't start with at least 4 letters.
                """
                entity = Entity()
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=Entity, slug_fail=True, username_fail=True))

            def test_cannot_create_entities_with_bulk_create(self):
                """
                Asserts that creating entities with bulk_create raises a NotImplementedError.
                """
                entity_1 = Entity(slug='zzzzzz')
                entity_2 = Entity(slug='ZZZ-ZZZ')
                with self.assertRaises(NotImplementedError) as cm:
                    Entity.objects.bulk_create([entity_1, entity_2])
                self.assertEqual(first=str(cm.exception), second="bulk_create is not implemented.")

            def test_cannot_delete_entities_with_queryset_delete(self):
                """
                Asserts that deleting entities via the manager or a queryset (all, filter, exclude) raises a NotImplementedError.
                """
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

            def test_cannot_create_entity_with_an_invalid_id_1(self):
                """
                Asserts that an entity with an id whose first character is '0' is invalid, since the first character must be a non-zero digit, and saving it raises a ValidationError.
                """
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

            def test_cannot_create_entity_with_an_invalid_id_2(self):
                """
                Asserts that an entity with an id longer than the maximum length (16 characters) is invalid, and saving it raises a ValidationError for illegal characters and exceeding the maximum length.
                """
                old_entity = self.create_one_entity()
                old_entity_id = old_entity.id
                new_entity_id = '{}1'.format(old_entity_id)
                self.assertNotEqual(first=new_entity_id, second=old_entity_id)
                new_entity = Entity(slug='yyyyyy', username='yyyyyy', id=new_entity_id)
                self.assertEqual(first=new_entity.id, second=new_entity_id)
                self.assertNotEqual(first=new_entity.id, second=old_entity.id)
                self.assertEqual(first=len(new_entity.id), second=16)
                for i in range(1, 16):
                    self.assertIn(member=new_entity.id[i], container=[str(i) for i in range(10)])
                with self.assertRaises(ValidationError) as cm:
                    new_entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._id_contains_illegal_characters_and_ensure_this_value_has_at_most_max_length_characters_errors_dict_by_max_length_and_value_length(max_length=15, value_length=16))

            def test_cannot_create_entity_with_an_invalid_id_3(self):
                """
                Asserts that an entity with an id whose first character is a non-digit (e.g. '_', a letter, or a special character) is invalid, and saving it raises a ValidationError.
                """
                old_entity = self.create_one_entity()
                old_entity_id = old_entity.id
                old_entity_id_as_list = list(old_entity_id)
                old_entity_id_as_list[0] = random.choice(['_', 'k', 'K', '!', '@', '#'])
                new_entity_id = ''.join(old_entity_id_as_list)
                self.assertEqual(first=new_entity_id, second='{}{}'.format(old_entity_id_as_list[0], old_entity_id[1:]))
                self.assertNotEqual(first=new_entity_id, second=old_entity_id)
                new_entity = Entity(slug='yyyyyy', username='yyyyyy', id=new_entity_id)
                self.assertEqual(first=new_entity.id, second=new_entity_id)
                self.assertNotEqual(first=new_entity.id, second=old_entity.id)
                self.assertEqual(first=len(new_entity.id), second=15)
                with self.assertRaises(AssertionError) as cm:
                    self.assertIn(member=new_entity.id[0], container=[str(i) for i in range(1, 10)])
                self.assertEqual(first=str(cm.exception), second="'{}' not found in ['1', '2', '3', '4', '5', '6', '7', '8', '9']".format(old_entity_id_as_list[0]))
                self.assertNotIn(member=new_entity.id[0], container=[str(i) for i in range(1, 10)])
                for i in range(1, 15):
                    self.assertIn(member=new_entity.id[i], container=[str(i) for i in range(10)])
                with self.assertRaises(ValidationError) as cm:
                    new_entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._id_contains_illegal_characters_errors_dict())

            def test_cannot_create_entity_with_an_invalid_id_4(self):
                """
                Asserts that an entity with an id shorter than the required length (14 characters) is invalid, and saving it raises a ValidationError for illegal characters.
                """
                old_entity = self.create_one_entity()
                old_entity_id = old_entity.id
                new_entity_id = '{}'.format(old_entity_id[:14])
                self.assertNotEqual(first=new_entity_id, second=old_entity_id)
                new_entity = Entity(slug='yyyyyy', username='yyyyyy', id=new_entity_id)
                self.assertEqual(first=new_entity.id, second=new_entity_id)
                self.assertNotEqual(first=new_entity.id, second=old_entity.id)
                self.assertEqual(first=len(new_entity.id), second=14)
                for i in range(1, 14):
                    self.assertIn(member=new_entity.id[i], container=[str(i) for i in range(10)])
                with self.assertRaises(ValidationError) as cm:
                    new_entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._id_contains_illegal_characters_errors_dict())

            def test_cannot_create_entity_with_reserved_username(self):
                """
                Asserts that creating an entity with a reserved username ('webmaster') raises a ValidationError.
                """
                entity = Entity(slug='webmaster')
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._this_username_is_already_taken_errors_dict(slug_fail=True, username_fail=True))

            def test_cannot_create_entity_with_reserved_and_too_short_username(self):
                """
                Asserts that creating an entity with a reserved username that is also too short ('mail') raises a ValidationError for a too-short username.
                """
                entity = Entity(slug='mail')
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=4))

            def test_cannot_create_entity_with_existing_username(self):
                """
                Asserts that creating an entity whose username matches an already-saved entity's username raises a ValidationError.
                """
                entity_1 = Entity(slug='zzzzzz')
                entity_1.save()
                entity_2 = Entity(slug='ZZZ-ZZZ')
                with self.assertRaises(ValidationError) as cm:
                    entity_2.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._this_username_is_already_taken_errors_dict(slug_fail=True, username_fail=True))

            def test_automatic_creation_of_username_and_id(self):
                """
                Asserts that saving an entity with only a slug automatically generates the matching username and a 15-digit id.
                """
                entity = Entity(slug='zzzzzz')
                entity.save()
                self.assertEqual(first=entity.username, second='zzzzzz')
                self.assertEqual(first=entity.slug, second='zzzzzz')
                self.assertEqual(first=len(entity.id), second=15)

            def test_automatic_creation_of_id(self):
                """
                Asserts that saving an entity with a slug and username automatically generates a 15-digit numeric id, starting with a non-zero digit.
                """
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
                """
                Asserts that creating two entities generates distinct usernames, slugs and ids for each.
                """
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
                """
                Asserts that a slug and username shorter than MIN_SLUG_LENGTH/MIN_USERNAME_LENGTH raise a ValidationError.
                """
                entity = Entity(slug='a' * 5, username='a' * 5)
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=5))

            def test_slug_and_username_min_length_ok_1(self):
                """
                Asserts that a slug and username exactly at MIN_SLUG_LENGTH/MIN_USERNAME_LENGTH save successfully.
                """
                entity = Entity(slug='a' * 6, username='a' * 6)
                entity.save()

            def test_slug_and_username_min_length_ok_2(self):
                """
                Asserts that with the default MIN_SLUG_LENGTH, all slugs in SLUGS_TO_TEST_LIST that meet the minimum length are saved successfully.
                """
                self.assertEqual(first=Entity.settings.MIN_SLUG_LENGTH, second=6)
                test_settings = {
                    "expected_counts_tuple": (8, 0),
                }
                self.run_test_all_slugs_to_test_list(test_settings=test_settings)

            @override_settings(ENTITY_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.ENTITY_SETTINGS, MIN_SLUG_LENGTH=tests_settings.OVERRIDE_ENTITY_SETTINGS.MIN_SLUG_LENGTH))
            def test_slug_min_length_fail_username_min_length_ok(self):
                """
                Asserts that with an overridden, larger MIN_SLUG_LENGTH, only slugs in SLUGS_TO_TEST_LIST that meet the new minimum are saved successfully, and the rest fail.
                """
                self.assertEqual(first=Entity.settings.MIN_SLUG_LENGTH, second=60)
                test_settings = {
                    "expected_counts_tuple": (4, 4),
                }
                self.run_test_all_slugs_to_test_list(test_settings=test_settings)

            def test_slug_and_username_max_length_fail(self):
                """
                Asserts that a slug and username longer than MAX_SLUG_LENGTH/MAX_USERNAME_LENGTH raise a ValidationError.
                """
                entity = Entity(slug='a' * 201, username='z' * 201)
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=201))

            def test_slug_max_length_ok_username_max_length_fail_1(self):
                """
                Asserts that a slug within MAX_SLUG_LENGTH but a username exceeding MAX_USERNAME_LENGTH raises a ValidationError for both.
                """
                entity = Entity(slug='b' * 200, username='b' * 200)
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=200))

            def test_slug_max_length_ok_username_max_length_fail_2(self):
                """
                Asserts that a slug within MAX_SLUG_LENGTH but a username slightly over MAX_USERNAME_LENGTH raises a ValidationError for both.
                """
                entity = Entity(slug='b' * 121, username='b' * 121)
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=121))

            def test_slug_max_length_fail_username_max_length_ok_with_username(self):
                """
                Asserts that a slug exceeding MAX_SLUG_LENGTH (due to hyphens inflating its length) raises a ValidationError, even when an explicit username within the limit is given.
                """
                entity = Entity(slug='a-' * 120, username='a' * 120)
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, slug_value_length=239))

            def test_slug_max_length_fail_username_max_length_ok_without_username(self):
                """
                Asserts that a slug exceeding MAX_SLUG_LENGTH (due to hyphens inflating its length) raises a ValidationError, even when no username is given and it would be derived from the slug.
                """
                entity = Entity(slug='a-' * 120)
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, slug_value_length=239))

            def test_slug_and_username_max_length_ok(self):
                """
                Asserts that a slug and username at exactly the maximum allowed lengths save successfully.
                """
                entity = Entity(slug='a' * 120 + '-' * 80, username='a' * 120)
                entity.save()

            def test_star2000_is_valid_username(self):
                """
                Asserts that a username starting with 4 or more letters followed by digits ('star2000') is valid.
                """
                entity = Entity(slug='star2000', username='star2000')
                entity.save()

            def test_come2us_is_valid_username(self):
                """
                Asserts that a username starting with 4 or more letters followed by digits ('come2us') is valid.
                """
                entity = Entity(slug='come2us', username='come2us')
                entity.save()

            def test_000000_is_invalid_username(self):
                """
                Asserts that a username consisting only of digits ('000000') is invalid since it doesn't start with 4 or more letters.
                """
                entity = Entity(slug='0' * 6, username='0' * 6)
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=Entity, slug_fail=True, username_fail=True))

            def test_0test1_is_invalid_username(self):
                """
                Asserts that a username starting with a digit ('0test1') is invalid since it doesn't start with 4 or more letters.
                """
                entity = Entity(slug='0-test-1', username='0test1')
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=Entity, slug_fail=True, username_fail=True))

            def test_slug_and_username_dont_match_but_valid(self):
                """
                Asserts that a valid slug and valid username that don't parse to the same value raise a ValidationError for mismatch.
                """
                entity = Entity(slug='star2001', username='star2000')
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._slug_does_not_parse_to_username_errors_dict(model=Entity))

            def test_slug_and_username_dont_match_and_invalid(self):
                """
                Asserts that a slug and username that are both invalid and don't match each other raise a ValidationError for the username not starting with 4 or more letters.
                """
                entity = Entity(slug='0-test-2', username='0test1')
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=Entity, slug_fail=True, username_fail=True))


        # @only_on_sites_with_login  # ~~~~ TODO
        class EntityAllMainLanguagesEnglishTestCase(EntityTestCaseMixin, SiteTestCase):
            """
            Tests the Entity model, for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        # @only_on_sites_with_login  # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='fr')
        class EntityAllMainLanguagesFrenchTestCase(EntityTestCaseMixin, SiteTestCase):
            """
            Tests the Entity model, for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        # @only_on_sites_with_login  # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='de')
        class EntityAllMainLanguagesGermanTestCase(EntityTestCaseMixin, SiteTestCase):
            """
            Tests the Entity model, for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        # @only_on_sites_with_login  # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='es')
        class EntityAllMainLanguagesSpanishTestCase(EntityTestCaseMixin, SiteTestCase):
            """
            Tests the Entity model, for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        # @only_on_sites_with_login  # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='pt')
        class EntityAllMainLanguagesPortugueseTestCase(EntityTestCaseMixin, SiteTestCase):
            """
            Tests the Entity model, for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        # @only_on_sites_with_login  # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='it')
        class EntityAllMainLanguagesItalianTestCase(EntityTestCaseMixin, SiteTestCase):
            """
            Tests the Entity model, for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        # @only_on_sites_with_login  # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='nl')
        class EntityAllMainLanguagesDutchTestCase(EntityTestCaseMixin, SiteTestCase):
            """
            Tests the Entity model, for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        # @only_on_sites_with_login  # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='he')
        class EntityAllMainLanguagesHebrewTestCase(EntityTestCaseMixin, SiteTestCase):
            """
            Tests the Entity model, for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class ReservedUsernameTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the ReservedUsername model's validations and behavior, such as required fields, uniqueness, and length limits.
            """
            def test_cannot_create_reserved_username_without_a_username(self):
                """
                Asserts that saving a ReservedUsername without a username or slug raises a ValidationError.
                """
                reserved_username = ReservedUsername()
                with self.assertRaises(ValidationError) as cm:
                    reserved_username.save()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._username_is_required_error_message]})

            def test_cannot_create_reserved_username_with_empty_username(self):
                """
                Asserts that saving a ReservedUsername with an empty username raises a ValidationError.
                """
                reserved_username = ReservedUsername(username='')
                with self.assertRaises(ValidationError) as cm:
                    reserved_username.save()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._username_is_required_error_message]})

            def test_cannot_create_reserved_username_with_empty_slug(self):
                """
                Asserts that saving a ReservedUsername with an empty slug raises a ValidationError.
                """
                reserved_username = ReservedUsername(slug='')
                with self.assertRaises(ValidationError) as cm:
                    reserved_username.save()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._username_is_required_error_message]})

            def test_cannot_create_reserved_usernames_with_bulk_create(self):
                """
                Asserts that creating reserved usernames with bulk_create raises a NotImplementedError.
                """
                reserved_username_1 = ReservedUsername(slug='zzzzzz')
                reserved_username_2 = ReservedUsername(slug='ZZZ-ZZZ')
                with self.assertRaises(NotImplementedError) as cm:
                    ReservedUsername.objects.bulk_create([reserved_username_1, reserved_username_2])
                self.assertEqual(first=str(cm.exception), second="bulk_create is not implemented.")

            def test_cannot_delete_reserved_usernames_with_queryset_delete(self):
                """
                Asserts that deleting reserved usernames via the manager or a queryset (all, filter, exclude) raises a NotImplementedError.
                """
                with self.assertRaises(NotImplementedError) as cm:
                    ReservedUsername.objects.delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    ReservedUsername.objects.all().delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    ReservedUsername.objects.filter(pk=1).delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    ReservedUsername.objects.all().exclude(pk=2).delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")

            def test_can_create_reserved_username_with_reserved_username(self):
                """
                Asserts that a reserved username can itself be created with a reserved slug ('webmaster'), unlike regular entities.
                """
                reserved_username = ReservedUsername(slug='webmaster')
                reserved_username.save()

            def test_can_create_reserved_username_with_reserved_and_too_short_username(self):
                """
                Asserts that a reserved username can be created with a reserved and too-short slug ('mail'), unlike regular entities.
                """
                reserved_username = ReservedUsername(slug='mail')
                reserved_username.save()

            def test_cannot_create_reserved_username_with_existing_username_1(self):
                """
                Asserts that creating a reserved username whose username matches an existing Entity's username raises a ValidationError.
                """
                entity = Entity(slug='zzzzzz')
                entity.save()
                reserved_username = ReservedUsername(slug='ZZZ-ZZZ')
                with self.assertRaises(ValidationError) as cm:
                    reserved_username.save()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._this_username_is_already_taken_error_message], 'username': [self._this_username_is_already_taken_error_message]})

            def test_cannot_create_reserved_username_with_existing_username_2(self):
                """
                Asserts that creating a reserved username whose username matches another existing ReservedUsername's username raises a ValidationError.
                """
                reserved_username_1 = ReservedUsername(slug='zzzzzz')
                reserved_username_1.save()
                reserved_username_2 = ReservedUsername(slug='ZZZ-ZZZ')
                with self.assertRaises(ValidationError) as cm:
                    reserved_username_2.save()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._this_username_is_already_taken_error_message], 'username': [self._this_username_is_already_taken_error_message]})

            def test_star2000_is_valid_username(self):
                """
                Asserts that a username starting with 4 or more letters followed by digits ('star2000') is valid for a reserved username.
                """
                reserved_username = ReservedUsername(slug='star2000', username='star2000')
                reserved_username.save()

            def test_come2us_is_valid_username(self):
                """
                Asserts that a username starting with 4 or more letters followed by digits ('come2us') is valid for a reserved username.
                """
                reserved_username = ReservedUsername(slug='come2us', username='come2us')
                reserved_username.save()

            def test_000000_is_valid_username(self):
                """
                Asserts that, unlike regular entities, a reserved username consisting only of digits ('000000') is valid.
                """
                reserved_username = ReservedUsername(slug='0' * 6, username='0' * 6)
                reserved_username.save()

            def test_0test1_is_valid_username(self):
                """
                Asserts that, unlike regular entities, a reserved username starting with a digit ('0test1') is valid.
                """
                reserved_username = ReservedUsername(slug='0-test-1', username='0test1')
                reserved_username.save()

            def test_0_is_valid_username_1(self):
                """
                Asserts that a reserved username can be created with only a one-character slug ('0'), with the username derived automatically.
                """
                reserved_username = ReservedUsername(slug='0')
                reserved_username.save()

            def test_0_is_valid_username_2(self):
                """
                Asserts that a reserved username can be created with only a one-character username ('0'), with the slug derived automatically.
                """
                reserved_username = ReservedUsername(username='0')
                reserved_username.save()

            def test_long_username_is_valid_username_1(self):
                """
                Asserts that a reserved username can be created with a 250-character slug, with no maximum length enforced.
                """
                reserved_username = ReservedUsername(slug='0' * 250)
                reserved_username.save()

            def test_long_username_is_valid_username_2(self):
                """
                Asserts that a reserved username can be created with a 250-character username, with no maximum length enforced.
                """
                reserved_username = ReservedUsername(username='0' * 250)
                reserved_username.save()

            def test_username_too_long_exception_1(self):
                """
                Asserts that a slug of 5000 characters exceeds the database column's character limit and raises a DataError.
                """
                reserved_username = ReservedUsername(slug='0' * 5000)
                with self.assertRaises(DataError) as cm:
                    reserved_username.save()
                self.assertIn(member=self._value_too_long_for_type_character_varying_255_error_message, container=str(cm.exception))

            def test_username_too_long_exception_2(self):
                """
                Asserts that a username of 5000 characters exceeds the database column's character limit and raises a DataError.
                """
                reserved_username = ReservedUsername(username='0' * 5000)
                with self.assertRaises(DataError) as cm:
                    reserved_username.save()
                self.assertIn(member=self._value_too_long_for_type_character_varying_255_error_message, container=str(cm.exception))

            def test_username_too_long_exception_3(self):
                """
                Asserts that a slug of 260 characters exceeds the database column's character limit and raises a DataError.
                """
                reserved_username = ReservedUsername(slug='0' * 260)
                with self.assertRaises(DataError) as cm:
                    reserved_username.save()
                self.assertIn(member=self._value_too_long_for_type_character_varying_255_error_message, container=str(cm.exception))

            def test_username_too_long_exception_4(self):
                """
                Asserts that a username of 260 characters exceeds the database column's character limit and raises a DataError.
                """
                reserved_username = ReservedUsername(username='0' * 260)
                with self.assertRaises(DataError) as cm:
                    reserved_username.save()
                self.assertIn(member=self._value_too_long_for_type_character_varying_255_error_message, container=str(cm.exception))

            def test_slug_and_username_dont_match_1(self):
                """
                Asserts that a valid slug and valid username that don't parse to the same value raise a ValidationError for mismatch.
                """
                reserved_username = ReservedUsername(slug='star2001', username='star2000')
                with self.assertRaises(ValidationError) as cm:
                    reserved_username.save()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._slug_does_not_parse_to_username_error_message]})

            def test_slug_and_username_dont_match_2(self):
                """
                Asserts that a slug and username that don't parse to the same value raise a ValidationError for mismatch, even when both would individually be valid for reserved usernames.
                """
                reserved_username = ReservedUsername(slug='0-test-2', username='0test1')
                with self.assertRaises(ValidationError) as cm:
                    reserved_username.save()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._slug_does_not_parse_to_username_error_message]})


        class ReservedUsernameAllMainLanguagesEnglishTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            """
            Tests the ReservedUsername model, for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @override_settings(LANGUAGE_CODE='fr')
        class ReservedUsernameAllMainLanguagesFrenchTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            """
            Tests the ReservedUsername model, for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @override_settings(LANGUAGE_CODE='de')
        class ReservedUsernameAllMainLanguagesGermanTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            """
            Tests the ReservedUsername model, for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @override_settings(LANGUAGE_CODE='es')
        class ReservedUsernameAllMainLanguagesSpanishTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            """
            Tests the ReservedUsername model, for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @override_settings(LANGUAGE_CODE='pt')
        class ReservedUsernameAllMainLanguagesPortugueseTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            """
            Tests the ReservedUsername model, for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @override_settings(LANGUAGE_CODE='it')
        class ReservedUsernameAllMainLanguagesItalianTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            """
            Tests the ReservedUsername model, for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @override_settings(LANGUAGE_CODE='nl')
        class ReservedUsernameAllMainLanguagesDutchTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            """
            Tests the ReservedUsername model, for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @override_settings(LANGUAGE_CODE='he')
        class ReservedUsernameAllMainLanguagesHebrewTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            """
            Tests the ReservedUsername model, for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class UserTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyMatchAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, SpeedyMatchAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the User model's validations and behavior, such as required fields, slug/username/id generation, password handling, and concurrency protection.
            """
            def create_one_user(self):
                """
                Creates and saves one default user with a fixed slug and username, and asserts its username, slug and id are set correctly.

                :return: The created user.
                :rtype: speedy.core.accounts.models.User
                """
                user = DefaultUserFactory(slug='zzzzzz', username='zzzzzz')
                user.save_user_and_profile()
                self.assertEqual(first=user.username, second='zzzzzz')
                self.assertEqual(first=user.slug, second='zzzzzz')
                self.assertEqual(first=len(user.id), second=15)
                return user

            def run_test_cannot_create_user_with_all_the_required_fields_number(self, number, gender_is_valid=False):
                """
                Attempts to create a user whose required fields are all set to the given number (as strings, except gender), and asserts saving it raises a ValidationError with the expected errors.

                :param number: The number to use as the value of all required fields.
                :type number: int
                :param gender_is_valid: Whether the given number is a valid gender value. Defaults to False.
                :type gender_is_valid: bool
                """
                user = User(**{field_name: (str(number) if (not (field_name in ['gender'])) else number) for field_name in self._user_all_the_required_fields_keys()})
                with self.assertRaises(ValidationError) as cm:
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=number, gender_is_valid=gender_is_valid))

            def run_test_all_slugs_to_test_list(self, test_settings):
                """
                Attempts to create a user for each slug in tests_settings.SLUGS_TO_TEST_LIST, counts successes and failures according to the current MIN_SLUG_LENGTH setting, and asserts the resulting counts and model counts match the expected values.

                :param test_settings: A dict containing the key "expected_counts_tuple", a tuple of (ok_count, model_save_failures_count) expected for the current settings.
                :type test_settings: dict
                """
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

            def run_test_check_password_skip_password_hash_upgrade_if_doesnt_pass_password_validators(self, iterations):
                """
                Asserts that checking an invalid raw password against a hash encoded with the given iteration count succeeds but does not trigger a hash upgrade, since the password fails the password validators.

                :param iterations: The number of PBKDF2 iterations used to encode the test password hash.
                :type iterations: int
                """
                # Using a password that is too short or with too few unique characters.
                from django.contrib.auth.hashers import PBKDF2PasswordHasher
                self.assertNotEqual(first=iterations, second=560000)
                invalid_password = random.choice(['8' * 3, '8' * 10, '10203040', 'abc', 'abcdef'])
                hasher = PBKDF2PasswordHasher()
                encoded = hasher.encode(password=invalid_password, salt=hasher.salt(), iterations=iterations)
                user = DefaultUserFactory()
                user.password = encoded
                user.save()
                decoded = hasher.decode(encoded=user.password)
                self.assertEqual(first=decoded["iterations"], second=iterations)
                self.assertIs(expr1=user.check_password(raw_password=invalid_password), expr2=True)
                self.assertIs(expr1=user.password, expr2=encoded)
                decoded = hasher.decode(encoded=user.password)
                self.assertEqual(first=decoded["iterations"], second=iterations)
                self.assertIs(expr1=user.check_password(raw_password=invalid_password), expr2=True)
                self.assertIs(expr1=user.password, expr2=encoded)

            def run_test_check_password_doesnt_skip_password_hash_upgrade_if_passes_password_validators(self, iterations):
                """
                Asserts that checking a valid raw password against a hash encoded with the given (non-default) iteration count succeeds and upgrades the stored password hash to use the default iteration count.

                :param iterations: The number of PBKDF2 iterations used to encode the test password hash.
                :type iterations: int
                """
                # Using a valid password that will pass all password validators.
                from django.contrib.auth.hashers import PBKDF2PasswordHasher
                self.assertNotEqual(first=iterations, second=560000)
                valid_password = 'abcdef12'
                hasher = PBKDF2PasswordHasher()
                encoded = hasher.encode(password=valid_password, salt=hasher.salt(), iterations=iterations)
                user = DefaultUserFactory()
                user.password = encoded
                user.save()
                decoded = hasher.decode(encoded=user.password)
                self.assertEqual(first=decoded["iterations"], second=iterations)
                self.assertIs(expr1=user.check_password(raw_password=valid_password), expr2=True)
                self.assertIsNot(expr1=user.password, expr2=encoded)
                decoded = hasher.decode(encoded=user.password)
                self.assertEqual(first=decoded["iterations"], second=560000)
                encoded = user.password
                self.assertIs(expr1=user.check_password(raw_password=valid_password), expr2=True)
                self.assertIs(expr1=user.password, expr2=encoded)

            def run_test_check_password_skip_password_hash_upgrade_if_iterations_are_big_enough(self, iterations):
                """
                Asserts that checking a valid raw password against a hash encoded with an already-sufficient iteration count succeeds without upgrading the stored password hash.

                :param iterations: The number of PBKDF2 iterations used to encode the test password hash.
                :type iterations: int
                """
                # Using a valid password that will pass all password validators.
                from django.contrib.auth.hashers import PBKDF2PasswordHasher
                self.assertNotEqual(first=iterations, second=560000)
                valid_password = 'abcdef12'
                hasher = PBKDF2PasswordHasher()
                encoded = hasher.encode(password=valid_password, salt=hasher.salt(), iterations=iterations)
                user = DefaultUserFactory()
                user.password = encoded
                user.save()
                decoded = hasher.decode(encoded=user.password)
                self.assertEqual(first=decoded["iterations"], second=iterations)
                self.assertIs(expr1=user.check_password(raw_password=valid_password), expr2=True)
                self.assertIs(expr1=user.password, expr2=encoded)
                decoded = hasher.decode(encoded=user.password)
                self.assertEqual(first=decoded["iterations"], second=iterations)
                self.assertIs(expr1=user.check_password(raw_password=valid_password), expr2=True)
                self.assertIs(expr1=user.password, expr2=encoded)

            def run_test_call_set_username_and_slug_race_condition_user_model_should_not_change(self, test_choice):
                """
                Asserts that if a user's username and slug are changed concurrently by another process after the in-memory instance was loaded, saving the stale in-memory instance raises a ConcurrencyError and leaves the username and slug unchanged, for both choices of new username/slug.

                :param test_choice: Which concurrent username/slug change to simulate (1 for a custom username, 2 for the user's id as username).
                :type test_choice: int
                """
                user = ActiveUserFactory()
                username = user.username
                self.assertEqual(first=user.username, second=username)
                self.assertEqual(first=user.slug, second=username)
                user_instance_2 = User.objects.get(pk=user.pk)
                if (test_choice == 1):
                    user_instance_2.username, user_instance_2.slug, user_instance_2.special_username = "jenniferconnelly1234", "jennifer-connelly-1234", False
                elif (test_choice == 2):
                    user_instance_2.username, user_instance_2.slug, user_instance_2.special_username = user_instance_2.id, user_instance_2.id, True
                else:
                    raise NotImplementedError("Invalid test choice.")
                user_instance_2.save()
                if (test_choice == 1):
                    self.assertEqual(first=user_instance_2.username, second="jenniferconnelly1234")
                    self.assertEqual(first=user_instance_2.slug, second="jennifer-connelly-1234")
                elif (test_choice == 2):
                    self.assertEqual(first=user_instance_2.username, second=user.id)
                    self.assertEqual(first=user_instance_2.slug, second=user.id)
                else:
                    raise NotImplementedError("Invalid test choice.")
                # Race condition: username and slug should not change.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                if (test_choice == 1):
                    self.assertEqual(first=user.username, second="jenniferconnelly1234")
                    self.assertEqual(first=user.slug, second="jennifer-connelly-1234")
                elif (test_choice == 2):
                    self.assertEqual(first=user.username, second=user.id)
                    self.assertEqual(first=user.slug, second=user.id)
                else:
                    raise NotImplementedError("Invalid test choice.")
                user_instance_2.username, user_instance_2.slug, user_instance_2.special_username = username, username, False
                user_instance_2.save()
                self.assertEqual(first=user_instance_2.username, second=username)
                self.assertEqual(first=user_instance_2.slug, second=username)
                # Race condition: username and slug should not change.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.username, second=username)
                self.assertEqual(first=user.slug, second=username)

            def test_model_settings(self):
                """
                Asserts the User model's username, slug, age and password length settings, and the maximum number of friends allowed, have the expected default values.
                """
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
                """
                Asserts that overriding the age-related User settings updates the effective settings and the derived valid age ranges accordingly.
                """
                self.assertEqual(first=User.settings.MIN_AGE_ALLOWED_IN_MODEL, second=2)
                self.assertEqual(first=User.settings.MAX_AGE_ALLOWED_IN_MODEL, second=240)
                self.assertEqual(first=User.settings.MIN_AGE_ALLOWED_IN_FORMS, second=2)
                self.assertEqual(first=User.settings.MAX_AGE_ALLOWED_IN_FORMS, second=178)
                self.assertEqual(first=User.AGE_VALID_VALUES_IN_MODEL, second=range(User.settings.MIN_AGE_ALLOWED_IN_MODEL, User.settings.MAX_AGE_ALLOWED_IN_MODEL))
                self.assertEqual(first=User.AGE_VALID_VALUES_IN_MODEL, second=range(2, 240))
                self.assertEqual(first=User.AGE_VALID_VALUES_IN_FORMS, second=range(User.settings.MIN_AGE_ALLOWED_IN_FORMS, User.settings.MAX_AGE_ALLOWED_IN_FORMS))
                self.assertEqual(first=User.AGE_VALID_VALUES_IN_FORMS, second=range(2, 178))

            def test_localizable_fields(self):
                """
                Asserts the User model's LOCALIZABLE_FIELDS, NAME_LOCALIZABLE_FIELDS and NAME_REQUIRED_LOCALIZABLE_FIELDS have the expected values.
                """
                self.assertTupleEqual(tuple1=User.LOCALIZABLE_FIELDS, tuple2=('first_name', 'last_name', 'city'))
                self.assertTupleEqual(tuple1=User.NAME_LOCALIZABLE_FIELDS, tuple2=('first_name', 'last_name'))
                self.assertTupleEqual(tuple1=User.NAME_REQUIRED_LOCALIZABLE_FIELDS, tuple2=('first_name',))

            def test_gender_valid_values(self):
                """
                Asserts that User.GENDER_VALID_VALUES contains the range of valid gender integer values.
                """
                self.assertListEqual(list1=User.GENDER_VALID_VALUES, list2=list(range(User.GENDER_UNKNOWN + 1, User.GENDER_MAX_VALUE_PLUS_ONE)))
                self.assertListEqual(list1=User.GENDER_VALID_VALUES, list2=list(range(1, 3 + 1)))

            def test_gender_strings(self):
                """
                Asserts the User model's gender string constants and ALL_GENDERS list match the expected values and are consistent with GENDERS_DICT.
                """
                self.assertEqual(first=User.GENDER_FEMALE_STRING, second='female')
                self.assertEqual(first=User.GENDER_MALE_STRING, second='male')
                self.assertEqual(first=User.GENDER_OTHER_STRING, second='other')
                self.assertListEqual(list1=User.ALL_GENDERS, list2=list(User.GENDERS_DICT.values()))
                self.assertListEqual(list1=User.ALL_GENDERS, list2=[User.GENDERS_DICT[gender] for gender in User.GENDER_VALID_VALUES])
                self.assertListEqual(list1=User.ALL_GENDERS, list2=[User.GENDER_FEMALE_STRING, User.GENDER_MALE_STRING, User.GENDER_OTHER_STRING])
                self.assertListEqual(list1=User.ALL_GENDERS, list2=['female', 'male', 'other'])

            def test_genders_dict(self):
                """
                Asserts User.GENDERS_DICT maps each valid gender value to its expected string representation.
                """
                self.assertListEqual(list1=list(User.GENDERS_DICT.keys()), list2=User.GENDER_VALID_VALUES)
                self.assertListEqual(list1=list(User.GENDERS_DICT.items()), list2=[(1, 'female'), (2, 'male'), (3, 'other')])
                self.assertDictEqual(d1=User.GENDERS_DICT, d2={1: 'female', 2: 'male', 3: 'other'})

            def test_diet_valid_values(self):
                """
                Asserts that User.DIET_VALID_VALUES contains the range of valid diet integer values.
                """
                self.assertListEqual(list1=User.DIET_VALID_VALUES, list2=list(range(User.DIET_UNKNOWN + 1, User.DIET_MAX_VALUE_PLUS_ONE)))
                self.assertListEqual(list1=User.DIET_VALID_VALUES, list2=list(range(1, 3 + 1)))

            def test_smoking_status_valid_values(self):
                """
                Asserts that User.SMOKING_STATUS_VALID_VALUES contains the range of valid smoking status integer values.
                """
                self.assertListEqual(list1=User.SMOKING_STATUS_VALID_VALUES, list2=list(range(User.SMOKING_STATUS_UNKNOWN + 1, User.SMOKING_STATUS_MAX_VALUE_PLUS_ONE)))
                self.assertListEqual(list1=User.SMOKING_STATUS_VALID_VALUES, list2=list(range(1, 3 + 1)))

            def test_relationship_status_valid_values(self):
                """
                Asserts that User.RELATIONSHIP_STATUS_VALID_VALUES contains the range of valid relationship status integer values.
                """
                self.assertListEqual(list1=User.RELATIONSHIP_STATUS_VALID_VALUES, list2=list(range(User.RELATIONSHIP_STATUS_UNKNOWN + 1, User.RELATIONSHIP_STATUS_MAX_VALUE_PLUS_ONE)))
                self.assertListEqual(list1=User.RELATIONSHIP_STATUS_VALID_VALUES, list2=list(range(1, 9 + 1)))

            def test_cannot_create_user_without_all_the_required_fields(self):
                """
                Asserts that saving a user with no fields set raises a ValidationError listing all the missing required fields.
                """
                user = User()
                with self.assertRaises(ValidationError) as cm:
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None))

            def test_cannot_create_user_with_all_the_required_fields_blank(self):
                """
                Asserts that saving a user whose required fields are all set to an empty string raises a ValidationError listing the blank required fields.
                """
                user = User(**{field_name: '' for field_name in self._user_all_the_required_fields_keys()})
                with self.assertRaises(ValidationError) as cm:
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=''))

            def test_cannot_create_user_with_all_the_required_fields_zero(self):
                """
                Asserts that setting all the required fields to 0 raises a ValidationError with the expected errors.
                """
                self.run_test_cannot_create_user_with_all_the_required_fields_number(number=0)

            def test_cannot_create_user_with_all_the_required_fields_minus_one(self):
                """
                Asserts that setting all the required fields to -1 raises a ValidationError with the expected errors.
                """
                self.run_test_cannot_create_user_with_all_the_required_fields_number(number=-1)

            def test_cannot_create_user_with_all_the_required_fields_ninety_nine(self):
                """
                Asserts that setting all the required fields to 99 raises a ValidationError with the expected errors.
                """
                self.run_test_cannot_create_user_with_all_the_required_fields_number(number=99)

            def test_cannot_create_user_with_all_the_required_fields_one(self):
                """
                Asserts that setting all the required fields to 1 raises a ValidationError with the expected errors, noting that 1 is a valid gender value.
                """
                self.run_test_cannot_create_user_with_all_the_required_fields_number(number=1, gender_is_valid=True)

            def test_cannot_create_user_with_empty_slug(self):
                """
                Asserts that creating a user with an empty slug raises a ValidationError since the username doesn't start with 4 or more letters.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))

            def test_cannot_create_user_with_unknown_gender(self):
                """
                Asserts that creating a user with the unknown gender value raises a ValidationError for an invalid choice.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(gender=User.GENDER_UNKNOWN)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._value_is_not_a_valid_choice_errors_dict_by_field_name_and_value(field_name='gender', value=0))

            def test_cannot_create_users_with_bulk_create(self):
                """
                Asserts that creating users with bulk_create raises a NotImplementedError.
                """
                user_1 = User(slug='zzzzzz')
                user_2 = User(slug='ZZZ-ZZZ')
                with self.assertRaises(NotImplementedError) as cm:
                    User.objects.bulk_create([user_1, user_2])
                self.assertEqual(first=str(cm.exception), second="bulk_create is not implemented.")

            def test_cannot_delete_users_with_queryset_delete(self):
                """
                Asserts that deleting users via the manager or a queryset (all, filter, exclude) raises a NotImplementedError.
                """
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

            def test_cannot_create_user_with_an_invalid_id_1(self):
                """
                Asserts that creating a user with an id whose first character is '0' raises a ValidationError, since the first character must be a non-zero digit.
                """
                old_user = self.create_one_user()
                old_user_id = old_user.id
                old_user_id_as_list = list(old_user_id)
                old_user_id_as_list[0] = '0'
                new_user_id = ''.join(old_user_id_as_list)
                self.assertEqual(first=new_user_id, second='0{}'.format(old_user_id[1:]))
                self.assertNotEqual(first=new_user_id, second=old_user_id)
                with self.assertRaises(ValidationError) as cm:
                    new_user = DefaultUserFactory(slug='yyyyyy', username='yyyyyy', id=new_user_id)
                self.assertDictEqual(d1=dict(cm.exception), d2=self._id_contains_illegal_characters_errors_dict())

            def test_cannot_create_user_with_an_invalid_id_2(self):
                """
                Asserts that creating a user with an id longer than the maximum length (16 characters) raises a ValidationError for illegal characters and exceeding the maximum length.
                """
                old_user = self.create_one_user()
                old_user_id = old_user.id
                new_user_id = '{}1'.format(old_user_id)
                self.assertNotEqual(first=new_user_id, second=old_user_id)
                with self.assertRaises(ValidationError) as cm:
                    new_user = DefaultUserFactory(slug='yyyyyy', username='yyyyyy', id=new_user_id)
                self.assertDictEqual(d1=dict(cm.exception), d2=self._id_contains_illegal_characters_and_ensure_this_value_has_at_most_max_length_characters_errors_dict_by_max_length_and_value_length(max_length=15, value_length=16))

            def test_cannot_create_user_with_an_invalid_id_3(self):
                """
                Asserts that creating a user with an id whose first character is a non-digit (e.g. '_', a letter, or a special character) raises a ValidationError.
                """
                old_user = self.create_one_user()
                old_user_id = old_user.id
                old_user_id_as_list = list(old_user_id)
                old_user_id_as_list[0] = random.choice(['_', 'k', 'K', '!', '@', '#'])
                new_user_id = ''.join(old_user_id_as_list)
                self.assertEqual(first=new_user_id, second='{}{}'.format(old_user_id_as_list[0], old_user_id[1:]))
                self.assertNotEqual(first=new_user_id, second=old_user_id)
                with self.assertRaises(ValidationError) as cm:
                    new_user = DefaultUserFactory(slug='yyyyyy', username='yyyyyy', id=new_user_id)
                self.assertDictEqual(d1=dict(cm.exception), d2=self._id_contains_illegal_characters_errors_dict())

            def test_cannot_create_user_with_an_invalid_id_4(self):
                """
                Asserts that creating a user with an id shorter than the required length (14 characters) raises a ValidationError for illegal characters.
                """
                old_user = self.create_one_user()
                old_user_id = old_user.id
                new_user_id = '{}'.format(old_user_id[:14])
                self.assertNotEqual(first=new_user_id, second=old_user_id)
                with self.assertRaises(ValidationError) as cm:
                    new_user = DefaultUserFactory(slug='yyyyyy', username='yyyyyy', id=new_user_id)
                self.assertDictEqual(d1=dict(cm.exception), d2=self._id_contains_illegal_characters_errors_dict())

            def test_cannot_create_user_with_reserved_username(self):
                """
                Asserts that creating a user with a reserved username ('webmaster') raises a ValidationError.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='webmaster')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._this_username_is_already_taken_errors_dict(slug_fail=True, username_fail=True))

            def test_cannot_create_user_with_reserved_and_too_short_username(self):
                """
                Asserts that creating a user with a reserved username that is also too short ('mail') raises a ValidationError for a too-short username.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='mail')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=4))

            def test_admin_is_invalid_username(self):
                """
                Asserts that creating a regular user with the username 'admin' (too short and reserved) raises a ValidationError.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='admin')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=5))

            def test_doron_is_invalid_username(self):
                """
                Asserts that creating a regular user with the username 'doron' (too short and reserved) raises a ValidationError.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='doron')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=5))

            def test_can_create_user_admin_with_special_username(self):
                """
                Asserts that a user can be created with the reserved username 'admin' when special_username is True.
                """
                user = DefaultUserFactory(slug='admin', special_username=True)
                user.save_user_and_profile()

            def test_can_create_user_mail_with_special_username(self):
                """
                Asserts that a user can be created with the reserved username 'mail' when special_username is True.
                """
                user = DefaultUserFactory(slug='mail', special_username=True)
                user.save_user_and_profile()

            def test_can_create_user_webmaster_with_special_username(self):
                """
                Asserts that a user can be created with the reserved username 'webmaster' when special_username is True.
                """
                user = DefaultUserFactory(slug='webmaster', special_username=True)
                user.save_user_and_profile()

            def test_can_create_user_doron_with_special_username(self):
                """
                Asserts that a user can be created with the reserved username 'doron' when special_username is True.
                """
                user = DefaultUserFactory(slug='doron', special_username=True)
                user.save_user_and_profile()

            def test_can_create_user_jennifer_with_special_username(self):
                """
                Asserts that a user can be created with the username 'jennifer' when special_username is True.
                """
                user = DefaultUserFactory(slug='jennifer', special_username=True)
                user.save_user_and_profile()

            def test_cannot_create_user_without_a_slug_with_special_username(self):
                """
                Asserts that creating a user without a slug, even with special_username set to True, raises a ValidationError.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='', special_username=True)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._username_is_required_error_message]})  # ~~~~ TODO: fix models! Should be 'slug' and not '__all__'.

            def test_cannot_create_user_with_a_username_and_different_slug_with_special_username(self):
                """
                Asserts that creating a user with special_username set to True but a username that doesn't match the given slug raises a ValidationError for the mismatch.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='webmaster', username='webmaster1', special_username=True)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._slug_does_not_parse_to_username_error_message]})  # ~~~~ TODO: fix models! Should be 'slug' and not '__all__'.

            def test_cannot_create_two_users_with_the_same_username_with_special_username(self):
                """
                Asserts that creating two users with special_username set to True whose usernames collide ('admin' and 'adm-in') raises a ValidationError for the second one.
                """
                user_1 = DefaultUserFactory(slug='admin', special_username=True)
                user_1.save_user_and_profile()
                with self.assertRaises(ValidationError) as cm:
                    user_2 = DefaultUserFactory(slug='adm-in', special_username=True)
                    user_2.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._this_username_is_already_taken_error_message], 'username': [self._this_username_is_already_taken_error_message]})  # ~~~~ TODO: fix models! Should be 'slug' and not '__all__'.

            def test_cannot_create_user_with_existing_username_1(self):
                """
                Asserts that creating a user whose username matches an existing Entity's username raises a ValidationError.
                """
                entity = Entity(slug='zzzzzz')
                entity.save()
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='ZZZ-ZZZ')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._this_username_is_already_taken_errors_dict(slug_fail=True, username_fail=True))

            def test_cannot_create_user_with_existing_username_2(self):
                """
                Asserts that creating a user whose username matches another existing user's username raises a ValidationError.
                """
                user_1 = DefaultUserFactory(slug='zzzzzz')
                user_1.save_user_and_profile()
                with self.assertRaises(ValidationError) as cm:
                    user_2 = DefaultUserFactory(slug='ZZZ-ZZZ')
                    user_2.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._this_username_is_already_taken_errors_dict(slug_fail=True, username_fail=True))

            def test_cannot_create_user_with_is_superuser_and_is_staff_not_equal(self):
                """
                Asserts that creating a user with is_superuser and is_staff set to different values raises a ValidationError, while equal values (both True or both False) are allowed.
                """
                user = DefaultUserFactory(is_superuser=False, is_staff=False)
                user.save_user_and_profile()
                user = DefaultUserFactory(is_superuser=True, is_staff=True)
                user.save_user_and_profile()
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(is_superuser=True, is_staff=False)
                    user.save_user_and_profile()
                self.assertListEqual(list1=list(cm.exception), list2=[self._superuser_must_be_equal_to_staff_error_message])
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(is_superuser=False, is_staff=True)
                    user.save_user_and_profile()
                self.assertListEqual(list1=list(cm.exception), list2=[self._superuser_must_be_equal_to_staff_error_message])

            def test_has_no_confirmed_email(self):
                """
                Asserts that a user with only unconfirmed email addresses has has_confirmed_email equal to False.
                """
                user = DefaultUserFactory()
                UserEmailAddressFactory(user=user, is_confirmed=False)
                UserEmailAddressFactory(user=user, is_confirmed=False)
                self.assertIs(expr1=user.has_confirmed_email, expr2=False)

            def test_has_a_confirmed_email(self):
                """
                Asserts that a user with at least one confirmed email address has has_confirmed_email equal to True.
                """
                user = DefaultUserFactory()
                UserEmailAddressFactory(user=user, is_confirmed=False)
                UserEmailAddressFactory(user=user, is_confirmed=True)
                self.assertIs(expr1=user.has_confirmed_email, expr2=True)

            def test_user_id_length(self):
                """
                Asserts that a newly created user has a 15-character id.
                """
                user = DefaultUserFactory()
                self.assertEqual(first=len(user.id), second=15)

            def test_user_id_number_in_range(self):
                """
                Asserts that a newly created user's id, interpreted as a number, falls within the expected 15-digit range.
                """
                user = DefaultUserFactory()
                self.assertGreaterEqual(a=int(user.id), b=10 ** 14)
                self.assertLess(a=int(user.id), b=10 ** 15)

            def test_slug_and_username_min_length_fail(self):
                """
                Asserts that a slug and username shorter than MIN_SLUG_LENGTH/MIN_USERNAME_LENGTH raise a ValidationError.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='a' * 5)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=5))

            def test_slug_and_username_min_length_ok_1(self):
                """
                Asserts that a slug and username exactly at MIN_SLUG_LENGTH/MIN_USERNAME_LENGTH save successfully.
                """
                user = DefaultUserFactory(slug='a' * 6)
                user.save_user_and_profile()

            def test_first_name_is_not_optional(self):
                """
                Asserts that creating a user with a blank first name in English raises a ValidationError for the first name field in every language.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(first_name_en="")
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2={'first_name_{language_code}'.format(language_code=language_code).replace("-", "_"): [self._this_field_cannot_be_blank_error_message] for language_code, language_name in django_settings.LANGUAGES})

            def test_first_name_is_none(self):
                """
                Asserts that creating a user with a None first name in English and Hebrew raises a ValidationError for the first name field in every language.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(first_name_en=None, first_name_he=None)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2={'first_name_{language_code}'.format(language_code=language_code).replace("-", "_"): [self._this_field_cannot_be_null_error_message] for language_code, language_name in django_settings.LANGUAGES})

            def test_last_name_is_optional(self):
                """
                Asserts that a user can be created with a blank last name in English, and that the last name is blank in every supported language.
                """
                user = DefaultUserFactory(last_name_en="")
                user.save_user_and_profile()
                self.assertEqual(first=user.last_name, second="")
                self.assertEqual(first=user.last_name_en, second="")
                self.assertEqual(first=user.last_name_fr, second="")
                self.assertEqual(first=user.last_name_de, second="")
                self.assertEqual(first=user.last_name_es, second="")
                self.assertEqual(first=user.last_name_pt, second="")
                self.assertEqual(first=user.last_name_it, second="")
                self.assertEqual(first=user.last_name_nl, second="")
                self.assertEqual(first=user.last_name_sv, second="")
                self.assertEqual(first=user.last_name_ko, second="")
                self.assertEqual(first=user.last_name_fi, second="")
                self.assertEqual(first=user.last_name_he, second="")

            def test_last_name_is_none(self):
                """
                Asserts that creating a user with a None last name in English and Hebrew raises an IntegrityError for the not-null constraint on the last_name_en column.
                """
                with self.assertRaises(IntegrityError) as cm:
                    user = DefaultUserFactory(last_name_en=None, last_name_he=None)
                    user.save_user_and_profile()
                self.assertIn(member=self._not_null_constraint_error_message_by_column_and_relation(column="last_name_en", relation="accounts_user"), container=str(cm.exception))

            def test_first_name_and_last_name_are_long(self):
                """
                Asserts that a first and last name of 200 characters in English exceed the maximum length (150) for every supported language's first_name and last_name fields, raising a ValidationError.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(first_name_en="a" * 200, last_name_en="b" * 200)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2={field_name: [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=150, value_length=200)] for field_name in ['first_name_en', 'first_name_fr', 'first_name_de', 'first_name_es', 'first_name_pt', 'first_name_it', 'first_name_nl', 'first_name_ja', 'first_name_ru', 'first_name_zh', 'first_name_pl', 'first_name_fa', 'first_name_he', 'first_name_ko', 'first_name_ar', 'first_name_id', 'first_name_uk', 'first_name_tr', 'first_name_vi', 'first_name_cs', 'first_name_sv', 'first_name_fi', 'first_name_hu', 'first_name_th', 'first_name_el', 'first_name_ms', 'first_name_sr', 'first_name_ro', 'first_name_bn', 'first_name_ca', 'first_name_no', 'first_name_bg', 'first_name_da', 'first_name_sk', 'first_name_hi', 'first_name_et', 'first_name_hr', 'first_name_az', 'first_name_zh_yue', 'first_name_lt', 'first_name_sl', 'first_name_eu', 'first_name_hy', 'first_name_uz', 'first_name_ta', 'first_name_lv', 'last_name_en', 'last_name_fr', 'last_name_de', 'last_name_es', 'last_name_pt', 'last_name_it', 'last_name_nl', 'last_name_ja', 'last_name_ru', 'last_name_zh', 'last_name_pl', 'last_name_fa', 'last_name_he', 'last_name_ko', 'last_name_ar', 'last_name_id', 'last_name_uk', 'last_name_tr', 'last_name_vi', 'last_name_cs', 'last_name_sv', 'last_name_fi', 'last_name_hu', 'last_name_th', 'last_name_el', 'last_name_ms', 'last_name_sr', 'last_name_ro', 'last_name_bn', 'last_name_ca', 'last_name_no', 'last_name_bg', 'last_name_da', 'last_name_sk', 'last_name_hi', 'last_name_et', 'last_name_hr', 'last_name_az', 'last_name_zh_yue', 'last_name_lt', 'last_name_sl', 'last_name_eu', 'last_name_hy', 'last_name_uz', 'last_name_ta', 'last_name_lv']})

            def test_slug_and_username_min_length_ok_2(self):
                """
                Asserts that with the default MIN_SLUG_LENGTH, all slugs in SLUGS_TO_TEST_LIST that meet the minimum length are saved successfully.
                """
                self.assertEqual(first=User.settings.MIN_SLUG_LENGTH, second=6)
                test_settings = {
                    "expected_counts_tuple": (8, 0),
                }
                self.run_test_all_slugs_to_test_list(test_settings=test_settings)

            @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MIN_SLUG_LENGTH=tests_settings.OVERRIDE_USER_SETTINGS.MIN_SLUG_LENGTH))
            def test_slug_min_length_fail_username_min_length_ok(self):
                """
                Asserts that with an overridden, larger MIN_SLUG_LENGTH, only slugs in SLUGS_TO_TEST_LIST that meet the new minimum are saved successfully, and the rest fail.
                """
                self.assertEqual(first=User.settings.MIN_SLUG_LENGTH, second=60)
                test_settings = {
                    "expected_counts_tuple": (4, 4),
                }
                self.run_test_all_slugs_to_test_list(test_settings=test_settings)

            def test_slug_and_username_max_length_fail(self):
                """
                Asserts that a slug longer than MAX_SLUG_LENGTH/MAX_USERNAME_LENGTH raises a ValidationError.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='a' * 201)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=201))

            def test_slug_max_length_ok_username_max_length_fail_1(self):
                """
                Asserts that a slug within MAX_SLUG_LENGTH but a derived username exceeding MAX_USERNAME_LENGTH raises a ValidationError for both.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='b' * 200)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=200))

            def test_slug_max_length_ok_username_max_length_fail_2(self):
                """
                Asserts that a slug within MAX_SLUG_LENGTH but a derived username slightly over MAX_USERNAME_LENGTH raises a ValidationError for both.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='a' * 41)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=41))

            def test_slug_and_username_max_length_ok(self):
                """
                Asserts that a slug at exactly MAX_USERNAME_LENGTH saves successfully.
                """
                user = DefaultUserFactory(slug='a' * 40)
                user.save_user_and_profile()

            def test_star2000_is_valid_username(self):
                """
                Asserts that a username starting with 4 or more letters followed by digits ('star2000') is valid for a user.
                """
                user = DefaultUserFactory(slug='star2000', username='star2000')
                user.save_user_and_profile()

            def test_jennifer_is_valid_username(self):
                """
                Asserts that the username 'jennifer' (8 letters) is a valid regular (non-special) username for a user.
                """
                user = DefaultUserFactory(slug='jennifer')
                user.save_user_and_profile()

            def test_come2us_is_invalid_username(self):
                """
                Asserts that, unlike entities, a username starting with 4 or more letters followed by digits ('come2us') is invalid for a regular user, since it starts with fewer than 4 letters before a digit boundary check specific to users.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='come2us', username='come2us')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))

            def test_000000_is_invalid_username(self):
                """
                Asserts that a username consisting only of digits ('000000') is invalid for a user since it doesn't start with 4 or more letters.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='0' * 6, username='0' * 6)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))

            def test_0test1_is_invalid_username(self):
                """
                Asserts that a username starting with a digit ('0test1') is invalid for a user since it doesn't start with 4 or more letters.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='0-test-1', username='0test1')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))

            def test_slug_and_username_dont_match_but_valid(self):
                """
                Asserts that a valid slug and valid username that don't parse to the same value raise a ValidationError for mismatch.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='star2001', username='star2000')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._slug_does_not_parse_to_username_errors_dict(model=User))

            def test_slug_and_username_dont_match_and_invalid(self):
                """
                Asserts that a slug and username that are both invalid and don't match each other raise a ValidationError for the username not starting with 4 or more letters.
                """
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='0-test-2', username='0test1')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))

            def test_user_can_change_password_1(self):
                """
                Asserts that a user can change their password to a new 8-character password, and only the new password (not the original or an incorrect similar one) authenticates afterwards.
                """
                new_password = 'abcdef12'
                incorrect_new_password = '7' * 8
                self.assertEqual(first=len(new_password), second=8)
                user = DefaultUserFactory()
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                user.set_password(raw_password=new_password)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=incorrect_new_password), expr2=False)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=False)

            def test_user_can_change_password_2(self):
                """
                Asserts that a user can change their password to a new 120-character password, and only the new password (not the original or an incorrect similar one) authenticates afterwards.
                """
                new_password = 'abcdef' + ('8' * 114)
                incorrect_new_password = 'abcde8' + ('8' * 114)
                self.assertEqual(first=len(new_password), second=120)
                user = DefaultUserFactory()
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                user.set_password(raw_password=new_password)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=incorrect_new_password), expr2=False)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=False)

            def test_user_can_change_password_3(self):
                """
                Asserts that a user can change their password to a new 120-character password containing slashes, and only the new password (not the original or an incorrect similar one) authenticates afterwards.
                """
                new_password = 'abcd//' + ('8' * 114)
                incorrect_new_password = 'abcd/?' + ('8' * 114)
                self.assertEqual(first=len(new_password), second=120)
                user = DefaultUserFactory()
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                user.set_password(raw_password=new_password)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=incorrect_new_password), expr2=False)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=False)

            def test_password_too_short_exception(self):
                """
                Asserts that setting a password shorter than the minimum length (6 characters) raises a ValidationError and leaves the original password unchanged.
                """
                new_password = 'abcdef'
                self.assertEqual(first=len(new_password), second=6)
                user = DefaultUserFactory()
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                with self.assertRaises(ValidationError) as cm:
                    user.set_password(raw_password=new_password)
                self.assertListEqual(list1=list(cm.exception), list2=[self._password_too_short_error_message])
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=False)

            def test_password_too_long_exception(self):
                """
                Asserts that setting a password longer than the maximum length (121 characters) raises a ValidationError and leaves the original password unchanged.
                """
                new_password = 'abcdef' + ('8' * 115)
                self.assertEqual(first=len(new_password), second=121)
                user = DefaultUserFactory()
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                with self.assertRaises(ValidationError) as cm:
                    user.set_password(raw_password=new_password)
                self.assertListEqual(list1=list(cm.exception), list2=[self._password_too_long_error_message])
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=False)

            def test_password_not_enough_unique_characters_exception(self):
                """
                Asserts that setting a password with fewer than 6 unique characters raises a ValidationError and leaves the original password unchanged.
                """
                new_password = '1234' * 2
                self.assertEqual(first=len(new_password), second=8)
                user = DefaultUserFactory()
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                with self.assertRaises(ValidationError) as cm:
                    user.set_password(raw_password=new_password)
                self.assertListEqual(list1=list(cm.exception), list2=[self._your_password_must_contain_at_least_6_unique_characters_error_message])
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=False)

            def test_password_too_short_and_not_enough_unique_characters_exception(self):
                """
                Asserts that setting a password that is both too short and has too few unique characters raises a ValidationError with both error messages, and leaves the original password unchanged.
                """
                new_password = '8' * 3
                self.assertEqual(first=len(new_password), second=3)
                user = DefaultUserFactory()
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                with self.assertRaises(ValidationError) as cm:
                    user.set_password(raw_password=new_password)
                self.assertListEqual(list1=list(cm.exception), list2=[self._password_too_short_error_message, self._your_password_must_contain_at_least_6_unique_characters_error_message])
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=False)

            def test_password_too_long_and_not_enough_unique_characters_exception(self):
                """
                Asserts that setting a password that is both too long and has too few unique characters raises a ValidationError with both error messages, and leaves the original password unchanged.
                """
                new_password = '8' * 121
                self.assertEqual(first=len(new_password), second=121)
                user = DefaultUserFactory()
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                with self.assertRaises(ValidationError) as cm:
                    user.set_password(raw_password=new_password)
                self.assertListEqual(list1=list(cm.exception), list2=[self._password_too_long_error_message, self._your_password_must_contain_at_least_6_unique_characters_error_message])
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=False)

            def test_check_password_skip_password_hash_upgrade_if_doesnt_pass_password_validators_1(self):
                """
                Runs the hash-upgrade-skip test with 160000 iterations for a password that doesn't pass validators.
                """
                self.run_test_check_password_skip_password_hash_upgrade_if_doesnt_pass_password_validators(iterations=160000)

            def test_check_password_skip_password_hash_upgrade_if_doesnt_pass_password_validators_2(self):
                """
                Runs the hash-upgrade-skip test with 36000 iterations for a password that doesn't pass validators.
                """
                self.run_test_check_password_skip_password_hash_upgrade_if_doesnt_pass_password_validators(iterations=36000)

            def test_check_password_doesnt_skip_password_hash_upgrade_if_passes_password_validators_1(self):
                """
                Runs the hash-upgrade-doesn't-skip test with 160000 iterations for a password that passes validators.
                """
                self.run_test_check_password_doesnt_skip_password_hash_upgrade_if_passes_password_validators(iterations=160000)

            def test_check_password_doesnt_skip_password_hash_upgrade_if_passes_password_validators_2(self):
                """
                Runs the hash-upgrade-doesn't-skip test with 36000 iterations for a password that passes validators.
                """
                self.run_test_check_password_doesnt_skip_password_hash_upgrade_if_passes_password_validators(iterations=36000)

            def test_check_password_skip_password_hash_upgrade_if_iterations_are_big_enough_1(self):
                """
                Runs the hash-upgrade-skip-if-iterations-big-enough test with 160001 iterations.
                """
                self.run_test_check_password_skip_password_hash_upgrade_if_iterations_are_big_enough(iterations=160001)

            def test_check_password_skip_password_hash_upgrade_if_iterations_are_big_enough_2(self):
                """
                Runs the hash-upgrade-skip-if-iterations-big-enough test with 170000 iterations.
                """
                self.run_test_check_password_skip_password_hash_upgrade_if_iterations_are_big_enough(iterations=170000)

            def test_check_password_skip_password_hash_upgrade_if_iterations_are_big_enough_3(self):
                """
                Runs the hash-upgrade-skip-if-iterations-big-enough test with 390000 iterations.
                """
                self.run_test_check_password_skip_password_hash_upgrade_if_iterations_are_big_enough(iterations=390000)

            def test_user_names_in_both_websites(self):
                """
                Asserts that a user's full_name, get_full_name(), first and last name combinations, and localized name formatting are correct and consistent across Speedy Net and Speedy Match for users of various activation states.
                """
                for user in [DefaultUserFactory(), InactiveUserFactory(), SpeedyNetInactiveUserFactory(), ActiveUserFactory()]:
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
                        raise NotImplementedError("Unsupported SITE_ID.")

            def test_user_profile_last_visit_str(self):
                """
                This test depends on the time zone of the computer running the tests. If you run them on your local computer, and your local date is different from the current date at UTC, then this test will be skipped with a reason. On the website, it might display "Today" even if the last visit date is "tomorrow" or "yesterday", depending on the server's time zone.
                """
                user_1 = ActiveUserFactory()
                # If user_1.profile.last_visit_str is not "Today", skip this test.
                if (not (user_1.profile.last_visit_str == {'en': "Today", 'fr': "Aujourd’hui", 'de': "Heute", 'es': "Hoy", 'pt': "Hoje", 'it': "Oggi", 'nl': "Vandaag", 'sv': "Idag", 'ko': "오늘", 'fi': "Tänään", 'he': "היום"}[self.language_code])):
                    self.assertEqual(first=user_1.profile.last_visit_str, second={'en': "Yesterday", 'fr': "Hier", 'de': "Gestern", 'es': "Ayer", 'pt': "Ontem", 'it': "Ieri", 'nl': "Gisteren", 'sv': "Igår", 'ko': "어제", 'fi': "Eilen", 'he': "אתמול"}[self.language_code])
                    print("{}::Skipped test - user_1.profile.last_visit_str is \"Yesterday\", dates don't match.".format(self.id()))
                    self.skipTest(reason="Skipped test - dates don't match.")
                    return

                self.assertEqual(first=user_1.profile.last_visit_str, second={'en': "Today", 'fr': "Aujourd’hui", 'de': "Heute", 'es': "Hoy", 'pt': "Hoje", 'it': "Oggi", 'nl': "Vandaag", 'sv': "Idag", 'ko': "오늘", 'fi': "Tänään", 'he': "היום"}[self.language_code])
                user_2 = ActiveUserFactory()
                user_2.profile.last_visit -= relativedelta(days=1)
                user_2.save_user_and_profile()
                # If user_2.profile.last_visit_str is not "Yesterday", skip this test.
                if (not (user_2.profile.last_visit_str == {'en': "Yesterday", 'fr': "Hier", 'de': "Gestern", 'es': "Ayer", 'pt': "Ontem", 'it': "Ieri", 'nl': "Gisteren", 'sv': "Igår", 'ko': "어제", 'fi': "Eilen", 'he': "אתמול"}[self.language_code])):
                    self.assertEqual(first=user_2.profile.last_visit_str, second={'en': "Today", 'fr': "Aujourd’hui", 'de': "Heute", 'es': "Hoy", 'pt': "Hoje", 'it': "Oggi", 'nl': "Vandaag", 'sv': "Idag", 'ko': "오늘", 'fi': "Tänään", 'he': "היום"}[self.language_code])
                    print("{}::Skipped test - user_2.profile.last_visit_str is \"Today\", dates don't match.".format(self.id()))
                    self.skipTest(reason="Skipped test - dates don't match.")
                    return

                self.assertEqual(first=user_2.profile.last_visit_str, second={'en': "Yesterday", 'fr': "Hier", 'de': "Gestern", 'es': "Ayer", 'pt': "Ontem", 'it': "Ieri", 'nl': "Gisteren", 'sv': "Igår", 'ko': "어제", 'fi': "Eilen", 'he': "אתמול"}[self.language_code])
                user_3 = ActiveUserFactory()
                user_3.profile.last_visit -= relativedelta(days=2)
                user_3.save_user_and_profile()
                self.assertIs(expr1={'en': "(2\xa0days\xa0ago)", 'fr': "(il\xa0y\xa0a\xa02\xa0jours)", 'de': "(vor\xa02\xa0Tage)", 'es': "(hace\xa02\xa0días)", 'pt': "(há\xa02\xa0dias)", 'it': "(2\xa0giorni\xa0fa)", 'nl': "(2\xa0dagen\xa0geleden)", 'sv': "(2\xa0dagar\xa0sedan)", 'ko': "(2일\xa0전에)", 'fi': "(2\xa0päivää\xa0sitten)", 'he': "(לפני\xa0יומיים)"}[self.language_code] in user_3.profile.last_visit_str, expr2=True)
                user_4 = ActiveUserFactory()
                user_4.profile.last_visit -= relativedelta(days=3)
                user_4.save_user_and_profile()
                self.assertIs(expr1={'en': "(3\xa0days\xa0ago)", 'fr': "(il\xa0y\xa0a\xa03\xa0jours)", 'de': "(vor\xa03\xa0Tage)", 'es': "(hace\xa03\xa0días)", 'pt': "(há\xa03\xa0dias)", 'it': "(3\xa0giorni\xa0fa)", 'nl': "(3\xa0dagen\xa0geleden)", 'sv': "(3\xa0dagar\xa0sedan)", 'ko': "(3일\xa0전에)", 'fi': "(3\xa0päivää\xa0sitten)", 'he': "(לפני\xa03\xa0ימים)"}[self.language_code] in user_4.profile.last_visit_str, expr2=True)
                user_5 = ActiveUserFactory()
                user_5.profile.last_visit -= relativedelta(weeks=1)
                user_5.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0week\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0semaine)", 'de': "(vor\xa01\xa0Woche)", 'es': "(hace\xa01\xa0semana)", 'pt': "(há\xa01\xa0semana)", 'it': "(1\xa0settimana\xa0fa)", 'nl': "(1\xa0week\xa0geleden)", 'sv': "(1\xa0vecka\xa0sedan)", 'ko': "(1주\xa0전에)", 'fi': "(1\xa0viikko\xa0sitten)", 'he': "(לפני\xa0שבוע)"}[self.language_code] in user_5.profile.last_visit_str, expr2=True)
                user_6 = ActiveUserFactory()
                user_6.profile.last_visit -= relativedelta(days=8)
                user_6.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0week, 1\xa0day\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0semaine, 1\xa0jour)", 'de': "(vor\xa01\xa0Woche, 1\xa0Tag)", 'es': "(hace\xa01\xa0semana, 1\xa0día)", 'pt': "(há\xa01\xa0semana, 1\xa0dia)", 'it': "(1\xa0settimana, 1\xa0giorno\xa0fa)", 'nl': "(1\xa0week, 1\xa0dag\xa0geleden)", 'sv': "(1\xa0vecka, 1\xa0dag\xa0sedan)", 'ko': "(1주, 1일\xa0전에)", 'fi': "(1\xa0viikko, 1\xa0päivä\xa0sitten)", 'he': "(לפני\xa0שבוע ויום)"}[self.language_code] in user_6.profile.last_visit_str, expr2=True)
                user_7 = ActiveUserFactory()
                user_7.profile.last_visit -= relativedelta(days=9)
                user_7.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0week, 2\xa0days\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0semaine, 2\xa0jours)", 'de': "(vor\xa01\xa0Woche, 2\xa0Tage)", 'es': "(hace\xa01\xa0semana, 2\xa0días)", 'pt': "(há\xa01\xa0semana, 2\xa0dias)", 'it': "(1\xa0settimana, 2\xa0giorni\xa0fa)", 'nl': "(1\xa0week, 2\xa0dagen\xa0geleden)", 'sv': "(1\xa0vecka, 2\xa0dagar\xa0sedan)", 'ko': "(1주, 2일\xa0전에)", 'fi': "(1\xa0viikko, 2\xa0päivää\xa0sitten)", 'he': "(לפני\xa0שבוע ויומיים)"}[self.language_code] in user_7.profile.last_visit_str, expr2=True)
                user_8 = ActiveUserFactory()
                user_8.profile.last_visit -= relativedelta(days=10)
                user_8.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0week, 3\xa0days\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0semaine, 3\xa0jours)", 'de': "(vor\xa01\xa0Woche, 3\xa0Tage)", 'es': "(hace\xa01\xa0semana, 3\xa0días)", 'pt': "(há\xa01\xa0semana, 3\xa0dias)", 'it': "(1\xa0settimana, 3\xa0giorni\xa0fa)", 'nl': "(1\xa0week, 3\xa0dagen\xa0geleden)", 'sv': "(1\xa0vecka, 3\xa0dagar\xa0sedan)", 'ko': "(1주, 3일\xa0전에)", 'fi': "(1\xa0viikko, 3\xa0päivää\xa0sitten)", 'he': "(לפני\xa0שבוע ו-3\xa0ימים)"}[self.language_code] in user_8.profile.last_visit_str, expr2=True)
                user_9 = ActiveUserFactory()
                user_9.profile.last_visit -= relativedelta(weeks=2)
                user_9.save_user_and_profile()
                self.assertIs(expr1={'en': "(2\xa0weeks\xa0ago)", 'fr': "(il\xa0y\xa0a\xa02\xa0semaines)", 'de': "(vor\xa02\xa0Wochen)", 'es': "(hace\xa02\xa0semanas)", 'pt': "(há\xa02\xa0semanas)", 'it': "(2\xa0settimane\xa0fa)", 'nl': "(2\xa0weken\xa0geleden)", 'sv': "(2\xa0veckor\xa0sedan)", 'ko': "(2주\xa0전에)", 'fi': "(2\xa0viikkoa\xa0sitten)", 'he': "(לפני\xa0שבועיים)"}[self.language_code] in user_9.profile.last_visit_str, expr2=True)
                user_10 = ActiveUserFactory()
                user_10.profile.last_visit -= relativedelta(months=1)
                user_10.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0month\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0mois)", 'de': "(vor\xa01\xa0Monat)", 'es': "(hace\xa01\xa0mes)", 'pt': "(há\xa01\xa0mês)", 'it': "(1\xa0mese\xa0fa)", 'nl': "(1\xa0maand\xa0geleden)", 'sv': "(1\xa0månad\xa0sedan)", 'ko': "(1개월\xa0전에)", 'fi': "(1\xa0kuukausi\xa0sitten)", 'he': "(לפני\xa0חודש)"}[self.language_code] in user_10.profile.last_visit_str, expr2=True)
                user_11 = ActiveUserFactory()
                user_11.profile.last_visit -= relativedelta(months=2)
                user_11.save_user_and_profile()
                self.assertIs(expr1={'en': "(2\xa0months\xa0ago)", 'fr': "(il\xa0y\xa0a\xa02\xa0mois)", 'de': "(vor\xa02\xa0Monate)", 'es': "(hace\xa02\xa0meses)", 'pt': "(há\xa02\xa0meses)", 'it': "(2\xa0mesi\xa0fa)", 'nl': "(2\xa0maanden\xa0geleden)", 'sv': "(2\xa0månader\xa0sedan)", 'ko': "(2개월\xa0전에)", 'fi': "(2\xa0kuukautta\xa0\xa0sitten)", 'he': "(לפני\xa0חודשיים)"}[self.language_code] in user_11.profile.last_visit_str, expr2=True)
                user_12 = ActiveUserFactory()
                user_12.profile.last_visit -= relativedelta(months=2, weeks=1)
                user_12.save_user_and_profile()
                self.assertIs(expr1={'en': "(2\xa0months, 1\xa0week\xa0ago)", 'fr': "(il\xa0y\xa0a\xa02\xa0mois, 1\xa0semaine)", 'de': "(vor\xa02\xa0Monate, 1\xa0Woche)", 'es': "(hace\xa02\xa0meses, 1\xa0semana)", 'pt': "(há\xa02\xa0meses, 1\xa0semana)", 'it': "(2\xa0mesi, 1\xa0settimana\xa0fa)", 'nl': "(2\xa0maanden, 1\xa0week\xa0geleden)", 'sv': "(2\xa0månader, 1\xa0vecka\xa0sedan)", 'ko': "(2개월, 1주\xa0전에)", 'fi': "(2\xa0kuukautta\xa0, 1\xa0viikko\xa0sitten)", 'he': "(לפני\xa0חודשיים ושבוע)"}[self.language_code] in user_12.profile.last_visit_str, expr2=True)
                user_13 = ActiveUserFactory()
                user_13.profile.last_visit -= relativedelta(months=2, weeks=2)
                user_13.save_user_and_profile()
                self.assertIs(expr1={'en': "(2\xa0months, 2\xa0weeks\xa0ago)", 'fr': "(il\xa0y\xa0a\xa02\xa0mois, 2\xa0semaines)", 'de': "(vor\xa02\xa0Monate, 2\xa0Wochen)", 'es': "(hace\xa02\xa0meses, 2\xa0semanas)", 'pt': "(há\xa02\xa0meses, 2\xa0semanas)", 'it': "(2\xa0mesi, 2\xa0settimane\xa0fa)", 'nl': "(2\xa0maanden, 2\xa0weken\xa0geleden)", 'sv': "(2\xa0månader, 2\xa0veckor\xa0sedan)", 'ko': "(2개월, 2주\xa0전에)", 'fi': "(2\xa0kuukautta\xa0, 2\xa0viikkoa\xa0sitten)", 'he': "(לפני\xa0חודשיים ושבועיים)"}[self.language_code] in user_13.profile.last_visit_str, expr2=True)
                user_14 = ActiveUserFactory()
                user_14.profile.last_visit -= relativedelta(months=3)
                user_14.save_user_and_profile()
                self.assertIs(expr1={'en': "(3\xa0months\xa0ago)", 'fr': "(il\xa0y\xa0a\xa03\xa0mois)", 'de': "(vor\xa03\xa0Monate)", 'es': "(hace\xa03\xa0meses)", 'pt': "(há\xa03\xa0meses)", 'it': "(3\xa0mesi\xa0fa)", 'nl': "(3\xa0maanden\xa0geleden)", 'sv': "(3\xa0månader\xa0sedan)", 'ko': "(3개월\xa0전에)", 'fi': "(3\xa0kuukautta\xa0\xa0sitten)", 'he': "(לפני\xa03\xa0חודשים)"}[self.language_code] in user_14.profile.last_visit_str, expr2=True)
                user_15 = ActiveUserFactory()
                user_15.profile.last_visit -= relativedelta(months=3, weeks=1)
                user_15.save_user_and_profile()
                self.assertIs(expr1={'en': "(3\xa0months, 1\xa0week\xa0ago)", 'fr': "(il\xa0y\xa0a\xa03\xa0mois, 1\xa0semaine)", 'de': "(vor\xa03\xa0Monate, 1\xa0Woche)", 'es': "(hace\xa03\xa0meses, 1\xa0semana)", 'pt': "(há\xa03\xa0meses, 1\xa0semana)", 'it': "(3\xa0mesi, 1\xa0settimana\xa0fa)", 'nl': "(3\xa0maanden, 1\xa0week\xa0geleden)", 'sv': "(3\xa0månader, 1\xa0vecka\xa0sedan)", 'ko': "(3개월, 1주\xa0전에)", 'fi': "(3\xa0kuukautta\xa0, 1\xa0viikko\xa0sitten)", 'he': "(לפני\xa03\xa0חודשים ושבוע)"}[self.language_code] in user_15.profile.last_visit_str, expr2=True)
                user_16 = ActiveUserFactory()
                user_16.profile.last_visit -= relativedelta(months=3, weeks=2)
                user_16.save_user_and_profile()
                self.assertIs(expr1={'en': "(3\xa0months, 2\xa0weeks\xa0ago)", 'fr': "(il\xa0y\xa0a\xa03\xa0mois, 2\xa0semaines)", 'de': "(vor\xa03\xa0Monate, 2\xa0Wochen)", 'es': "(hace\xa03\xa0meses, 2\xa0semanas)", 'pt': "(há\xa03\xa0meses, 2\xa0semanas)", 'it': "(3\xa0mesi, 2\xa0settimane\xa0fa)", 'nl': "(3\xa0maanden, 2\xa0weken\xa0geleden)", 'sv': "(3\xa0månader, 2\xa0veckor\xa0sedan)", 'ko': "(3개월, 2주\xa0전에)", 'fi': "(3\xa0kuukautta\xa0, 2\xa0viikkoa\xa0sitten)", 'he': "(לפני\xa03\xa0חודשים ושבועיים)"}[self.language_code] in user_16.profile.last_visit_str, expr2=True)
                user_17 = ActiveUserFactory()
                user_17.profile.last_visit -= relativedelta(years=1)
                user_17.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0year\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0année)", 'de': "(vor\xa01\xa0Jahr)", 'es': "(hace\xa01\xa0año)", 'pt': "(há\xa01\xa0ano)", 'it': "(1\xa0anno\xa0fa)", 'nl': "(1\xa0jaar\xa0geleden)", 'sv': "(1\xa0år\xa0sedan)", 'ko': "(1년\xa0전에)", 'fi': "(1\xa0vuosi\xa0sitten)", 'he': "(לפני\xa0שנה)"}[self.language_code] in user_17.profile.last_visit_str, expr2=True)
                user_18 = ActiveUserFactory()
                user_18.profile.last_visit -= relativedelta(years=1, weeks=1)
                user_18.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0year\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0année)", 'de': "(vor\xa01\xa0Jahr)", 'es': "(hace\xa01\xa0año)", 'pt': "(há\xa01\xa0ano)", 'it': "(1\xa0anno\xa0fa)", 'nl': "(1\xa0jaar\xa0geleden)", 'sv': "(1\xa0år\xa0sedan)", 'ko': "(1년\xa0전에)", 'fi': "(1\xa0vuosi\xa0sitten)", 'he': "(לפני\xa0שנה)"}[self.language_code] in user_18.profile.last_visit_str, expr2=True)
                user_19 = ActiveUserFactory()
                user_19.profile.last_visit -= relativedelta(years=1, months=1)
                user_19.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0year, 1\xa0month\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0année, 1\xa0mois)", 'de': "(vor\xa01\xa0Jahr, 1\xa0Monat)", 'es': "(hace\xa01\xa0año, 1\xa0mes)", 'pt': "(há\xa01\xa0ano, 1\xa0mês)", 'it': "(1\xa0anno, 1\xa0mese\xa0fa)", 'nl': "(1\xa0jaar, 1\xa0maand\xa0geleden)", 'sv': "(1\xa0år, 1\xa0månad\xa0sedan)", 'ko': "(1년, 1개월\xa0전에)", 'fi': "(1\xa0vuosi, 1\xa0kuukausi\xa0sitten)", 'he': "(לפני\xa0שנה וחודש)"}[self.language_code] in user_19.profile.last_visit_str, expr2=True)
                user_20 = ActiveUserFactory()
                user_20.profile.last_visit -= relativedelta(years=1, months=1, weeks=1)
                user_20.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0year, 1\xa0month\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0année, 1\xa0mois)", 'de': "(vor\xa01\xa0Jahr, 1\xa0Monat)", 'es': "(hace\xa01\xa0año, 1\xa0mes)", 'pt': "(há\xa01\xa0ano, 1\xa0mês)", 'it': "(1\xa0anno, 1\xa0mese\xa0fa)", 'nl': "(1\xa0jaar, 1\xa0maand\xa0geleden)", 'sv': "(1\xa0år, 1\xa0månad\xa0sedan)", 'ko': "(1년, 1개월\xa0전에)", 'fi': "(1\xa0vuosi, 1\xa0kuukausi\xa0sitten)", 'he': "(לפני\xa0שנה וחודש)"}[self.language_code] in user_20.profile.last_visit_str, expr2=True)
                user_21 = ActiveUserFactory()
                user_21.profile.last_visit -= relativedelta(years=2)
                user_21.save_user_and_profile()
                self.assertIs(expr1={'en': "(2\xa0years\xa0ago)", 'fr': "(il\xa0y\xa0a\xa02\xa0ans)", 'de': "(vor\xa02\xa0Jahre)", 'es': "(hace\xa02\xa0años)", 'pt': "(há\xa02\xa0anos)", 'it': "(2\xa0anni\xa0fa)", 'nl': "(2\xa0jaar\xa0geleden)", 'sv': "(2\xa0år\xa0sedan)", 'ko': "(2년\xa0전에)", 'fi': "(2\xa0vuotta\xa0sitten)", 'he': "(לפני\xa0שנתיים)"}[self.language_code] in user_21.profile.last_visit_str, expr2=True)
                user_22 = ActiveUserFactory()
                user_22.profile.last_visit -= relativedelta(years=2, weeks=2)
                user_22.save_user_and_profile()
                self.assertIs(expr1={'en': "(2\xa0years\xa0ago)", 'fr': "(il\xa0y\xa0a\xa02\xa0ans)", 'de': "(vor\xa02\xa0Jahre)", 'es': "(hace\xa02\xa0años)", 'pt': "(há\xa02\xa0anos)", 'it': "(2\xa0anni\xa0fa)", 'nl': "(2\xa0jaar\xa0geleden)", 'sv': "(2\xa0år\xa0sedan)", 'ko': "(2년\xa0전에)", 'fi': "(2\xa0vuotta\xa0sitten)", 'he': "(לפני\xa0שנתיים)"}[self.language_code] in user_22.profile.last_visit_str, expr2=True)
                user_23 = ActiveUserFactory()
                user_23.profile.last_visit -= (relativedelta(years=1) - relativedelta(weeks=1))
                user_23.save_user_and_profile()
                self.assertIs(expr1={'en': "(11\xa0months, 3\xa0weeks\xa0ago)", 'fr': "(il\xa0y\xa0a\xa011\xa0mois, 3\xa0semaines)", 'de': "(vor\xa011\xa0Monate, 3\xa0Wochen)", 'es': "(hace\xa011\xa0meses, 3\xa0semanas)", 'pt': "(há\xa011\xa0meses, 3\xa0semanas)", 'it': "(11\xa0mesi, 3\xa0settimane\xa0fa)", 'nl': "(11\xa0maanden, 3\xa0weken\xa0geleden)", 'sv': "(11\xa0månader, 3\xa0veckor\xa0sedan)", 'ko': "(11개월, 3주\xa0전에)", 'fi': "(11\xa0kuukautta\xa0, 3\xa0viikkoa\xa0sitten)", 'he': "(לפני\xa011\xa0חודשים ו-3\xa0שבועות)"}[self.language_code] in user_23.profile.last_visit_str, expr2=True)
                user_24 = ActiveUserFactory()
                user_24.profile.last_visit -= (relativedelta(years=1) - relativedelta(weeks=2))
                user_24.save_user_and_profile()
                self.assertIs(expr1={'en': "(11\xa0months, 2\xa0weeks\xa0ago)", 'fr': "(il\xa0y\xa0a\xa011\xa0mois, 2\xa0semaines)", 'de': "(vor\xa011\xa0Monate, 2\xa0Wochen)", 'es': "(hace\xa011\xa0meses, 2\xa0semanas)", 'pt': "(há\xa011\xa0meses, 2\xa0semanas)", 'it': "(11\xa0mesi, 2\xa0settimane\xa0fa)", 'nl': "(11\xa0maanden, 2\xa0weken\xa0geleden)", 'sv': "(11\xa0månader, 2\xa0veckor\xa0sedan)", 'ko': "(11개월, 2주\xa0전에)", 'fi': "(11\xa0kuukautta\xa0, 2\xa0viikkoa\xa0sitten)", 'he': "(לפני\xa011\xa0חודשים ושבועיים)"}[self.language_code] in user_24.profile.last_visit_str, expr2=True)
                user_25 = ActiveUserFactory()
                user_25.profile.last_visit -= (relativedelta(years=2) - relativedelta(weeks=2))
                user_25.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0year, 11\xa0months\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0année, 11\xa0mois)", 'de': "(vor\xa01\xa0Jahr, 11\xa0Monate)", 'es': "(hace\xa01\xa0año, 11\xa0meses)", 'pt': "(há\xa01\xa0ano, 11\xa0meses)", 'it': "(1\xa0anno, 11\xa0mesi\xa0fa)", 'nl': "(1\xa0jaar, 11\xa0maanden\xa0geleden)", 'sv': "(1\xa0år, 11\xa0månader\xa0sedan)", 'ko': "(1년, 11개월\xa0전에)", 'fi': "(1\xa0vuosi, 11\xa0kuukautta\xa0\xa0sitten)", 'he': "(לפני\xa0שנה ו-11\xa0חודשים)"}[self.language_code] in user_25.profile.last_visit_str, expr2=True)
                user_26 = ActiveUserFactory()
                user_26.profile.last_visit -= relativedelta(years=2, months=2, weeks=2)
                user_26.save_user_and_profile()
                self.assertIs(expr1={'en': "(2\xa0years, 2\xa0months\xa0ago)", 'fr': "(il\xa0y\xa0a\xa02\xa0ans, 2\xa0mois)", 'de': "(vor\xa02\xa0Jahre, 2\xa0Monate)", 'es': "(hace\xa02\xa0años, 2\xa0meses)", 'pt': "(há\xa02\xa0anos, 2\xa0meses)", 'it': "(2\xa0anni, 2\xa0mesi\xa0fa)", 'nl': "(2\xa0jaar, 2\xa0maanden\xa0geleden)", 'sv': "(2\xa0år, 2\xa0månader\xa0sedan)", 'ko': "(2년, 2개월\xa0전에)", 'fi': "(2\xa0vuotta, 2\xa0kuukautta\xa0\xa0sitten)", 'he': "(לפני\xa0שנתיים וחודשיים)"}[self.language_code] in user_26.profile.last_visit_str, expr2=True)

            def test_user_main_language_code(self):
                """
                Asserts that a user's main_language_code reflects 'en' by default and the active profile's language once activated, across activation, deactivation, and reactivation transitions on both sites.
                """
                user = DefaultUserFactory()
                self.assertEqual(first=user.main_language_code, second='en')
                user = InactiveUserFactory()
                self.assertEqual(first=user.main_language_code, second='en')
                user = SpeedyNetInactiveUserFactory()
                self.assertEqual(first=user.main_language_code, second='en')
                user = ActiveUserFactory()
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=user.main_language_code, second='en')
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=user.main_language_code, second=self.language_code)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                user.is_active = False
                user.save()
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.main_language_code, second='en')
                user.is_active = True
                user.save()
                user = User.objects.get(pk=user.pk)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=user.main_language_code, second='en')
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=user.main_language_code, second=self.language_code)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                user.speedy_net_profile.deactivate()
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.main_language_code, second='en')
                user.speedy_net_profile.activate()
                user = User.objects.get(pk=user.pk)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=user.main_language_code, second='en')
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=user.main_language_code, second=self.language_code)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    pass
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    user.speedy_match_profile.deactivate()
                    user = User.objects.get(pk=user.pk)
                    self.assertEqual(first=user.main_language_code, second='en')
                    step, error_messages = user.speedy_match_profile.validate_profile_and_activate()
                    self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                    user = User.objects.get(pk=user.pk)
                    self.assertEqual(first=user.main_language_code, second=self.language_code)
                    user.speedy_match_profile.deactivate()
                    user = User.objects.get(pk=user.pk)
                    self.assertEqual(first=user.main_language_code, second='en')
                    for i in range(0, 11):
                        user.speedy_match_profile.activation_step = i
                        user.speedy_match_profile.save()
                        user = User.objects.get(pk=user.pk)
                        if (i in range(7, 11)):
                            self.assertEqual(first=user.main_language_code, second=self.language_code)
                        else:
                            self.assertEqual(first=user.main_language_code, second='en')
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")

            def test_deleted_user_name(self):
                """
                Asserts that marking a deactivated user as deleted and clearing their photo sets their name to the site-specific deleted-user name.
                """
                user = DefaultUserFactory()
                user.speedy_net_profile.deactivate()
                self.assertEqual(first=user.is_active, second=False)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
                self.assertNotEqual(first=user.name, second=self._speedy_net_deleted_user_name)
                self.assertNotEqual(first=user.name, second=self._speedy_match_deleted_user_name)
                user._mark_as_deleted()
                user.photo = None
                user.save_user_and_profile()
                user = User.objects.get(pk=user.pk)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=user.name, second=self._speedy_net_deleted_user_name)
                    self.assertNotEqual(first=user.name, second=self._speedy_match_deleted_user_name)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=user.name, second=self._speedy_match_deleted_user_name)
                    self.assertNotEqual(first=user.name, second=self._speedy_net_deleted_user_name)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")

            def test_call_deactivate_race_condition_profile_should_not_become_active(self):
                """
                Asserts that saving a stale in-memory user after its profile was deactivated concurrently raises a ConcurrencyError and the profile remains inactive.
                """
                user = ActiveUserFactory()
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.profile.is_active, second=True)
                user_instance_2 = User.objects.get(pk=user.pk)
                user_instance_2.profile.deactivate()
                self.assertEqual(first=user_instance_2.profile.is_active, second=False)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=user_instance_2.is_active, second=False)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=user_instance_2.is_active, second=True)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                # Race condition: profile should not become active.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.profile.is_active, second=False)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=user.is_active, second=False)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=user.is_active, second=True)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")

            def test_call_deactivate_like_moderate_unmoderated_photos_race_condition_and_reactivate(self):
                """
                Asserts that deactivating a profile concurrently (while moderating out an unmoderated photo) raises a ConcurrencyError on the stale instance, and that the profile can later be properly reactivated (with a moderated profile picture where required).
                """
                user = ActiveUserFactory()
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.profile.is_active, second=True)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    pass
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=user.profile.activation_step, second=len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS))
                    self.assertEqual(first=user.profile.activation_step, second=10)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                user_instance_2 = User.objects.get(pk=user.pk)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertIs(expr1=user_instance_2.photo is None, expr2=True)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertIs(expr1=user_instance_2.photo is None, expr2=False)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                if (not (user_instance_2.photo is None)):
                    image = user_instance_2.photo
                    image.visible_on_website = False
                    image.speedy_image_moderation_time = now()
                    image.aws_image_moderation_time = now()
                    image.save()
                user_instance_2.photo = None
                user_instance_2.profile.deactivate()
                user_instance_2.save_user_and_profile()
                self.assertEqual(first=user_instance_2.profile.is_active, second=False)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=user_instance_2.is_active, second=False)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=user_instance_2.profile.activation_step, second=2)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                # Race condition: profile should not become active.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.profile.is_active, second=False)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=user.is_active, second=False)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=user.profile.activation_step, second=2)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                # Reactivate.
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    user_instance_2.profile.activate()
                    self.assertEqual(first=user_instance_2.is_active, second=True)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    image.visible_on_website = True
                    image.save()
                    # Check that the user cannot be activated without a profile picture.
                    step, error_messages = user_instance_2.profile.validate_profile_and_activate(commit=False)
                    self.assertEqual(first=step, second=2)
                    self.assertListEqual(list1=error_messages, list2=["['{expected_error_message}']".format(expected_error_message=self._a_profile_picture_is_required_error_message).replace("\xa0", "\\xa0")])
                    # Activate the user with a profile picture.
                    user_instance_2.photo = image
                    user_instance_2.save_user_and_profile()
                    step, error_messages = user_instance_2.profile.validate_profile_and_activate()
                    self.assert_step_and_error_messages_ok(step=step, error_messages=error_messages)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                self.assertEqual(first=user_instance_2.profile.is_active, second=True)
                # Race condition: profile should not become inactive.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.profile.is_active, second=True)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=user.is_active, second=True)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=user.profile.activation_step, second=len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS))
                    self.assertEqual(first=user.profile.activation_step, second=10)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")

            def test_call_set_is_active_race_condition_user_model_should_not_change(self):
                """
                Asserts that saving a stale in-memory user after is_active was changed concurrently raises a ConcurrencyError and leaves is_active unchanged.
                """
                user = ActiveUserFactory()
                self.assertEqual(first=user.is_active, second=True)
                user_instance_2 = User.objects.get(pk=user.pk)
                user_instance_2.is_active = False
                user_instance_2.save()
                self.assertEqual(first=user_instance_2.is_active, second=False)
                # Race condition: is_active should not change.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.is_active, second=False)
                user_instance_2.is_active = True
                user_instance_2.save()
                self.assertEqual(first=user_instance_2.is_active, second=True)
                # Race condition: is_active should not change.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.is_active, second=True)

            def test_call_set_is_deleted_race_condition_user_model_should_not_change(self):
                """
                Asserts that saving a stale in-memory user after is_deleted was changed concurrently raises a ConcurrencyError and leaves is_deleted and is_deleted_time unchanged.
                """
                user = ActiveUserFactory()
                self.assertIs(expr1=user.is_deleted, expr2=False)
                self.assertIs(expr1=user.is_deleted_time is None, expr2=True)
                user_instance_2 = User.objects.get(pk=user.pk)
                user_instance_2._mark_as_deleted()
                self.assertIs(expr1=user_instance_2.is_deleted, expr2=True)
                self.assertIs(expr1=user_instance_2.is_deleted_time is None, expr2=False)
                # Race condition: is_deleted should not change.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertIs(expr1=user.is_deleted, expr2=True)
                self.assertIs(expr1=user.is_deleted_time is None, expr2=False)
                user_instance_2.is_deleted = False
                user_instance_2.is_deleted_time = None
                user_instance_2.save()
                self.assertIs(expr1=user_instance_2.is_deleted, expr2=False)
                self.assertIs(expr1=user_instance_2.is_deleted_time is None, expr2=True)
                # Race condition: is_deleted should not change.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertIs(expr1=user.is_deleted, expr2=False)
                self.assertIs(expr1=user.is_deleted_time is None, expr2=True)

            def test_call_set_username_and_slug_race_condition_user_model_should_not_change_1(self):
                """
                Runs the username/slug race-condition helper with test_choice=1.
                """
                self.run_test_call_set_username_and_slug_race_condition_user_model_should_not_change(test_choice=1)

            def test_call_set_username_and_slug_race_condition_user_model_should_not_change_2(self):
                """
                Runs the username/slug race-condition helper with test_choice=2.
                """
                self.run_test_call_set_username_and_slug_race_condition_user_model_should_not_change(test_choice=2)

            def test_call_set_is_staff_and_is_superuser_race_condition_user_model_should_not_change(self):
                """
                Asserts that saving a stale in-memory user after is_staff and is_superuser were changed concurrently raises a ConcurrencyError and leaves both fields unchanged.
                """
                user = ActiveUserFactory()
                self.assertEqual(first=user.is_staff, second=False)
                self.assertEqual(first=user.is_superuser, second=False)
                user_instance_2 = User.objects.get(pk=user.pk)
                user_instance_2.is_staff = True
                user_instance_2.is_superuser = True
                user_instance_2.save()
                self.assertEqual(first=user_instance_2.is_staff, second=True)
                self.assertEqual(first=user_instance_2.is_superuser, second=True)
                # Race condition: is_staff and is_superuser should not change.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.is_staff, second=True)
                self.assertEqual(first=user.is_superuser, second=True)
                user_instance_2.is_staff = False
                user_instance_2.is_superuser = False
                user_instance_2.save()
                self.assertEqual(first=user_instance_2.is_staff, second=False)
                self.assertEqual(first=user_instance_2.is_superuser, second=False)
                # Race condition: is_staff and is_superuser should not change.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.is_staff, second=False)
                self.assertEqual(first=user.is_superuser, second=False)

            def test_call_set_password_race_condition_user_model_should_not_change(self):
                """
                Asserts that saving a stale in-memory user after its password was changed concurrently (to unusable, then to a new password, multiple times) raises a ConcurrencyError and leaves the password unchanged.
                """
                user = ActiveUserFactory()
                self.assertIs(expr1=(user.has_usable_password() is True), expr2=True)
                user_instance_2 = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.password, second=user_instance_2.password)
                user_instance_2.set_unusable_password()
                user_instance_2.save()
                self.assertIs(expr1=(user_instance_2.has_usable_password() is False), expr2=True)
                self.assertNotEqual(first=user.password, second=user_instance_2.password)
                # Race condition: password should not change.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertIs(expr1=(user.has_usable_password() is False), expr2=True)
                self.assertEqual(first=user.password, second=user_instance_2.password)
                user_instance_2 = User.objects.get(pk=user.pk)
                user_instance_2.set_password(raw_password="aabbccddef12")
                user_instance_2.save()
                self.assertIs(expr1=(user_instance_2.has_usable_password() is True), expr2=True)
                self.assertNotEqual(first=user.password, second=user_instance_2.password)
                # Race condition: password should not change.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertIs(expr1=(user.has_usable_password() is True), expr2=True)
                self.assertEqual(first=user.password, second=user_instance_2.password)
                user_instance_2 = User.objects.get(pk=user.pk)
                user_instance_2.set_password(raw_password="abcdef34ab!!")
                user_instance_2.save()
                self.assertIs(expr1=(user_instance_2.has_usable_password() is True), expr2=True)
                self.assertNotEqual(first=user.password, second=user_instance_2.password)
                # Race condition: password should not change.
                with self.assertRaises(ConcurrencyError) as cm:
                    user.save_user_and_profile()
                self.assertEqual(first=str(cm.exception), second="Update did not affect any rows.")
                user = User.objects.get(pk=user.pk)
                self.assertIs(expr1=(user.has_usable_password() is True), expr2=True)
                self.assertEqual(first=user.password, second=user_instance_2.password)


        @only_on_sites_with_login
        class UserAllMainLanguagesEnglishTestCase(UserTestCaseMixin, SiteTestCase):
            """
            Tests the User model, for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class UserAllMainLanguagesFrenchTestCase(UserTestCaseMixin, SiteTestCase):
            """
            Tests the User model, for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class UserAllMainLanguagesGermanTestCase(UserTestCaseMixin, SiteTestCase):
            """
            Tests the User model, for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class UserAllMainLanguagesSpanishTestCase(UserTestCaseMixin, SiteTestCase):
            """
            Tests the User model, for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class UserAllMainLanguagesPortugueseTestCase(UserTestCaseMixin, SiteTestCase):
            """
            Tests the User model, for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class UserAllMainLanguagesItalianTestCase(UserTestCaseMixin, SiteTestCase):
            """
            Tests the User model, for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class UserAllMainLanguagesDutchTestCase(UserTestCaseMixin, SiteTestCase):
            """
            Tests the User model, for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class UserAllMainLanguagesHebrewTestCase(UserTestCaseMixin, SiteTestCase):
            """
            Tests the User model, for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        # @only_on_sites_with_login
        # class UserAllLanguagesEnglishTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='en')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='fr')
        # class UserAllLanguagesFrenchTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='fr')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='de')
        # class UserAllLanguagesGermanTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='de')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='es')
        # class UserAllLanguagesSpanishTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='es')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='pt')
        # class UserAllLanguagesPortugueseTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='pt')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='it')
        # class UserAllLanguagesItalianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='it')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='nl')
        # class UserAllLanguagesDutchTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='nl')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='ja')
        # class UserAllLanguagesJapaneseTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='ja')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='ru')
        # class UserAllLanguagesRussianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='ru')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='zh')
        # class UserAllLanguagesChineseTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='zh')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='pl')
        # class UserAllLanguagesPolishTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='pl')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='fa')
        # class UserAllLanguagesPersianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='fa')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='he')
        # class UserAllLanguagesHebrewTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='he')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='ko')
        # class UserAllLanguagesKoreanTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='ko')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='ar')
        # class UserAllLanguagesArabicTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='ar')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='id')
        # class UserAllLanguagesIndonesianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='id')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='uk')
        # class UserAllLanguagesUkrainianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='uk')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='tr')
        # class UserAllLanguagesTurkishTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='tr')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='vi')
        # class UserAllLanguagesVietnameseTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='vi')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='cs')
        # class UserAllLanguagesCzechTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='cs')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='sv')
        # class UserAllLanguagesSwedishTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='sv')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='fi')
        # class UserAllLanguagesFinnishTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='fi')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='hu')
        # class UserAllLanguagesHungarianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='hu')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='th')
        # class UserAllLanguagesThaiTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='th')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='el')
        # class UserAllLanguagesGreekTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='el')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='ms')
        # class UserAllLanguagesMalayTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='ms')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='sr')
        # class UserAllLanguagesSerbianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='sr')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='ro')
        # class UserAllLanguagesRomanianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='ro')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='bn')
        # class UserAllLanguagesBengaliTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='bn')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='ca')
        # class UserAllLanguagesCatalanTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='ca')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='no')
        # class UserAllLanguagesNorwegianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='no')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='bg')
        # class UserAllLanguagesBulgarianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='bg')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='da')
        # class UserAllLanguagesDanishTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='da')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='sk')
        # class UserAllLanguagesSlovakTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='sk')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='hi')
        # class UserAllLanguagesHindiTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='hi')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='et')
        # class UserAllLanguagesEstonianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='et')
        #
        #
        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='hr')
        # class UserAllLanguagesCroatianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='hr')

        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='az')
        # class UserAllLanguagesAzerbaijaniTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='az')

        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='zh-yue')
        # class UserAllLanguagesCantoneseTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='zh-yue')

        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='lt')
        # class UserAllLanguagesLithuanianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='lt')

        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='sl')
        # class UserAllLanguagesSlovenianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='sl')

        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='eu')
        # class UserAllLanguagesBasqueTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='eu')

        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='hy')
        # class UserAllLanguagesArmenianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='hy')

        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='uz')
        # class UserAllLanguagesUzbekTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='uz')

        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='ta')
        # class UserAllLanguagesTamilTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='ta')

        # @only_on_sites_with_login
        # @override_settings(LANGUAGE_CODE='lv')
        # class UserAllLanguagesLatvianTestCase(UserTestCaseMixin, SiteTestCase):
        #     def validate_all_values(self):
        #         super().validate_all_values()
        #         self.assertEqual(first=self.language_code, second='lv')

        class UserWithDataTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the User model with additional profile data (password, slug, gender, date of birth).

            Methods:
                set_up(self): Sets up a random password and a base data dict (password, slug, gender, date_of_birth) for creating users.
                test_valid_date_of_birth_list_ok(self): Asserts that users can be created with each valid date of birth from the test settings list.
                test_invalid_date_of_birth_list_fail(self): Asserts that creating a user fails with a ValidationError for each invalid date of birth from the test settings list.
            """
            def set_up(self):
                """
                Sets up a random password and a base data dict (password, slug, gender, date_of_birth) for creating users.
                """
                super().set_up()
                self.password = get_random_user_password()
                self.data = {
                    'password': self.password,
                    'slug': 'user-1234',
                    'gender': 1,
                    'date_of_birth': '1900-08-20',
                }

            def test_valid_date_of_birth_list_ok(self):
                """
                Asserts that a user can be created and saved successfully with each valid date of birth from VALID_DATE_OF_BIRTH_IN_MODEL_LIST, and that the resulting user's fields and counts are as expected.
                """
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
                """
                Asserts that creating a user fails with a ValidationError for each invalid date of birth from INVALID_DATE_OF_BIRTH_IN_MODEL_LIST, and that no objects are created.
                """
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


        @only_on_sites_with_login
        class UserWithDataWithLastNameAllMainLanguagesEnglishTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data including a last name, for all main languages (English).

            Methods:
                set_up(self): Sets up the user's first and last name in the English alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the English alphabet, to be used in validate_all_values.
                """
                # Check names in English alphabet.
                super().set_up()
                self.data.update({
                    'first_name_en': "Doron",
                    'last_name_en': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class UserWithDataWithLastNameAllMainLanguagesFrenchTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data including a last name, for all main languages (French).

            Methods:
                set_up(self): Sets up the user's first and last name in the French alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the French alphabet, to be used in validate_all_values.
                """
                # Check names in French alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fr': "Alizée",
                    'last_name_fr': "Jacotey",
                })
                self.first_name = "Alizée"
                self.last_name = "Jacotey"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class UserWithDataWithLastNameAllMainLanguagesGermanTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data including a last name, for all main languages (German).

            Methods:
                set_up(self): Sets up the user's first and last name in the German alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the German alphabet, to be used in validate_all_values.
                """
                # Check names in German alphabet.
                super().set_up()
                self.data.update({
                    'first_name_de': "Doron",
                    'last_name_de': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class UserWithDataWithLastNameAllMainLanguagesSpanishTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data including a last name, for all main languages (Spanish).

            Methods:
                set_up(self): Sets up the user's first and last name in the Spanish alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the Spanish alphabet, to be used in validate_all_values.
                """
                # Check names in Spanish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_es': "Lionel",
                    'last_name_es': "Messi",
                })
                self.first_name = "Lionel"
                self.last_name = "Messi"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class UserWithDataWithLastNameAllMainLanguagesPortugueseTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data including a last name, for all main languages (Portuguese).

            Methods:
                set_up(self): Sets up the user's first and last name in the Portuguese alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the Portuguese alphabet, to be used in validate_all_values.
                """
                # Check names in Portuguese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_pt': "Cristiano",
                    'last_name_pt': "Ronaldo",
                })
                self.first_name = "Cristiano"
                self.last_name = "Ronaldo"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class UserWithDataWithLastNameAllMainLanguagesItalianTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data including a last name, for all main languages (Italian).

            Methods:
                set_up(self): Sets up the user's first and last name in the Italian alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the Italian alphabet, to be used in validate_all_values.
                """
                # Check names in Italian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_it': "Andrea",
                    'last_name_it': "Bocelli",
                })
                self.first_name = "Andrea"
                self.last_name = "Bocelli"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class UserWithDataWithLastNameAllMainLanguagesDutchTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data including a last name, for all main languages (Dutch).

            Methods:
                set_up(self): Sets up the user's first and last name in the Dutch alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the Dutch alphabet, to be used in validate_all_values.
                """
                # Check names in Dutch alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class UserWithDataWithLastNameAllMainLanguagesHebrewTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data including a last name, for all main languages (Hebrew).

            Methods:
                set_up(self): Sets up the user's first and last name in the Hebrew alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the Hebrew alphabet, to be used in validate_all_values.
                """
                # Check names in Hebrew alphabet.
                super().set_up()
                self.data.update({
                    'first_name_he': "דורון",
                    'last_name_he': "מטלון",
                })
                self.first_name = "דורון"
                self.last_name = "מטלון"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        class UserWithDataWithoutLastNameAllMainLanguagesEnglishTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data without a last name, for all main languages (English).

            Methods:
                set_up(self): Sets up the user's first name (with no last name) in the English alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first name (with no last name) in the English alphabet, to be used in validate_all_values.
                """
                # Check names in English alphabet.
                super().set_up()
                self.data.update({
                    'first_name_en': "Doron",
                    'last_name_en': "",
                })
                self.first_name = "Doron"
                self.last_name = ""

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class UserWithDataWithoutLastNameAllMainLanguagesFrenchTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data without a last name, for all main languages (French).

            Methods:
                set_up(self): Sets up the user's first name (with no last name) in the French alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the French alphabet, to be used in validate_all_values.
                """
                # Check names in French alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fr': "Alizée",
                    'last_name_fr': "",
                })
                self.first_name = "Alizée"
                self.last_name = ""

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class UserWithDataWithoutLastNameAllMainLanguagesGermanTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data without a last name, for all main languages (German).

            Methods:
                set_up(self): Sets up the user's first name (with no last name) in the German alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the German alphabet, to be used in validate_all_values.
                """
                # Check names in German alphabet.
                super().set_up()
                self.data.update({
                    'first_name_de': "Doron",
                    'last_name_de': "",
                })
                self.first_name = "Doron"
                self.last_name = ""

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class UserWithDataWithoutLastNameAllMainLanguagesSpanishTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data without a last name, for all main languages (Spanish).

            Methods:
                set_up(self): Sets up the user's first name (with no last name) in the Spanish alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the Spanish alphabet, to be used in validate_all_values.
                """
                # Check names in Spanish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_es': "Lionel",
                    'last_name_es': "",
                })
                self.first_name = "Lionel"
                self.last_name = ""

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class UserWithDataWithoutLastNameAllMainLanguagesPortugueseTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data without a last name, for all main languages (Portuguese).

            Methods:
                set_up(self): Sets up the user's first name (with no last name) in the Portuguese alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the Portuguese alphabet, to be used in validate_all_values.
                """
                # Check names in Portuguese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_pt': "Cristiano",
                    'last_name_pt': "",
                })
                self.first_name = "Cristiano"
                self.last_name = ""

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class UserWithDataWithoutLastNameAllMainLanguagesItalianTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data without a last name, for all main languages (Italian).

            Methods:
                set_up(self): Sets up the user's first name (with no last name) in the Italian alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the Italian alphabet, to be used in validate_all_values.
                """
                # Check names in Italian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_it': "Andrea",
                    'last_name_it': "",
                })
                self.first_name = "Andrea"
                self.last_name = ""

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class UserWithDataWithoutLastNameAllMainLanguagesDutchTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data without a last name, for all main languages (Dutch).

            Methods:
                set_up(self): Sets up the user's first name (with no last name) in the Dutch alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the Dutch alphabet, to be used in validate_all_values.
                """
                # Check names in Dutch alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class UserWithDataWithoutLastNameAllMainLanguagesHebrewTestCase(UserWithDataTestCaseMixin, SiteTestCase):
            """
            Tests creating a user with data without a last name, for all main languages (Hebrew).

            Methods:
                set_up(self): Sets up the user's first name (with no last name) in the Hebrew alphabet, to be used in validate_all_values.
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def set_up(self):
                """
                Sets up the user's first and last name in the Hebrew alphabet, to be used in validate_all_values.
                """
                # Check names in Hebrew alphabet.
                super().set_up()
                self.data.update({
                    'first_name_he': "דורון",
                    'last_name_he': "",
                })
                self.first_name = "דורון"
                self.last_name = ""

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class UserEmailAddressTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin, TestCaseMixin):
            """
            Tests the UserEmailAddress model.
            """
            def test_cannot_create_user_email_address_without_all_the_required_fields(self):
                """
                Asserts that creating a UserEmailAddress without all the required fields raises a ValidationError and creates no objects.
                """
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
                """
                Asserts that creating a UserEmailAddress with any of several invalid email formats raises a ValidationError and creates no email address objects.
                """
                email_list = ['email', 'email@example', 'email@example.', 'email@.example', 'email@example.com.', 'email@.example.com', 'email@example..com']
                user = DefaultUserFactory()
                for email in email_list:
                    user_email_address = UserEmailAddress(user=user, email=email)
                    with self.assertRaises(ValidationError) as cm:
                        user_email_address.save()
                    self.assertDictEqual(d1=dict(cm.exception), d2=self._enter_a_valid_email_address_errors_dict())
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
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
                """
                Asserts that adding an email address that is already confirmed by another user raises a ValidationError and doesn't create a new email address for the new user.
                """
                existing_user = DefaultUserFactory()
                existing_user_email = UserEmailAddressFactory(user=existing_user, email='email@example.com', is_confirmed=True)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
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
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
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
                """
                Asserts that adding an uppercase variant of an email address already confirmed by another user raises a ValidationError and doesn't create a new email address for the new user.
                """
                existing_user = DefaultUserFactory()
                existing_user_email = UserEmailAddressFactory(user=existing_user, email='email@example.com', is_confirmed=True)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
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
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
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
                """
                Asserts that adding an email address that is currently unconfirmed and recently added by another user raises a ValidationError, since it isn't old enough to be deleted and reassigned.
                """
                # Unconfirmed email address is deleted if another user adds it again.
                existing_user = DefaultUserFactory()
                existing_user_email = UserEmailAddressFactory(user=existing_user, email='email@example.com', is_confirmed=False)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                user = DefaultUserFactory()
                user_email_address = UserEmailAddress(user=user, email='email@example.com')
                with self.assertRaises(ValidationError) as cm:
                    user_email_address.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._this_email_is_already_in_use_errors_dict())
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=1,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=1,
                )

            def test_non_unique_unconfirmed_email_address_registered_6_minutes_ago(self):
                """
                Asserts that an unconfirmed email address registered more than 5 minutes ago is deleted and successfully reassigned to a new user who adds it, removing it from the original user.
                """
                # Unconfirmed email address is deleted if another user adds it again.
                existing_user = DefaultUserFactory()
                existing_user_email = UserEmailAddressFactory(user=existing_user, email='email@example.com', is_confirmed=False)
                existing_user_email.date_created -= timedelta(minutes=6)
                existing_user_email.save()
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                user = DefaultUserFactory()
                user_email_address = UserEmailAddress(user=user, email='email@example.com')
                user_email_address.save()
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
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
                """
                Asserts that adding an uppercase variant of an email address that is currently unconfirmed and recently added by another user raises a ValidationError, since it isn't old enough to be deleted and reassigned.
                """
                # Unconfirmed email address is deleted if another user adds it again.
                existing_user = DefaultUserFactory()
                existing_user_email = UserEmailAddressFactory(user=existing_user, email='email77@example.com', is_confirmed=False)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                user = DefaultUserFactory()
                user_email_address = UserEmailAddress(user=user, email='EMAIL77@EXAMPLE.COM')
                with self.assertRaises(ValidationError) as cm:
                    user_email_address.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._this_email_is_already_in_use_errors_dict())
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=1,
                    confirmed_email_address_count=0,
                    unconfirmed_email_address_count=1,
                )

            def test_non_unique_unconfirmed_email_address_uppercase_registered_6_minutes_ago(self):
                """
                Asserts that an unconfirmed email address registered more than 5 minutes ago is deleted and successfully reassigned (in its lowercase form) to a new user who adds it as uppercase, removing it from the original user.
                """
                # Unconfirmed email address is deleted if another user adds it again.
                existing_user = DefaultUserFactory()
                existing_user_email = UserEmailAddressFactory(user=existing_user, email='email77@example.com', is_confirmed=False)
                existing_user_email.date_created -= timedelta(minutes=6)
                existing_user_email.save()
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                user = DefaultUserFactory()
                user_email_address = UserEmailAddress(user=user, email='EMAIL77@EXAMPLE.COM')
                user_email_address.save()
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=0,
                    user_primary_email_addresses_count=0,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
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
                """
                Asserts that two different users can each have their own distinct unconfirmed email address (case-insensitively different), with both addresses coexisting.
                """
                # Unconfirmed email address is deleted if another user adds it again.
                existing_user = DefaultUserFactory()
                existing_user_email = UserEmailAddressFactory(user=existing_user, email='email77@example.com', is_confirmed=False)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                user = DefaultUserFactory()
                user_email_address = UserEmailAddress(user=user, email='EMAIL755@EXAMPLE.COM')
                user_email_address.save()
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                existing_user = User.objects.get(pk=existing_user.pk)
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=existing_user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
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
                """
                Asserts that saving a UserEmailAddress with an uppercase email converts it to lowercase.
                """
                user = DefaultUserFactory()
                user_email_address = UserEmailAddress(user=user, email='EMAIL77@EXAMPLE.COM')
                user_email_address.save()
                self.assertEqual(first=user_email_address.email, second='email77@example.com')
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
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
                """
                Asserts that creating a UserEmailAddress via the factory with an uppercase email converts it to lowercase.
                """
                user = DefaultUserFactory()
                user_email_address = UserEmailAddressFactory(user=user, email='EMAIL75@EXAMPLE.COM')
                self.assertEqual(first=user_email_address.email, second='email75@example.com')
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
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
                """
                Asserts that saving the same unconfirmed UserEmailAddress 5 times doesn't create duplicate email address objects.
                """
                user = DefaultUserFactory()
                user_email_address = UserEmailAddress(user=user, email='email75@example.com')
                for i in range(5):
                    user_email_address.save()
                self.assertEqual(first=user_email_address.email, second='email75@example.com')
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=1,
                )
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
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
                """
                Asserts that saving the same confirmed UserEmailAddress 5 times doesn't create duplicate email address objects.
                """
                user = DefaultUserFactory()
                user_email_address = UserEmailAddress(user=user, email='email75@example.com', is_confirmed=True)
                for i in range(5):
                    user_email_address.save()
                self.assertEqual(first=user_email_address.email, second='email75@example.com')
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
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

            def test_confirming_the_first_email_address_makes_it_primary(self):
                """
                Asserts that confirming a user's second unconfirmed email address (when the first is also unconfirmed) makes it the new primary and confirmed email address, while the first becomes non-primary.
                """
                user = DefaultUserFactory()
                user_email_address_1 = UserEmailAddress(user=user, email='email75@example.com', is_confirmed=False)
                user_email_address_1.save()
                user_email_address_2 = UserEmailAddress(user=user, email='email76@example.com', is_confirmed=False)
                user_email_address_2.save()
                user_email_address_1 = UserEmailAddress.objects.get(pk=user_email_address_1.pk)
                user_email_address_2 = UserEmailAddress.objects.get(pk=user_email_address_2.pk)
                self.assertEqual(first=user_email_address_1.is_confirmed, second=False)
                self.assertEqual(first=user_email_address_1.is_primary, second=True)
                self.assertEqual(first=user_email_address_2.is_confirmed, second=False)
                self.assertEqual(first=user_email_address_2.is_primary, second=False)
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=2,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=0,
                    user_unconfirmed_email_addresses_count=2,
                )
                user_email_address_2.verify()
                user_email_address_1 = UserEmailAddress.objects.get(pk=user_email_address_1.pk)
                user_email_address_2 = UserEmailAddress.objects.get(pk=user_email_address_2.pk)
                self.assertEqual(first=user_email_address_1.is_confirmed, second=False)
                self.assertEqual(first=user_email_address_1.is_primary, second=False)
                self.assertEqual(first=user_email_address_2.is_confirmed, second=True)
                self.assertEqual(first=user_email_address_2.is_primary, second=True)
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=2,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=1,
                )
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=2,
                    confirmed_email_address_count=1,
                    unconfirmed_email_address_count=1,
                )

            def test_confirming_the_second_email_address_doesnt_make_it_primary(self):
                """
                Asserts that confirming a user's second email address does not make it primary when the first email address is already confirmed and primary.
                """
                user = DefaultUserFactory()
                user_email_address_1 = UserEmailAddress(user=user, email='email75@example.com', is_confirmed=True)
                user_email_address_1.save()
                user_email_address_2 = UserEmailAddress(user=user, email='email76@example.com', is_confirmed=False)
                user_email_address_2.save()
                user_email_address_1 = UserEmailAddress.objects.get(pk=user_email_address_1.pk)
                user_email_address_2 = UserEmailAddress.objects.get(pk=user_email_address_2.pk)
                self.assertEqual(first=user_email_address_1.is_confirmed, second=True)
                self.assertEqual(first=user_email_address_1.is_primary, second=True)
                self.assertEqual(first=user_email_address_2.is_confirmed, second=False)
                self.assertEqual(first=user_email_address_2.is_primary, second=False)
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=2,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=1,
                )
                user_email_address_2.verify()
                user_email_address_1 = UserEmailAddress.objects.get(pk=user_email_address_1.pk)
                user_email_address_2 = UserEmailAddress.objects.get(pk=user_email_address_2.pk)
                self.assertEqual(first=user_email_address_1.is_confirmed, second=True)
                self.assertEqual(first=user_email_address_1.is_primary, second=True)
                self.assertEqual(first=user_email_address_2.is_confirmed, second=True)
                self.assertEqual(first=user_email_address_2.is_primary, second=False)
                user = User.objects.get(pk=user.pk)
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=2,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=2,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assert_models_count(
                    entity_count=1,
                    user_count=1,
                    user_email_address_count=2,
                    confirmed_email_address_count=2,
                    unconfirmed_email_address_count=0,
                )

            def test_user_email_address_ordering(self):
                """
                Asserts that a user's email addresses are ordered by date_created, and that this ordering is preserved after deleting one of the addresses.
                """
                # If UserEmailAddress.Meta.ordering is not equal to ('date_created',) in models, this test should fail.
                user = DefaultUserFactory()
                user_email_address_1 = UserEmailAddress(user=user, email='email75@example.com', is_confirmed=True)
                user_email_address_1.save()
                sleep(0.01)
                user_email_address_2 = UserEmailAddress(user=user, email='test-email-77@example.org', is_confirmed=False)
                user_email_address_2.save()
                sleep(0.01)
                user_email_address_3 = UserEmailAddress(user=user, email='email88@example.info', is_confirmed=False)
                user_email_address_3.save()
                sleep(0.01)
                user_email_address_4 = UserEmailAddress(user=user, email='email99@example.co.uk', is_confirmed=False)
                user_email_address_4.save()
                sleep(0.01)
                self.assert_user_email_addresses_count(
                    user=user,
                    user_email_addresses_count=4,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=3,
                )
                user_email_addresses = list(user.email_addresses.all())
                self.assertListEqual(list1=[address.email for address in user_email_addresses], list2=['email75@example.com', 'test-email-77@example.org', 'email88@example.info', 'email99@example.co.uk'])
                self.assertListEqual(list1=[address.pk for address in user_email_addresses], list2=[user_email_address_1.pk, user_email_address_2.pk, user_email_address_3.pk, user_email_address_4.pk])
                self.assertListEqual(list1=[address.pk for address in user_email_addresses], list2=[user_email_address_1.id, user_email_address_2.id, user_email_address_3.id, user_email_address_4.id])
                user_email_address_3.delete()
                user_email_addresses = list(user.email_addresses.all())
                self.assertListEqual(list1=[address.email for address in user_email_addresses], list2=['email75@example.com', 'test-email-77@example.org', 'email99@example.co.uk'])
                self.assertListEqual(list1=[address.pk for address in user_email_addresses], list2=[user_email_address_1.pk, user_email_address_2.pk, user_email_address_4.pk])
                self.assertListEqual(list1=[address.pk for address in user_email_addresses], list2=[user_email_address_1.id, user_email_address_2.id, user_email_address_4.id])

            def test_cannot_create_user_email_addresses_with_bulk_create(self):
                """
                Asserts that calling bulk_create on the UserEmailAddress manager raises a NotImplementedError.
                """
                with self.assertRaises(NotImplementedError) as cm:
                    UserEmailAddress.objects.bulk_create([])
                self.assertEqual(first=str(cm.exception), second="bulk_create is not implemented.")

            def test_cannot_delete_user_email_addresses_with_queryset_delete(self):
                """
                Asserts that calling delete on the UserEmailAddress manager or any of its querysets raises a NotImplementedError.
                """
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
        class UserEmailAddressAllMainLanguagesEnglishTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            """
            Tests the UserEmailAddress model, for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class UserEmailAddressAllMainLanguagesFrenchTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            """
            Tests the UserEmailAddress model, for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class UserEmailAddressAllMainLanguagesGermanTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            """
            Tests the UserEmailAddress model, for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class UserEmailAddressAllMainLanguagesSpanishTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            """
            Tests the UserEmailAddress model, for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class UserEmailAddressAllMainLanguagesPortugueseTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            """
            Tests the UserEmailAddress model, for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class UserEmailAddressAllMainLanguagesItalianTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            """
            Tests the UserEmailAddress model, for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class UserEmailAddressAllMainLanguagesDutchTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            """
            Tests the UserEmailAddress model, for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class UserEmailAddressAllMainLanguagesHebrewTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            """
            Tests the UserEmailAddress model, for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


