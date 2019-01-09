from django.conf import settings as django_settings
from django.test import override_settings
from friendship.models import Friend, FriendshipRequest

from speedy.core.settings import tests as tests_settings
from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_sites_with_login, exclude_on_speedy_match
from speedy.core.base.test.utils import get_django_settings_class_with_override_settings
from speedy.core.accounts.models import User

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.tests.test_factories import USER_PASSWORD, ActiveUserFactory


@only_on_sites_with_login
class UserFriendListViewTestCase(SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.user_friends_list_url = '/{}/friends/'.format(self.user.slug)
        self.other_user_friends_list_url = '/{}/friends/'.format(self.other_user.slug)

    @exclude_on_speedy_match
    def test_visitor_can_open_the_page(self):
        self.client.logout()
        r = self.client.get(path=self.user_friends_list_url)
        self.assertEqual(first=r.status_code, second=200)

    def test_user_can_open_his_friends_page(self):
        r = self.client.get(path=self.user_friends_list_url)
        self.assertEqual(first=r.status_code, second=200)

    def test_user_can_open_other_users_friends_page(self):
        r = self.client.get(path=self.other_user_friends_list_url)
        self.assertEqual(first=r.status_code, second=200)


@only_on_sites_with_login
class ReceivedFriendshipRequestsListView(SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.page_url = '/{}/friends/received-requests/'.format(self.user.slug)
        self.other_page_url = '/{}/friends/received-requests/'.format(self.other_user.slug)

    @exclude_on_speedy_match
    def test_visitor_cannot_open_the_page(self):
        self.client.logout()
        r = self.client.get(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_can_open_the_page(self):
        r = self.client.get(path=self.page_url)
        self.assertEqual(first=r.status_code, second=200)

    def test_user_cannot_open_other_users_requests_page(self):
        r = self.client.get(path=self.other_page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.other_page_url))


@only_on_sites_with_login
class SentFriendshipRequestsListView(SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.page_url = '/{}/friends/sent-requests/'.format(self.user.slug)
        self.other_page_url = '/{}/friends/sent-requests/'.format(self.other_user.slug)

    @exclude_on_speedy_match
    def test_visitor_cannot_open_the_page(self):
        self.client.logout()
        r = self.client.get(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_can_open_the_page(self):
        r = self.client.get(path=self.page_url)
        self.assertEqual(first=r.status_code, second=200)

    def test_user_cannot_open_other_users_requests_page(self):
        r = self.client.get(path=self.other_page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.other_page_url))


@only_on_sites_with_login
class UserFriendRequestViewTestCase(SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.page_url = '/{}/friends/request/'.format(self.other_user.slug)
        self.same_user_page_url = '/{}/friends/request/'.format(self.user.slug)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)

    def test_visitor_cannot_send_friend_request(self):
        self.client.logout()
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))
        self.assertIsNone(obj=r.context)

    def test_user_can_send_friend_request(self):
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user.get_absolute_url())
        self.assertEqual(first=self.other_user.friendship_requests_received.count(), second=1)
        self.assertEqual(first=self.user.friendship_requests_sent.count(), second=1)
        friendship_request = self.other_user.friendship_requests_received.first()
        self.assertEqual(first=friendship_request.from_user, second=self.user)
        self.assertEqual(first=friendship_request.to_user, second=self.other_user)
        self.assertIsNone(obj=r.context)
        r = self.client.get(path=self.other_user.get_absolute_url())
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=['Friend request sent.']) ###### TODO

    def test_user_cannot_send_friend_request_twice(self):
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user.get_absolute_url())
        self.assertEqual(first=self.other_user.friendship_requests_received.count(), second=1)
        self.assertEqual(first=self.user.friendship_requests_sent.count(), second=1)
        self.assertIsNone(obj=r.context)
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user.get_absolute_url())
        self.assertEqual(first=self.other_user.friendship_requests_received.count(), second=1)
        self.assertEqual(first=self.user.friendship_requests_sent.count(), second=1)
        self.assertIsNone(obj=r.context)
        r = self.client.get(path=self.other_user.get_absolute_url())
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=["Friendship already requested."]) ###### TODO
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=["Friendship already requested"])#### # ~~~~ TODO: remove this line!

    def test_user_cannot_send_friend_request_to_a_friend(self):
        self.assertFalse(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
        Friend.objects.add_friend(from_user=self.user, to_user=self.other_user).accept()
        self.assertTrue(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user.get_absolute_url())
        self.assertEqual(first=self.user.friendship_requests_received.count(), second=0)
        self.assertEqual(first=self.user.friendship_requests_sent.count(), second=0)
        self.assertIsNone(obj=r.context)
        r = self.client.get(path=self.user.get_absolute_url())
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=["Users are already friends."]) ###### TODO
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=["Users are already friends"])#### # ~~~~ TODO: remove this line!

    def test_user_cannot_send_friend_request_to_himself(self):
        r = self.client.post(path=self.same_user_page_url)
        self.assertRedirects(response=r, expected_url=self.user.get_absolute_url())
        self.assertEqual(first=self.user.friendship_requests_received.count(), second=0)
        self.assertEqual(first=self.user.friendship_requests_sent.count(), second=0)
        self.assertIsNone(obj=r.context)
        r = self.client.get(path=self.user.get_absolute_url())
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=["Users cannot be friends with themselves."]) ###### TODO
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=["Users cannot be friends with themselves"])#### # ~~~~ TODO: remove this line!

    @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MAX_NUMBER_OF_FRIENDS_ALLOWED=tests_settings.OVERRIDE_USER_SETTINGS.MAX_NUMBER_OF_FRIENDS_ALLOWED))
    def test_user_can_send_friend_request_if_not_maximum(self):
        self.assertEqual(first=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED, second=4)
        for i in range(User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED - 1):
            Friend.objects.add_friend(from_user=self.user, to_user=ActiveUserFactory()).accept()
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user.get_absolute_url())
        self.assertEqual(first=self.other_user.friendship_requests_received.count(), second=1)
        self.assertEqual(first=self.user.friendship_requests_sent.count(), second=1)
        friendship_request = self.other_user.friendship_requests_received.first()
        self.assertEqual(first=friendship_request.from_user, second=self.user)
        self.assertEqual(first=friendship_request.to_user, second=self.other_user)
        self.assertIsNone(obj=r.context)
        r = self.client.get(path=self.other_user.get_absolute_url())
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=['Friend request sent.']) ###### TODO

    @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MAX_NUMBER_OF_FRIENDS_ALLOWED=tests_settings.OVERRIDE_USER_SETTINGS.MAX_NUMBER_OF_FRIENDS_ALLOWED))
    def test_user_cannot_send_friend_request_if_maximum(self):
        self.assertEqual(first=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED, second=4)
        for i in range(User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED):
            Friend.objects.add_friend(from_user=self.user, to_user=ActiveUserFactory()).accept()
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user.get_absolute_url(), fetch_redirect_response=False)
        self.assertEqual(first=self.other_user.friendship_requests_received.count(), second=0)
        self.assertEqual(first=self.user.friendship_requests_sent.count(), second=0)
        self.assertIsNone(obj=r.context)
        r = self.client.get(path=self.other_user.get_absolute_url())
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=["You already have 4 friends. You can't have more than 4 friends on Speedy Net. Please remove friends before you proceed."]) ###### TODO


@only_on_sites_with_login
class CancelFriendRequestViewTestCase(SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.page_url = '/{}/friends/request/cancel/'.format(self.other_user.slug)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)

    def test_visitor_cannot_cancel_friend_request(self):
        self.client.logout()
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))
        self.assertIsNone(obj=r.context)

    def test_user_can_cancel_friend_request(self):
        Friend.objects.add_friend(from_user=self.user, to_user=self.other_user)
        self.assertEqual(first=FriendshipRequest.objects.count(), second=1)
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user.get_absolute_url(), fetch_redirect_response=False)
        r = self.client.get(path=self.other_user.get_absolute_url())
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=["You've cancelled your friend request."]) ###### TODO


@only_on_sites_with_login
class AcceptFriendRequestViewTestCase(SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        friendship_request = Friend.objects.add_friend(from_user=self.user, to_user=self.other_user)
        self.page_url = '/{}/friends/request/accept/{}/'.format(self.other_user.slug, friendship_request.pk)
        self.other_user_friends_list_url = '/{}/friends/'.format(self.other_user.slug)

    def test_visitor_cannot_accept_friend_request(self):
        self.client.logout()
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))
        self.assertIsNone(obj=r.context)

    def test_user_cannot_accept_friend_request_he_sent_another_user(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))
        self.assertIsNone(obj=r.context)

    def test_user_that_has_received_request_can_accept_it(self):
        self.client.login(username=self.other_user.slug, password=USER_PASSWORD)
        self.assertFalse(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user_friends_list_url)
        self.assertTrue(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
        self.assertIsNone(obj=r.context)
        r = self.client.get(path=self.other_user_friends_list_url)
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=['Friend request accepted.']) ###### TODO

    @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MAX_NUMBER_OF_FRIENDS_ALLOWED=tests_settings.OVERRIDE_USER_SETTINGS.MAX_NUMBER_OF_FRIENDS_ALLOWED))
    def test_user_that_has_received_request_can_accept_it_if_not_maximum(self):
        self.assertEqual(first=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED, second=4)
        for i in range(User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED - 1):
            Friend.objects.add_friend(from_user=self.other_user, to_user=ActiveUserFactory()).accept()
        self.client.login(username=self.other_user.slug, password=USER_PASSWORD)
        self.assertFalse(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user_friends_list_url)
        self.assertTrue(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
        self.assertIsNone(obj=r.context)
        r = self.client.get(path=self.other_user_friends_list_url)
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=['Friend request accepted.']) ###### TODO

    @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MAX_NUMBER_OF_FRIENDS_ALLOWED=tests_settings.OVERRIDE_USER_SETTINGS.MAX_NUMBER_OF_FRIENDS_ALLOWED))
    def test_user_that_has_received_request_cannot_accept_it_if_maximum(self):
        self.assertEqual(first=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED, second=4)
        for i in range(User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED):
            Friend.objects.add_friend(from_user=self.other_user, to_user=ActiveUserFactory()).accept()
        self.client.login(username=self.other_user.slug, password=USER_PASSWORD)
        self.assertFalse(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user_friends_list_url, fetch_redirect_response=False)
        self.assertFalse(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
        r = self.client.get(path=self.other_user_friends_list_url)
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=["You already have 4 friends. You can't have more than 4 friends on Speedy Net. Please remove friends before you proceed."]) ###### TODO
        self.assertFalse(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))

    @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MAX_NUMBER_OF_FRIENDS_ALLOWED=tests_settings.OVERRIDE_USER_SETTINGS.MAX_NUMBER_OF_FRIENDS_ALLOWED))
    def test_user_that_has_received_request_can_accept_it_if_other_not_maximum(self):
        self.assertEqual(first=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED, second=4)
        for i in range(User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED - 1):
            Friend.objects.add_friend(from_user=self.user, to_user=ActiveUserFactory()).accept()
        self.client.login(username=self.other_user.slug, password=USER_PASSWORD)
        self.assertFalse(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user_friends_list_url)
        self.assertTrue(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
        self.assertIsNone(obj=r.context)
        r = self.client.get(path=self.other_user_friends_list_url)
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=['Friend request accepted.']) ###### TODO

    @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MAX_NUMBER_OF_FRIENDS_ALLOWED=tests_settings.OVERRIDE_USER_SETTINGS.MAX_NUMBER_OF_FRIENDS_ALLOWED))
    def test_user_that_has_received_request_cannot_accept_it_if_other_maximum(self):
        self.assertEqual(first=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED, second=4)
        for i in range(User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED):
            Friend.objects.add_friend(from_user=self.user, to_user=ActiveUserFactory()).accept()
        self.client.login(username=self.other_user.slug, password=USER_PASSWORD)
        self.assertFalse(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user_friends_list_url, fetch_redirect_response=False)
        self.assertFalse(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
        r = self.client.get(path=self.other_user_friends_list_url)
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=["This user already has 4 friends. They can't have more than 4 friends on Speedy Net. Please ask them to remove friends before you proceed."]) ###### TODO
        self.assertFalse(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))


@only_on_sites_with_login
class RejectFriendRequestViewTestCase(SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        friendship_request = Friend.objects.add_friend(from_user=self.user, to_user=self.other_user)
        self.page_url = '/{}/friends/request/reject/{}/'.format(self.other_user.slug, friendship_request.pk)
        self.other_user_friends_list_url = '/{}/friends/'.format(self.other_user.slug)

    def test_visitor_cannot_reject_friend_request(self):
        self.client.logout()
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))
        self.assertIsNone(obj=r.context)

    def test_user_cannot_reject_friend_request_he_sent_another_user(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))
        self.assertIsNone(obj=r.context)

    def test_user_that_has_received_request_can_reject_it(self):
        self.client.login(username=self.other_user.slug, password=USER_PASSWORD)
        self.assertFalse(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user_friends_list_url)
        self.assertFalse(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
        self.assertEqual(first=self.other_user.friendship_requests_received.count(), second=0)
        self.assertIsNone(obj=r.context)
        r = self.client.get(path=self.other_user_friends_list_url)
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=['Friend request rejected.']) ###### TODO


@only_on_sites_with_login
class RemoveFriendViewTestCase(SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        Friend.objects.add_friend(from_user=self.user, to_user=self.other_user).accept()
        self.page_url = '/{}/friends/remove/'.format(self.other_user.slug)
        self.opposite_url = '/{}/friends/remove/'.format(self.user.slug)

    def test_visitor_has_no_access(self):
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))
        self.assertIsNone(obj=r.context)

    def test_user_can_remove_other_user(self):
        self.assertEqual(first=Friend.objects.count(), second=1 * 2)
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user.get_absolute_url())
        self.assertEqual(first=Friend.objects.count(), second=0)
        self.assertIsNone(obj=r.context)
        r = self.client.get(path=self.other_user.get_absolute_url())
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=['You have removed this user from friends.']) ###### TODO

    def test_other_user_can_remove_first_user(self):
        self.assertEqual(first=Friend.objects.count(), second=1 * 2)
        self.client.login(username=self.other_user.slug, password=USER_PASSWORD)
        r = self.client.post(path=self.opposite_url)
        self.assertRedirects(response=r, expected_url=self.user.get_absolute_url())
        self.assertEqual(first=Friend.objects.count(), second=0)
        self.assertIsNone(obj=r.context)
        r = self.client.get(path=self.other_user.get_absolute_url())
        self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=['You have removed this user from friends.']) ###### TODO


