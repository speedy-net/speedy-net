from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from time import sleep
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta

        from django.test import override_settings
        from django.db.utils import DataError, IntegrityError
        from django.core.exceptions import ValidationError

        from speedy.core.base.test.utils import get_random_user_password

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.base.test.utils import get_django_settings_class_with_override_settings
        from speedy.core.accounts.test.mixins import SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin
        from speedy.core.accounts.test.user_factories import DefaultUserFactory, InactiveUserFactory, ActiveUserFactory
        from speedy.core.accounts.test.user_email_address_factories import UserEmailAddressFactory

        from speedy.core.accounts.models import Entity, ReservedUsername, User, UserEmailAddress


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
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=5))

            def test_slug_and_username_min_length_ok_1(self):
                entity = Entity(slug='a' * 6, username='a' * 6)
                entity.save()

            def test_slug_and_username_min_length_ok_2(self):
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
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=201))

            def test_slug_max_length_ok_username_max_length_fail_1(self):
                entity = Entity(slug='b' * 200, username='b' * 200)
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=200))

            def test_slug_max_length_ok_username_max_length_fail_2(self):
                entity = Entity(slug='b' * 121, username='b' * 121)
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=Entity, slug_fail=True, username_fail=True, username_value_length=121))

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

            def test_0test1_is_invalid_username(self):
                entity = Entity(slug='0-test-1', username='0test1')
                with self.assertRaises(ValidationError) as cm:
                    entity.save()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=Entity, slug_fail=True, username_fail=True))

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


        # @only_on_sites_with_login # ~~~~ TODO
        class EntityEnglishTestCase(EntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        # @only_on_sites_with_login # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='fr')
        class EntityFrenchTestCase(EntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        # @only_on_sites_with_login # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='de')
        class EntityGermanTestCase(EntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        # @only_on_sites_with_login # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='es')
        class EntitySpanishTestCase(EntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        # @only_on_sites_with_login # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='pt')
        class EntityPortugueseTestCase(EntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        # @only_on_sites_with_login # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='it')
        class EntityItalianTestCase(EntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        # @only_on_sites_with_login # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='nl')
        class EntityDutchTestCase(EntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        # @only_on_sites_with_login # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='sv')
        class EntitySwedishTestCase(EntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        # @only_on_sites_with_login # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='ko')
        class EntityKoreanTestCase(EntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        # @only_on_sites_with_login # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='fi')
        class EntityFinnishTestCase(EntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        # @only_on_sites_with_login # ~~~~ TODO
        @override_settings(LANGUAGE_CODE='he')
        class EntityHebrewTestCase(EntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class ReservedUsernameTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreAccountsLanguageMixin):
            def test_cannot_create_reserved_username_without_a_username(self):
                reserved_username = ReservedUsername()
                with self.assertRaises(ValidationError) as cm:
                    reserved_username.save()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._username_is_required_error_message]})

            def test_cannot_create_reserved_username_with_empty_username(self):
                reserved_username = ReservedUsername(username='')
                with self.assertRaises(ValidationError) as cm:
                    reserved_username.save()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._username_is_required_error_message]})

            def test_cannot_create_reserved_username_with_empty_slug(self):
                reserved_username = ReservedUsername(slug='')
                with self.assertRaises(ValidationError) as cm:
                    reserved_username.save()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._username_is_required_error_message]})

            def test_cannot_create_reserved_usernames_with_bulk_create(self):
                reserved_username_1 = ReservedUsername(slug='zzzzzz')
                reserved_username_2 = ReservedUsername(slug='ZZZ-ZZZ')
                with self.assertRaises(NotImplementedError) as cm:
                    ReservedUsername.objects.bulk_create([reserved_username_1, reserved_username_2])
                self.assertEqual(first=str(cm.exception), second="bulk_create is not implemented.")

            def test_cannot_delete_reserved_usernames_with_queryset_delete(self):
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
                reserved_username = ReservedUsername(slug='webmaster')
                reserved_username.save()

            def test_can_create_reserved_username_with_reserved_and_too_short_username(self):
                reserved_username = ReservedUsername(slug='mail')
                reserved_username.save()

            def test_cannot_create_reserved_username_with_existing_username_1(self):
                entity = Entity(slug='zzzzzz')
                entity.save()
                reserved_username = ReservedUsername(slug='ZZZ-ZZZ')
                with self.assertRaises(ValidationError) as cm:
                    reserved_username.save()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._this_username_is_already_taken_error_message], 'username': [self._this_username_is_already_taken_error_message]})

            def test_cannot_create_reserved_username_with_existing_username_2(self):
                reserved_username_1 = ReservedUsername(slug='zzzzzz')
                reserved_username_1.save()
                reserved_username_2 = ReservedUsername(slug='ZZZ-ZZZ')
                with self.assertRaises(ValidationError) as cm:
                    reserved_username_2.save()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._this_username_is_already_taken_error_message], 'username': [self._this_username_is_already_taken_error_message]})

            def test_star2000_is_valid_username(self):
                reserved_username = ReservedUsername(slug='star2000', username='star2000')
                reserved_username.save()

            def test_come2us_is_valid_username(self):
                reserved_username = ReservedUsername(slug='come2us', username='come2us')
                reserved_username.save()

            def test_000000_is_valid_username(self):
                reserved_username = ReservedUsername(slug='0' * 6, username='0' * 6)
                reserved_username.save()

            def test_0test1_is_valid_username(self):
                reserved_username = ReservedUsername(slug='0-test-1', username='0test1')
                reserved_username.save()

            def test_0_is_valid_username_1(self):
                reserved_username = ReservedUsername(slug='0')
                reserved_username.save()

            def test_0_is_valid_username_2(self):
                reserved_username = ReservedUsername(username='0')
                reserved_username.save()

            def test_long_username_is_valid_username_1(self):
                reserved_username = ReservedUsername(slug='0' * 250)
                reserved_username.save()

            def test_long_username_is_valid_username_2(self):
                reserved_username = ReservedUsername(username='0' * 250)
                reserved_username.save()

            def test_username_too_long_exception_1(self):
                reserved_username = ReservedUsername(slug='0' * 5000)
                with self.assertRaises(DataError) as cm:
                    reserved_username.save()
                self.assertIn(member=self._value_too_long_for_type_character_varying_255_error_message, container=str(cm.exception))

            def test_username_too_long_exception_2(self):
                reserved_username = ReservedUsername(username='0' * 5000)
                with self.assertRaises(DataError) as cm:
                    reserved_username.save()
                self.assertIn(member=self._value_too_long_for_type_character_varying_255_error_message, container=str(cm.exception))

            def test_username_too_long_exception_3(self):
                reserved_username = ReservedUsername(slug='0' * 260)
                with self.assertRaises(DataError) as cm:
                    reserved_username.save()
                self.assertIn(member=self._value_too_long_for_type_character_varying_255_error_message, container=str(cm.exception))

            def test_username_too_long_exception_4(self):
                reserved_username = ReservedUsername(username='0' * 260)
                with self.assertRaises(DataError) as cm:
                    reserved_username.save()
                self.assertIn(member=self._value_too_long_for_type_character_varying_255_error_message, container=str(cm.exception))

            def test_slug_and_username_dont_match_1(self):
                reserved_username = ReservedUsername(slug='star2001', username='star2000')
                with self.assertRaises(ValidationError) as cm:
                    reserved_username.save()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._slug_does_not_parse_to_username_error_message]})

            def test_slug_and_username_dont_match_2(self):
                reserved_username = ReservedUsername(slug='0-test-2', username='0test1')
                with self.assertRaises(ValidationError) as cm:
                    reserved_username.save()
                self.assertDictEqual(d1=dict(cm.exception), d2={'__all__': [self._slug_does_not_parse_to_username_error_message]})


        class ReservedUsernameEnglishTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @override_settings(LANGUAGE_CODE='fr')
        class ReservedUsernameFrenchTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @override_settings(LANGUAGE_CODE='de')
        class ReservedUsernameGermanTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @override_settings(LANGUAGE_CODE='es')
        class ReservedUsernameSpanishTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @override_settings(LANGUAGE_CODE='pt')
        class ReservedUsernamePortugueseTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @override_settings(LANGUAGE_CODE='it')
        class ReservedUsernameItalianTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @override_settings(LANGUAGE_CODE='nl')
        class ReservedUsernameDutchTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @override_settings(LANGUAGE_CODE='sv')
        class ReservedUsernameSwedishTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @override_settings(LANGUAGE_CODE='ko')
        class ReservedUsernameKoreanTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @override_settings(LANGUAGE_CODE='fi')
        class ReservedUsernameFinnishTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @override_settings(LANGUAGE_CODE='he')
        class ReservedUsernameHebrewTestCase(ReservedUsernameTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


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
                self.assertTupleEqual(tuple1=User.NAME_REQUIRED_LOCALIZABLE_FIELDS, tuple2=('first_name',))

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

            def test_cannot_create_user_with_all_the_required_fields_minus_one(self):
                self.run_test_cannot_create_user_with_all_the_required_fields_number(number=-1)

            def test_cannot_create_user_with_all_the_required_fields_ninety_nine(self):
                self.run_test_cannot_create_user_with_all_the_required_fields_number(number=99)

            def test_cannot_create_user_with_all_the_required_fields_one(self):
                self.run_test_cannot_create_user_with_all_the_required_fields_number(number=1, gender_is_valid=True)

            def test_cannot_create_user_with_empty_slug(self):
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))

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

            def test_admin_is_invalid_username(self):
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='admin')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=5))

            def test_doron_is_invalid_username(self):
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='doron')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=5))

            def test_can_create_user_admin_with_special_username(self):
                user = DefaultUserFactory(slug='admin', special_username=True)
                user.save_user_and_profile()

            def test_can_create_user_mail_with_special_username(self):
                user = DefaultUserFactory(slug='mail', special_username=True)
                user.save_user_and_profile()

            def test_can_create_user_webmaster_with_special_username(self):
                user = DefaultUserFactory(slug='webmaster', special_username=True)
                user.save_user_and_profile()

            def test_can_create_user_doron_with_special_username(self):
                user = DefaultUserFactory(slug='doron', special_username=True)
                user.save_user_and_profile()

            def test_can_create_user_jennifer_with_special_username(self):
                user = DefaultUserFactory(slug='jennifer', special_username=True)
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
                self.assertIs(expr1=user.has_confirmed_email, expr2=False)

            def test_has_a_confirmed_email(self):
                user = DefaultUserFactory()
                UserEmailAddressFactory(user=user, is_confirmed=False)
                UserEmailAddressFactory(user=user, is_confirmed=True)
                self.assertIs(expr1=user.has_confirmed_email, expr2=True)

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
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=5))

            def test_slug_and_username_min_length_ok_1(self):
                user = DefaultUserFactory(slug='a' * 6)
                user.save_user_and_profile()

            def test_first_name_is_not_optional(self):
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(first_name_en="")
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2={'first_name_{language_code}'.format(language_code=language_code): [self._this_field_cannot_be_blank_error_message] for language_code, language_name in django_settings.LANGUAGES})

            def test_first_name_is_none(self):
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(first_name_en=None, first_name_he=None)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2={'first_name_{language_code}'.format(language_code=language_code): [self._this_field_cannot_be_null_error_message] for language_code, language_name in django_settings.LANGUAGES})

            def test_last_name_is_optional(self):
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
                with self.assertRaises(IntegrityError) as cm:
                    user = DefaultUserFactory(last_name_en=None, last_name_he=None)
                    user.save_user_and_profile()
                self.assertIn(member=self._not_null_constraint_error_message_by_column_and_relation(column="last_name_en", relation="accounts_user"), container=str(cm.exception))

            def test_first_name_and_last_name_are_long(self):
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(first_name_en="a" * 200, last_name_en="b" * 200)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2={field_name: [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=150, value_length=200)] for field_name in ['first_name_en', 'first_name_fr', 'first_name_de', 'first_name_es', 'first_name_pt', 'first_name_it', 'first_name_nl', 'first_name_sv', 'first_name_ko', 'first_name_fi', 'first_name_he', 'last_name_en', 'last_name_fr', 'last_name_de', 'last_name_es', 'last_name_pt', 'last_name_it', 'last_name_nl', 'last_name_sv', 'last_name_ko', 'last_name_fi', 'last_name_he']})

            def test_slug_and_username_min_length_ok_2(self):
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
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=201))

            def test_slug_max_length_ok_username_max_length_fail_1(self):
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='b' * 200)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=200))

            def test_slug_max_length_ok_username_max_length_fail_2(self):
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='a' * 41)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(model=User, slug_fail=True, username_fail=True, username_value_length=41))

            def test_slug_and_username_max_length_ok(self):
                user = DefaultUserFactory(slug='a' * 40)
                user.save_user_and_profile()

            def test_star2000_is_valid_username(self):
                user = DefaultUserFactory(slug='star2000', username='star2000')
                user.save_user_and_profile()

            def test_jennifer_is_valid_username(self):
                user = DefaultUserFactory(slug='jennifer')
                user.save_user_and_profile()

            def test_come2us_is_invalid_username(self):
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='come2us', username='come2us')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))

            def test_000000_is_invalid_username(self):
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='0' * 6, username='0' * 6)
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))

            def test_0test1_is_invalid_username(self):
                with self.assertRaises(ValidationError) as cm:
                    user = DefaultUserFactory(slug='0-test-1', username='0test1')
                    user.save_user_and_profile()
                self.assertDictEqual(d1=dict(cm.exception), d2=self._username_must_start_with_4_or_more_letters_errors_dict(model=User, slug_fail=True, username_fail=True))

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

            def test_user_can_change_password(self):
                new_password = '8' * 8
                incorrect_new_password = '7' * 8
                user = DefaultUserFactory()
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                user.set_password(raw_password=new_password)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=incorrect_new_password), expr2=False)
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=False)

            def test_password_too_short_exception(self):
                new_password = '8' * 3
                user = DefaultUserFactory()
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                with self.assertRaises(ValidationError) as cm:
                    user.set_password(raw_password=new_password)
                self.assertListEqual(list1=list(cm.exception), list2=[self._password_too_short_error_message])
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=False)

            def test_password_too_long_exception(self):
                new_password = '8' * 121
                user = DefaultUserFactory()
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                with self.assertRaises(ValidationError) as cm:
                    user.set_password(raw_password=new_password)
                self.assertListEqual(list1=list(cm.exception), list2=[self._password_too_long_error_message])
                self.assertIs(expr1=user.check_password(raw_password=tests_settings.USER_PASSWORD), expr2=True)
                self.assertIs(expr1=user.check_password(raw_password=new_password), expr2=False)

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
                print(user_6.profile.last_visit_str)
                #self.assertIs(expr1={'en': "(1\xa0week\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0semaine)", 'de': "(vor\xa01\xa0Woche)", 'es': "(hace\xa01\xa0semana)", 'pt': "(há\xa01\xa0semana)", 'it': "(1\xa0settimana\xa0fa)", 'nl': "(1\xa0week\xa0geleden)", 'sv': "(1\xa0vecka\xa0sedan)", 'ko': "(1주\xa0전에)", 'fi': "(1\xa0viikko\xa0sitten)", 'he': "(לפני\xa0שבוע)"}[self.language_code] in user_6.profile.last_visit_str, expr2=True)
                user_7 = ActiveUserFactory()
                user_7.profile.last_visit -= relativedelta(days=9)
                user_7.save_user_and_profile()
                print(user_7.profile.last_visit_str)
                #self.assertIs(expr1={'en': "(1\xa0week\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0semaine)", 'de': "(vor\xa01\xa0Woche)", 'es': "(hace\xa01\xa0semana)", 'pt': "(há\xa01\xa0semana)", 'it': "(1\xa0settimana\xa0fa)", 'nl': "(1\xa0week\xa0geleden)", 'sv': "(1\xa0vecka\xa0sedan)", 'ko': "(1주\xa0전에)", 'fi': "(1\xa0viikko\xa0sitten)", 'he': "(לפני\xa0שבוע)"}[self.language_code] in user_7.profile.last_visit_str, expr2=True)
                user_8 = ActiveUserFactory()
                user_8.profile.last_visit -= relativedelta(days=10)
                user_8.save_user_and_profile()
                print(user_8.profile.last_visit_str)
                #self.assertIs(expr1={'en': "(1\xa0week\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0semaine)", 'de': "(vor\xa01\xa0Woche)", 'es': "(hace\xa01\xa0semana)", 'pt': "(há\xa01\xa0semana)", 'it': "(1\xa0settimana\xa0fa)", 'nl': "(1\xa0week\xa0geleden)", 'sv': "(1\xa0vecka\xa0sedan)", 'ko': "(1주\xa0전에)", 'fi': "(1\xa0viikko\xa0sitten)", 'he': "(לפני\xa0שבוע)"}[self.language_code] in user_8.profile.last_visit_str, expr2=True)
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
                user_12.profile.last_visit -= relativedelta(months=3)
                user_12.save_user_and_profile()
                self.assertIs(expr1={'en': "(3\xa0months\xa0ago)", 'fr': "(il\xa0y\xa0a\xa03\xa0mois)", 'de': "(vor\xa03\xa0Monate)", 'es': "(hace\xa03\xa0meses)", 'pt': "(há\xa03\xa0meses)", 'it': "(3\xa0mesi\xa0fa)", 'nl': "(3\xa0maanden\xa0geleden)", 'sv': "(3\xa0månader\xa0sedan)", 'ko': "(3개월\xa0전에)", 'fi': "(3\xa0kuukautta\xa0\xa0sitten)", 'he': "(לפני\xa03\xa0חודשים)"}[self.language_code] in user_12.profile.last_visit_str, expr2=True)
                user_13 = ActiveUserFactory()
                user_13.profile.last_visit -= relativedelta(months=3, weeks=1)
                user_13.save_user_and_profile()
                self.assertIs(expr1={'en': "(3\xa0months, 1\xa0week\xa0ago)", 'fr': "(il\xa0y\xa0a\xa03\xa0mois, 1\xa0semaine)", 'de': "(vor\xa03\xa0Monate, 1\xa0Woche)", 'es': "(hace\xa03\xa0meses, 1\xa0semana)", 'pt': "(há\xa03\xa0meses, 1\xa0semana)", 'it': "(3\xa0mesi, 1\xa0settimana\xa0fa)", 'nl': "(3\xa0maanden, 1\xa0week\xa0geleden)", 'sv': "(3\xa0månader, 1\xa0vecka\xa0sedan)", 'ko': "(3개월, 1주\xa0전에)", 'fi': "(3\xa0kuukautta\xa0, 1\xa0viikko\xa0sitten)", 'he': "(לפני\xa03\xa0חודשים ושבוע)"}[self.language_code] in user_13.profile.last_visit_str, expr2=True)
                user_14 = ActiveUserFactory()
                user_14.profile.last_visit -= relativedelta(months=3, weeks=2)
                user_14.save_user_and_profile()
                self.assertIs(expr1={'en': "(3\xa0months, 2\xa0weeks\xa0ago)", 'fr': "(il\xa0y\xa0a\xa03\xa0mois, 2\xa0semaines)", 'de': "(vor\xa03\xa0Monate, 2\xa0Wochen)", 'es': "(hace\xa03\xa0meses, 2\xa0semanas)", 'pt': "(há\xa03\xa0meses, 2\xa0semanas)", 'it': "(3\xa0mesi, 2\xa0settimane\xa0fa)", 'nl': "(3\xa0maanden, 2\xa0weken\xa0geleden)", 'sv': "(3\xa0månader, 2\xa0veckor\xa0sedan)", 'ko': "(3개월, 2주\xa0전에)", 'fi': "(3\xa0kuukautta\xa0, 2\xa0viikkoa\xa0sitten)", 'he': "(לפני\xa03\xa0חודשים ושבועיים)"}[self.language_code] in user_14.profile.last_visit_str, expr2=True)
                user_15 = ActiveUserFactory()
                user_15.profile.last_visit -= relativedelta(years=1)
                user_15.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0year\xa0ago)", 'fr': " (il\xa0y\xa0a\xa01\xa0année)", 'de': "(vor\xa01\xa0Jahr)", 'es': "(hace\xa01\xa0años)", 'pt': "(há\xa01\xa0ano)", 'it': "(1\xa0anno\xa0fa)", 'nl': "(1\xa0jaar\xa0geleden)", 'sv': "(1\xa0år\xa0sedan)", 'ko': "(1년\xa0전에)", 'fi': "(1\xa0vuosi\xa0sitten)", 'he': "(לפני\xa0שנה)"}[self.language_code] in user_15.profile.last_visit_str, expr2=True)
                user_16 = ActiveUserFactory()
                user_16.profile.last_visit -= relativedelta(years=1, weeks=1)
                user_16.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0year\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0année)", 'de': "(vor\xa01\xa0Jahr)", 'es': "(hace\xa01\xa0años)", 'pt': "(há\xa01\xa0ano)", 'it': "(1\xa0anno\xa0fa)", 'nl': "(1\xa0jaar\xa0geleden)", 'sv': "(1\xa0år\xa0sedan)", 'ko': "(1년\xa0전에)", 'fi': "(1\xa0vuosi\xa0sitten)", 'he': "(לפני\xa0שנה)"}[self.language_code] in user_16.profile.last_visit_str, expr2=True)
                user_17 = ActiveUserFactory()
                user_17.profile.last_visit -= relativedelta(years=1, months=1)
                user_17.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0year, 1\xa0month\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0année, 1\xa0mois)", 'de': "(vor\xa01\xa0Jahr, 1\xa0Monat)", 'es': "(hace\xa01\xa0años, 1\xa0mes)", 'pt': "(há\xa01\xa0ano, 1\xa0mês)", 'it': "(1\xa0anno, 1\xa0mese\xa0fa)", 'nl': "(1\xa0jaar, 1\xa0maand\xa0geleden)", 'sv': "(1\xa0år, 1\xa0månad\xa0sedan)", 'ko': "(1년, 1개월\xa0전에)", 'fi': "(1\xa0vuosi, 1\xa0kuukausi\xa0sitten)", 'he': "(לפני\xa0שנה וחודש)"}[self.language_code] in user_17.profile.last_visit_str, expr2=True)
                user_18 = ActiveUserFactory()
                user_18.profile.last_visit -= relativedelta(years=1, months=1, weeks=1)
                user_18.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0year, 1\xa0month\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0année, 1\xa0mois)", 'de': "(vor\xa01\xa0Jahr, 1\xa0Monat)", 'es': "(hace\xa01\xa0años, 1\xa0mes)", 'pt': "(há\xa01\xa0ano, 1\xa0mês)", 'it': "(1\xa0anno, 1\xa0mese\xa0fa)", 'nl': "(1\xa0jaar, 1\xa0maand\xa0geleden)", 'sv': "(1\xa0år, 1\xa0månad\xa0sedan)", 'ko': "(1년, 1개월\xa0전에)", 'fi': "(1\xa0vuosi, 1\xa0kuukausi\xa0sitten)", 'he': "(לפני\xa0שנה וחודש)"}[self.language_code] in user_18.profile.last_visit_str, expr2=True)
                user_19 = ActiveUserFactory()
                user_19.profile.last_visit -= relativedelta(years=2)
                user_19.save_user_and_profile()
                self.assertIs(expr1={'en': "(2\xa0years\xa0ago)", 'fr': "(il\xa0y\xa0a\xa02\xa0années)", 'de': "(vor\xa02\xa0Jahre)", 'es': "(hace\xa02\xa0años)", 'pt': "(há\xa02\xa0anos)", 'it': "(2\xa0anni\xa0fa)", 'nl': "(2\xa0jaar\xa0geleden)", 'sv': "(2\xa0år\xa0sedan)", 'ko': "(2년\xa0전에)", 'fi': "(2\xa0vuotta\xa0sitten)", 'he': "(לפני\xa0שנתיים)"}[self.language_code] in user_19.profile.last_visit_str, expr2=True)
                user_20 = ActiveUserFactory()
                user_20.profile.last_visit -= relativedelta(years=2, weeks=2)
                user_20.save_user_and_profile()
                self.assertIs(expr1={'en': "(2\xa0years\xa0ago)", 'fr': "(il\xa0y\xa0a\xa02\xa0années)", 'de': "(vor\xa02\xa0Jahre)", 'es': "(hace\xa02\xa0años)", 'pt': "(há\xa02\xa0anos)", 'it': "(2\xa0anni\xa0fa)", 'nl': "(2\xa0jaar\xa0geleden)", 'sv': "(2\xa0år\xa0sedan)", 'ko': "(2년\xa0전에)", 'fi': "(2\xa0vuotta\xa0sitten)", 'he': "(לפני\xa0שנתיים)"}[self.language_code] in user_20.profile.last_visit_str, expr2=True)
                user_21 = ActiveUserFactory()
                user_21.profile.last_visit -= (relativedelta(years=1) - relativedelta(weeks=1))
                user_21.save_user_and_profile()
                self.assertIs(expr1={'en': "(11\xa0months, 3\xa0weeks\xa0ago)", 'fr': "(il\xa0y\xa0a\xa011\xa0mois, 3\xa0semaines)", 'de': "(vor\xa011\xa0Monate, 3\xa0Wochen)", 'es': "(hace\xa011\xa0meses, 3\xa0semanas)", 'pt': "(há\xa011\xa0meses, 3\xa0semanas)", 'it': "(11\xa0mesi, 3\xa0settimane\xa0fa)", 'nl': "(11\xa0maanden, 3\xa0weken\xa0geleden)", 'sv': "(11\xa0månader, 3\xa0veckor\xa0sedan)", 'ko': "(11개월, 3주\xa0전에)", 'fi': "(11\xa0kuukautta\xa0, 3\xa0viikkoa\xa0sitten)", 'he': "(לפני\xa011\xa0חודשים ו-3\xa0שבועות)"}[self.language_code] in user_21.profile.last_visit_str, expr2=True)
                user_22 = ActiveUserFactory()
                user_22.profile.last_visit -= (relativedelta(years=1) - relativedelta(weeks=2))
                user_22.save_user_and_profile()
                self.assertIs(expr1={'en': "(11\xa0months, 2\xa0weeks\xa0ago)", 'fr': "(il\xa0y\xa0a\xa011\xa0mois, 2\xa0semaines)", 'de': "(vor\xa011\xa0Monate, 2\xa0Wochen)", 'es': "(hace\xa011\xa0meses, 2\xa0semanas)", 'pt': "(há\xa011\xa0meses, 2\xa0semanas)", 'it': "(11\xa0mesi, 2\xa0settimane\xa0fa)", 'nl': "(11\xa0maanden, 2\xa0weken\xa0geleden)", 'sv': "(11\xa0månader, 2\xa0veckor\xa0sedan)", 'ko': "(11개월, 2주\xa0전에)", 'fi': "(11\xa0kuukautta\xa0, 2\xa0viikkoa\xa0sitten)", 'he': "(לפני\xa011\xa0חודשים ושבועיים)"}[self.language_code] in user_22.profile.last_visit_str, expr2=True)
                user_23 = ActiveUserFactory()
                user_23.profile.last_visit -= (relativedelta(years=2) - relativedelta(weeks=2))
                user_23.save_user_and_profile()
                self.assertIs(expr1={'en': "(1\xa0year, 11\xa0months\xa0ago)", 'fr': "(il\xa0y\xa0a\xa01\xa0année, 11\xa0mois)", 'de': "(vor\xa01\xa0Jahr, 11\xa0Monate)", 'es': "(hace\xa01\xa0años, 11\xa0meses)", 'pt': "(há\xa01\xa0ano, 11\xa0meses)", 'it': "(1\xa0anno, 11\xa0mesi\xa0fa)", 'nl': "(1\xa0jaar, 11\xa0maanden\xa0geleden)", 'sv': "(1\xa0år, 11\xa0månader\xa0sedan)", 'ko': "(1년, 11개월\xa0전에)", 'fi': "(1\xa0vuosi, 11\xa0kuukautta\xa0\xa0sitten)", 'he': "(לפני\xa0שנה ו-11\xa0חודשים)"}[self.language_code] in user_23.profile.last_visit_str, expr2=True)


        @only_on_sites_with_login
        class UserWithLastNameEnglishTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in English alphabet.
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
        @override_settings(LANGUAGE_CODE='fr')
        class UserWithLastNameFrenchTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in French alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fr': "Alizée",
                    'last_name_fr': "Jacotey",
                })
                self.first_name = "Alizée"
                self.last_name = "Jacotey"

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class UserWithLastNameGermanTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in German alphabet.
                super().set_up()
                self.data.update({
                    'first_name_de': "Doron",
                    'last_name_de': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class UserWithLastNameSpanishTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Spanish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_es': "Lionel",
                    'last_name_es': "Messi",
                })
                self.first_name = "Lionel"
                self.last_name = "Messi"

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class UserWithLastNamePortugueseTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Portuguese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_pt': "Cristiano",
                    'last_name_pt': "Ronaldo",
                })
                self.first_name = "Cristiano"
                self.last_name = "Ronaldo"

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class UserWithLastNameItalianTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Italian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_it': "Andrea",
                    'last_name_it': "Bocelli",
                })
                self.first_name = "Andrea"
                self.last_name = "Bocelli"

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class UserWithLastNameDutchTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Dutch alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class UserWithLastNameSwedishTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Swedish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_sv': "Doron",
                    'last_name_sv': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class UserWithLastNameKoreanTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Korean alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ko': "Doron",
                    'last_name_ko': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class UserWithLastNameFinnishTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Finnish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fi': "Doron",
                    'last_name_fi': "Matalon",
                })
                self.first_name = "Doron"
                self.last_name = "Matalon"

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class UserWithLastNameHebrewTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Hebrew alphabet.
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


        @only_on_sites_with_login
        class UserWithoutLastNameEnglishTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in English alphabet.
                super().set_up()
                self.data.update({
                    'first_name_en': "Doron",
                    'last_name_en': "",
                })
                self.first_name = "Doron"
                self.last_name = ""

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class UserWithoutLastNameFrenchTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in French alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fr': "Alizée",
                    'last_name_fr': "",
                })
                self.first_name = "Alizée"
                self.last_name = ""

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class UserWithoutLastNameGermanTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in German alphabet.
                super().set_up()
                self.data.update({
                    'first_name_de': "Doron",
                    'last_name_de': "",
                })
                self.first_name = "Doron"
                self.last_name = ""

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class UserWithoutLastNameSpanishTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Spanish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_es': "Lionel",
                    'last_name_es': "",
                })
                self.first_name = "Lionel"
                self.last_name = ""

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class UserWithoutLastNamePortugueseTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Portuguese alphabet.
                super().set_up()
                self.data.update({
                    'first_name_pt': "Cristiano",
                    'last_name_pt': "",
                })
                self.first_name = "Cristiano"
                self.last_name = ""

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class UserWithoutLastNameItalianTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Italian alphabet.
                super().set_up()
                self.data.update({
                    'first_name_it': "Andrea",
                    'last_name_it': "",
                })
                self.first_name = "Andrea"
                self.last_name = ""

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class UserWithoutLastNameDutchTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Dutch alphabet.
                super().set_up()
                self.data.update({
                    'first_name_nl': "Doron",
                    'last_name_nl': "",
                })
                self.first_name = "Doron"
                self.last_name = ""

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class UserWithoutLastNameSwedishTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Swedish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_sv': "Doron",
                    'last_name_sv': "",
                })
                self.first_name = "Doron"
                self.last_name = ""

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class UserWithoutLastNameKoreanTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Korean alphabet.
                super().set_up()
                self.data.update({
                    'first_name_ko': "Doron",
                    'last_name_ko': "",
                })
                self.first_name = "Doron"
                self.last_name = ""

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class UserWithoutLastNameFinnishTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Finnish alphabet.
                super().set_up()
                self.data.update({
                    'first_name_fi': "Doron",
                    'last_name_fi': "",
                })
                self.first_name = "Doron"
                self.last_name = ""

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class UserWithoutLastNameHebrewTestCase(UserTestCaseMixin, SiteTestCase):
            def set_up(self):
                # Check names in Hebrew alphabet.
                super().set_up()
                self.data.update({
                    'first_name_he': "דורון",
                    'last_name_he': "",
                })
                self.first_name = "דורון"
                self.last_name = ""

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
        @override_settings(LANGUAGE_CODE='fr')
        class UserEmailAddressFrenchTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class UserEmailAddressGermanTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class UserEmailAddressSpanishTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class UserEmailAddressPortugueseTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class UserEmailAddressItalianTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class UserEmailAddressDutchTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class UserEmailAddressSwedishTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class UserEmailAddressKoreanTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class UserEmailAddressFinnishTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class UserEmailAddressHebrewTestCase(UserEmailAddressTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


