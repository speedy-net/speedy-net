"""
Test cases for the UserLike manager of Speedy Match.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.core.exceptions import ValidationError

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.blocks.models import Block
        from speedy.match.likes.models import UserLike


        @only_on_speedy_match
        class UserLikeManagerOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the UserLike manager's add_like, remove_all_likes_from_user and remove_all_likes_to_user methods, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates two active users, user_1 and user_2.
                test_user_likes_himself_raises_an_exception(self): Asserts a user cannot like himself.
                test_user_likes_other_user_twice_raises_an_exception(self): Asserts a user cannot like another user twice.
                test_user_cannot_like_a_user_who_blocked_him(self): Asserts a user cannot like a user who blocked him.
                test_user_cannot_like_a_user_he_blocked(self): Asserts a user cannot like a user he blocked.
                test_remove_all_likes_from_user(self): Asserts remove_all_likes_from_user removes only likes originating from the given user.
                test_remove_all_likes_to_user(self): Asserts remove_all_likes_to_user removes only likes directed to the given user.
            """

            def set_up(self):
                """
                Creates two active users, user_1 and user_2.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()

            def test_user_likes_himself_raises_an_exception(self):
                """
                Asserts that adding a like from a user to himself raises a ValidationError and no UserLike is created.
                """
                self.assertEqual(first=UserLike.objects.count(), second=0)
                with self.assertRaises(ValidationError) as cm:
                    UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_1)
                self.assertEqual(first=str(cm.exception.message), second='Users cannot like themselves.')
                self.assertListEqual(list1=list(cm.exception), list2=['Users cannot like themselves.'])
                self.assertEqual(first=UserLike.objects.count(), second=0)

            def test_user_likes_other_user_twice_raises_an_exception(self):
                """
                Asserts that adding the same like twice raises a ValidationError and the second like is not created.
                """
                UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                self.assertEqual(first=UserLike.objects.count(), second=1)
                with self.assertRaises(ValidationError) as cm:
                    UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                self.assertEqual(first=str(cm.exception.message), second='User already likes other user.')
                self.assertListEqual(list1=list(cm.exception), list2=['User already likes other user.'])
                self.assertEqual(first=UserLike.objects.count(), second=1)

            def test_user_cannot_like_a_user_who_blocked_him(self):
                """
                Asserts that a user cannot like a user who has blocked him; a ValidationError is raised and no UserLike is created.
                """
                Block.objects.block(blocker=self.user_2, blocked=self.user_1)
                self.assertEqual(first=UserLike.objects.count(), second=0)
                with self.assertRaises(ValidationError) as cm:
                    UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                self.assertEqual(first=str(cm.exception.message), second='User cannot like a blocked user.')
                self.assertListEqual(list1=list(cm.exception), list2=['User cannot like a blocked user.'])
                self.assertEqual(first=UserLike.objects.count(), second=0)

            def test_user_cannot_like_a_user_he_blocked(self):
                """
                Asserts that a user cannot like a user he has blocked; a ValidationError is raised and no UserLike is created.
                """
                Block.objects.block(blocker=self.user_1, blocked=self.user_2)
                self.assertEqual(first=UserLike.objects.count(), second=0)
                with self.assertRaises(ValidationError) as cm:
                    UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                self.assertEqual(first=str(cm.exception.message), second='User cannot like a blocked user.')
                self.assertListEqual(list1=list(cm.exception), list2=['User cannot like a blocked user.'])
                self.assertEqual(first=UserLike.objects.count(), second=0)

            def test_remove_all_likes_from_user(self):
                """
                Asserts remove_all_likes_from_user removes only the likes that originate from the given user, leaving likes directed to him intact.
                """
                third_user = ActiveUserFactory()
                UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                UserLike.objects.add_like(from_user=self.user_1, to_user=third_user)
                UserLike.objects.add_like(from_user=third_user, to_user=self.user_1)
                self.assertEqual(first=UserLike.objects.count(), second=3)
                UserLike.objects.remove_all_likes_from_user(from_user=self.user_1)
                self.assertEqual(first=UserLike.objects.count(), second=1)
                self.assertEqual(first=UserLike.objects.filter(from_user=self.user_1).count(), second=0)
                self.assertEqual(first=UserLike.objects.filter(from_user=third_user, to_user=self.user_1).count(), second=1)

            def test_remove_all_likes_to_user(self):
                """
                Asserts remove_all_likes_to_user removes only the likes that are directed to the given user, leaving likes he initiated intact.
                """
                third_user = ActiveUserFactory()
                UserLike.objects.add_like(from_user=self.user_2, to_user=self.user_1)
                UserLike.objects.add_like(from_user=third_user, to_user=self.user_1)
                UserLike.objects.add_like(from_user=self.user_1, to_user=third_user)
                self.assertEqual(first=UserLike.objects.count(), second=3)
                UserLike.objects.remove_all_likes_to_user(to_user=self.user_1)
                self.assertEqual(first=UserLike.objects.count(), second=1)
                self.assertEqual(first=UserLike.objects.filter(to_user=self.user_1).count(), second=0)
                self.assertEqual(first=UserLike.objects.filter(from_user=self.user_1, to_user=third_user).count(), second=1)


