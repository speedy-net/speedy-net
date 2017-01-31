from speedy.core.accounts.tests.test_factories import UserFactory
from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software
from ..models import Block


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class BlockManagerTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()

    def test_block(self):
        self.assertEqual(first=Block.objects.count(), second=0)
        block = Block.objects.block(self.user, self.other_user)
        self.assertEqual(first=Block.objects.count(), second=1)
        self.assertEqual(first=block.blocker_id, second=self.user.id)
        self.assertEqual(first=block.blockee_id, second=self.other_user.id)

    def test_existing_block(self):
        block = Block.objects.block(self.user, self.other_user)
        self.assertEqual(first=Block.objects.count(), second=1)
        block2 = Block.objects.block(self.user, self.other_user)
        self.assertEqual(first=Block.objects.count(), second=1)
        self.assertEqual(first=block, second=block2)

    def test_unblock(self):
        Block.objects.block(self.user, self.other_user)
        self.assertEqual(first=Block.objects.count(), second=1)
        Block.objects.unblock(self.user, self.other_user)
        self.assertEqual(first=Block.objects.count(), second=0)
        Block.objects.unblock(self.user, self.other_user)
        self.assertEqual(first=Block.objects.count(), second=0)

    def test_has_blocked_true(self):
        Block.objects.block(self.user, self.other_user)
        self.assertTrue(expr=Block.objects.has_blocked(self.user, self.other_user))

    def test_has_blocked_false(self):
        self.assertFalse(expr=Block.objects.has_blocked(self.user, self.other_user))
