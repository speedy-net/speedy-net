from django.core.exceptions import ValidationError

from speedy.core.accounts.models import normalize_slug, normalize_username, Entity
from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software, exclude_on_speedy_match
from .test_factories import ActiveUserFactory, UserEmailAddressFactory


class NormalizeSlugTestCase(TestCase):
    def test_convert_to_lowercase(self):
        self.assertEqual(first=normalize_slug(slug='CamelCase'), second='camelcase')

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
    def test_this(self):
        self.assertEqual(first=normalize_username(slug='this-is-a-slug'), second='thisisaslug')
        self.assertEqual(first=normalize_username(slug='.this_is...a_slug--'), second='thisisaslug')


class EntityTestCase(TestCase):
    def test_automatic_creation_of_id(self):
        entity = Entity(slug='zzzzzz')
        entity.save()
        self.assertEqual(first=15, second=len(entity.id))

    def test_slug_and_username_min_length_fail(self):
        entity = Entity(slug='a' * 5, username='a' * 5)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'slug': \['Ensure this value has at least 6 characters \(it has 5\).'\]", callable=entity.full_clean)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'username': \['Ensure this value has at least 6 characters \(it has 5\).'\]", callable=entity.full_clean)

    def test_slug_and_username_min_length_ok(self):
        entity = Entity(slug='a' * 6, username='a' * 6)
        self.assertIsNone(obj=entity.full_clean(exclude={'id'}))

    def test_slug_and_username_max_length_fail(self):
        entity = Entity(slug='a' * 201, username='z' * 201)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'slug': \['Ensure this value has at most 200 characters \(it has 201\).'\]", callable=entity.full_clean)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'username': \['Ensure this value has at most 120 characters \(it has 201\).'\]", callable=entity.full_clean)

    def test_slug_and_username_max_length_ok(self):
        entity = Entity(slug='a' * 120 + '-' * 80, username='a' * 120)
        self.assertIsNone(obj=entity.full_clean(exclude={'id'}))

    def test_star2000_is_valid_username(self):
        entity = Entity(slug='star2000', username='star2000')
        self.assertIsNone(obj=entity.full_clean(exclude={'id'}))

    def test_come2us_is_valid_username(self):
        entity = Entity(slug='come2us', username='come2us')
        self.assertIsNone(obj=entity.full_clean(exclude={'id'}))


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class UserTestCase(TestCase):
    @exclude_on_speedy_match
    def test_has_no_confirmed_email(self):
        user = ActiveUserFactory()
        UserEmailAddressFactory(user=user, is_confirmed=False)
        UserEmailAddressFactory(user=user, is_confirmed=False)
        self.assertFalse(expr=user.has_confirmed_email())

    def test_has_a_confirmed_email(self):
        user = ActiveUserFactory()
        UserEmailAddressFactory(user=user, is_confirmed=False)
        UserEmailAddressFactory(user=user, is_confirmed=True)
        self.assertTrue(expr=user.has_confirmed_email())

    def test_user_id_length(self):
        user = ActiveUserFactory()
        self.assertEqual(first=len(user.id), second=15)

    def test_user_id_number_in_range(self):
        user = ActiveUserFactory()
        self.assertGreaterEqual(a=int(user.id), b=10 ** 14)
        self.assertLess(a=int(user.id), b=10 ** 15)

    def test_slug_and_username_min_length_fail(self):
        user = ActiveUserFactory(slug='a' * 5)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'slug': \['Ensure this value has at least 6 characters \(it has 5\).'\]", callable=user.full_clean)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'username': \['Ensure this value has at least 6 characters \(it has 5\).'\]", callable=user.full_clean)

    def test_slug_and_username_min_length_ok(self):
        user = ActiveUserFactory(slug='a' * 6)
        self.assertIsNone(obj=user.full_clean())

    def test_slug_max_length_fail(self):
        user = ActiveUserFactory(slug='a' * 201)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'slug': \['Ensure this value has at most 200 characters \(it has 201\).'\]", callable=user.full_clean)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'username': \['Ensure this value has at most 40 characters \(it has 201\).'\]", callable=user.full_clean)

    def test_slug_max_length_ok(self):
        user = ActiveUserFactory(slug='b' * 200)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'username': \['Ensure this value has at most 40 characters \(it has 200\).'\]", callable=user.full_clean)

    def test_username_max_length_fail(self):
        user = ActiveUserFactory(slug='a' * 41)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'username': \['Ensure this value has at most 40 characters \(it has 41\).'\]", callable=user.full_clean)

    def test_username_max_length_ok(self):
        user = ActiveUserFactory(slug='a' * 40)
        self.assertIsNone(obj=user.full_clean())

    def test_star2000_is_valid_username(self):
        user = ActiveUserFactory(slug='star2000', username='star2000')
        self.assertIsNone(obj=user.full_clean(exclude={'id'}))

    def test_come2us_is_invalid_username(self):
        user = ActiveUserFactory(slug='come2us', username='come2us')
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'slug': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", callable=user.full_clean)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'username': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", callable=user.full_clean)

    def test_000000_is_invalid_username(self):
        user = ActiveUserFactory(slug='0' * 6, username='0' * 6)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'slug': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", callable=user.full_clean)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'username': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", callable=user.full_clean)

    def test_0test1_is_invalid_username(self):
        user = ActiveUserFactory(slug='0-test-1', username='0test1')
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'slug': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", callable=user.full_clean)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'username': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", callable=user.full_clean)

    def test_slug_and_username_dont_match_but_valid(self):
        user = ActiveUserFactory(slug='star2001', username='star2000')
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'slug': \['Slug does not parse to username.'\]", callable=user.full_clean)

    def test_slug_and_username_dont_match_and_invalid(self):
        user = ActiveUserFactory(slug='0-test-2', username='0test1')
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'slug': \['Slug does not parse to username.'\]", callable=user.full_clean)
        self.assertRaisesRegex(expected_exception=ValidationError, expected_regex="'username': \['Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'\]", callable=user.full_clean)

