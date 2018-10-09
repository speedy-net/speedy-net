from django.core.exceptions import ValidationError

from speedy.core.accounts.models import normalize_slug, normalize_username, Entity, User
from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software
from .test_factories import USER_PASSWORD, DefaultUserFactory, UserEmailAddressFactory


class NormalizeSlugTestCase(TestCase):
    def test_convert_to_lowercase(self):
        self.assertEqual(first=normalize_slug(slug='CamelCase'), second='camelcase')
        self.assertEqual(first=normalize_slug(slug='UPPERCASE'), second='uppercase')
        self.assertEqual(first=normalize_slug(slug='lowercase'), second='lowercase')

    def test_convert_dots_to_dashes(self):
        self.assertEqual(first=normalize_slug(slug='one.dot'), second='one-dot')
        self.assertEqual(first=normalize_slug(slug='two..dot.s'), second='two-dot-s')

    def test_convert_underscores_to_dashes(self):
        self.assertEqual(first=normalize_slug(slug='one_underscore'), second='one-underscore')
        self.assertEqual(first=normalize_slug(slug='two__under_scores'), second='two-under-scores')

    def test_convert_multiple_dashes_to_one(self):
        self.assertEqual(first=normalize_slug(slug='three---dash---es'), second='three-dash-es')

    def test_cut_leading_symbols(self):
        self.assertEqual(first=normalize_slug(slug='-dash'), second='dash')
        self.assertEqual(first=normalize_slug(slug='..dots'), second='dots')
        self.assertEqual(first=normalize_slug(slug='_under_score'), second='under-score')

    def test_cut_trailing_symbols(self):
        self.assertEqual(first=normalize_slug(slug='dash-'), second='dash')
        self.assertEqual(first=normalize_slug(slug='dots...'), second='dots')
        self.assertEqual(first=normalize_slug(slug='under_score_'), second='under-score')


class NormalizeUsernameTestCase(TestCase):
    def test_remove_dashes_dots_and_underscores(self):
        self.assertEqual(first=normalize_username(slug='this-is-a-slug'), second='thisisaslug')
        self.assertEqual(first=normalize_username(slug='.this_is...a_slug--'), second='thisisaslug')


class EntityTestCase(TestCase):
    def create_one_entity(self):
        entity = Entity(slug='zzzzzz', username='zzzzzz')
        entity.save()
        # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertEqual(first=entity.username, second='zzzzzz')
        self.assertEqual(first=entity.slug, second='zzzzzz')
        self.assertEqual(first=len(entity.id), second=15)
        return entity

    def test_cannot_create_entity_without_a_slug(self):
        entity = Entity()
        with self.assertRaises(ValidationError) as cm:
            entity.save()
            # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Ensure this value has at least 6 characters (it has 0).'], 'slug': ['Ensure this value has at least 6 characters (it has 0).']})

    def test_cannot_create_entities_with_bulk_create(self):
        entity_1 = Entity(slug='zzzzzz')
        entity_2 = Entity(slug='ZZZ-ZZZ')
        with self.assertRaises(NotImplementedError) as cm:
            Entity.objects.bulk_create([entity_1, entity_2])
        self.assertEqual(first=str(cm.exception), second="bulk_create is not implemented.")

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
            # new_entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'id': ['id contains illegal characters']})

    def test_cannot_create_entity_with_existing_username(self):
        entity_1 = Entity(slug='zzzzzz')
        entity_1.save()
        # entity_1.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        entity_2 = Entity(slug='ZZZ-ZZZ')
        with self.assertRaises(ValidationError) as cm:
            entity_2.save()
            # entity_2.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['This username is already taken.'], 'slug': ['This username is already taken.']})

    def test_automatic_creation_of_username_and_id(self):
        entity = Entity(slug='zzzzzz')
        entity.save()
        # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertEqual(first=entity.username, second='zzzzzz')
        self.assertEqual(first=entity.slug, second='zzzzzz')
        self.assertEqual(first=len(entity.id), second=15)

    def test_automatic_creation_of_id(self):
        entity = Entity(slug='zzzzzz', username='zzzzzz')
        entity.save()
        # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
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
        # entity_1.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        entity_2 = Entity(slug='ZZZ-ZZZ-2')
        entity_2.save()
        # entity_2.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
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
            # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Ensure this value has at least 6 characters (it has 5).'], 'slug': ['Ensure this value has at least 6 characters (it has 5).']})

    def test_slug_and_username_min_length_ok(self):
        entity = Entity(slug='a' * 6, username='a' * 6)
        entity.save()
        # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()

    def test_slug_and_username_max_length_fail(self):
        entity = Entity(slug='a' * 201, username='z' * 201)
        with self.assertRaises(ValidationError) as cm:
            entity.save()
            # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Ensure this value has at most 120 characters (it has 201).'], 'slug': ['Ensure this value has at most 200 characters (it has 201).']})

    def test_slug_and_username_max_length_ok(self):
        entity = Entity(slug='a' * 120 + '-' * 80, username='a' * 120)
        entity.save()
        # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()

    def test_star2000_is_valid_username(self):
        entity = Entity(slug='star2000', username='star2000')
        entity.save()
        # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()

    def test_come2us_is_valid_username(self):
        entity = Entity(slug='come2us', username='come2us')
        entity.save()
        # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()

    def test_000000_is_invalid_username(self):
        entity = Entity(slug='0' * 6, username='0' * 6)
        with self.assertRaises(ValidationError) as cm:
            entity.save()
            # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Username must start with 4 or more letters, and may contain letters, digits or dashes.'], 'slug': ['Username must start with 4 or more letters, and may contain letters, digits or dashes.']})

    def test_0test1_is_invalid_username(self):
        entity = Entity(slug='0-test-1', username='0test1')
        with self.assertRaises(ValidationError) as cm:
            entity.save()
            # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Username must start with 4 or more letters, and may contain letters, digits or dashes.'], 'slug': ['Username must start with 4 or more letters, and may contain letters, digits or dashes.']})

    def test_slug_and_username_dont_match_but_valid(self):
        entity = Entity(slug='star2001', username='star2000')
        with self.assertRaises(ValidationError) as cm:
            entity.save()
            # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'slug': ['Slug does not parse to username.']})

    def test_slug_and_username_dont_match_and_invalid(self):
        entity = Entity(slug='0-test-2', username='0test1')
        with self.assertRaises(ValidationError) as cm:
            entity.save()
            # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Username must start with 4 or more letters, and may contain letters, digits or dashes.'], 'slug': ['Slug does not parse to username.']})


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class UserTestCase(TestCase):
    def test_gender_valid_values(self):
        self.assertListEqual(list1=User.GENDER_VALID_VALUES, list2=list(range(User.GENDER_UNKNOWN + 1, User.GENDER_MAX_VALUE_PLUS_ONE)))
        self.assertListEqual(list1=User.GENDER_VALID_VALUES, list2=list(range(1, 3 + 1)))

    def test_diet_valid_values(self):
        self.assertListEqual(list1=User.DIET_VALID_VALUES, list2=list(range(User.DIET_UNKNOWN + 1, User.DIET_MAX_VALUE_PLUS_ONE)))
        self.assertListEqual(list1=User.DIET_VALID_VALUES, list2=list(range(1, 3 + 1)))

    def test_cannot_create_user_without_all_the_required_fields(self):
        user = User()
        with self.assertRaises(ValidationError) as cm:
            user.save_user_and_profile()
            # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'slug': ['Ensure this value has at least 6 characters (it has 0).'], 'gender': ['This field cannot be null.'], 'last_name': ['This field cannot be blank.'], 'password': ['This field cannot be blank.'], 'first_name': ['This field cannot be blank.'], 'username': ['Ensure this value has at least 6 characters (it has 0).'], 'date_of_birth': ['This field cannot be null.']})

    def test_cannot_create_user_with_empty_slug(self):
        with self.assertRaises(ValidationError) as cm:
            user = DefaultUserFactory(slug='')
            user.save_user_and_profile()
            # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Ensure this value has at least 6 characters (it has 0).'], 'slug': ['Ensure this value has at least 6 characters (it has 0).']})

    def test_cannot_create_user_with_unknown_gender(self):
        with self.assertRaises(ValidationError) as cm:
            user = DefaultUserFactory(gender=User.GENDER_UNKNOWN)
            user.save_user_and_profile()
            # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'gender': ['Value 0 is not a valid choice.']})

    def test_cannot_create_users_with_bulk_create(self):
        user_1 = User(slug='zzzzzz')
        user_2 = User(slug='ZZZ-ZZZ')
        with self.assertRaises(NotImplementedError) as cm:
            User.objects.bulk_create([user_1, user_2])
        self.assertEqual(first=str(cm.exception), second="bulk_create is not implemented.")

    def test_cannot_create_user_with_existing_username_1(self):
        entity = Entity(slug='zzzzzz')
        entity.save()
        # entity.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        with self.assertRaises(ValidationError) as cm:
            user = DefaultUserFactory(slug='ZZZ-ZZZ')
            user.save_user_and_profile()
            # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['This username is already taken.'], 'slug': ['This username is already taken.']})

    def test_cannot_create_user_with_existing_username_2(self):
        user_1 = DefaultUserFactory(slug='zzzzzz')
        user_1.save_user_and_profile()
        # user_1.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        with self.assertRaises(ValidationError) as cm:
            user_2 = DefaultUserFactory(slug='ZZZ-ZZZ')
            user_2.save_user_and_profile()
            # user_2.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['This username is already taken.'], 'slug': ['This username is already taken.']})

    def test_has_no_confirmed_email(self):
        user = DefaultUserFactory()
        UserEmailAddressFactory(user=user, is_confirmed=False)
        UserEmailAddressFactory(user=user, is_confirmed=False)
        self.assertFalse(expr=user.has_confirmed_email())

    def test_has_a_confirmed_email(self):
        user = DefaultUserFactory()
        UserEmailAddressFactory(user=user, is_confirmed=False)
        UserEmailAddressFactory(user=user, is_confirmed=True)
        self.assertTrue(expr=user.has_confirmed_email())

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
            # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Ensure this value has at least 6 characters (it has 5).'], 'slug': ['Ensure this value has at least 6 characters (it has 5).']})

    def test_slug_and_username_min_length_ok(self):
        user = DefaultUserFactory(slug='a' * 6)
        user.save_user_and_profile()
        # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()

    def test_slug_max_length_fail(self):
        with self.assertRaises(ValidationError) as cm:
            user = DefaultUserFactory(slug='a' * 201)
            user.save_user_and_profile()
            # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Ensure this value has at most 40 characters (it has 201).'], 'slug': ['Ensure this value has at most 200 characters (it has 201).']})

    def test_slug_max_length_ok(self):
        with self.assertRaises(ValidationError) as cm:
            user = DefaultUserFactory(slug='b' * 200)
            user.save_user_and_profile()
            # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Ensure this value has at most 40 characters (it has 200).']})

    def test_username_max_length_fail(self):
        with self.assertRaises(ValidationError) as cm:
            user = DefaultUserFactory(slug='a' * 41)
            user.save_user_and_profile()
            # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Ensure this value has at most 40 characters (it has 41).']})

    def test_username_max_length_ok(self):
        user = DefaultUserFactory(slug='a' * 40)
        user.save_user_and_profile()
        # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()

    def test_star2000_is_valid_username(self):
        user = DefaultUserFactory(slug='star2000', username='star2000')
        user.save_user_and_profile()
        # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()

    def test_come2us_is_invalid_username(self):
        with self.assertRaises(ValidationError) as cm:
            user = DefaultUserFactory(slug='come2us', username='come2us')
            user.save_user_and_profile()
            # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'], 'slug': ['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.']})

    def test_000000_is_invalid_username(self):
        with self.assertRaises(ValidationError) as cm:
            user = DefaultUserFactory(slug='0' * 6, username='0' * 6)
            user.save_user_and_profile()
            # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'], 'slug': ['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.']})

    def test_0test1_is_invalid_username(self):
        with self.assertRaises(ValidationError) as cm:
            user = DefaultUserFactory(slug='0-test-1', username='0test1')
            user.save_user_and_profile()
            # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'], 'slug': ['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.']})

    def test_slug_and_username_dont_match_but_valid(self):
        with self.assertRaises(ValidationError) as cm:
            user = DefaultUserFactory(slug='star2001', username='star2000')
            user.save_user_and_profile()
            # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'slug': ['Slug does not parse to username.']})

    def test_slug_and_username_dont_match_and_invalid(self):
        with self.assertRaises(ValidationError) as cm:
            user = DefaultUserFactory(slug='0-test-2', username='0test1')
            user.save_user_and_profile()
            # user.full_clean() # ~~~~ TODO: remove this line! test should also work without .full_clean()
        self.assertDictEqual(d1=dict(cm.exception), d2={'username': ['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'], 'slug': ['Slug does not parse to username.']})

    def test_user_can_change_password(self):
        new_password = '8' * 8
        incorrect_new_password = '7' * 8
        user = DefaultUserFactory()
        self.assertTrue(expr=user.check_password(raw_password=USER_PASSWORD))
        user.set_password(raw_password=new_password)
        self.assertTrue(expr=user.check_password(raw_password=new_password))
        self.assertFalse(expr=user.check_password(raw_password=incorrect_new_password))
        self.assertFalse(expr=user.check_password(raw_password=USER_PASSWORD))

    def test_password_too_short_exception(self):
        new_password = '8' * 3
        user = DefaultUserFactory()
        self.assertTrue(expr=user.check_password(raw_password=USER_PASSWORD))
        with self.assertRaises(ValidationError) as cm:
            user.set_password(raw_password=new_password)
        self.assertEqual(first=str(cm.exception.message), second='Password too short.')
        self.assertListEqual(list1=list(cm.exception), list2=['Password too short.'])
        self.assertTrue(expr=user.check_password(raw_password=USER_PASSWORD))
        self.assertFalse(expr=user.check_password(raw_password=new_password))

    def test_password_too_long_exception(self):
        new_password = '8' * 121
        user = DefaultUserFactory()
        self.assertTrue(expr=user.check_password(raw_password=USER_PASSWORD))
        with self.assertRaises(ValidationError) as cm:
            user.set_password(raw_password=new_password)
        self.assertEqual(first=str(cm.exception.message), second='Password too long.')
        self.assertListEqual(list1=list(cm.exception), list2=['Password too long.'])
        self.assertTrue(expr=user.check_password(raw_password=USER_PASSWORD))
        self.assertFalse(expr=user.check_password(raw_password=new_password))


