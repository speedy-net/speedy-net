from django.test import TestCase

from speedy.net.accounts.test_factories import UserFactory
from .models import EntityLike
from .test_factories import EntityLikeFactory

class LikeViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.page_url = '/{}/likes/like/'.format(self.other_user.slug)

    def test_can_like(self):
        self.client.login(username=self.user.slug, password='111')
        self.assertEqual(EntityLike.objects.count(), 0)
        r = self.client.post(self.page_url)
        self.assertRedirects(r, self.other_user.get_absolute_url())
        self.assertEqual(EntityLike.objects.count(), 1)
        like = EntityLike.objects.first()
        self.assertEqual(like.from_user.id, self.user.id)
        self.assertEqual(like.to_entity.id, self.other_user.id)


class UnlikeViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.page_url = '/{}/likes/unlike/'.format(self.other_user.slug)

    def test_can_like(self):
        self.client.login(username=self.user.slug, password='111')
        EntityLike.objects.create(from_user=self.user, to_entity=self.other_user)
        self.assertEqual(EntityLike.objects.count(), 1)
        r = self.client.post(self.page_url)
        self.assertRedirects(r, self.other_user.get_absolute_url())
        self.assertEqual(EntityLike.objects.count(), 0)


class LikeListViewsTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.default_url = '/{}/likes/'.format(self.user.slug)
        self.to_url = '/{}/likes/to/'.format(self.user.slug)
        self.from_url = '/{}/likes/from/'.format(self.user.slug)
        self.mutual_url = '/{}/likes/mutual/'.format(self.user.slug)
        self.to_likes = {
            EntityLikeFactory(from_user=self.user),
            EntityLikeFactory(from_user=self.user),
            EntityLikeFactory(from_user=self.user),
        }
        self.mutual_likes = {
            EntityLikeFactory(from_user=self.user, to_entity=self.other_user),
        }
        self.to_likes |= self.mutual_likes
        self.from_likes = {
            EntityLikeFactory(to_entity=self.user),
            EntityLikeFactory(to_entity=self.user),
            EntityLikeFactory(to_entity=self.user, from_user=self.other_user),
        }
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_has_no_access(self):
        self.client.logout()
        self.assertEqual(self.client.get(self.to_url).status_code, 302)
        self.assertEqual(self.client.get(self.from_url).status_code, 302)
        self.assertEqual(self.client.get(self.mutual_url).status_code, 302)

    def test_default_redirect(self):
        r = self.client.get(self.default_url)
        self.assertRedirects(r, self.to_url)

    def test_user_can_see_who_he_likes(self):
        r = self.client.get(self.to_url)
        self.assertEqual(r.status_code, 200)
        self.assertSetEqual(set(r.context['object_list']), self.to_likes)

    def test_user_can_see_who_likes_him(self):
        r = self.client.get(self.from_url)
        self.assertEqual(r.status_code, 200)
        self.assertSetEqual(set(r.context['object_list']), self.from_likes)

    def test_user_can_see_mutual_likes(self):
        r = self.client.get(self.mutual_url)
        self.assertEqual(r.status_code, 200)
        self.assertSetEqual(set(r.context['object_list']), self.mutual_likes)
