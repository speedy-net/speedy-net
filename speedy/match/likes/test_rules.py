from django.contrib.auth.models import AnonymousUser
from speedy.core.test import TestCase

from speedy.match.likes.models import EntityLike
from speedy.net.accounts.test_factories import UserFactory
from speedy.net.blocks.models import Block


class LikeTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.anon = AnonymousUser()

    def test_anonymous_cannot_like(self):
        self.assertFalse(self.anon.has_perm('likes.like', self.other_user))

    def test_user_cannot_like_self(self):
        self.assertFalse(self.user.has_perm('likes.like', self.user))

    def test_user_can_like(self):
        self.assertTrue(self.user.has_perm('likes.like', self.other_user))

    def test_user_cannot_like_if_blocked(self):
        Block.objects.block(blocker=self.other_user, blockee=self.user)
        self.assertFalse(self.user.has_perm('likes.like', self.other_user))

    def test_user_cannot_like_twice(self):
        EntityLike.objects.create(from_user=self.user, to_entity=self.other_user)
        self.assertFalse(self.user.has_perm('likes.like', self.other_user))


class UnlikeTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.anon = AnonymousUser()

    def test_anonymous_cannot_unlike(self):
        self.assertFalse(self.anon.has_perm('likes.unlike', self.other_user))

    def test_user_cannot_unlike_self(self):
        self.assertFalse(self.user.has_perm('likes.unlike', self.user))

    def test_user_cannot_unlike_if_doesnt_like(self):
        self.assertFalse(self.user.has_perm('likes.unlike', self.other_user))

    def test_user_can_unlike_if_likes(self):
        EntityLike.objects.create(from_user=self.user, to_entity=self.other_user)
        self.assertTrue(self.user.has_perm('likes.unlike', self.other_user))


class ViewLikesTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.anon = AnonymousUser()

    def test_anonymous_cannot_view_likes(self):
        self.assertFalse(self.anon.has_perm('likes.view_likes', self.user))

    def test_other_user_cannot_view_likes(self):
        self.assertFalse(self.other_user.has_perm('likes.view_likes', self.user))

    def test_user_can_view_likes(self):
        self.assertTrue(self.user.has_perm('likes.view_likes', self.user))
