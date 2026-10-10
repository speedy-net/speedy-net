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
            """
            Tests the 'likes.like' permission rule, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates a user, another user, and an anonymous user.
                test_anonymous_cannot_like(self): Asserts an anonymous user has no permission to like.
                test_user_cannot_like_self(self): Asserts a user has no permission to like himself.
                test_user_can_like(self): Asserts a user has permission to like another user.
                test_user_cannot_like_other_user_if_blocked(self): Asserts a user has no permission to like a user he blocked.
                test_user_cannot_like_other_user_if_blocking(self): Asserts a user has no permission to like a user who blocked him.
                test_user_cannot_like_twice(self): Asserts a user has no permission to like a user he already likes.
            """
            def set_up(self):
                """
                Creates a user, another user, and an anonymous user.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()
                self.anonymous_user = AnonymousUser()

            def test_anonymous_cannot_like(self):
                """
                Asserts an anonymous user has no permission to like another user.
                """
                self.assertIs(expr1=self.anonymous_user.has_perm(perm='likes.like', obj=self.other_user), expr2=False)

            def test_user_cannot_like_self(self):
                """
                Asserts a user has no permission to like himself.
                """
                self.assertIs(expr1=self.user.has_perm(perm='likes.like', obj=self.user), expr2=False)

            def test_user_can_like(self):
                """
                Asserts a user has permission to like another user.
                """
                self.assertIs(expr1=self.user.has_perm(perm='likes.like', obj=self.other_user), expr2=True)

            def test_user_cannot_like_other_user_if_blocked(self):
                """
                Asserts a user has no permission to like another user he has blocked.
                """
                Block.objects.block(blocker=self.user, blocked=self.other_user)
                self.assertIs(expr1=self.user.has_perm(perm='likes.like', obj=self.other_user), expr2=False)

            def test_user_cannot_like_other_user_if_blocking(self):
                """
                Asserts a user has no permission to like another user who has blocked him.
                """
                Block.objects.block(blocker=self.other_user, blocked=self.user)
                self.assertIs(expr1=self.user.has_perm(perm='likes.like', obj=self.other_user), expr2=False)

            def test_user_cannot_like_twice(self):
                """
                Asserts a user has no permission to like another user he already likes.
                """
                UserLike.objects.add_like(from_user=self.user, to_user=self.other_user)
                self.assertIs(expr1=self.user.has_perm(perm='likes.like', obj=self.other_user), expr2=False)


        @only_on_speedy_match
        class UnlikeRulesOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the 'likes.unlike' permission rule, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates a user, another user, and an anonymous user.
                test_anonymous_cannot_unlike(self): Asserts an anonymous user has no permission to unlike.
                test_user_cannot_unlike_self(self): Asserts a user has no permission to unlike himself.
                test_user_cannot_unlike_if_doesnt_like(self): Asserts a user has no permission to unlike a user he doesn't like.
                test_user_can_unlike_if_likes(self): Asserts a user has permission to unlike a user he likes.
            """
            def set_up(self):
                """
                Creates a user, another user, and an anonymous user.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()
                self.anonymous_user = AnonymousUser()

            def test_anonymous_cannot_unlike(self):
                """
                Asserts an anonymous user has no permission to unlike another user.
                """
                self.assertIs(expr1=self.anonymous_user.has_perm(perm='likes.unlike', obj=self.other_user), expr2=False)

            def test_user_cannot_unlike_self(self):
                """
                Asserts a user has no permission to unlike himself.
                """
                self.assertIs(expr1=self.user.has_perm(perm='likes.unlike', obj=self.user), expr2=False)

            def test_user_cannot_unlike_if_doesnt_like(self):
                """
                Asserts a user has no permission to unlike another user he doesn't currently like.
                """
                self.assertIs(expr1=self.user.has_perm(perm='likes.unlike', obj=self.other_user), expr2=False)

            def test_user_can_unlike_if_likes(self):
                """
                Asserts a user has permission to unlike another user he currently likes.
                """
                UserLike.objects.add_like(from_user=self.user, to_user=self.other_user)
                self.assertIs(expr1=self.user.has_perm(perm='likes.unlike', obj=self.other_user), expr2=True)


        @only_on_speedy_match
        class ViewLikesRulesOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the 'likes.view_likes' permission rule, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates a user, another user, and an anonymous user.
                test_anonymous_cannot_view_likes(self): Asserts an anonymous user has no permission to view a user's likes.
                test_other_user_cannot_view_likes(self): Asserts a user has no permission to view another user's likes.
                test_user_can_view_likes(self): Asserts a user has permission to view his own likes.
            """
            def set_up(self):
                """
                Creates a user, another user, and an anonymous user.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()
                self.anonymous_user = AnonymousUser()

            def test_anonymous_cannot_view_likes(self):
                """
                Asserts an anonymous user has no permission to view a user's likes.
                """
                self.assertIs(expr1=self.anonymous_user.has_perm(perm='likes.view_likes', obj=self.user), expr2=False)

            def test_other_user_cannot_view_likes(self):
                """
                Asserts a user has no permission to view another user's likes.
                """
                self.assertIs(expr1=self.other_user.has_perm(perm='likes.view_likes', obj=self.user), expr2=False)

            def test_user_can_view_likes(self):
                """
                Asserts a user has permission to view his own likes.
                """
                self.assertIs(expr1=self.user.has_perm(perm='likes.view_likes', obj=self.user), expr2=True)


        @only_on_speedy_match
        class UserLikeRulesOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the you_like_user, user_likes_you and both_are_users rule helper functions, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates a user, another user, an anonymous user, an entity, and a reserved username.
                test_you_like_user_false(self): Asserts you_like_user returns False when there's no like between the users.
                test_you_like_user_true(self): Asserts you_like_user returns True only in the direction the like was made.
                test_user_likes_you_false(self): Asserts user_likes_you returns False when there's no like between the users.
                test_user_likes_you_true(self): Asserts user_likes_you returns True only in the direction the like was made.
                test_mutual_likes_false(self): Asserts you_like_user and user_likes_you both return False when there's no like relation.
                test_mutual_likes_true(self): Asserts you_like_user and user_likes_you both return True in both directions when each user likes the other.
                test_both_are_users_true(self): Asserts both_are_users returns True when both arguments are users.
                test_both_are_users_false(self): Asserts both_are_users returns False whenever at least one argument is not a user (anonymous user, entity, or reserved username).
            """
            def set_up(self):
                """
                Creates a user, another user, an anonymous user, an entity, and a reserved username, to be used as both user and non-user arguments.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()
                self.anonymous_user = AnonymousUser()
                self.entity = Entity()
                self.reserved_username = ReservedUsername()

            def test_you_like_user_false(self):
                """
                Asserts you_like_user returns False in both directions when there's no like between the two users.
                """
                self.assertIs(expr1=you_like_user(user=self.user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=you_like_user(user=self.other_user, other_user=self.user), expr2=False)

            def test_you_like_user_true(self):
                """
                Asserts you_like_user returns True only for the direction in which the like was made, and False for the reverse direction.
                """
                UserLike.objects.add_like(from_user=self.user, to_user=self.other_user)
                self.assertIs(expr1=you_like_user(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=you_like_user(user=self.other_user, other_user=self.user), expr2=False)

            def test_user_likes_you_false(self):
                """
                Asserts user_likes_you returns False in both directions when there's no like between the two users.
                """
                self.assertIs(expr1=user_likes_you(user=self.user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=user_likes_you(user=self.other_user, other_user=self.user), expr2=False)

            def test_user_likes_you_true(self):
                """
                Asserts user_likes_you returns True only for the direction in which the other user was liked, and False for the reverse direction.
                """
                UserLike.objects.add_like(from_user=self.other_user, to_user=self.user)
                self.assertIs(expr1=user_likes_you(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=user_likes_you(user=self.other_user, other_user=self.user), expr2=False)

            def test_mutual_likes_false(self):
                """
                Asserts both you_like_user and user_likes_you return False in both directions when there's no like relation between the two users.
                """
                self.assertIs(expr1=you_like_user(user=self.user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=you_like_user(user=self.other_user, other_user=self.user), expr2=False)
                self.assertIs(expr1=user_likes_you(user=self.user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=user_likes_you(user=self.other_user, other_user=self.user), expr2=False)

            def test_mutual_likes_true(self):
                """
                Asserts both you_like_user and user_likes_you return True in both directions when each user likes the other (mutual likes).
                """
                UserLike.objects.add_like(from_user=self.user, to_user=self.other_user)
                UserLike.objects.add_like(from_user=self.other_user, to_user=self.user)
                self.assertIs(expr1=you_like_user(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=you_like_user(user=self.other_user, other_user=self.user), expr2=True)
                self.assertIs(expr1=user_likes_you(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=user_likes_you(user=self.other_user, other_user=self.user), expr2=True)

            def test_both_are_users_true(self):
                """
                Asserts both_are_users returns True in both directions when both arguments are users.
                """
                self.assertIs(expr1=both_are_users(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=both_are_users(user=self.other_user, other_user=self.user), expr2=True)

            def test_both_are_users_false(self):
                """
                Asserts both_are_users returns False whenever at least one of the two arguments is not a user (anonymous user, entity, or reserved username), in all argument orders and combinations.
                """
                self.assertIs(expr1=both_are_users(user=self.user, other_user=self.anonymous_user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.other_user, other_user=self.anonymous_user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.anonymous_user, other_user=self.user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.anonymous_user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.user, other_user=self.entity), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.other_user, other_user=self.entity), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.entity, other_user=self.user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.entity, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.anonymous_user, other_user=self.entity), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.entity, other_user=self.anonymous_user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.user, other_user=self.reserved_username), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.other_user, other_user=self.reserved_username), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.reserved_username, other_user=self.user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.reserved_username, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.anonymous_user, other_user=self.reserved_username), expr2=False)
                self.assertIs(expr1=both_are_users(user=self.reserved_username, other_user=self.anonymous_user), expr2=False)


