from django.contrib.auth.models import AnonymousUser

from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from speedy.core.base.test import TestCase, only_on_speedy_match
from speedy.core.blocks.models import Block
from speedy.match.likes.models import UserLike


@only_on_speedy_match
class LikeTestCase(TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.anon = AnonymousUser()

    def test_anonymous_cannot_like(self):
        self.assertFalse(expr=self.anon.has_perm(perm='likes.like', obj=self.other_user))

    def test_user_cannot_like_self(self):
        self.assertFalse(expr=self.user.has_perm(perm='likes.like', obj=self.user))

    def test_user_can_like(self):
        self.assertTrue(expr=self.user.has_perm(perm='likes.like', obj=self.other_user))

    def test_user_cannot_like_if_blocked(self):
        Block.objects.block(blocker=self.other_user, blocked=self.user)
        self.assertFalse(expr=self.user.has_perm(perm='likes.like', obj=self.other_user))

    def test_user_cannot_like_twice(self):
        UserLike.objects.create(from_user=self.user, to_user=self.other_user)
        self.assertFalse(expr=self.user.has_perm(perm='likes.like', obj=self.other_user))


@only_on_speedy_match
class UnlikeTestCase(TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.anon = AnonymousUser()

    def test_anonymous_cannot_unlike(self):
        self.assertFalse(expr=self.anon.has_perm(perm='likes.unlike', obj=self.other_user))

    def test_user_cannot_unlike_self(self):
        self.assertFalse(expr=self.user.has_perm(perm='likes.unlike', obj=self.user))

    def test_user_cannot_unlike_if_doesnt_like(self):
        self.assertFalse(expr=self.user.has_perm(perm='likes.unlike', obj=self.other_user))

    def test_user_can_unlike_if_likes(self):
        UserLike.objects.create(from_user=self.user, to_user=self.other_user)
        self.assertTrue(expr=self.user.has_perm(perm='likes.unlike', obj=self.other_user))


@only_on_speedy_match
class ViewLikesTestCase(TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.anon = AnonymousUser()

    def test_anonymous_cannot_view_likes(self):
        self.assertFalse(expr=self.anon.has_perm(perm='likes.view_likes', obj=self.user))

    def test_other_user_cannot_view_likes(self):
        self.assertFalse(expr=self.other_user.has_perm(perm='likes.view_likes', obj=self.user))

    def test_user_can_view_likes(self):
        self.assertTrue(expr=self.user.has_perm(perm='likes.view_likes', obj=self.user))


