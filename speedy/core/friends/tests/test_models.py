from django.conf import settings as django_settings
from friendship.models import Friend

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_sites_with_login
    from speedy.core.blocks.models import Block

    from speedy.core.accounts.test.user_factories import ActiveUserFactory


    @only_on_sites_with_login
    class FriendBlocksTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user_1 = ActiveUserFactory()
            self.user_2 = ActiveUserFactory()
            Friend.objects.add_friend(from_user=self.user_1, to_user=ActiveUserFactory()).accept()
            Friend.objects.add_friend(from_user=self.user_1, to_user=ActiveUserFactory())
            Friend.objects.add_friend(from_user=ActiveUserFactory(), to_user=self.user_1)

        def assert_counters(self, user, requests, sent_requests, friends):
            self.assertEqual(first=len(Friend.objects.requests(user=user)), second=requests)
            self.assertEqual(first=len(Friend.objects.sent_requests(user=user)), second=sent_requests)
            self.assertEqual(first=len(Friend.objects.friends(user=user)), second=friends)

        def test_set_up(self):
            self.assert_counters(user=self.user_1, requests=1, sent_requests=1, friends=1)
            self.assert_counters(user=self.user_2, requests=0, sent_requests=0, friends=0)

        def test_if_no_relation_between_users_nothing_get_affected(self):
            Block.objects.block(blocker=self.user_1, blocked=self.user_2)
            self.assert_counters(user=self.user_1, requests=1, sent_requests=1, friends=1)
            self.assert_counters(user=self.user_2, requests=0, sent_requests=0, friends=0)
            Block.objects.unblock(blocker=self.user_1, blocked=self.user_2)
            self.assert_counters(user=self.user_1, requests=1, sent_requests=1, friends=1)
            self.assert_counters(user=self.user_2, requests=0, sent_requests=0, friends=0)

        def test_if_user1_blocked_user2_request_is_removed(self):
            Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_2)
            self.assert_counters(user=self.user_1, requests=1, sent_requests=2, friends=1)
            self.assert_counters(user=self.user_2, requests=1, sent_requests=0, friends=0)
            Block.objects.block(blocker=self.user_1, blocked=self.user_2)
            self.assert_counters(user=self.user_1, requests=1, sent_requests=1, friends=1)
            self.assert_counters(user=self.user_2, requests=0, sent_requests=0, friends=0)
            Block.objects.unblock(blocker=self.user_1, blocked=self.user_2)
            self.assert_counters(user=self.user_1, requests=1, sent_requests=1, friends=1)
            self.assert_counters(user=self.user_2, requests=0, sent_requests=0, friends=0)

        def test_if_user2_blocked_user1_request_is_removed(self):
            Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_2)
            self.assert_counters(user=self.user_1, requests=1, sent_requests=2, friends=1)
            self.assert_counters(user=self.user_2, requests=1, sent_requests=0, friends=0)
            Block.objects.block(blocker=self.user_2, blocked=self.user_1)
            self.assert_counters(user=self.user_1, requests=1, sent_requests=1, friends=1)
            self.assert_counters(user=self.user_2, requests=0, sent_requests=0, friends=0)
            Block.objects.unblock(blocker=self.user_2, blocked=self.user_1)
            self.assert_counters(user=self.user_1, requests=1, sent_requests=1, friends=1)
            self.assert_counters(user=self.user_2, requests=0, sent_requests=0, friends=0)

        def test_if_user1_blocked_user2_friendship_is_removed(self):
            Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_2).accept()
            self.assert_counters(user=self.user_1, requests=1, sent_requests=1, friends=2)
            self.assert_counters(user=self.user_2, requests=0, sent_requests=0, friends=1)
            Block.objects.block(blocker=self.user_1, blocked=self.user_2)
            self.assert_counters(user=self.user_1, requests=1, sent_requests=1, friends=1)
            self.assert_counters(user=self.user_2, requests=0, sent_requests=0, friends=0)
            Block.objects.unblock(blocker=self.user_1, blocked=self.user_2)
            self.assert_counters(user=self.user_1, requests=1, sent_requests=1, friends=1)
            self.assert_counters(user=self.user_2, requests=0, sent_requests=0, friends=0)

        def test_if_user2_blocked_user1_friendship_is_removed(self):
            Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_2).accept()
            self.assert_counters(user=self.user_1, requests=1, sent_requests=1, friends=2)
            self.assert_counters(user=self.user_2, requests=0, sent_requests=0, friends=1)
            Block.objects.block(blocker=self.user_2, blocked=self.user_1)
            self.assert_counters(user=self.user_1, requests=1, sent_requests=1, friends=1)
            self.assert_counters(user=self.user_2, requests=0, sent_requests=0, friends=0)
            Block.objects.unblock(blocker=self.user_2, blocked=self.user_1)
            self.assert_counters(user=self.user_1, requests=1, sent_requests=1, friends=1)
            self.assert_counters(user=self.user_2, requests=0, sent_requests=0, friends=0)


