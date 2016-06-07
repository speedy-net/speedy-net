from django.test import TestCase

from .models import Entity


class EntityTestCase(TestCase):

    def test_automatic_creation_of_id_and_slug(self):
        entity = Entity()
        entity.save()
        self.assertEqual(15, len(entity.id))
        self.assertEqual(entity.id, entity.slug)
