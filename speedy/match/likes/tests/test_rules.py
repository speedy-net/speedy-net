from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.contrib.auth.models import AnonymousUser

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.blocks.models import Block
        from speedy.match.likes.models import UserLike


        @only_on_speedy_match
        class LikeRulesTestCase(SiteTestCase):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()
                self.anon = AnonymousUser()

            def test_anonymous_cannot_like(self):
                self.assertIs(expr1=self.anon.has_perm(perm='likes.like', obj=self.other_user), expr2=False)

            def test_user_cannot_like_self(self):
                self.assertIs(expr1=self.user.has_perm(perm='likes.like', obj=self.user), expr2=False)

            def test_user_can_like(self):
                self.assertIs(expr1=self.user.has_perm(perm='likes.like', obj=self.other_user), expr2=True)

            def test_user_cannot_like_other_user_if_blocked(self):
                Block.objects.block(blocker=self.user, blocked=self.other_user)
                self.assertIs(expr1=self.user.has_perm(perm='likes.like', obj=self.other_user), expr2=False)

            def test_user_cannot_like_other_user_if_blocking(self):
                Block.objects.block(blocker=self.other_user, blocked=self.user)
                self.assertIs(expr1=self.user.has_perm(perm='likes.like', obj=self.other_user), expr2=False)

            def test_user_cannot_like_twice(self):
                UserLike.objects.add_like(from_user=self.user, to_user=self.other_user)
                self.assertIs(expr1=self.user.has_perm(perm='likes.like', obj=self.other_user), expr2=False)


        @only_on_speedy_match
        class UnlikeRulesTestCase(SiteTestCase):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()
                self.anon = AnonymousUser()

            def test_anonymous_cannot_unlike(self):
                self.assertIs(expr1=self.anon.has_perm(perm='likes.unlike', obj=self.other_user), expr2=False)

            def test_user_cannot_unlike_self(self):
                self.assertIs(expr1=self.user.has_perm(perm='likes.unlike', obj=self.user), expr2=False)

            def test_user_cannot_unlike_if_doesnt_like(self):
                self.assertIs(expr1=self.user.has_perm(perm='likes.unlike', obj=self.other_user), expr2=False)

            def test_user_can_unlike_if_likes(self):
                UserLike.objects.add_like(from_user=self.user, to_user=self.other_user)
                self.assertIs(expr1=self.user.has_perm(perm='likes.unlike', obj=self.other_user), expr2=True)


        @only_on_speedy_match
        class ViewLikesRulesTestCase(SiteTestCase):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()
                self.anon = AnonymousUser()

            def test_anonymous_cannot_view_likes(self):
                self.assertIs(expr1=self.anon.has_perm(perm='likes.view_likes', obj=self.user), expr2=False)

            def test_other_user_cannot_view_likes(self):
                self.assertIs(expr1=self.other_user.has_perm(perm='likes.view_likes', obj=self.user), expr2=False)

            def test_user_can_view_likes(self):
                self.assertIs(expr1=self.user.has_perm(perm='likes.view_likes', obj=self.user), expr2=True)


