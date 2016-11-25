from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError

from speedy.core.test import TestCase
from ..models import normalize_slug, normalize_username, Entity, User
from .test_factories import UserFactory, UserEmailAddressFactory


class NormalizeSlugTestCase(TestCase):
    def test_convert_to_lowercase(self):
        self.assertEqual(normalize_slug('CamelCase'), 'camelcase')

    def test_convert_dots_to_dashes(self):
        self.assertEqual(normalize_slug('one.dot'), 'one-dot')
        self.assertEqual(normalize_slug('two..dot.s'), 'two-dot-s')

    def test_convert_underscores_to_dashes(self):
        self.assertEqual(normalize_slug('one_underscore'), 'one-underscore')
        self.assertEqual(normalize_slug('two__under_scores'), 'two-under-scores')

    def test_convert_multiple_dashes_to_one(self):
        self.assertEqual(normalize_slug('three---dash---es'), 'three-dash-es')

    def test_cut_leading_symbols(self):
        self.assertEqual(normalize_slug('-dash'), 'dash')
        self.assertEqual(normalize_slug('..dots'), 'dots')
        self.assertEqual(normalize_slug('_under_score'), 'under-score')

    def test_cut_trailing_symbols(self):
        self.assertEqual(normalize_slug('dash-'), 'dash')
        self.assertEqual(normalize_slug('dots...'), 'dots')
        self.assertEqual(normalize_slug('under_score_'), 'under-score')


class NormalizeUsernameTestCase(TestCase):
    def test_this(self):
        self.assertEqual(normalize_username('this-is-a-slug'), 'thisisaslug')
        self.assertEqual(normalize_username('.this_is...a_slug--'), 'thisisaslug')


class EntityTestCase(TestCase):

    def test_automatic_creation_of_id(self):
        entity = Entity(slug='zzzzzz')
        entity.save()
        self.assertEqual(15, len(entity.id))

    def test_slug_and_username_min_length_fail(self):
        entity = Entity(slug='a' * 5, username='a' * 5)
        self.assertRaisesRegex(ValidationError, "'slug': \['Ensure this value has at least 6 characters \(it has 5\).'\]", entity.full_clean)
        self.assertRaisesRegex(ValidationError, "'username': \['Ensure this value has at least 6 characters \(it has 5\).'\]", entity.full_clean)

    def test_slug_and_username_min_length_ok(self):
        entity = Entity(slug='a' * 6, username='a' * 6)
        self.assertIsNone(entity.full_clean(exclude={'id'}))

    def test_slug_and_username_max_length_fail(self):
        entity = Entity(slug='a' * 201, username='z' * 201)
        self.assertRaisesRegex(ValidationError, "'slug': \['Ensure this value has at most 200 characters \(it has 201\).'\]", entity.full_clean)
        self.assertRaisesRegex(ValidationError, "'username': \['Ensure this value has at most 120 characters \(it has 201\).'\]", entity.full_clean)

    def test_slug_and_username_max_length_ok(self):
        entity = Entity(slug='a' * 120 + '-' * 80, username='a' * 120)
        self.assertIsNone(entity.full_clean(exclude={'id'}))

    def test_star2000_is_valid_username(self):
        entity = Entity(slug='star2000', username='star2000')
        self.assertIsNone(entity.full_clean(exclude={'id'}))

    def test_come2us_is_valid_username(self):
        entity = Entity(slug='come2us', username='come2us')
        self.assertIsNone(entity.full_clean(exclude={'id'}))


class UserTestCase(TestCase):

    def test_has_no_confirmed_email(self):
        user = UserFactory()
        UserEmailAddressFactory(user=user, is_confirmed=False)
        UserEmailAddressFactory(user=user, is_confirmed=False)
        self.assertFalse(user.has_confirmed_email())

    def test_has_a_confirmed_email(self):
        user = UserFactory()
        UserEmailAddressFactory(user=user, is_confirmed=False)
        UserEmailAddressFactory(user=user, is_confirmed=True)
        self.assertTrue(user.has_confirmed_email())

    def test_user_id_length(self):
        user = UserFactory()
        self.assertEqual(len(user.id), 15)

    def test_user_id_number_in_range(self):
        user = UserFactory()
        self.assertGreaterEqual(int(user.id), 10 ** 14)
        self.assertLess(int(user.id), 10 ** 15)

    def test_slug_and_username_min_length_fail(self):
        user = UserFactory(slug='a' * 5)
        self.assertRaisesRegex(ValidationError, "'slug': \['Ensure this value has at least 6 characters \(it has 5\).'\]", user.full_clean)
        self.assertRaisesRegex(ValidationError, "'username': \['Ensure this value has at least 6 characters \(it has 5\).'\]", user.full_clean)

    def test_slug_and_username_min_length_ok(self):
        user = UserFactory(slug='a' * 6)
        self.assertIsNone(user.full_clean())

    def test_slug_max_length_fail(self):
        user = UserFactory(slug='a' * 201)
        self.assertRaisesRegex(ValidationError, "'slug': \['Ensure this value has at most 200 characters \(it has 201\).'\]", user.full_clean)
        self.assertRaisesRegex(ValidationError, "'username': \['Ensure this value has at most 50 characters \(it has 201\).'\]", user.full_clean)

    def test_slug_max_length_ok(self):
        user = UserFactory(slug='b' * 200)
        self.assertRaisesRegex(ValidationError, "'username': \['Ensure this value has at most 50 characters \(it has 200\).'\]", user.full_clean)

    def test_username_max_length_fail(self):
        user = UserFactory(slug='a' * 51)
        self.assertRaisesRegex(ValidationError, "'username': \['Ensure this value has at most 50 characters \(it has 51\).'\]", user.full_clean)

    def test_username_max_length_ok(self):
        user = UserFactory(slug='a' * 50)
        self.assertIsNone(user.full_clean())

    def test_star2000_is_valid_username(self):
        user = UserFactory(slug='star2000', username='star2000')
        self.assertIsNone(user.full_clean(exclude={'id'}))

    def test_come2us_is_invalid_username(self):
        user = UserFactory(slug='come2us', username='come2us')
        self.assertRaisesRegex(ValidationError, "'slug': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", user.full_clean)
        self.assertRaisesRegex(ValidationError, "'username': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", user.full_clean)

    def test_000000_is_invalid_username(self):
        user = UserFactory(slug='0' * 6, username='0' * 6)
        self.assertRaisesRegex(ValidationError, "'slug': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", user.full_clean)
        self.assertRaisesRegex(ValidationError, "'username': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", user.full_clean)

    def test_0test1_is_invalid_username(self):
        user = UserFactory(slug='0-test-1', username='0test1')
        self.assertRaisesRegex(ValidationError, "'slug': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", user.full_clean)
        self.assertRaisesRegex(ValidationError, "'username': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", user.full_clean)

    def test_slug_and_username_dont_match_but_valid(self):
        # ~~~~ TODO: this test should test an exception because the slug and the username don't match.
        # _('Slug does not parse to username.')
        user = UserFactory(slug='star2001', username='star2000')
        self.assertIsNone(user.full_clean(exclude={'id'})) # should fail

    def test_slug_and_username_dont_match_and_invalid(self):
        user = UserFactory(slug='0-test-2', username='0test1')
        self.assertRaisesRegex(ValidationError, "'slug': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", user.full_clean)
        self.assertRaisesRegex(ValidationError, "'username': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", user.full_clean)

