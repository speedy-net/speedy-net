from django.test import TestCase

from .models import Entity
from .test_factories import UserFactory, UserEmailAddressFactory


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
