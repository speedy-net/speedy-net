from django.conf import settings as django_settings
from django.core.exceptions import ValidationError

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.blocks.models import Block

        from speedy.core.accounts.test.user_factories import ActiveUserFactory


        @only_on_sites_with_login
        class BlockManagerTestCase(SiteTestCase):
            def set_up(self):
                super().set_up()
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

            def test_user_blocks_themself_throws_an_exception(self):
                with self.assertRaises(ValidationError) as cm:
                    Block.objects.block(blocker=self.user, blocked=self.user)
                self.assertEqual(first=str(cm.exception.message), second='Users cannot block themselves.') ###### TODO
                self.assertListEqual(list1=list(cm.exception), list2=['Users cannot block themselves.']) ###### TODO

            def test_cannot_delete_blocks_with_queryset_delete(self):
                with self.assertRaises(NotImplementedError) as cm:
                    Block.objects.delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    Block.objects.all().delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    Block.objects.filter(pk=1).delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    Block.objects.all().exclude(pk=2).delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")


