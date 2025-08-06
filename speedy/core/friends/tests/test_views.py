from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import random
        from time import sleep

        from dateutil.relativedelta import relativedelta

        from django.test import override_settings

        from friendship.models import Friend, FriendshipRequest

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.friends.test.mixins import SpeedyCoreFriendsLanguageMixin
        from speedy.core.base.test.utils import get_django_settings_class_with_override_settings

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.base.utils import get_both_genders_context_from_users
        from speedy.core.accounts.models import User


        class UserFriendListViewTestCaseMixin(TestCaseMixin):
            def set_up(self):
                super().set_up()
                self.first_user = ActiveUserFactory()
                self.second_user = ActiveUserFactory()
                self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
                self.first_user_friends_list_url = '/{}/friends/'.format(self.first_user.slug)
                self.second_user_friends_list_url = '/{}/friends/'.format(self.second_user.slug)

            def test_visitor_can_open_the_page(self):
                raise NotImplementedError("This test is not implemented in this mixin.")

            def test_visitor_cannot_open_the_page(self):
                raise NotImplementedError("This test is not implemented in this mixin.")

            def test_user_can_open_other_users_friends_page(self):
                raise NotImplementedError("This test is not implemented in this mixin.")

            def test_user_cannot_open_other_users_friends_page(self):
                raise NotImplementedError("This test is not implemented in this mixin.")

            def test_user_can_open_his_friends_page(self):
                r = self.client.get(path=self.first_user_friends_list_url)
                self.assertEqual(first=r.status_code, second=200)


        @only_on_sites_with_login
        class ReceivedFriendshipRequestsListViewOnlyEnglishTestCase(SiteTestCase):
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
        class SentFriendshipRequestsListViewOnlyEnglishTestCase(SiteTestCase):
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


        class UserFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin, TestCaseMixin):
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

            def test_user_cannot_send_friendship_request_to_a_user_who_sent_them_a_friendship_request(self):
                r = self.client.post(path=self.page_url)
                expected_url = self.second_user.get_absolute_url()
                self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
                self.assertEqual(first=self.first_user.friendship_requests_received.count(), second=0)
                self.assertEqual(first=self.first_user.friendship_requests_sent.count(), second=1)
                self.assertEqual(first=self.second_user.friendship_requests_received.count(), second=1)
                self.assertEqual(first=self.second_user.friendship_requests_sent.count(), second=0)
                self.assertIsNone(obj=r.context)
                r = self.client.get(path=expected_url)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._friendship_request_sent_success_message])
                r = self.client.get(path=expected_url)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])
                self.client.logout()
                self.client.login(username=self.second_user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.post(path=self.same_user_page_url)
                expected_url = self.first_user.get_absolute_url()
                self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
                self.assertEqual(first=self.first_user.friendship_requests_received.count(), second=0)
                self.assertEqual(first=self.first_user.friendship_requests_sent.count(), second=1)
                self.assertEqual(first=self.second_user.friendship_requests_received.count(), second=1)
                self.assertEqual(first=self.second_user.friendship_requests_sent.count(), second=0)
                self.assertIsNone(obj=r.context)
                r = self.client.get(path=expected_url)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._this_user_already_requested_friendship_from_you_error_message_dict_by_gender[self.first_user.get_gender()]])
                r = self.client.get(path=expected_url)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])

            def test_user_cannot_send_friendship_request_to_a_friend(self):
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=False)
                Friend.objects.add_friend(from_user=self.first_user, to_user=self.second_user).accept()
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=True)
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
        class UserFriendshipRequestViewAllLanguagesEnglishTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class UserFriendshipRequestViewAllLanguagesFrenchTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class UserFriendshipRequestViewAllLanguagesGermanTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class UserFriendshipRequestViewAllLanguagesSpanishTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class UserFriendshipRequestViewAllLanguagesPortugueseTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class UserFriendshipRequestViewAllLanguagesItalianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class UserFriendshipRequestViewAllLanguagesDutchTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class UserFriendshipRequestViewAllLanguagesSwedishTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class UserFriendshipRequestViewAllLanguagesKoreanTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class UserFriendshipRequestViewAllLanguagesFinnishTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class UserFriendshipRequestViewAllLanguagesHebrewTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class CancelFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin, TestCaseMixin):
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
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._youve_cancelled_your_friendship_request_success_message_dict_by_gender[self.first_user.get_gender()]])
                r = self.client.get(path=expected_url)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])


        @only_on_sites_with_login
        class CancelFriendshipRequestViewAllLanguagesEnglishTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class CancelFriendshipRequestViewAllLanguagesFrenchTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class CancelFriendshipRequestViewAllLanguagesGermanTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class CancelFriendshipRequestViewAllLanguagesSpanishTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class CancelFriendshipRequestViewAllLanguagesPortugueseTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class CancelFriendshipRequestViewAllLanguagesItalianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class CancelFriendshipRequestViewAllLanguagesDutchTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class CancelFriendshipRequestViewAllLanguagesSwedishTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class CancelFriendshipRequestViewAllLanguagesKoreanTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class CancelFriendshipRequestViewAllLanguagesFinnishTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class CancelFriendshipRequestViewAllLanguagesHebrewTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class AcceptFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin, TestCaseMixin):
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

            def test_user_cannot_accept_friendship_request_they_sent_another_user(self):
                self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.post(path=self.page_url)
                self.assertEqual(first=r.status_code, second=403)

            def test_user_that_has_received_request_can_accept_it(self):
                self.client.login(username=self.second_user.slug, password=tests_settings.USER_PASSWORD)
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=False)
                r = self.client.post(path=self.page_url)
                expected_url = self.first_user.get_absolute_url()
                self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=True)
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
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=False)
                r = self.client.post(path=self.page_url)
                expected_url = self.first_user.get_absolute_url()
                self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=True)
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
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=False)
                r = self.client.post(path=self.page_url)
                expected_url = self.first_user.get_absolute_url()
                self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=False)
                r = self.client.get(path=expected_url)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._you_already_have_friends_error_message_by_user_number_of_friends_and_gender(user_number_of_friends=4, gender=self.second_user.get_gender())])
                r = self.client.get(path=expected_url)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=False)

            @override_settings(USER_SETTINGS=get_django_settings_class_with_override_settings(django_settings_class=django_settings.USER_SETTINGS, MAX_NUMBER_OF_FRIENDS_ALLOWED=tests_settings.OVERRIDE_USER_SETTINGS.MAX_NUMBER_OF_FRIENDS_ALLOWED))
            def test_user_that_has_received_request_can_accept_it_if_other_not_maximum(self):
                self.assertEqual(first=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED, second=4)
                for i in range(User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED - 1):
                    Friend.objects.add_friend(from_user=self.first_user, to_user=ActiveUserFactory()).accept()
                self.client.login(username=self.second_user.slug, password=tests_settings.USER_PASSWORD)
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=False)
                r = self.client.post(path=self.page_url)
                expected_url = self.first_user.get_absolute_url()
                self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=True)
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
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=False)
                r = self.client.post(path=self.page_url)
                expected_url = self.first_user.get_absolute_url()
                self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=False)
                r = self.client.get(path=expected_url)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._this_user_already_has_friends_error_message_by_other_user_number_of_friends_and_both_genders(other_user_number_of_friends=4, both_genders=get_both_genders_context_from_users(user=self.second_user, other_user=self.first_user))])
                r = self.client.get(path=expected_url)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=False)


        @only_on_sites_with_login
        class AcceptFriendshipRequestViewAllLanguagesEnglishTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AcceptFriendshipRequestViewAllLanguagesFrenchTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AcceptFriendshipRequestViewAllLanguagesGermanTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AcceptFriendshipRequestViewAllLanguagesSpanishTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AcceptFriendshipRequestViewAllLanguagesPortugueseTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AcceptFriendshipRequestViewAllLanguagesItalianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AcceptFriendshipRequestViewAllLanguagesDutchTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AcceptFriendshipRequestViewAllLanguagesSwedishTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AcceptFriendshipRequestViewAllLanguagesKoreanTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AcceptFriendshipRequestViewAllLanguagesFinnishTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AcceptFriendshipRequestViewAllLanguagesHebrewTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class RejectFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin, TestCaseMixin):
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

            def test_user_cannot_reject_friendship_request_they_sent_another_user(self):
                self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.post(path=self.page_url)
                self.assertEqual(first=r.status_code, second=403)

            def test_user_that_has_received_request_can_reject_it(self):
                self.client.login(username=self.second_user.slug, password=tests_settings.USER_PASSWORD)
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=False)
                r = self.client.post(path=self.page_url)
                expected_url = self.first_user.get_absolute_url()
                self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200, fetch_redirect_response=False)
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.first_user, user2=self.second_user), expr2=False)
                self.assertEqual(first=self.second_user.friendship_requests_received.count(), second=0)
                self.assertIsNone(obj=r.context)
                r = self.client.get(path=expected_url)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[self._friendship_request_rejected_success_message])
                r = self.client.get(path=expected_url)
                self.assertListEqual(list1=list(map(str, r.context['messages'])), list2=[])


        @only_on_sites_with_login
        class RejectFriendshipRequestViewAllLanguagesEnglishTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class RejectFriendshipRequestViewAllLanguagesFrenchTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class RejectFriendshipRequestViewAllLanguagesGermanTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class RejectFriendshipRequestViewAllLanguagesSpanishTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class RejectFriendshipRequestViewAllLanguagesPortugueseTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class RejectFriendshipRequestViewAllLanguagesItalianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class RejectFriendshipRequestViewAllLanguagesDutchTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class RejectFriendshipRequestViewAllLanguagesSwedishTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class RejectFriendshipRequestViewAllLanguagesKoreanTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class RejectFriendshipRequestViewAllLanguagesFinnishTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class RejectFriendshipRequestViewAllLanguagesHebrewTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class RemoveFriendViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin, TestCaseMixin):
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
        class RemoveFriendViewAllLanguagesEnglishTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class RemoveFriendViewAllLanguagesFrenchTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class RemoveFriendViewAllLanguagesGermanTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class RemoveFriendViewAllLanguagesSpanishTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class RemoveFriendViewAllLanguagesPortugueseTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class RemoveFriendViewAllLanguagesItalianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class RemoveFriendViewAllLanguagesDutchTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class RemoveFriendViewAllLanguagesSwedishTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class RemoveFriendViewAllLanguagesKoreanTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class RemoveFriendViewAllLanguagesFinnishTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class RemoveFriendViewAllLanguagesHebrewTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class FriendListsViewsObjectListTestCaseMixin(TestCaseMixin):
            def set_up(self):
                super().set_up()
                self.user_1 = ActiveUserFactory(gender=random.choice([User.GENDER_FEMALE, User.GENDER_MALE]))
                self.user_2 = ActiveUserFactory()
                self.user_3 = ActiveUserFactory()
                self.user_4 = ActiveUserFactory()
                self.user_5 = ActiveUserFactory()
                self.user_6 = ActiveUserFactory()
                self.user_7 = ActiveUserFactory()
                self.user_8 = ActiveUserFactory()
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_3).accept()
                Friend.objects.add_friend(from_user=self.user_4, to_user=self.user_1).accept()
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_5)
                Friend.objects.add_friend(from_user=self.user_1, to_user=self.user_6)
                Friend.objects.add_friend(from_user=self.user_7, to_user=self.user_1)
                Friend.objects.add_friend(from_user=self.user_8, to_user=self.user_1)
                Friend.objects.add_friend(from_user=self.user_2, to_user=self.user_3).accept()
                Friend.objects.add_friend(from_user=self.user_2, to_user=self.user_5)
                Friend.objects.add_friend(from_user=self.user_7, to_user=self.user_2)
                sleep(0.02)
                self.user_8.profile.update_last_visit()
                sleep(0.01)
                self.user_7.profile.update_last_visit()
                sleep(0.01)
                self.user_6.profile.update_last_visit()
                sleep(0.01)
                self.user_5.profile.update_last_visit()
                sleep(0.01)
                self.user_4.profile.update_last_visit()
                sleep(0.01)
                self.user_3.profile.update_last_visit()
                sleep(0.01)
                self.user_2.profile.update_last_visit()
                sleep(0.01)
                self.user_1.profile.update_last_visit()
                sleep(0.01)
                self.user_4.speedy_net_profile.last_visit -= relativedelta(days=1850)
                self.user_4.speedy_match_profile.last_visit -= relativedelta(days=1850)
                self.user_6.speedy_net_profile.last_visit -= relativedelta(days=1850)
                self.user_6.speedy_match_profile.last_visit -= relativedelta(days=1850)
                self.user_8.speedy_net_profile.last_visit -= relativedelta(days=1850)
                self.user_8.speedy_match_profile.last_visit -= relativedelta(days=1850)
                self.user_4.save_user_and_profile()
                self.user_6.save_user_and_profile()
                self.user_8.save_user_and_profile()
                self.user_1 = User.objects.get(pk=self.user_1.pk)

            def update_users_gender_to_match_to_gender_other(self):
                self.user_3.speedy_match_profile.gender_to_match = [User.GENDER_OTHER]
                self.user_5.speedy_match_profile.gender_to_match = [User.GENDER_OTHER]
                self.user_7.speedy_match_profile.gender_to_match = [User.GENDER_OTHER]
                self.user_3.save_user_and_profile()
                self.user_5.save_user_and_profile()
                self.user_7.save_user_and_profile()
                self.user_1 = User.objects.get(pk=self.user_1.pk)


        @only_on_sites_with_login
        class UserFriendListViewObjectListOnlyEnglishTestCase(FriendListsViewsObjectListTestCaseMixin, SiteTestCase):
            def test_site_user_friend_list_view_object_list(self):
                self.assertIs(expr1=all([(friendship.to_user == self.user_1) for friendship in self.user_1.site_friends]), expr2=True)
                users_list = [friendship.from_user for friendship in self.user_1.site_friends]
                self.assertEqual(first=len(users_list), second=len(self.user_1.site_friends))
                self.assertEqual(first=len(users_list), second=2)
                self.assertListEqual(list1=users_list, list2=[self.user_3, self.user_4])
                self.assertIs(expr1=all([(friendship.to_user == self.user_1) for friendship in self.user_1.speedy_net_friends]), expr2=True)
                users_list = [friendship.from_user for friendship in self.user_1.speedy_net_friends]
                self.assertEqual(first=len(users_list), second=len(self.user_1.speedy_net_friends))
                self.assertEqual(first=len(users_list), second=2)
                self.assertListEqual(list1=users_list, list2=[self.user_3, self.user_4])
                self.assertEqual(first=self.user_1.site_friends, second=self.user_1.speedy_net_friends)

                self.update_users_gender_to_match_to_gender_other()
                self.assertIs(expr1=all([(friendship.to_user == self.user_1) for friendship in self.user_1.site_friends]), expr2=True)
                users_list = [friendship.from_user for friendship in self.user_1.site_friends]
                self.assertEqual(first=len(users_list), second=len(self.user_1.site_friends))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 2, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
                self.assertListEqual(list1=users_list, list2={django_settings.SPEEDY_NET_SITE_ID: [self.user_3, self.user_4], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_4]}[self.site.id])
                self.assertIs(expr1=all([(friendship.to_user == self.user_1) for friendship in self.user_1.speedy_net_friends]), expr2=True)
                users_list = [friendship.from_user for friendship in self.user_1.speedy_net_friends]
                self.assertEqual(first=len(users_list), second=len(self.user_1.speedy_net_friends))
                self.assertEqual(first=len(users_list), second=2)
                self.assertListEqual(list1=users_list, list2=[self.user_3, self.user_4])
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=self.user_1.site_friends, second=self.user_1.speedy_net_friends)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertNotEqual(first=self.user_1.site_friends, second=self.user_1.speedy_net_friends)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")


        @only_on_sites_with_login
        class ReceivedFriendshipRequestsListViewObjectListOnlyEnglishTestCase(FriendListsViewsObjectListTestCaseMixin, SiteTestCase):
            def test_site_received_friendship_requests_list_view_object_list(self):
                self.assertIs(expr1=all([(friendship.to_user == self.user_1) for friendship in self.user_1.received_friendship_requests]), expr2=True)
                users_list = [friendship.from_user for friendship in self.user_1.received_friendship_requests]
                self.assertEqual(first=len(users_list), second=len(self.user_1.received_friendship_requests))
                self.assertEqual(first=len(users_list), second=2)
                self.assertListEqual(list1=users_list, list2=[self.user_7, self.user_8])

                self.update_users_gender_to_match_to_gender_other()
                self.assertIs(expr1=all([(friendship.to_user == self.user_1) for friendship in self.user_1.received_friendship_requests]), expr2=True)
                users_list = [friendship.from_user for friendship in self.user_1.received_friendship_requests]
                self.assertEqual(first=len(users_list), second=len(self.user_1.received_friendship_requests))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 2, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
                self.assertListEqual(list1=users_list, list2={django_settings.SPEEDY_NET_SITE_ID: [self.user_7, self.user_8], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_8]}[self.site.id])


        @only_on_sites_with_login
        class SentFriendshipRequestsListViewObjectListOnlyEnglishTestCase(FriendListsViewsObjectListTestCaseMixin, SiteTestCase):
            def test_site_sent_friendship_requests_list_view_object_list(self):
                self.assertIs(expr1=all([(friendship.from_user == self.user_1) for friendship in self.user_1.sent_friendship_requests]), expr2=True)
                users_list = [friendship.to_user for friendship in self.user_1.sent_friendship_requests]
                self.assertEqual(first=len(users_list), second=len(self.user_1.sent_friendship_requests))
                self.assertEqual(first=len(users_list), second=2)
                self.assertListEqual(list1=users_list, list2=[self.user_5, self.user_6])

                self.update_users_gender_to_match_to_gender_other()
                self.assertIs(expr1=all([(friendship.from_user == self.user_1) for friendship in self.user_1.sent_friendship_requests]), expr2=True)
                users_list = [friendship.to_user for friendship in self.user_1.sent_friendship_requests]
                self.assertEqual(first=len(users_list), second=len(self.user_1.sent_friendship_requests))
                self.assertEqual(first=len(users_list), second={django_settings.SPEEDY_NET_SITE_ID: 2, django_settings.SPEEDY_MATCH_SITE_ID: 1}[self.site.id])
                self.assertListEqual(list1=users_list, list2={django_settings.SPEEDY_NET_SITE_ID: [self.user_5, self.user_6], django_settings.SPEEDY_MATCH_SITE_ID: [self.user_6]}[self.site.id])


