from speedy.core.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software
from django.test import override_settings
from friendship.models import Friend, FriendshipRequest

from speedy.core.test import exclude_on_speedy_match
from speedy.net.accounts.tests.test_factories import UserFactory


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class UserFriendListViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.client.login(username=self.user.slug, password='111')

    @exclude_on_speedy_match
    def test_visitor_can_open_the_page(self):
        self.client.logout()
        r = self.client.get('/{}/friends/'.format(self.user.slug))
        self.assertEqual(first=r.status_code, second=200)

    def test_user_can_open_his_friends_page(self):
        r = self.client.get('/{}/friends/'.format(self.user.slug))
        self.assertEqual(first=r.status_code, second=200)

    def test_user_can_open_other_users_friends_page(self):
        r = self.client.get('/{}/friends/'.format(self.other_user.slug))
        self.assertEqual(first=r.status_code, second=200)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class ReceivedFriendshipRequestsListView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.client.login(username=self.user.slug, password='111')
        self.page_url = '/{}/friends/received-requests/'.format(self.user.slug)
        self.other_page_url = '/{}/friends/received-requests/'.format(self.other_user.slug)

    @exclude_on_speedy_match
    def test_visitor_cannot_open_the_page(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)

    def test_user_cannot_open_other_users_requests_page(self):
        r = self.client.get(self.other_page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.other_page_url))


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class SentFriendshipRequestsListView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.client.login(username=self.user.slug, password='111')
        self.page_url = '/{}/friends/sent-requests/'.format(self.user.slug)
        self.other_page_url = '/{}/friends/sent-requests/'.format(self.other_user.slug)

    @exclude_on_speedy_match
    def test_visitor_cannot_open_the_page(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_can_open_the_page(self):
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)

    def test_user_cannot_open_other_users_requests_page(self):
        r = self.client.get(self.other_page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.other_page_url))


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class UserFriendRequestViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.page_url = '/{}/friends/request/'.format(self.other_user.slug)
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_cannot_send_friend_request(self):
        self.client.logout()
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_can_send_friend_request(self):
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user.get_absolute_url())
        self.assertEqual(first=self.other_user.friendship_requests_received.count(), second=1)
        self.assertEqual(first=self.user.friendship_requests_sent.count(), second=1)
        frequest = self.other_user.friendship_requests_received.all()[0]
        self.assertEqual(first=frequest.from_user, second=self.user)
        self.assertEqual(first=frequest.to_user, second=self.other_user)

    def test_user_cannot_send_friend_request_twice(self):
        r1 = self.client.post(self.page_url)
        r2 = self.client.post(self.page_url)
        self.assertRedirects(response=r2, expected_url=self.other_user.get_absolute_url())
        self.assertEqual(first=self.other_user.friendship_requests_received.count(), second=1)

    @override_settings(MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED=1)
    def test_user_cannot_send_friend_request_if_maximum(self):
        Friend.objects.add_friend(self.user, UserFactory()).accept()
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user.get_absolute_url(), fetch_redirect_response=False)
        r = self.client.get(self.other_user.get_absolute_url())
        self.assertIn(member="You already have 1 friends. You can't have more than 1 friends on Speedy Net. Please remove friends before you proceed.", container=map(str, r.context['messages']))


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class CancelFriendRequestViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.page_url = '/{}/friends/request/cancel/'.format(self.other_user.slug)
        self.client.login(username=self.user.slug, password='111')

    def test_visitor_cannot_cancel_friend_request(self):
        self.client.logout()
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_can_cancel_friend_request(self):
        Friend.objects.add_friend(self.user, self.other_user)
        self.assertEqual(first=FriendshipRequest.objects.count(), second=1)
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user.get_absolute_url(), fetch_redirect_response=False)
        r = self.client.get(self.other_user.get_absolute_url())
        self.assertIn(member="You've cancelled your friend request.", container=map(str, r.context['messages']))


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class AcceptFriendRequestViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        frequest = Friend.objects.add_friend(self.user, self.other_user)
        self.page_url = '/{}/friends/request/accept/{}/'.format(self.other_user.slug, frequest.id)

    def test_visitor_cannot_accept_friend_request(self):
        self.client.logout()
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_cannot_accept_friend_request_he_sent_another_user(self):
        self.client.login(username=self.user.slug, password='111')
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_that_has_received_request_can_accept_it(self):
        self.client.login(username=self.other_user.slug, password='111')
        self.assertFalse(expr=Friend.objects.are_friends(self.user, self.other_user))
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url='/{}/friends/'.format(self.other_user.slug))
        self.assertTrue(expr=Friend.objects.are_friends(self.user, self.other_user))

    @override_settings(MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED=1)
    def test_user_that_has_received_request_cannot_accept_it_if_maximum(self):
        Friend.objects.add_friend(self.other_user, UserFactory()).accept()
        self.client.login(username=self.other_user.slug, password='111')
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url='/{}/friends/'.format(self.other_user.slug), fetch_redirect_response=False)
        r = self.client.get('/{}/friends/'.format(self.other_user.slug))
        self.assertIn(member="You already have 1 friends. You can't have more than 1 friends on Speedy Net. Please remove friends before you proceed.", container=map(str, r.context['messages']))
        self.assertFalse(expr=Friend.objects.are_friends(self.user, self.other_user))

    @override_settings(MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED=1)
    def test_user_that_has_received_request_cannot_accept_it_if_other_maximum(self):
        Friend.objects.add_friend(self.user, UserFactory()).accept()
        self.client.login(username=self.other_user.slug, password='111')
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url='/{}/friends/'.format(self.other_user.slug), fetch_redirect_response=False)
        r = self.client.get('/{}/friends/'.format(self.other_user.slug))
        self.assertIn(member="This user already has 1 friends. They can't have more than 1 friends on Speedy Net. Please ask them to remove friends before you proceed.", container=map(str, r.context['messages']))
        self.assertFalse(expr=Friend.objects.are_friends(self.user, self.other_user))


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class RejectFriendRequestViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        frequest = Friend.objects.add_friend(self.user, self.other_user)
        self.page_url = '/{}/friends/request/reject/{}/'.format(self.other_user.slug, frequest.id)

    def test_visitor_cannot_reject_friend_request(self):
        self.client.logout()
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_cannot_reject_friend_request_he_sent_another_user(self):
        self.client.login(username=self.user.slug, password='111')
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_that_has_received_request_can_reject_it(self):
        self.client.login(username=self.other_user.slug, password='111')
        self.assertFalse(expr=Friend.objects.are_friends(self.user, self.other_user))
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url='/{}/friends/'.format(self.other_user.slug))
        self.assertFalse(expr=Friend.objects.are_friends(self.user, self.other_user))
        # self.assertIsNotNone(obj=self.other_user.friendship_requests_received.all()[0].rejected)
        self.assertEqual(first=self.other_user.friendship_requests_received.count(), second=0)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class RemoveFriendViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        Friend.objects.add_friend(self.user, self.other_user).accept()
        self.page_url = '/{}/friends/remove/'.format(self.other_user.slug)
        self.opposite_url = '/{}/friends/remove/'.format(self.user.slug)

    def test_visitor_has_no_access(self):
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_can_remove_other_user(self):
        self.assertEqual(first=Friend.objects.count(), second=1 * 2)
        self.client.login(username=self.user.slug, password='111')
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url=self.other_user.get_absolute_url())
        self.assertEqual(first=Friend.objects.count(), second=0)

    def test_other_user_can_remove_first_user(self):
        self.assertEqual(first=Friend.objects.count(), second=1 * 2)
        self.client.login(username=self.other_user.slug, password='111')
        r = self.client.post(self.opposite_url)
        self.assertRedirects(response=r, expected_url=self.user.get_absolute_url())
        self.assertEqual(first=Friend.objects.count(), second=0)
