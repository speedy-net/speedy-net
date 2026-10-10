"""
Test cases for the models of the friends app of Speedy Core: friendships, friendship requests, blocks and friends counters.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from time import sleep

        from friendship.models import Friend, FriendshipRequest

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
        from speedy.core.accounts.models import User
        from speedy.core.blocks.models import Block
        from speedy.core.friends.managers import FriendManager


        @only_on_sites_with_login
        class FriendBlocksOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the interaction between blocking users and friendship requests/friendships, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates two users, one accepted friendship and one pending friendship request in each direction for user_1.
                assert_counters(self, user, received_friendship_requests, sent_friendship_requests, friends): Asserts the user's received/sent friendship request counts and friends count, via several equivalent APIs.
                test_set_up(self): Asserts the initial counters set up in set_up are as expected for both users.
                test_delete_users(self): Asserts deleting all other users resets user_1's counters to zero, and new friendships update the counters correctly afterwards.
                test_if_no_relation_between_users_nothing_get_affected(self): Asserts blocking/unblocking two users with no relation between them does not change either user's counters.
                test_if_user1_blocked_user2_request_is_removed(self): Asserts blocking removes a pending friendship request between the two users, and unblocking does not restore it.
                test_if_user2_blocked_user1_request_is_removed(self): Asserts blocking removes a pending friendship request between the two users regardless of who blocks whom, and unblocking does not restore it.
                test_if_user1_blocked_user2_friendship_is_removed(self): Asserts blocking removes an accepted friendship between the two users, and unblocking does not restore it.
                test_if_user2_blocked_user1_friendship_is_removed(self): Asserts blocking removes an accepted friendship between the two users regardless of who blocks whom, and unblocking does not restore it.
            """
            def set_up(self):
                """
                Create two users, one accepted friendship and one pending friendship request in each direction for user_1.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                Friend.objects.add_friend(from_user=self.user_1, to_user=ActiveUserFactory()).accept()
                Friend.objects.add_friend(from_user=self.user_1, to_user=ActiveUserFactory())
                Friend.objects.add_friend(from_user=ActiveUserFactory(), to_user=self.user_1)

            def assert_counters(self, user, received_friendship_requests, sent_friendship_requests, friends):
                """
                Assert the given user's received friendship requests count, sent friendship requests count and friends count, via several equivalent APIs.

                :param user: The user whose counters are being asserted.
                :type user: speedy.core.accounts.models.User
                :param received_friendship_requests: The expected number of received friendship requests.
                :type received_friendship_requests: int
                :param sent_friendship_requests: The expected number of sent friendship requests.
                :type sent_friendship_requests: int
                :param friends: The expected number of friends.
                :type friends: int
                """
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=len(Friend.objects.requests(user=user)), second=received_friendship_requests)
                self.assertEqual(first=FriendshipRequest.objects.filter(to_user=user).count(), second=received_friendship_requests)
                self.assertEqual(first=user.friendship_requests_received.count(), second=received_friendship_requests)
                self.assertEqual(first=len(Friend.objects.sent_requests(user=user)), second=sent_friendship_requests)
                self.assertEqual(first=FriendshipRequest.objects.filter(from_user=user).count(), second=sent_friendship_requests)
                self.assertEqual(first=user.friendship_requests_sent.count(), second=sent_friendship_requests)
                self.assertEqual(first=len(Friend.objects.friends(user=user)), second=friends)
                self.assertEqual(first=Friend.objects.filter(to_user=user).count(), second=friends)
                self.assertEqual(first=Friend.objects.filter(from_user=user).count(), second=friends)
                self.assertEqual(first=FriendManager.get_all_friends_count(user=user), second=friends)
                self.assertEqual(first=user.friends.count(), second=friends)
                self.assertEqual(first=user.speedy_net_profile.all_friends_count, second=friends)

            def test_set_up(self):
                """
                Asserts the initial counters set up in set_up are as expected: user_1 has one received request, one sent request and one friend; user_2 has none.
                """
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=1, friends=1)
                self.assert_counters(user=self.user_2, received_friendship_requests=0, sent_friendship_requests=0, friends=0)

            def test_delete_users(self):
                """
                Asserts deleting all users except user_1 resets user_1's counters to zero, and new friendships (in both directions) correctly update the friends counter afterwards.
                """
                for user in User.objects.all().exclude(pk=self.user_1.pk):
                    user.delete()
                self.user_2 = None
                self.assert_counters(user=self.user_1, received_friendship_requests=0, sent_friendship_requests=0, friends=0)
                Friend.objects.add_friend(from_user=self.user_1, to_user=ActiveUserFactory()).accept()
                self.assert_counters(user=self.user_1, received_friendship_requests=0, sent_friendship_requests=0, friends=1)
                Friend.objects.add_friend(from_user=ActiveUserFactory(), to_user=self.user_1).accept()
                self.assert_counters(user=self.user_1, received_friendship_requests=0, sent_friendship_requests=0, friends=2)

            def test_if_no_relation_between_users_nothing_get_affected(self):
                """
                Asserts blocking and unblocking two users who have no friendship request or friendship between them does not change either user's counters.
                """
                Block.objects.block(blocker=self.user_1, blocked=self.user_2)
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=1, friends=1)
                self.assert_counters(user=self.user_2, received_friendship_requests=0, sent_friendship_requests=0, friends=0)
                Block.objects.unblock(blocker=self.user_1, blocked=self.user_2)
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=1, friends=1)
                self.assert_counters(user=self.user_2, received_friendship_requests=0, sent_friendship_requests=0, friends=0)

            def test_if_user1_blocked_user2_request_is_removed(self):
                """
                Asserts that after user_1 sends a friendship request to user_2, blocking user_2 removes that pending request, and unblocking does not restore it.
                """
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_2)
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=2, friends=1)
                self.assert_counters(user=self.user_2, received_friendship_requests=1, sent_friendship_requests=0, friends=0)
                Block.objects.block(blocker=self.user_1, blocked=self.user_2)
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=1, friends=1)
                self.assert_counters(user=self.user_2, received_friendship_requests=0, sent_friendship_requests=0, friends=0)
                Block.objects.unblock(blocker=self.user_1, blocked=self.user_2)
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=1, friends=1)
                self.assert_counters(user=self.user_2, received_friendship_requests=0, sent_friendship_requests=0, friends=0)

            def test_if_user2_blocked_user1_request_is_removed(self):
                """
                Asserts that after user_1 sends a friendship request to user_2, blocking user_1 (by user_2) removes that pending request, and unblocking does not restore it.
                """
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_2)
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=2, friends=1)
                self.assert_counters(user=self.user_2, received_friendship_requests=1, sent_friendship_requests=0, friends=0)
                Block.objects.block(blocker=self.user_2, blocked=self.user_1)
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=1, friends=1)
                self.assert_counters(user=self.user_2, received_friendship_requests=0, sent_friendship_requests=0, friends=0)
                Block.objects.unblock(blocker=self.user_2, blocked=self.user_1)
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=1, friends=1)
                self.assert_counters(user=self.user_2, received_friendship_requests=0, sent_friendship_requests=0, friends=0)

            def test_if_user1_blocked_user2_friendship_is_removed(self):
                """
                Asserts that after user_1 and user_2 become friends, blocking user_2 removes that friendship, and unblocking does not restore it.
                """
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_2).accept()
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=1, friends=2)
                self.assert_counters(user=self.user_2, received_friendship_requests=0, sent_friendship_requests=0, friends=1)
                Block.objects.block(blocker=self.user_1, blocked=self.user_2)
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=1, friends=1)
                self.assert_counters(user=self.user_2, received_friendship_requests=0, sent_friendship_requests=0, friends=0)
                Block.objects.unblock(blocker=self.user_1, blocked=self.user_2)
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=1, friends=1)
                self.assert_counters(user=self.user_2, received_friendship_requests=0, sent_friendship_requests=0, friends=0)

            def test_if_user2_blocked_user1_friendship_is_removed(self):
                """
                Asserts that after user_1 and user_2 become friends, blocking user_1 (by user_2) removes that friendship, and unblocking does not restore it.
                """
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_2).accept()
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=1, friends=2)
                self.assert_counters(user=self.user_2, received_friendship_requests=0, sent_friendship_requests=0, friends=1)
                Block.objects.block(blocker=self.user_2, blocked=self.user_1)
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=1, friends=1)
                self.assert_counters(user=self.user_2, received_friendship_requests=0, sent_friendship_requests=0, friends=0)
                Block.objects.unblock(blocker=self.user_2, blocked=self.user_1)
                self.assert_counters(user=self.user_1, received_friendship_requests=1, sent_friendship_requests=1, friends=1)
                self.assert_counters(user=self.user_2, received_friendship_requests=0, sent_friendship_requests=0, friends=0)


        @only_on_sites_with_login
        class FriendListsOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the ordering of site_friends, speedy_net_friends, received_friendship_requests and sent_friendship_requests, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates six users with varying attributes and last-visit times.
                test_site_friends_list(self): Asserts site_friends and speedy_net_friends are ordered by last visit and filtered according to the current site.
                test_site_received_friendship_requests_list(self): Asserts received_friendship_requests is ordered by last visit and filtered according to the current site.
                test_site_sent_friendship_requests_list(self): Asserts sent_friendship_requests is ordered by last visit and filtered according to the current site.
            """
            def set_up(self):
                """
                Create six users with varying attributes (relationship status, diet match, relationship status match) and staggered last-visit times.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.user_3 = ActiveUserFactory()
                self.user_4 = ActiveUserFactory()
                self.user_5 = ActiveUserFactory()
                self.user_6 = ActiveUserFactory()
                self.user_1.relationship_status = User.RELATIONSHIP_STATUS_MARRIED
                self.user_2.speedy_match_profile.diet_match = {str(User.DIET_VEGAN): 5, str(User.DIET_VEGETARIAN): 4, str(User.DIET_CARNIST): 2}
                self.user_5.speedy_match_profile.relationship_status_match[str(User.RELATIONSHIP_STATUS_MARRIED)] = SpeedyMatchSiteProfile.RANK_0
                self.user_1.save_user_and_profile()
                self.user_2.save_user_and_profile()
                self.user_5.save_user_and_profile()
                sleep(0.02)
                self.user_6.profile.update_last_visit()
                sleep(0.01)
                self.user_4.profile.update_last_visit()
                sleep(0.01)
                self.user_3.profile.update_last_visit()
                sleep(0.01)
                self.user_2.profile.update_last_visit()

            def test_site_friends_list(self):
                """
                Asserts site_friends and speedy_net_friends only include friendships where the user is the "to user", are ordered by the friend's last visit (most recent first), and on Speedy Match site_friends only includes friends who match (excludes blocked relationship status matches), while speedy_net_friends always includes all Speedy Net friends.
                """
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_5).accept()
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_4).accept()
                Friend.objects.add_friend(from_user=self.user_3, to_user=self.user_1).accept()
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_2)
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assertIs(expr1=all([(friendship.to_user == self.user_1) for friendship in self.user_1.site_friends]), expr2=True)
                users_list = [friendship.from_user for friendship in self.user_1.site_friends]
                self.assertEqual(first=len(users_list), second=len(self.user_1.site_friends))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 3, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
                self.assertListEqual(list1=users_list, list2={django_settings.SPEEDY_NET_SITE_ID: [self.user_3, self.user_4, self.user_5], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_3, self.user_4]}[self.site.id])
                self.assertIs(expr1=all([(friendship.to_user == self.user_1) for friendship in self.user_1.speedy_net_friends]), expr2=True)
                users_list = [friendship.from_user for friendship in self.user_1.speedy_net_friends]
                self.assertEqual(first=len(users_list), second=len(self.user_1.speedy_net_friends))
                self.assertEqual(first=len(users_list), second=3)
                self.assertListEqual(list1=users_list, list2=[self.user_3, self.user_4, self.user_5])
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=self.user_1.site_friends, second=self.user_1.speedy_net_friends)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertNotEqual(first=self.user_1.site_friends, second=self.user_1.speedy_net_friends)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                sleep(0.01)
                self.user_5.profile.update_last_visit()
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assertIs(expr1=all([(friendship.to_user == self.user_1) for friendship in self.user_1.site_friends]), expr2=True)
                users_list = [friendship.from_user for friendship in self.user_1.site_friends]
                self.assertEqual(first=len(users_list), second=len(self.user_1.site_friends))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 3, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
                self.assertListEqual(list1=users_list, list2={django_settings.SPEEDY_NET_SITE_ID: [self.user_5, self.user_3, self.user_4], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_3, self.user_4]}[self.site.id])
                self.assertIs(expr1=all([(friendship.to_user == self.user_1) for friendship in self.user_1.speedy_net_friends]), expr2=True)
                users_list = [friendship.from_user for friendship in self.user_1.speedy_net_friends]
                self.assertEqual(first=len(users_list), second=len(self.user_1.speedy_net_friends))
                self.assertEqual(first=len(users_list), second=3)
                self.assertListEqual(list1=users_list, list2=[self.user_5, self.user_3, self.user_4])
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=self.user_1.site_friends, second=self.user_1.speedy_net_friends)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertNotEqual(first=self.user_1.site_friends, second=self.user_1.speedy_net_friends)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")

            def test_site_received_friendship_requests_list(self):
                """
                Asserts received_friendship_requests only includes requests where the user is the "to user", is ordered by the sender's last visit (most recent first), and on Speedy Match only includes senders who match the user.
                """
                Friend.objects.add_friend(from_user=self.user_5, to_user=self.user_1)
                Friend.objects.add_friend(from_user=self.user_4, to_user=self.user_1).accept()
                Friend.objects.add_friend(from_user=self.user_3, to_user=self.user_1)
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_2)
                Friend.objects.add_friend(from_user=self.user_6, to_user=self.user_1)
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assertIs(expr1=all([(friendship_request.to_user == self.user_1) for friendship_request in self.user_1.received_friendship_requests]), expr2=True)
                users_list = [friendship_request.from_user for friendship_request in self.user_1.received_friendship_requests]
                self.assertEqual(first=len(users_list), second=len(self.user_1.received_friendship_requests))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 3, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
                self.assertListEqual(list1=users_list, list2={django_settings.SPEEDY_NET_SITE_ID: [self.user_3, self.user_6, self.user_5], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_3, self.user_6]}[self.site.id])
                sleep(0.01)
                self.user_5.profile.update_last_visit()
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assertIs(expr1=all([(friendship_request.to_user == self.user_1) for friendship_request in self.user_1.received_friendship_requests]), expr2=True)
                users_list = [friendship_request.from_user for friendship_request in self.user_1.received_friendship_requests]
                self.assertEqual(first=len(users_list), second=len(self.user_1.received_friendship_requests))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 3, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
                self.assertListEqual(list1=users_list, list2={django_settings.SPEEDY_NET_SITE_ID: [self.user_5, self.user_3, self.user_6], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_3, self.user_6]}[self.site.id])

            def test_site_sent_friendship_requests_list(self):
                """
                Asserts sent_friendship_requests only includes requests where the user is the "from user", is ordered by the recipient's last visit (most recent first), and on Speedy Match only includes recipients who match the user.
                """
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_5)
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_4).accept()
                Friend.objects.add_friend(from_user=self.user_3, to_user=self.user_1)
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_2)
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_6)
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assertIs(expr1=all([(friendship_request.from_user == self.user_1) for friendship_request in self.user_1.sent_friendship_requests]), expr2=True)
                users_list = [friendship_request.to_user for friendship_request in self.user_1.sent_friendship_requests]
                self.assertEqual(first=len(users_list), second=len(self.user_1.sent_friendship_requests))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 3, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
                self.assertListEqual(list1=users_list, list2={django_settings.SPEEDY_NET_SITE_ID: [self.user_2, self.user_6, self.user_5], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_2, self.user_6]}[self.site.id])
                sleep(0.01)
                self.user_5.profile.update_last_visit()
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assertIs(expr1=all([(friendship_request.from_user == self.user_1) for friendship_request in self.user_1.sent_friendship_requests]), expr2=True)
                users_list = [friendship_request.to_user for friendship_request in self.user_1.sent_friendship_requests]
                self.assertEqual(first=len(users_list), second=len(self.user_1.sent_friendship_requests))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 3, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
                self.assertListEqual(list1=users_list, list2={django_settings.SPEEDY_NET_SITE_ID: [self.user_5, self.user_2, self.user_6], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_2, self.user_6]}[self.site.id])


