from django.conf import settings as django_settings
from django.test import override_settings
from friendship.models import Friend, FriendshipRequest

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test import tests_settings
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_sites_with_login
    from speedy.core.friends.test.mixins import SpeedyCoreFriendsLanguageMixin
    from speedy.core.base.test.utils import get_django_settings_class_with_override_settings
    from speedy.core.base.utils import get_both_genders_context_from_users
    from speedy.core.accounts.models import User

    from speedy.core.accounts.test.user_factories import ActiveUserFactory


    class UserFriendListViewTestCaseMixin(object):
        def set_up(self):
            super().set_up()
            self.first_user = ActiveUserFactory()
            self.second_user = ActiveUserFactory()
            self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
            self.first_user_friends_list_url = '/{}/friends/'.format(self.first_user.slug)
            self.second_user_friends_list_url = '/{}/friends/'.format(self.second_user.slug)

        def test_visitor_can_open_the_page(self):
            raise NotImplementedError()

        def test_visitor_cannot_open_the_page(self):
            raise NotImplementedError()

        def test_user_can_open_other_users_friends_page(self):
            raise NotImplementedError()

        def test_user_cannot_open_other_users_friends_page(self):
            raise NotImplementedError()

        def test_user_can_open_his_friends_page(self):
            r = self.client.get(path=self.first_user_friends_list_url)
            self.assertEqual(first=r.status_code, second=200)


    @only_on_sites_with_login
    class ReceivedFriendshipRequestsListView(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.first_user = ActiveUserFactory()
            self.second_user = ActiveUserFactory()
            self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
            self.page_url = '/{}/friends/received-requests/'.format(self.first_user.slug)
            self.other_page_url = '/{}/friends/received-requests/'.format(self.second_user.slug)

        def test_visitor_cannot_open_the_page(self):
            self.client.logout()
            r = self.client.get(path=self.page_url)
            self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

        def test_user_can_open_the_page(self):
            r = self.client.get(path=self.page_url)
            self.assertEqual(first=r.status_code, second=200)

        def test_user_cannot_open_other_users_requests_page(self):
            r = self.client.get(path=self.other_page_url)
            self.assertEqual(first=r.status_code, second=403)


    @only_on_sites_with_login
    class SentFriendshipRequestsListView(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.first_user = ActiveUserFactory()
            self.second_user = ActiveUserFactory()
            self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
            self.page_url = '/{}/friends/sent-requests/'.format(self.first_user.slug)
            self.other_page_url = '/{}/friends/sent-requests/'.format(self.second_user.slug)

        def test_visitor_cannot_open_the_page(self):
            self.client.logout()
            r = self.client.get(path=self.page_url)
            self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

        def test_user_can_open_the_page(self):
            r = self.client.get(path=self.page_url)
            self.assertEqual(first=r.status_code, second=200)

        def test_user_cannot_open_other_users_requests_page(self):
            r = self.client.get(path=self.other_page_url)
            self.assertEqual(first=r.status_code, second=403)


    class UserFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin):
        def set_up(self):
            super().set_up()
            self.first_user = ActiveUserFactory()
            self.second_user = ActiveUserFactory()
            self.page_url = '/{}/friends/request/'.format(self.second_user.slug)
            self.same_user_page_url = '/{}/friends/request/'.format(self.first_user.slug)
            self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)

        def test_visitor_cannot_send_friendship_request(self):
            self.client.logout()
            r = self.client.post(path=self.page_url)
            self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
            self.assertIsNone(obj=r.context)

        def test_user_can_send_friendship_request(self):
            r = self.client.post(path=self.page_url)
            expected_url = self.second_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertEqual(first=self.second_user.friendship_requests_received.count(), second=1)
            self.assertEqual(first=self.first_user.friendship_requests_sent.count(), second=1)
            friendship_request = self.second_user.friendship_requests_received.first()
            self.assertEqual(first=friendship_request.from_user, second=self.first_user)
            self.assertEqual(first=friendship_request.to_user, second=self.second_user)
            self.assertIsNone(obj=r.context)
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._friendship_request_sent_success_message])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])

        def test_user_cannot_send_friendship_request_twice(self):
            r = self.client.post(path=self.page_url)
            expected_url = self.second_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertEqual(first=self.second_user.friendship_requests_received.count(), second=1)
            self.assertEqual(first=self.first_user.friendship_requests_sent.count(), second=1)
            self.assertIsNone(obj=r.context)
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._friendship_request_sent_success_message])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])
            r = self.client.post(path=self.page_url)
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertEqual(first=self.second_user.friendship_requests_received.count(), second=1)
            self.assertEqual(first=self.first_user.friendship_requests_sent.count(), second=1)
            self.assertIsNone(obj=r.context)
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._you_already_requested_friendship_from_this_user_error_message_dict_by_gender[self.second_user.get_gender()]])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])

        def test_user_cannot_send_friendship_request_to_a_friend(self):
            self.assertFalse(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))
            Friend.objects.add_friend(from_user=self.first_user, to_user=self.second_user).accept()
            self.assertTrue(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))
            r = self.client.post(path=self.page_url)
            expected_url = self.second_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertEqual(first=self.first_user.friendship_requests_received.count(), second=0)
            self.assertEqual(first=self.first_user.friendship_requests_sent.count(), second=0)
            self.assertIsNone(obj=r.context)
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._you_already_are_friends_with_this_user_error_message_dict_by_both_genders[get_both_genders_context_from_users(user=self.first_user, other_user=self.second_user)]])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])

        def test_user_cannot_send_friendship_request_to_himself(self):
            r = self.client.post(path=self.same_user_page_url)
            expected_url = self.first_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertEqual(first=self.first_user.friendship_requests_received.count(), second=0)
            self.assertEqual(first=self.first_user.friendship_requests_sent.count(), second=0)
            self.assertIsNone(obj=r.context)
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._you_cannot_be_friends_with_yourself_error_message_dict_by_gender[self.first_user.get_gender()]])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])

        @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MAX_NUMBER_OF_FRIENDS_ALLOWED=tests_settings.OVERRIDE_USER_SETTINGS.MAX_NUMBER_OF_FRIENDS_ALLOWED))
        def test_user_can_send_friendship_request_if_not_maximum(self):
            self.assertEqual(first=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED, second=4)
            for i in range(User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED - 1):
                Friend.objects.add_friend(from_user=self.first_user, to_user=ActiveUserFactory()).accept()
            r = self.client.post(path=self.page_url)
            expected_url = self.second_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertEqual(first=self.second_user.friendship_requests_received.count(), second=1)
            self.assertEqual(first=self.first_user.friendship_requests_sent.count(), second=1)
            friendship_request = self.second_user.friendship_requests_received.first()
            self.assertEqual(first=friendship_request.from_user, second=self.first_user)
            self.assertEqual(first=friendship_request.to_user, second=self.second_user)
            self.assertIsNone(obj=r.context)
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._friendship_request_sent_success_message])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])

        @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MAX_NUMBER_OF_FRIENDS_ALLOWED=tests_settings.OVERRIDE_USER_SETTINGS.MAX_NUMBER_OF_FRIENDS_ALLOWED))
        def test_user_cannot_send_friendship_request_if_maximum(self):
            self.assertEqual(first=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED, second=4)
            for i in range(User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED):
                Friend.objects.add_friend(from_user=self.first_user, to_user=ActiveUserFactory()).accept()
            r = self.client.post(path=self.page_url)
            expected_url = self.second_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertEqual(first=self.second_user.friendship_requests_received.count(), second=0)
            self.assertEqual(first=self.first_user.friendship_requests_sent.count(), second=0)
            self.assertIsNone(obj=r.context)
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._you_already_have_friends_error_message_by_user_number_of_friends_and_gender(user_number_of_friends=4, gender=self.first_user.get_gender())])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])


    @only_on_sites_with_login
    class UserFriendshipRequestViewEnglishTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='en')


    @only_on_sites_with_login
    @override_settings(LANGUAGE_CODE='he')
    class UserFriendshipRequestViewHebrewTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='he')


    class CancelFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin):
        def set_up(self):
            super().set_up()
            self.first_user = ActiveUserFactory()
            self.second_user = ActiveUserFactory()
            self.page_url = '/{}/friends/request/cancel/'.format(self.second_user.slug)
            self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)

        def test_visitor_cannot_cancel_friendship_request(self):
            self.client.logout()
            r = self.client.post(path=self.page_url)
            self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
            self.assertIsNone(obj=r.context)

        def test_user_can_cancel_friendship_request(self):
            Friend.objects.add_friend(from_user=self.first_user, to_user=self.second_user)
            self.assertEqual(first=FriendshipRequest.objects.count(), second=1)
            r = self.client.post(path=self.page_url)
            expected_url = self.second_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._youve_cancelled_your_friendship_request_success_message])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])


    @only_on_sites_with_login
    class CancelFriendshipRequestViewEnglishTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='en')


    @only_on_sites_with_login
    @override_settings(LANGUAGE_CODE='he')
    class CancelFriendshipRequestViewHebrewTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='he')


    class AcceptFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin):
        def set_up(self):
            super().set_up()
            self.first_user = ActiveUserFactory()
            self.second_user = ActiveUserFactory()
            friendship_request = Friend.objects.add_friend(from_user=self.first_user, to_user=self.second_user)
            self.page_url = '/{}/friends/request/accept/{}/'.format(self.second_user.slug, friendship_request.pk)
            self.second_user_friends_list_url = '/{}/friends/'.format(self.second_user.slug)

        def test_visitor_cannot_accept_friendship_request(self):
            self.client.logout()
            r = self.client.post(path=self.page_url)
            self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
            self.assertIsNone(obj=r.context)

        def test_user_cannot_accept_friendship_request_he_sent_another_user(self):
            self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
            r = self.client.post(path=self.page_url)
            self.assertEqual(first=r.status_code, second=403)

        def test_user_that_has_received_request_can_accept_it(self):
            self.client.login(username=self.second_user.slug, password=tests_settings.USER_PASSWORD)
            self.assertFalse(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))
            r = self.client.post(path=self.page_url)
            expected_url = self.first_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertTrue(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))
            self.assertIsNone(obj=r.context)
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._friendship_request_accepted_success_message])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])

        @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MAX_NUMBER_OF_FRIENDS_ALLOWED=tests_settings.OVERRIDE_USER_SETTINGS.MAX_NUMBER_OF_FRIENDS_ALLOWED))
        def test_user_that_has_received_request_can_accept_it_if_not_maximum(self):
            self.assertEqual(first=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED, second=4)
            for i in range(User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED - 1):
                Friend.objects.add_friend(from_user=self.second_user, to_user=ActiveUserFactory()).accept()
            self.client.login(username=self.second_user.slug, password=tests_settings.USER_PASSWORD)
            self.assertFalse(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))
            r = self.client.post(path=self.page_url)
            expected_url = self.first_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertTrue(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))
            self.assertIsNone(obj=r.context)
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._friendship_request_accepted_success_message])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])

        @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MAX_NUMBER_OF_FRIENDS_ALLOWED=tests_settings.OVERRIDE_USER_SETTINGS.MAX_NUMBER_OF_FRIENDS_ALLOWED))
        def test_user_that_has_received_request_cannot_accept_it_if_maximum(self):
            self.assertEqual(first=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED, second=4)
            for i in range(User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED):
                Friend.objects.add_friend(from_user=self.second_user, to_user=ActiveUserFactory()).accept()
            self.client.login(username=self.second_user.slug, password=tests_settings.USER_PASSWORD)
            self.assertFalse(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))
            r = self.client.post(path=self.page_url)
            expected_url = self.first_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertFalse(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._you_already_have_friends_error_message_by_user_number_of_friends_and_gender(user_number_of_friends=4, gender=self.second_user.get_gender())])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])
            self.assertFalse(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))

        @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MAX_NUMBER_OF_FRIENDS_ALLOWED=tests_settings.OVERRIDE_USER_SETTINGS.MAX_NUMBER_OF_FRIENDS_ALLOWED))
        def test_user_that_has_received_request_can_accept_it_if_other_not_maximum(self):
            self.assertEqual(first=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED, second=4)
            for i in range(User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED - 1):
                Friend.objects.add_friend(from_user=self.first_user, to_user=ActiveUserFactory()).accept()
            self.client.login(username=self.second_user.slug, password=tests_settings.USER_PASSWORD)
            self.assertFalse(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))
            r = self.client.post(path=self.page_url)
            expected_url = self.first_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertTrue(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))
            self.assertIsNone(obj=r.context)
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._friendship_request_accepted_success_message])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])

        @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MAX_NUMBER_OF_FRIENDS_ALLOWED=tests_settings.OVERRIDE_USER_SETTINGS.MAX_NUMBER_OF_FRIENDS_ALLOWED))
        def test_user_that_has_received_request_cannot_accept_it_if_other_maximum(self):
            self.assertEqual(first=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED, second=4)
            for i in range(User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED):
                Friend.objects.add_friend(from_user=self.first_user, to_user=ActiveUserFactory()).accept()
            self.client.login(username=self.second_user.slug, password=tests_settings.USER_PASSWORD)
            self.assertFalse(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))
            r = self.client.post(path=self.page_url)
            expected_url = self.first_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertFalse(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._this_user_already_has_friends_error_message_by_other_user_number_of_friends_and_both_genders(other_user_number_of_friends=4, both_genders=get_both_genders_context_from_users(user=self.second_user, other_user=self.first_user))])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])
            self.assertFalse(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))


    @only_on_sites_with_login
    class AcceptFriendshipRequestViewEnglishTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='en')


    @only_on_sites_with_login
    @override_settings(LANGUAGE_CODE='he')
    class AcceptFriendshipRequestViewHebrewTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='he')


    class RejectFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin):
        def set_up(self):
            super().set_up()
            self.first_user = ActiveUserFactory()
            self.second_user = ActiveUserFactory()
            friendship_request = Friend.objects.add_friend(from_user=self.first_user, to_user=self.second_user)
            self.page_url = '/{}/friends/request/reject/{}/'.format(self.second_user.slug, friendship_request.pk)
            self.second_user_friends_list_url = '/{}/friends/'.format(self.second_user.slug)

        def test_visitor_cannot_reject_friendship_request(self):
            self.client.logout()
            r = self.client.post(path=self.page_url)
            self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
            self.assertIsNone(obj=r.context)

        def test_user_cannot_reject_friendship_request_he_sent_another_user(self):
            self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
            r = self.client.post(path=self.page_url)
            self.assertEqual(first=r.status_code, second=403)

        def test_user_that_has_received_request_can_reject_it(self):
            self.client.login(username=self.second_user.slug, password=tests_settings.USER_PASSWORD)
            self.assertFalse(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))
            r = self.client.post(path=self.page_url)
            expected_url = self.first_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertFalse(expr=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user))
            self.assertEqual(first=self.second_user.friendship_requests_received.count(), second=0)
            self.assertIsNone(obj=r.context)
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._friendship_request_rejected_success_message])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])


    @only_on_sites_with_login
    class RejectFriendshipRequestViewEnglishTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='en')


    @only_on_sites_with_login
    @override_settings(LANGUAGE_CODE='he')
    class RejectFriendshipRequestViewHebrewTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='he')


    class RemoveFriendViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin):
        def set_up(self):
            super().set_up()
            self.first_user = ActiveUserFactory()
            self.second_user = ActiveUserFactory()
            Friend.objects.add_friend(from_user=self.first_user, to_user=self.second_user).accept()
            self.page_url = '/{}/friends/remove/'.format(self.second_user.slug)
            self.opposite_url = '/{}/friends/remove/'.format(self.first_user.slug)

        def test_visitor_has_no_access(self):
            r = self.client.post(path=self.page_url)
            self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
            self.assertIsNone(obj=r.context)

        def test_user_can_remove_other_user(self):
            self.assertEqual(first=Friend.objects.count(), second=1 * 2)
            self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
            r = self.client.post(path=self.page_url)
            expected_url = self.second_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertEqual(first=Friend.objects.count(), second=0)
            self.assertIsNone(obj=r.context)
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._you_have_removed_this_user_from_friends_success_message_dict_by_gender[self.second_user.get_gender()]])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])

        def test_other_user_can_remove_first_user(self):
            self.assertEqual(first=Friend.objects.count(), second=1 * 2)
            self.client.login(username=self.second_user.slug, password=tests_settings.USER_PASSWORD)
            r = self.client.post(path=self.opposite_url)
            expected_url = self.first_user.get_absolute_url()
            self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
            self.assertEqual(first=Friend.objects.count(), second=0)
            self.assertIsNone(obj=r.context)
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._you_have_removed_this_user_from_friends_success_message_dict_by_gender[self.first_user.get_gender()]])
            r = self.client.get(path=expected_url)
            self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])


    @only_on_sites_with_login
    class RemoveFriendViewEnglishTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='en')


    @only_on_sites_with_login
    @override_settings(LANGUAGE_CODE='he')
    class RemoveFriendViewHebrewTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='he')


