from django.core.exceptions import ValidationError

from speedy.core.base.test import TestCase, only_on_sites_with_login
from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from ..models import Block


@only_on_sites_with_login
class BlockManagerTestCase(TestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()

    def test_block(self):
        self.assertEqual(first=Block.objects.count(), second=0)
        block = Block.objects.block(blocker=self.user, blocked=self.other_user)
        self.assertEqual(first=Block.objects.count(), second=1)
        self.assertEqual(first=block.blocker_id, second=self.user.id)
        self.assertEqual(first=block.blocked_id, second=self.other_user.id)

    def test_existing_block(self):
        block = Block.objects.block(blocker=self.user, blocked=self.other_user)
        self.assertEqual(first=Block.objects.count(), second=1)
        block2 = Block.objects.block(blocker=self.user, blocked=self.other_user)
        self.assertEqual(first=Block.objects.count(), second=1)
        self.assertEqual(first=block, second=block2)

    def test_unblock(self):
        Block.objects.block(blocker=self.user, blocked=self.other_user)
        self.assertEqual(first=Block.objects.count(), second=1)
        Block.objects.unblock(blocker=self.user, blocked=self.other_user)
        self.assertEqual(first=Block.objects.count(), second=0)
        Block.objects.unblock(blocker=self.user, blocked=self.other_user)
        self.assertEqual(first=Block.objects.count(), second=0)

    def test_has_blocked_true(self):
        Block.objects.block(blocker=self.user, blocked=self.other_user)
        self.assertTrue(expr=Block.objects.has_blocked(blocker=self.user, blocked=self.other_user))

    def test_has_blocked_false(self):
        self.assertFalse(expr=Block.objects.has_blocked(blocker=self.user, blocked=self.other_user))

    def test_user_blocks_himself_throws_an_exception(self):
        with self.assertRaises(ValidationError) as cm:
            Block.objects.block(blocker=self.user, blocked=self.user)
        self.assertEqual(first=str(cm.exception.message), second='Users cannot block themselves.')
        self.assertListEqual(list1=list(cm.exception), list2=['Users cannot block themselves.'])


