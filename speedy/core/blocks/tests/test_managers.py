"""
Test cases for the managers of the blocks app of Speedy Core.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.core.exceptions import ValidationError

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.blocks.models import Block


        @only_on_sites_with_login
        class BlockManagerOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the BlockManager methods for blocking, unblocking, checking block status, and removing blocks between entities.

            Methods:
                test_block(self): Asserts blocking an entity creates a Block instance with the expected blocker and blocked ids.
                test_existing_block(self): Asserts blocking an already-blocked entity returns the existing Block instance instead of creating a new one.
                test_unblock(self): Asserts unblocking removes the Block instance, and is a no-op if no block exists.
                test_has_blocked_true(self): Asserts has_blocked returns True when the blocker has blocked the blocked entity.
                test_has_blocked_false(self): Asserts has_blocked returns False when no block exists.
                test_there_is_block_false(self): Asserts there_is_block returns False in both directions when no block exists between the two entities.
                test_there_is_block_true_when_blocker_blocked_the_other(self): Asserts there_is_block returns True in both directions when the first entity has blocked the second.
                test_there_is_block_true_when_blocked_blocked_the_blocker(self): Asserts there_is_block returns True in both directions when the second entity has blocked the first.
                test_remove_all_blocks_by_entity(self): Asserts remove_all_blocks_by_entity removes only the blocks created by the given entity, leaving blocks against it intact.
                test_remove_all_blocks_of_entity(self): Asserts remove_all_blocks_of_entity removes only the blocks targeting the given entity, leaving blocks it created intact.
                test_user_blocks_himself_raises_an_exception(self): Asserts blocking oneself raises a ValidationError with the expected message.
                test_cannot_delete_blocks_with_queryset_delete(self): Asserts that calling delete() on the Block queryset (in various forms) raises NotImplementedError.
            """
            def set_up(self):
                """
                Creates two active users (user, other_user) for use in the tests.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()

            def test_block(self):
                """
                Asserts blocking an entity creates a Block instance with the expected blocker and blocked ids.
                """
                self.assertEqual(first=Block.objects.count(), second=0)
                block = Block.objects.block(blocker=self.user, blocked=self.other_user)
                self.assertEqual(first=Block.objects.count(), second=1)
                self.assertEqual(first=block.blocker_id, second=self.user.id)
                self.assertEqual(first=block.blocked_id, second=self.other_user.id)

            def test_existing_block(self):
                """
                Asserts blocking an already-blocked entity returns the existing Block instance instead of creating a new one.
                """
                block = Block.objects.block(blocker=self.user, blocked=self.other_user)
                self.assertEqual(first=Block.objects.count(), second=1)
                block2 = Block.objects.block(blocker=self.user, blocked=self.other_user)
                self.assertEqual(first=Block.objects.count(), second=1)
                self.assertEqual(first=block, second=block2)

            def test_unblock(self):
                """
                Asserts unblocking removes the Block instance, and is a no-op if no block exists.
                """
                Block.objects.block(blocker=self.user, blocked=self.other_user)
                self.assertEqual(first=Block.objects.count(), second=1)
                Block.objects.unblock(blocker=self.user, blocked=self.other_user)
                self.assertEqual(first=Block.objects.count(), second=0)
                Block.objects.unblock(blocker=self.user, blocked=self.other_user)
                self.assertEqual(first=Block.objects.count(), second=0)

            def test_has_blocked_true(self):
                """
                Asserts has_blocked returns True when the blocker has blocked the blocked entity.
                """
                Block.objects.block(blocker=self.user, blocked=self.other_user)
                self.assertIs(expr1=Block.objects.has_blocked(blocker=self.user, blocked=self.other_user), expr2=True)

            def test_has_blocked_false(self):
                """
                Asserts has_blocked returns False when no block exists.
                """
                self.assertIs(expr1=Block.objects.has_blocked(blocker=self.user, blocked=self.other_user), expr2=False)

            def test_there_is_block_false(self):
                """
                Asserts there_is_block returns False in both directions when no block exists between the two entities.
                """
                self.assertIs(expr1=Block.objects.there_is_block(entity_1=self.user, entity_2=self.other_user), expr2=False)
                self.assertIs(expr1=Block.objects.there_is_block(entity_1=self.other_user, entity_2=self.user), expr2=False)

            def test_there_is_block_true_when_blocker_blocked_the_other(self):
                """
                Asserts there_is_block returns True in both directions when the first entity has blocked the second.
                """
                Block.objects.block(blocker=self.user, blocked=self.other_user)
                self.assertIs(expr1=Block.objects.there_is_block(entity_1=self.user, entity_2=self.other_user), expr2=True)
                self.assertIs(expr1=Block.objects.there_is_block(entity_1=self.other_user, entity_2=self.user), expr2=True)

            def test_there_is_block_true_when_blocked_blocked_the_blocker(self):
                """
                Asserts there_is_block returns True in both directions when the second entity has blocked the first.
                """
                Block.objects.block(blocker=self.other_user, blocked=self.user)
                self.assertIs(expr1=Block.objects.there_is_block(entity_1=self.user, entity_2=self.other_user), expr2=True)
                self.assertIs(expr1=Block.objects.there_is_block(entity_1=self.other_user, entity_2=self.user), expr2=True)

            def test_remove_all_blocks_by_entity(self):
                """
                Asserts remove_all_blocks_by_entity removes only the blocks created by the given entity, leaving blocks against it intact.
                """
                third_user = ActiveUserFactory()
                Block.objects.block(blocker=self.user, blocked=self.other_user)
                Block.objects.block(blocker=self.user, blocked=third_user)
                Block.objects.block(blocker=third_user, blocked=self.user)
                self.assertEqual(first=Block.objects.count(), second=3)
                Block.objects.remove_all_blocks_by_entity(blocker=self.user)
                self.assertEqual(first=Block.objects.count(), second=1)
                self.assertIs(expr1=Block.objects.has_blocked(blocker=self.user, blocked=self.other_user), expr2=False)
                self.assertIs(expr1=Block.objects.has_blocked(blocker=self.user, blocked=third_user), expr2=False)
                self.assertIs(expr1=Block.objects.has_blocked(blocker=third_user, blocked=self.user), expr2=True)

            def test_remove_all_blocks_of_entity(self):
                """
                Asserts remove_all_blocks_of_entity removes only the blocks targeting the given entity, leaving blocks it created intact.
                """
                third_user = ActiveUserFactory()
                Block.objects.block(blocker=self.other_user, blocked=self.user)
                Block.objects.block(blocker=third_user, blocked=self.user)
                Block.objects.block(blocker=self.user, blocked=third_user)
                self.assertEqual(first=Block.objects.count(), second=3)
                Block.objects.remove_all_blocks_of_entity(blocked=self.user)
                self.assertEqual(first=Block.objects.count(), second=1)
                self.assertIs(expr1=Block.objects.has_blocked(blocker=self.other_user, blocked=self.user), expr2=False)
                self.assertIs(expr1=Block.objects.has_blocked(blocker=third_user, blocked=self.user), expr2=False)
                self.assertIs(expr1=Block.objects.has_blocked(blocker=self.user, blocked=third_user), expr2=True)

            def test_user_blocks_himself_raises_an_exception(self):
                """
                Asserts blocking oneself raises a ValidationError with the expected message.
                """
                with self.assertRaises(ValidationError) as cm:
                    Block.objects.block(blocker=self.user, blocked=self.user)
                self.assertEqual(first=str(cm.exception.message), second='Users cannot block themselves.')  # ~~~~ TODO
                self.assertListEqual(list1=list(cm.exception), list2=['Users cannot block themselves.'])  # ~~~~ TODO

            def test_cannot_delete_blocks_with_queryset_delete(self):
                """
                Asserts that calling delete() on the Block queryset, directly or via all()/filter()/exclude(), always raises NotImplementedError.
                """
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


