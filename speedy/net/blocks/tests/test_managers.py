from speedy.core.test import TestCase

from speedy.net.accounts.tests.test_factories import UserFactory
from ..models import Block


class BlockManagerTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()

    def test_block(self):
        self.assertEqual(Block.objects.count(), 0)
        block = Block.objects.block(self.user, self.other_user)
        self.assertEqual(Block.objects.count(), 1)
        self.assertEqual(block.blocker_id, self.user.id)
        self.assertEqual(block.blockee_id, self.other_user.id)

    def test_existing_block(self):
        block = Block.objects.block(self.user, self.other_user)
        self.assertEqual(Block.objects.count(), 1)
        block2 = Block.objects.block(self.user, self.other_user)
        self.assertEqual(Block.objects.count(), 1)
        self.assertEqual(block, block2)

    def test_unblock(self):
        Block.objects.block(self.user, self.other_user)
        self.assertEqual(Block.objects.count(), 1)
        Block.objects.unblock(self.user, self.other_user)
        self.assertEqual(Block.objects.count(), 0)
        Block.objects.unblock(self.user, self.other_user)
        self.assertEqual(Block.objects.count(), 0)

    def test_has_blocked_true(self):
        Block.objects.block(self.user, self.other_user)
        self.assertTrue(Block.objects.has_blocked(self.user, self.other_user))

    def test_has_blocked_false(self):
        self.assertFalse(Block.objects.has_blocked(self.user, self.other_user))
