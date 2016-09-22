from django.test import TestCase

from .models import normalize_slug, normalize_username, Entity
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
    def test_automatic_creation_of_id_and_slug(self):
        entity = Entity()
        entity.save()
        self.assertEqual(15, len(entity.id))
        self.assertEqual(entity.id, entity.slug)


class UserTestCase(TestCase):
    def test_has_no_confirmed_email(self):
        user = UserFactory()
        UserEmailAddressFactory(user=user, is_confirmed=False)
        UserEmailAddressFactory(user=user, is_confirmed=False)
        self.assertFalse(user.has_confirmed_email())

    def test_has_no_confirmed_email(self):
        user = UserFactory()
        UserEmailAddressFactory(user=user, is_confirmed=False)
        UserEmailAddressFactory(user=user, is_confirmed=True)
        self.assertTrue(user.has_confirmed_email())
