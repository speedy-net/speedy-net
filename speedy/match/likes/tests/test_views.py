from time import sleep

from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test import tests_settings
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_speedy_match
    from speedy.match.likes.models import UserLike
    from speedy.core.blocks.models import Block
    from speedy.core.accounts.models import User
    from speedy.core.accounts.test.user_factories import ActiveUserFactory


    @only_on_speedy_match
    class LikeViewTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user_1 = ActiveUserFactory()
            self.user_2 = ActiveUserFactory()
            self.page_url = '/{}/likes/like/'.format(self.user_2.slug)

        def test_can_like(self):
            self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
            self.assertEqual(first=UserLike.objects.count(), second=0)
            r = self.client.post(path=self.page_url)
            self.assertRedirects(response=r, expected_url=self.user_2.get_absolute_url(), status_code=302, target_status_code=200)
            self.assertEqual(first=UserLike.objects.count(), second=1)
            like = UserLike.objects.first()
            self.assertEqual(first=like.from_user.id, second=self.user_1.id)
            self.assertEqual(first=like.to_user.id, second=self.user_2.id)


    @only_on_speedy_match
    class UnlikeViewTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user_1 = ActiveUserFactory()
            self.user_2 = ActiveUserFactory()
            self.page_url = '/{}/likes/unlike/'.format(self.user_2.slug)

        def test_can_unlike(self):
            self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
            self.assertEqual(first=UserLike.objects.count(), second=0)
            UserLike.objects.create(from_user=self.user_1, to_user=self.user_2)
            self.assertEqual(first=UserLike.objects.count(), second=1)
            r = self.client.post(path=self.page_url)
            self.assertRedirects(response=r, expected_url=self.user_2.get_absolute_url(), status_code=302, target_status_code=200)
            self.assertEqual(first=UserLike.objects.count(), second=0)


    @only_on_speedy_match
    class LikeListViewsTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user_1 = ActiveUserFactory()
            self.user_2 = ActiveUserFactory()
            self.user_3 = ActiveUserFactory()
            self.user_4 = ActiveUserFactory()
            self.user_5 = ActiveUserFactory()
            self.default_url = '/{}/likes/'.format(self.user_1.slug)
            self.to_url = '/{}/likes/people-i-like/'.format(self.user_1.slug)
            self.from_url = '/{}/likes/people-who-like-me/'.format(self.user_1.slug)
            self.mutual_url = '/{}/likes/mutual/'.format(self.user_1.slug)
            UserLike.objects.add_like(from_user=self.user_1, to_user=ActiveUserFactory(slug="user-99"))
            UserLike.objects.add_like(from_user=self.user_1, to_user=ActiveUserFactory(slug="user-98"))
            UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_3)
            UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
            UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_5)
            UserLike.objects.add_like(from_user=ActiveUserFactory(slug="user-97"), to_user=self.user_1)
            UserLike.objects.add_like(from_user=ActiveUserFactory(slug="user-96"), to_user=self.user_1)
            UserLike.objects.add_like(from_user=self.user_5, to_user=self.user_1)
            UserLike.objects.add_like(from_user=self.user_2, to_user=self.user_1)
            self.mutual_likes = {
                self.user_2,
                self.user_5,
            }
            self.to_likes = {
                User.objects.get(slug="user-99"),
                User.objects.get(slug="user-98"),
                self.user_3,
                self.user_2,
                self.user_5,
            }
            self.from_likes = {
                User.objects.get(slug="user-97"),
                User.objects.get(slug="user-96"),
                self.user_2,
                self.user_5,
            }
            self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
            sleep(0.02)
            self.user_5.profile.update_last_visit()
            sleep(0.01)
            self.user_4.profile.update_last_visit()
            sleep(0.01)
            self.user_2.profile.update_last_visit()
            sleep(0.01)
            self.user_3.profile.update_last_visit()

        def test_visitor_has_no_access(self):
            self.client.logout()
            self.assertEqual(first=self.client.get(path=self.to_url).status_code, second=302)
            self.assertEqual(first=self.client.get(path=self.from_url).status_code, second=302)
            self.assertEqual(first=self.client.get(path=self.mutual_url).status_code, second=302)

        def test_default_redirect(self):
            r = self.client.get(path=self.default_url)
            self.assertRedirects(response=r, expected_url=self.to_url, status_code=302, target_status_code=200)

        def test_user_can_see_who_they_like(self):
            r = self.client.get(path=self.to_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=5)
            self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=self.to_likes)
            self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2={self.user_1})
            to_likes = set(self.to_likes)
            UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_4)
            to_likes.add(self.user_4)
            r = self.client.get(path=self.to_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=6)
            self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=self.to_likes)
            self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=to_likes)
            self.assertEqual(first=r.context['object_list'][0].to_user, second=self.user_3)
            sleep(0.01)
            self.user_4.profile.update_last_visit()
            r = self.client.get(path=self.to_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=6)
            self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=self.to_likes)
            self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=to_likes)
            self.assertEqual(first=r.context['object_list'][0].to_user, second=self.user_4)
            Block.objects.block(blocker=self.user_4, blocked=self.user_1)
            r = self.client.get(path=self.to_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=6)
            self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=self.to_likes)
            self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=to_likes)
            Block.objects.block(blocker=self.user_1, blocked=self.user_4)
            r = self.client.get(path=self.to_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=5)
            self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=to_likes)
            self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=self.to_likes)
            Block.objects.unblock(blocker=self.user_1, blocked=self.user_4)
            r = self.client.get(path=self.to_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=5)
            self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=to_likes)
            self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=self.to_likes)

        def test_user_can_see_who_likes_them(self):
            r = self.client.get(path=self.from_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=4)
            self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2=self.from_likes)
            self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2={self.user_1})
            from_likes = set(self.from_likes)
            UserLike.objects.add_like(from_user=self.user_4, to_user=self.user_1)
            from_likes.add(self.user_4)
            r = self.client.get(path=self.from_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=5)
            self.assertNotEqual(first={like.from_user for like in r.context['object_list']}, second=self.from_likes)
            self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2=from_likes)
            self.assertEqual(first=r.context['object_list'][0].from_user, second=self.user_2)
            sleep(0.01)
            self.user_4.profile.update_last_visit()
            r = self.client.get(path=self.from_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=5)
            self.assertNotEqual(first={like.from_user for like in r.context['object_list']}, second=self.from_likes)
            self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2=from_likes)
            self.assertEqual(first=r.context['object_list'][0].from_user, second=self.user_4)
            Block.objects.block(blocker=self.user_1, blocked=self.user_4)
            r = self.client.get(path=self.from_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=4)
            self.assertNotEqual(first={like.from_user for like in r.context['object_list']}, second=from_likes)
            self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2=self.from_likes)
            Block.objects.unblock(blocker=self.user_1, blocked=self.user_4)
            r = self.client.get(path=self.from_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=5)
            self.assertNotEqual(first={like.from_user for like in r.context['object_list']}, second=self.from_likes)
            self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2=from_likes)

        def test_user_can_see_mutual_likes(self):
            r = self.client.get(path=self.mutual_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=2)
            self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=self.mutual_likes)
            self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2={self.user_1})
            mutual_likes = set(self.mutual_likes)
            UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_4)
            UserLike.objects.add_like(from_user=self.user_4, to_user=self.user_1)
            mutual_likes.add(self.user_4)
            r = self.client.get(path=self.mutual_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=3)
            self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=self.mutual_likes)
            self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=mutual_likes)
            self.assertEqual(first=r.context['object_list'][0].to_user, second=self.user_2)
            sleep(0.01)
            self.user_4.profile.update_last_visit()
            r = self.client.get(path=self.mutual_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=3)
            self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=self.mutual_likes)
            self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=mutual_likes)
            self.assertEqual(first=r.context['object_list'][0].to_user, second=self.user_4)
            Block.objects.block(blocker=self.user_4, blocked=self.user_1)
            r = self.client.get(path=self.mutual_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=2)
            self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=mutual_likes)
            self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=self.mutual_likes)
            Block.objects.unblock(blocker=self.user_4, blocked=self.user_1)
            r = self.client.get(path=self.mutual_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['object_list']), second=2)
            self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=mutual_likes)
            self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=self.mutual_likes)


