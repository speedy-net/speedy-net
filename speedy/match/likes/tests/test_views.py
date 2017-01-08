from speedy.core.test import TestCase

from speedy.net.accounts.tests.test_factories import UserFactory
from ..models import UserLike
from .test_factories import UserLikeFactory


class LikeViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.page_url = '/{}/likes/like/'.format(self.other_user.slug)

    def test_can_like(self):
        self.client.login(username=self.user.slug, password='111')
        self.assertEqual(first=UserLike.objects.count(), second=0)
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user.get_absolute_url())
        self.assertEqual(first=UserLike.objects.count(), second=1)
        like = UserLike.objects.first()
        self.assertEqual(first=like.from_user.id, second=self.user.id)
        self.assertEqual(first=like.to_user.id, second=self.other_user.id)


class UnlikeViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.page_url = '/{}/likes/unlike/'.format(self.other_user.slug)

    def test_can_like(self):
        self.client.login(username=self.user.slug, password='111')
        UserLike.objects.create(from_user=self.user, to_user=self.other_user)
        self.assertEqual(first=UserLike.objects.count(), second=1)
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user.get_absolute_url())
        self.assertEqual(first=UserLike.objects.count(), second=0)


class LikeListViewsTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.default_url = '/{}/likes/'.format(self.user.slug)
        self.to_url = '/{}/likes/to/'.format(self.user.slug)
        self.from_url = '/{}/likes/from/'.format(self.user.slug)
        self.mutual_url = '/{}/likes/mutual/'.format(self.user.slug)
        self.to_likes = {
            UserLikeFactory(from_user=self.user),
            UserLikeFactory(from_user=self.user),
            UserLikeFactory(from_user=self.user),
        }
        self.mutual_likes = {
            UserLikeFactory(from_user=self.user, to_user=self.other_user),
        }
        self.to_likes |= self.mutual_likes
        self.from_likes = {
            UserLikeFactory(to_user=self.user),
            UserLikeFactory(to_user=self.user),
            UserLikeFactory(to_user=self.user, from_user=self.other_user),
        }
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_has_no_access(self):
        self.client.logout()
        self.assertEqual(first=self.client.get(self.to_url).status_code, second=302)
        self.assertEqual(first=self.client.get(self.from_url).status_code, second=302)
        self.assertEqual(first=self.client.get(self.mutual_url).status_code, second=302)

    def test_default_redirect(self):
        r = self.client.get(self.default_url)
        self.assertRedirects(response=r, expected_url=self.to_url)

    def test_user_can_see_who_he_likes(self):
        r = self.client.get(self.to_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertSetEqual(set1=set(r.context['object_list']), set2=self.to_likes)

    def test_user_can_see_who_likes_him(self):
        r = self.client.get(self.from_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertSetEqual(set1=set(r.context['object_list']), set2=self.from_likes)

    def test_user_can_see_mutual_likes(self):
        r = self.client.get(self.mutual_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertSetEqual(set1=set(r.context['object_list']), set2=self.mutual_likes)
