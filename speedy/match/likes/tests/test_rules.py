from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.contrib.auth.models import AnonymousUser

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.accounts.models import Entity, ReservedUsername
        from speedy.core.blocks.models import Block
        from speedy.match.likes.models import UserLike

        from speedy.match.likes.rules import you_like_user, user_likes_you, both_are_users


        @only_on_speedy_match
        class LikeRulesOnlyEnglishTestCase(SiteTestCase):
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
        class UnlikeRulesOnlyEnglishTestCase(SiteTestCase):
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
        class ViewLikesRulesOnlyEnglishTestCase(SiteTestCase):
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


        @only_on_speedy_match
        class UserLikeRulesOnlyEnglishTestCase(SiteTestCase):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()
                self.anon = AnonymousUser()
                self.entity = Entity()
                self.reserved_username = ReservedUsername()

            def test_you_like_user_false(self):
                self.assertIs(expr1=you_like_user(user=self.user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=you_like_user(user=self.other_user, other_user=self.user), expr2=False)

            def test_you_like_user_true(self):
                UserLike.objects.add_like(from_user=self.user, to_user=self.other_user)
                self.assertIs(expr1=you_like_user(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=you_like_user(user=self.other_user, other_user=self.user), expr2=False)

            def test_user_likes_you_false(self):
                self.assertIs(expr1=user_likes_you(user=self.user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=user_likes_you(user=self.other_user, other_user=self.user), expr2=False)

            def test_user_likes_you_true(self):
                UserLike.objects.add_like(from_user=self.other_user, to_user=self.user)
                self.assertIs(expr1=user_likes_you(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=user_likes_you(user=self.other_user, other_user=self.user), expr2=False)

            def test_mutual_likes_false(self):
                self.assertIs(expr1=you_like_user(user=self.user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=you_like_user(user=self.other_user, other_user=self.user), expr2=False)
                self.assertIs(expr1=user_likes_you(user=self.user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=user_likes_you(user=self.other_user, other_user=self.user), expr2=False)

            def test_mutual_likes_true(self):
                UserLike.objects.add_like(from_user=self.user, to_user=self.other_user)
                UserLike.objects.add_like(from_user=self.other_user, to_user=self.user)
                self.assertIs(expr1=you_like_user(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=you_like_user(user=self.other_user, other_user=self.user), expr2=True)
                self.assertIs(expr1=user_likes_you(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=user_likes_you(user=self.other_user, other_user=self.user), expr2=True)

            def test_both_are_users_true(self):
                self.assertIs(expr1=both_are_users(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=both_are_users(user=self.other_user, other_user=self.user), expr2=True)

            def test_both_are_users_false(self):
                self.assertIs(expr1=both_are_users(user=self.user, other_user=self.anon), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.other_user, other_user=self.anon), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.anon, other_user=self.user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.anon, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.user, other_user=self.entity), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.other_user, other_user=self.entity), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.entity, other_user=self.user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.entity, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.anon, other_user=self.entity), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.entity, other_user=self.anon), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.user, other_user=self.reserved_username), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.other_user, other_user=self.reserved_username), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.reserved_username, other_user=self.user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.reserved_username, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.anon, other_user=self.reserved_username), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.reserved_username, other_user=self.anon), expr2=False)


