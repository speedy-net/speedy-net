from django.conf import settings as django_settings
from speedy.match.likes.models import UserLike

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_speedy_match
    from speedy.core.blocks.models import Block

    from speedy.core.accounts.test.user_factories import ActiveUserFactory


    @only_on_speedy_match
    class LikeBlocksTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user1 = ActiveUserFactory()
            self.user2 = ActiveUserFactory()
            UserLike.objects.add_like(from_user=self.user1, to_user=ActiveUserFactory())
            UserLike.objects.add_like(from_user=self.user1, to_user=ActiveUserFactory())
            UserLike.objects.add_like(from_user=self.user2, to_user=ActiveUserFactory())
            UserLike.objects.add_like(from_user=ActiveUserFactory(), to_user=self.user1)
            UserLike.objects.add_like(from_user=ActiveUserFactory(), to_user=self.user2)
            UserLike.objects.add_like(from_user=ActiveUserFactory(), to_user=self.user2)

        def assert_counters(self, user, from_user_likes, to_user_likes):
            self.assertEqual(first=len(UserLike.objects.filter(from_user=user)), second=from_user_likes)
            self.assertEqual(first=len(UserLike.objects.filter(to_user=user)), second=to_user_likes)

        def test_set_up(self):
            self.assert_counters(user=self.user1, from_user_likes=2, to_user_likes=1)
            self.assert_counters(user=self.user2, from_user_likes=1, to_user_likes=2)

        def test_if_no_relation_between_users_nothing_get_affected(self):
            Block.objects.block(blocker=self.user1, blocked=self.user2)
            self.assert_counters(user=self.user1, from_user_likes=2, to_user_likes=1)
            self.assert_counters(user=self.user2, from_user_likes=1, to_user_likes=2)
            Block.objects.unblock(blocker=self.user1, blocked=self.user2)
            self.assert_counters(user=self.user1, from_user_likes=2, to_user_likes=1)
            self.assert_counters(user=self.user2, from_user_likes=1, to_user_likes=2)

        def test_if_user1_blocked_user2_like_is_removed(self):
            UserLike.objects.add_like(from_user=self.user1, to_user=self.user2)
            self.assert_counters(user=self.user1, from_user_likes=3, to_user_likes=1)
            self.assert_counters(user=self.user2, from_user_likes=1, to_user_likes=3)
            Block.objects.block(blocker=self.user1, blocked=self.user2)
            self.assert_counters(user=self.user1, from_user_likes=2, to_user_likes=1)
            self.assert_counters(user=self.user2, from_user_likes=1, to_user_likes=2)
            Block.objects.unblock(blocker=self.user1, blocked=self.user2)
            self.assert_counters(user=self.user1, from_user_likes=2, to_user_likes=1)
            self.assert_counters(user=self.user2, from_user_likes=1, to_user_likes=2)

        def test_if_user2_blocked_user1_like_isnt_removed(self):
            UserLike.objects.add_like(from_user=self.user1, to_user=self.user2)
            self.assert_counters(user=self.user1, from_user_likes=3, to_user_likes=1)
            self.assert_counters(user=self.user2, from_user_likes=1, to_user_likes=3)
            Block.objects.block(blocker=self.user2, blocked=self.user1)
            self.assert_counters(user=self.user1, from_user_likes=3, to_user_likes=1)
            self.assert_counters(user=self.user2, from_user_likes=1, to_user_likes=3)
            Block.objects.unblock(blocker=self.user2, blocked=self.user1)
            self.assert_counters(user=self.user1, from_user_likes=3, to_user_likes=1)
            self.assert_counters(user=self.user2, from_user_likes=1, to_user_likes=3)


