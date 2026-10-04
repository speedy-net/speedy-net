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
            def set_up(self):
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()

            def test_user_likes_himself_raises_an_exception(self):
                self.assertEqual(first=UserLike.objects.count(), second=0)
                with self.assertRaises(ValidationError) as cm:
                    UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_1)
                self.assertEqual(first=str(cm.exception.message), second='Users cannot like themselves.')
                self.assertListEqual(list1=list(cm.exception), list2=['Users cannot like themselves.'])
                self.assertEqual(first=UserLike.objects.count(), second=0)

            def test_user_likes_other_user_twice_raises_an_exception(self):
                UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                self.assertEqual(first=UserLike.objects.count(), second=1)
                with self.assertRaises(ValidationError) as cm:
                    UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                self.assertEqual(first=str(cm.exception.message), second='User already likes other user.')
                self.assertListEqual(list1=list(cm.exception), list2=['User already likes other user.'])
                self.assertEqual(first=UserLike.objects.count(), second=1)

            def test_user_cannot_like_a_user_who_blocked_him(self):
                Block.objects.block(blocker=self.user_2, blocked=self.user_1)
                self.assertEqual(first=UserLike.objects.count(), second=0)
                with self.assertRaises(ValidationError) as cm:
                    UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                self.assertEqual(first=str(cm.exception.message), second='User cannot like a blocked user.')
                self.assertListEqual(list1=list(cm.exception), list2=['User cannot like a blocked user.'])
                self.assertEqual(first=UserLike.objects.count(), second=0)

            def test_user_cannot_like_a_user_he_blocked(self):
                Block.objects.block(blocker=self.user_1, blocked=self.user_2)
                self.assertEqual(first=UserLike.objects.count(), second=0)
                with self.assertRaises(ValidationError) as cm:
                    UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                self.assertEqual(first=str(cm.exception.message), second='User cannot like a blocked user.')
                self.assertListEqual(list1=list(cm.exception), list2=['User cannot like a blocked user.'])
                self.assertEqual(first=UserLike.objects.count(), second=0)

            def test_remove_all_likes_from_user(self):
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
                third_user = ActiveUserFactory()
                UserLike.objects.add_like(from_user=self.user_2, to_user=self.user_1)
                UserLike.objects.add_like(from_user=third_user, to_user=self.user_1)
                UserLike.objects.add_like(from_user=self.user_1, to_user=third_user)
                self.assertEqual(first=UserLike.objects.count(), second=3)
                UserLike.objects.remove_all_likes_to_user(to_user=self.user_1)
                self.assertEqual(first=UserLike.objects.count(), second=1)
                self.assertEqual(first=UserLike.objects.filter(to_user=self.user_1).count(), second=0)
                self.assertEqual(first=UserLike.objects.filter(from_user=self.user_1, to_user=third_user).count(), second=1)
