from friendship.models import Friend

from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from speedy.core.base.test import TestCase
from speedy.core.blocks.models import Block


class BlocksTestCase(TestCase):
    def setUp(self):
        self.user1 = ActiveUserFactory()
        self.user2 = ActiveUserFactory()
        Friend.objects.add_friend(from_user=self.user1, to_user=ActiveUserFactory()).accept()
        Friend.objects.add_friend(from_user=self.user1, to_user=ActiveUserFactory())
        Friend.objects.add_friend(from_user=ActiveUserFactory(), to_user=self.user1)

    def assertCounters(self, user, requests, sent_requests, friends):
        self.assertEqual(first=len(Friend.objects.requests(user=user)), second=requests)
        self.assertEqual(first=len(Friend.objects.sent_requests(user=user)), second=sent_requests)
        self.assertEqual(first=len(Friend.objects.friends(user=user)), second=friends)

    def test_setup(self):
        self.assertCounters(user=self.user1, requests=1, sent_requests=1, friends=1)

    def test_if_no_relation_between_users_nothings_get_affected(self):
        Block.objects.block(blocker=self.user1, blocked=self.user2)
        self.assertCounters(user=self.user1, requests=1, sent_requests=1, friends=1)
        self.assertCounters(user=self.user2, requests=0, sent_requests=0, friends=0)

    def test_if_user1_blocked_user2_requests_got_removed(self):
        Friend.objects.add_friend(from_user=self.user1, to_user=self.user2)
        self.assertCounters(user=self.user1, requests=1, sent_requests=2, friends=1)
        self.assertCounters(user=self.user2, requests=1, sent_requests=0, friends=0)
        Block.objects.block(blocker=self.user1, blocked=self.user2)
        self.assertCounters(user=self.user1, requests=1, sent_requests=1, friends=1)
        self.assertCounters(user=self.user2, requests=0, sent_requests=0, friends=0)

    def test_if_user1_blocked_user2_friendship_got_removed(self):
        Friend.objects.add_friend(from_user=self.user1, to_user=self.user2).accept()
        self.assertCounters(user=self.user1, requests=1, sent_requests=1, friends=2)
        self.assertCounters(user=self.user2, requests=0, sent_requests=0, friends=1)
        Block.objects.block(blocker=self.user1, blocked=self.user2)
        self.assertCounters(user=self.user1, requests=1, sent_requests=1, friends=1)
        self.assertCounters(user=self.user2, requests=0, sent_requests=0, friends=0)


