from django.core.exceptions import ValidationError

from speedy.core.test import TestCase
from .models import normalize_slug, normalize_username, Entity, User
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
    # def setUp(self):
    #     User()  # check that User.__init__ does not mutate Entity

    def test_automatic_creation_of_id(self):
        entity = Entity(slug='zzzzzz')
        entity.save()
        self.assertEqual(20, len(entity.id))

    def test_slug_and_username_min_length_fail(self):
        entity = Entity(slug='a' * 5, username='z' * 5)
        self.assertRaisesRegex(ValidationError, "'slug': \['Ensure this value has at least 6 characters \(it has 5\).'\]", entity.full_clean)
        self.assertRaisesRegex(ValidationError, "'username': \['Ensure this value has at least 6 characters \(it has 5\).'\]", entity.full_clean)

    def test_slug_and_username_min_length_ok(self):
        entity = Entity(slug='a' * 6, username='z' * 6)
        self.assertIsNone(entity.full_clean())

    def test_slug_and_username_max_length_fail(self):
        entity = Entity(slug='a' * 201, username='z' * 201)
        self.assertRaisesRegex(ValidationError, "'slug': \['Ensure this value has at most 200 characters \(it has 201\).'\]", entity.full_clean)
        self.assertRaisesRegex(ValidationError, "'username': \['Ensure this value has at most 120 characters \(it has 201\).'\]", entity.full_clean)

    def test_slug_and_username_max_length_ok(self):
        entity = Entity(slug='a' * 200, username='z' * 200)
        self.assertIsNone(entity.full_clean())


class UserTestCase(TestCase):

    # def setUp(self):
    #     Entity()  # check that Entity.__init__ does not mutate User

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

    def test_slug_and_username_min_length_fail(self):
        user = UserFactory(slug='a' * 5)
        self.assertRaisesRegex(ValidationError, "'slug': \['Ensure this value has at least 6 characters \(it has 5\).'\]", user.full_clean)
        self.assertRaisesRegex(ValidationError, "'username': \['Ensure this value has at least 6 characters \(it has 5\).'\]", user.full_clean)

    def test_slug_and_username_min_length_ok(self):
        user = UserFactory(slug='a' * 6)
        self.assertIsNone(user.full_clean())

    def test_slug_and_username_max_length_fail(self):
        user = UserFactory(slug='a' * 201)
        self.assertRaisesRegex(ValidationError, "'slug': \['Ensure this value has at most 200 characters \(it has 201\).'\]", user.full_clean)
        self.assertRaisesRegex(ValidationError, "'username': \['Ensure this value has at most 20 characters \(it has 201\).'\]", user.full_clean)

    def test_slug_and_username_max_length_ok(self):
        user = UserFactory(slug='a' * 20)
        self.assertIsNone(user.full_clean())
