from time import sleep

from django.conf import settings as django_settings
from friendship.models import Friend

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
        from speedy.core.accounts.models import User
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
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=len(Friend.objects.requests(user=user)), second=requests)
                self.assertEqual(first=len(Friend.objects.sent_requests(user=user)), second=sent_requests)
                self.assertEqual(first=len(Friend.objects.friends(user=user)), second=friends)
                self.assertEqual(first=user.speedy_net_profile.friends_count, second=friends)

            def test_set_up(self):
                self.assert_counters(user=self.user_1, requests=1, sent_requests=1, friends=1)
                self.assert_counters(user=self.user_2, requests=0, sent_requests=0, friends=0)

            def test_delete_users(self):
                for user in User.objects.all().exclude(pk=self.user_1.pk):
                    user.delete()
                self.user_2 = None
                self.assert_counters(user=self.user_1, requests=0, sent_requests=0, friends=0)
                Friend.objects.add_friend(from_user=self.user_1, to_user=ActiveUserFactory()).accept()
                self.assert_counters(user=self.user_1, requests=0, sent_requests=0, friends=1)
                Friend.objects.add_friend(from_user=ActiveUserFactory(), to_user=self.user_1).accept()
                self.assert_counters(user=self.user_1, requests=0, sent_requests=0, friends=2)

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


        @only_on_sites_with_login
        class FriendListsTestCase(SiteTestCase):
            def set_up(self):
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

            def test_site_all_friends_list(self):
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_5).accept()
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_4).accept()
                Friend.objects.add_friend(from_user=self.user_3, to_user=self.user_1).accept()
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_2)
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assertTrue(expr=all([(friendship.to_user == self.user_1) for friendship in self.user_1.all_friends]))
                users_list = [friendship.from_user for friendship in self.user_1.all_friends]
                self.assertEqual(first=len(users_list), second=len(self.user_1.all_friends))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 3, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
                self.assertEqual(first=users_list, second={django_settings.SPEEDY_NET_SITE_ID: [self.user_3, self.user_4, self.user_5], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_3, self.user_4]}[self.site.id])
                self.assertTrue(expr=all([(friendship.to_user == self.user_1) for friendship in self.user_1.all_speedy_net_friends]))
                users_list = [friendship.from_user for friendship in self.user_1.all_speedy_net_friends]
                self.assertEqual(first=len(users_list), second=len(self.user_1.all_speedy_net_friends))
                self.assertEqual(first=len(users_list), second=3)
                self.assertEqual(first=users_list, second=[self.user_3, self.user_4, self.user_5])
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=self.user_1.all_friends, second=self.user_1.all_speedy_net_friends)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertNotEqual(first=self.user_1.all_friends, second=self.user_1.all_speedy_net_friends)
                else:
                    raise NotImplementedError()
                sleep(0.01)
                self.user_5.profile.update_last_visit()
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assertTrue(expr=all([(friendship.to_user == self.user_1) for friendship in self.user_1.all_friends]))
                users_list = [friendship.from_user for friendship in self.user_1.all_friends]
                self.assertEqual(first=len(users_list), second=len(self.user_1.all_friends))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 3, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
                self.assertEqual(first=users_list, second={django_settings.SPEEDY_NET_SITE_ID: [self.user_5, self.user_3, self.user_4], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_3, self.user_4]}[self.site.id])
                self.assertTrue(expr=all([(friendship.to_user == self.user_1) for friendship in self.user_1.all_speedy_net_friends]))
                users_list = [friendship.from_user for friendship in self.user_1.all_speedy_net_friends]
                self.assertEqual(first=len(users_list), second=len(self.user_1.all_speedy_net_friends))
                self.assertEqual(first=len(users_list), second=3)
                self.assertEqual(first=users_list, second=[self.user_5, self.user_3, self.user_4])
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=self.user_1.all_friends, second=self.user_1.all_speedy_net_friends)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertNotEqual(first=self.user_1.all_friends, second=self.user_1.all_speedy_net_friends)
                else:
                    raise NotImplementedError()

            def test_site_received_friendship_requests_list(self):
                Friend.objects.add_friend(from_user=self.user_5, to_user=self.user_1)
                Friend.objects.add_friend(from_user=self.user_4, to_user=self.user_1).accept()
                Friend.objects.add_friend(from_user=self.user_3, to_user=self.user_1)
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_2)
                Friend.objects.add_friend(from_user=self.user_6, to_user=self.user_1)
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assertTrue(expr=all([(friendship_request.to_user == self.user_1) for friendship_request in self.user_1.received_friendship_requests]))
                users_list = [friendship_request.from_user for friendship_request in self.user_1.received_friendship_requests]
                self.assertEqual(first=len(users_list), second=len(self.user_1.received_friendship_requests))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 3, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
                self.assertEqual(first=users_list, second={django_settings.SPEEDY_NET_SITE_ID: [self.user_3, self.user_6, self.user_5], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_3, self.user_6]}[self.site.id])
                sleep(0.01)
                self.user_5.profile.update_last_visit()
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assertTrue(expr=all([(friendship_request.to_user == self.user_1) for friendship_request in self.user_1.received_friendship_requests]))
                users_list = [friendship_request.from_user for friendship_request in self.user_1.received_friendship_requests]
                self.assertEqual(first=len(users_list), second=len(self.user_1.received_friendship_requests))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 3, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
                self.assertEqual(first=users_list, second={django_settings.SPEEDY_NET_SITE_ID: [self.user_5, self.user_3, self.user_6], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_3, self.user_6]}[self.site.id])

            def test_site_sent_friendship_requests_list(self):
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_5)
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_4).accept()
                Friend.objects.add_friend(from_user=self.user_3, to_user=self.user_1)
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_2)
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_6)
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assertTrue(expr=all([(friendship_request.from_user == self.user_1) for friendship_request in self.user_1.sent_friendship_requests]))
                users_list = [friendship_request.to_user for friendship_request in self.user_1.sent_friendship_requests]
                self.assertEqual(first=len(users_list), second=len(self.user_1.sent_friendship_requests))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 3, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
                self.assertEqual(first=users_list, second={django_settings.SPEEDY_NET_SITE_ID: [self.user_2, self.user_6, self.user_5], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_2, self.user_6]}[self.site.id])
                sleep(0.01)
                self.user_5.profile.update_last_visit()
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assertTrue(expr=all([(friendship_request.from_user == self.user_1) for friendship_request in self.user_1.sent_friendship_requests]))
                users_list = [friendship_request.to_user for friendship_request in self.user_1.sent_friendship_requests]
                self.assertEqual(first=len(users_list), second=len(self.user_1.sent_friendship_requests))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 3, django_settings.SPEEDY_MATCH_SITE_ID: 2}[self.site.id])
                self.assertEqual(first=users_list, second={django_settings.SPEEDY_NET_SITE_ID: [self.user_5, self.user_2, self.user_6], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_2, self.user_6]}[self.site.id])


