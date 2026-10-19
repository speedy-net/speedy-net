"""
Test cases for the views of the friends app of Speedy Core: friend lists and friendship requests.
"""
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
            """
            Mixin that tests access to the user friend-list page. Subclasses run it once in English (on Speedy Net) or override some tests (on Speedy Match, where friend lists are irrelevant for other users).
            """

            def set_up(self):
                """
                Create two active users and log in as the first user.
                """
                super().set_up()
                self.first_user = ActiveUserFactory()
                self.second_user = ActiveUserFactory()
                self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
                self.first_user_friends_list_url = '/{}/friends/'.format(self.first_user.slug)
                self.second_user_friends_list_url = '/{}/friends/'.format(self.second_user.slug)

            def test_visitor_can_open_the_page(self):
                """
                Not implemented in this mixin. Subclasses must override this test.
                """
                raise NotImplementedError("test_visitor_can_open_the_page must be defined in classes inherited from UserFriendListViewTestCaseMixin.")

            def test_visitor_cannot_open_the_page(self):
                """
                Not implemented in this mixin. Subclasses must override this test.
                """
                raise NotImplementedError("test_visitor_cannot_open_the_page must be defined in classes inherited from UserFriendListViewTestCaseMixin.")

            def test_user_can_open_other_users_friends_page(self):
                """
                Not implemented in this mixin. Subclasses must override this test.
                """
                raise NotImplementedError("test_user_can_open_other_users_friends_page must be defined in classes inherited from UserFriendListViewTestCaseMixin.")

            def test_user_cannot_open_other_users_friends_page(self):
                """
                Not implemented in this mixin. Subclasses must override this test.
                """
                raise NotImplementedError("test_user_cannot_open_other_users_friends_page must be defined in classes inherited from UserFriendListViewTestCaseMixin.")

            def test_user_can_open_his_friends_page(self):
                """
                Asserts the logged-in user gets a 200 OK response when opening their own friends page.
                """
                r = self.client.get(path=self.first_user_friends_list_url)
                self.assertEqual(first=r.status_code, second=200)


        @only_on_sites_with_login
        class ReceivedFriendshipRequestsListViewOnlyEnglishTestCase(SiteTestCase):
            """
            Tests access to the received friendship requests page, run only once (in English) since it is language-independent.
            """

            def set_up(self):
                """
                Create two active users and log in as the first user.
                """
                super().set_up()
                self.first_user = ActiveUserFactory()
                self.second_user = ActiveUserFactory()
                self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
                self.page_url = '/{}/friends/received-requests/'.format(self.first_user.slug)
                self.other_page_url = '/{}/friends/received-requests/'.format(self.second_user.slug)

            def test_visitor_cannot_open_the_page(self):
                """
                Asserts a logged-out visitor is redirected to the login page when trying to view the received friendship requests page.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

            def test_user_can_open_the_page(self):
                """
                Asserts the logged-in user gets a 200 OK response when opening their own received friendship requests page.
                """
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)

            def test_user_cannot_open_other_users_requests_page(self):
                """
                Asserts the logged-in user gets a 403 Forbidden response when trying to view another user's received friendship requests page.
                """
                r = self.client.get(path=self.other_page_url)
                self.assertEqual(first=r.status_code, second=403)


        @only_on_sites_with_login
        class SentFriendshipRequestsListViewOnlyEnglishTestCase(SiteTestCase):
            """
            Tests access to the sent friendship requests page, run only once (in English) since it is language-independent.
            """

            def set_up(self):
                """
                Create two active users and log in as the first user.
                """
                super().set_up()
                self.first_user = ActiveUserFactory()
                self.second_user = ActiveUserFactory()
                self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
                self.page_url = '/{}/friends/sent-requests/'.format(self.first_user.slug)
                self.other_page_url = '/{}/friends/sent-requests/'.format(self.second_user.slug)

            def test_visitor_cannot_open_the_page(self):
                """
                Asserts a logged-out visitor is redirected to the login page when trying to view the sent friendship requests page.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

            def test_user_can_open_the_page(self):
                """
                Asserts the logged-in user gets a 200 OK response when opening their own sent friendship requests page.
                """
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)

            def test_user_cannot_open_other_users_requests_page(self):
                """
                Asserts the logged-in user gets a 403 Forbidden response when trying to view another user's sent friendship requests page.
                """
                r = self.client.get(path=self.other_page_url)
                self.assertEqual(first=r.status_code, second=403)


        class UserFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin, TestCaseMixin):
            """
            Mixin that tests sending a friendship request, run once per supported language via the AllMainLanguages subclasses below.
            """

            def set_up(self):
                """
                Create two active users, log in as the first user, and build the friendship request page URLs.
                """
                super().set_up()
                self.first_user = ActiveUserFactory()
                self.second_user = ActiveUserFactory()
                self.page_url = '/{}/friends/request/'.format(self.second_user.slug)
                self.same_user_page_url = '/{}/friends/request/'.format(self.first_user.slug)
                self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)

            def test_visitor_cannot_send_friendship_request(self):
                """
                Asserts a logged-out visitor is redirected to the login page when trying to send a friendship request.
                """
                self.client.logout()
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
                self.assertIsNone(obj=r.context)

            def test_user_can_send_friendship_request(self):
                """
                Asserts a logged-in user can send a friendship request to another user, creating exactly one received/sent request between them, and sees the "friendship request sent" success message exactly once.
                """
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
                """
                Asserts that sending a second friendship request to a user who already received one does not create a duplicate request and shows the "already requested friendship" error message.
                """
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
                """
                Asserts that when the first user sends the second user a friendship request, the second user attempting to send one back to the first user does not create a new request and shows the "this user already requested friendship from you" error message.
                """
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
                """
                Asserts that once two users are friends, sending a friendship request does not create any friendship request and shows the "already friends with this user" error message.
                """
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
                """
                Asserts that sending a friendship request to oneself does not create any friendship request and shows the "cannot be friends with yourself" error message.
                """
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
                """
                Asserts that a user who has fewer than the maximum allowed friends can send a friendship request and sees the "friendship request sent" success message.
                """
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
                """
                Asserts that a user who already has the maximum allowed number of friends cannot send a new friendship request, and sees the "you already have friends" error message.
                """
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
        class UserFriendshipRequestViewAllMainLanguagesEnglishTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests sending a friendship request, run once in English (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class UserFriendshipRequestViewAllMainLanguagesFrenchTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests sending a friendship request, run once in French (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class UserFriendshipRequestViewAllMainLanguagesGermanTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests sending a friendship request, run once in German (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class UserFriendshipRequestViewAllMainLanguagesSpanishTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests sending a friendship request, run once in Spanish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class UserFriendshipRequestViewAllMainLanguagesPortugueseTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests sending a friendship request, run once in Portuguese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class UserFriendshipRequestViewAllMainLanguagesItalianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests sending a friendship request, run once in Italian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class UserFriendshipRequestViewAllMainLanguagesDutchTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests sending a friendship request, run once in Dutch (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class UserFriendshipRequestViewAllMainLanguagesJapaneseTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Japanese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class UserFriendshipRequestViewAllMainLanguagesRussianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Russian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class UserFriendshipRequestViewAllMainLanguagesChineseTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Chinese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class UserFriendshipRequestViewAllMainLanguagesPolishTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Polish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class UserFriendshipRequestViewAllMainLanguagesPersianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Persian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class UserFriendshipRequestViewAllMainLanguagesHebrewTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests sending a friendship request, run once in Hebrew (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class UserFriendshipRequestViewAllMainLanguagesKoreanTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Korean (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class UserFriendshipRequestViewAllMainLanguagesArabicTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Arabic (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class UserFriendshipRequestViewAllMainLanguagesIndonesianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Indonesian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class UserFriendshipRequestViewAllMainLanguagesUkrainianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Ukrainian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class UserFriendshipRequestViewAllMainLanguagesTurkishTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Turkish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class UserFriendshipRequestViewAllMainLanguagesVietnameseTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Vietnamese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class UserFriendshipRequestViewAllMainLanguagesCzechTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Czech (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class UserFriendshipRequestViewAllMainLanguagesSwedishTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Swedish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class UserFriendshipRequestViewAllMainLanguagesFinnishTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Finnish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class UserFriendshipRequestViewAllMainLanguagesHungarianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Hungarian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class UserFriendshipRequestViewAllMainLanguagesThaiTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Thai (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class UserFriendshipRequestViewAllMainLanguagesGreekTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Greek (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class UserFriendshipRequestViewAllMainLanguagesMalayTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Malay (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class UserFriendshipRequestViewAllMainLanguagesSerbianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Serbian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class UserFriendshipRequestViewAllMainLanguagesRomanianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Romanian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class UserFriendshipRequestViewAllMainLanguagesBengaliTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Bengali (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class UserFriendshipRequestViewAllMainLanguagesCatalanTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Catalan (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class UserFriendshipRequestViewAllMainLanguagesNorwegianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Norwegian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class UserFriendshipRequestViewAllMainLanguagesBulgarianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Bulgarian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class UserFriendshipRequestViewAllMainLanguagesDanishTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Danish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class UserFriendshipRequestViewAllMainLanguagesSlovakTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Slovak (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class UserFriendshipRequestViewAllMainLanguagesHindiTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Hindi (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class UserFriendshipRequestViewAllMainLanguagesEstonianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Estonian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class UserFriendshipRequestViewAllMainLanguagesCroatianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Croatian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class UserFriendshipRequestViewAllMainLanguagesAzerbaijaniTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Azerbaijani (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class UserFriendshipRequestViewAllMainLanguagesCantoneseTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Cantonese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class UserFriendshipRequestViewAllMainLanguagesLithuanianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Lithuanian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class UserFriendshipRequestViewAllMainLanguagesSlovenianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Slovenian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class UserFriendshipRequestViewAllMainLanguagesBasqueTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Basque (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class UserFriendshipRequestViewAllMainLanguagesArmenianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Armenian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class UserFriendshipRequestViewAllMainLanguagesUzbekTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Uzbek (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class UserFriendshipRequestViewAllMainLanguagesTamilTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Tamil (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class UserFriendshipRequestViewAllMainLanguagesLatvianTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests sending a friendship request, run once in Latvian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class CancelFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin, TestCaseMixin):
            """
            Mixin that tests cancelling a friendship request, run once per supported language via the AllMainLanguages subclasses below.
            """

            def set_up(self):
                """
                Create two active users, log in as the first user, and build the cancel friendship request page URL.
                """
                super().set_up()
                self.first_user = ActiveUserFactory()
                self.second_user = ActiveUserFactory()
                self.page_url = '/{}/friends/request/cancel/'.format(self.second_user.slug)
                self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)

            def test_visitor_cannot_cancel_friendship_request(self):
                """
                Asserts a logged-out visitor is redirected to the login page when trying to cancel a friendship request.
                """
                self.client.logout()
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
                self.assertIsNone(obj=r.context)

            def test_user_can_cancel_friendship_request(self):
                """
                Asserts a logged-in user who sent a friendship request can cancel it, removing the request and showing the "you've cancelled your friendship request" success message.
                """
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
        class CancelFriendshipRequestViewAllMainLanguagesEnglishTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests cancelling a friendship request, run once in English (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class CancelFriendshipRequestViewAllMainLanguagesFrenchTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests cancelling a friendship request, run once in French (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class CancelFriendshipRequestViewAllMainLanguagesGermanTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests cancelling a friendship request, run once in German (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class CancelFriendshipRequestViewAllMainLanguagesSpanishTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests cancelling a friendship request, run once in Spanish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class CancelFriendshipRequestViewAllMainLanguagesPortugueseTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests cancelling a friendship request, run once in Portuguese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class CancelFriendshipRequestViewAllMainLanguagesItalianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests cancelling a friendship request, run once in Italian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class CancelFriendshipRequestViewAllMainLanguagesDutchTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests cancelling a friendship request, run once in Dutch (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class CancelFriendshipRequestViewAllMainLanguagesJapaneseTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Japanese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class CancelFriendshipRequestViewAllMainLanguagesRussianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Russian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class CancelFriendshipRequestViewAllMainLanguagesChineseTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Chinese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class CancelFriendshipRequestViewAllMainLanguagesPolishTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Polish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class CancelFriendshipRequestViewAllMainLanguagesPersianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Persian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class CancelFriendshipRequestViewAllMainLanguagesHebrewTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests cancelling a friendship request, run once in Hebrew (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class CancelFriendshipRequestViewAllMainLanguagesKoreanTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Korean (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class CancelFriendshipRequestViewAllMainLanguagesArabicTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Arabic (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class CancelFriendshipRequestViewAllMainLanguagesIndonesianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Indonesian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class CancelFriendshipRequestViewAllMainLanguagesUkrainianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Ukrainian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class CancelFriendshipRequestViewAllMainLanguagesTurkishTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Turkish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class CancelFriendshipRequestViewAllMainLanguagesVietnameseTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Vietnamese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class CancelFriendshipRequestViewAllMainLanguagesCzechTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Czech (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class CancelFriendshipRequestViewAllMainLanguagesSwedishTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Swedish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class CancelFriendshipRequestViewAllMainLanguagesFinnishTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Finnish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class CancelFriendshipRequestViewAllMainLanguagesHungarianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Hungarian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class CancelFriendshipRequestViewAllMainLanguagesThaiTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Thai (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class CancelFriendshipRequestViewAllMainLanguagesGreekTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Greek (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class CancelFriendshipRequestViewAllMainLanguagesMalayTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Malay (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class CancelFriendshipRequestViewAllMainLanguagesSerbianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Serbian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class CancelFriendshipRequestViewAllMainLanguagesRomanianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Romanian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class CancelFriendshipRequestViewAllMainLanguagesBengaliTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Bengali (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class CancelFriendshipRequestViewAllMainLanguagesCatalanTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Catalan (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class CancelFriendshipRequestViewAllMainLanguagesNorwegianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Norwegian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class CancelFriendshipRequestViewAllMainLanguagesBulgarianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Bulgarian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class CancelFriendshipRequestViewAllMainLanguagesDanishTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Danish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class CancelFriendshipRequestViewAllMainLanguagesSlovakTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Slovak (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class CancelFriendshipRequestViewAllMainLanguagesHindiTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Hindi (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class CancelFriendshipRequestViewAllMainLanguagesEstonianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Estonian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class CancelFriendshipRequestViewAllMainLanguagesCroatianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Croatian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class CancelFriendshipRequestViewAllMainLanguagesAzerbaijaniTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Azerbaijani (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class CancelFriendshipRequestViewAllMainLanguagesCantoneseTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Cantonese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class CancelFriendshipRequestViewAllMainLanguagesLithuanianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Lithuanian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class CancelFriendshipRequestViewAllMainLanguagesSlovenianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Slovenian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class CancelFriendshipRequestViewAllMainLanguagesBasqueTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Basque (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class CancelFriendshipRequestViewAllMainLanguagesArmenianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Armenian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class CancelFriendshipRequestViewAllMainLanguagesUzbekTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Uzbek (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class CancelFriendshipRequestViewAllMainLanguagesTamilTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Tamil (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class CancelFriendshipRequestViewAllMainLanguagesLatvianTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests cancelling a friendship request, run once in Latvian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class AcceptFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin, TestCaseMixin):
            """
            Mixin that tests accepting a friendship request, run once per supported language via the AllMainLanguages subclasses below.
            """

            def set_up(self):
                """
                Create two active users, have the first user send the second a friendship request, and build the accept friendship request page URL.
                """
                super().set_up()
                self.first_user = ActiveUserFactory()
                self.second_user = ActiveUserFactory()
                friendship_request = Friend.objects.add_friend(from_user=self.first_user, to_user=self.second_user)
                self.page_url = '/{}/friends/request/accept/{}/'.format(self.second_user.slug, friendship_request.pk)
                self.second_user_friends_list_url = '/{}/friends/'.format(self.second_user.slug)

            def test_visitor_cannot_accept_friendship_request(self):
                """
                Asserts a logged-out visitor is redirected to the login page when trying to accept a friendship request.
                """
                self.client.logout()
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
                self.assertIsNone(obj=r.context)

            def test_user_cannot_accept_friendship_request_they_sent_another_user(self):
                """
                Asserts the user who sent the friendship request gets a 403 Forbidden response when trying to accept it themselves.
                """
                self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.post(path=self.page_url)
                self.assertEqual(first=r.status_code, second=403)

            def test_user_that_has_received_request_can_accept_it(self):
                """
                Asserts the user who received the friendship request can accept it, becoming friends with the sender and seeing the "friendship request accepted" success message.
                """
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
                """
                Asserts the receiving user can accept the friendship request when they have fewer than the maximum allowed friends, becoming friends with the sender and seeing a success message.
                """
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
                """
                Asserts the receiving user cannot accept the friendship request when they already have the maximum allowed friends, remaining not friends with the sender and seeing the "you already have friends" error message.
                """
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
                """
                Asserts the receiving user can accept the friendship request when the sender has fewer than the maximum allowed friends, becoming friends and seeing a success message.
                """
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
                """
                Asserts the receiving user cannot accept the friendship request when the sender already has the maximum allowed friends, remaining not friends and seeing the "this user already has friends" error message.
                """
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
        class AcceptFriendshipRequestViewAllMainLanguagesEnglishTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests accepting a friendship request, run once in English (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AcceptFriendshipRequestViewAllMainLanguagesFrenchTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests accepting a friendship request, run once in French (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AcceptFriendshipRequestViewAllMainLanguagesGermanTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests accepting a friendship request, run once in German (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AcceptFriendshipRequestViewAllMainLanguagesSpanishTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests accepting a friendship request, run once in Spanish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AcceptFriendshipRequestViewAllMainLanguagesPortugueseTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests accepting a friendship request, run once in Portuguese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AcceptFriendshipRequestViewAllMainLanguagesItalianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests accepting a friendship request, run once in Italian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AcceptFriendshipRequestViewAllMainLanguagesDutchTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests accepting a friendship request, run once in Dutch (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class AcceptFriendshipRequestViewAllMainLanguagesJapaneseTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Japanese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class AcceptFriendshipRequestViewAllMainLanguagesRussianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Russian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class AcceptFriendshipRequestViewAllMainLanguagesChineseTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Chinese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class AcceptFriendshipRequestViewAllMainLanguagesPolishTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Polish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class AcceptFriendshipRequestViewAllMainLanguagesPersianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Persian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AcceptFriendshipRequestViewAllMainLanguagesHebrewTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests accepting a friendship request, run once in Hebrew (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AcceptFriendshipRequestViewAllMainLanguagesKoreanTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Korean (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class AcceptFriendshipRequestViewAllMainLanguagesArabicTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Arabic (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class AcceptFriendshipRequestViewAllMainLanguagesIndonesianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Indonesian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class AcceptFriendshipRequestViewAllMainLanguagesUkrainianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Ukrainian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class AcceptFriendshipRequestViewAllMainLanguagesTurkishTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Turkish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class AcceptFriendshipRequestViewAllMainLanguagesVietnameseTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Vietnamese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class AcceptFriendshipRequestViewAllMainLanguagesCzechTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Czech (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AcceptFriendshipRequestViewAllMainLanguagesSwedishTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Swedish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AcceptFriendshipRequestViewAllMainLanguagesFinnishTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Finnish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class AcceptFriendshipRequestViewAllMainLanguagesHungarianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Hungarian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class AcceptFriendshipRequestViewAllMainLanguagesThaiTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Thai (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class AcceptFriendshipRequestViewAllMainLanguagesGreekTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Greek (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class AcceptFriendshipRequestViewAllMainLanguagesMalayTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Malay (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class AcceptFriendshipRequestViewAllMainLanguagesSerbianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Serbian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class AcceptFriendshipRequestViewAllMainLanguagesRomanianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Romanian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class AcceptFriendshipRequestViewAllMainLanguagesBengaliTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Bengali (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class AcceptFriendshipRequestViewAllMainLanguagesCatalanTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Catalan (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class AcceptFriendshipRequestViewAllMainLanguagesNorwegianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Norwegian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class AcceptFriendshipRequestViewAllMainLanguagesBulgarianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Bulgarian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class AcceptFriendshipRequestViewAllMainLanguagesDanishTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Danish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class AcceptFriendshipRequestViewAllMainLanguagesSlovakTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Slovak (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class AcceptFriendshipRequestViewAllMainLanguagesHindiTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Hindi (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class AcceptFriendshipRequestViewAllMainLanguagesEstonianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Estonian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class AcceptFriendshipRequestViewAllMainLanguagesCroatianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Croatian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class AcceptFriendshipRequestViewAllMainLanguagesAzerbaijaniTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Azerbaijani (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class AcceptFriendshipRequestViewAllMainLanguagesCantoneseTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Cantonese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class AcceptFriendshipRequestViewAllMainLanguagesLithuanianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Lithuanian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class AcceptFriendshipRequestViewAllMainLanguagesSlovenianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Slovenian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class AcceptFriendshipRequestViewAllMainLanguagesBasqueTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Basque (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class AcceptFriendshipRequestViewAllMainLanguagesArmenianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Armenian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class AcceptFriendshipRequestViewAllMainLanguagesUzbekTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Uzbek (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class AcceptFriendshipRequestViewAllMainLanguagesTamilTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Tamil (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class AcceptFriendshipRequestViewAllMainLanguagesLatvianTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests accepting a friendship request, run once in Latvian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class RejectFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin, TestCaseMixin):
            """
            Mixin that tests rejecting a friendship request, run once per supported language via the AllMainLanguages subclasses below.
            """

            def set_up(self):
                """
                Create two active users, have the first user send the second a friendship request, and build the reject friendship request page URL.
                """
                super().set_up()
                self.first_user = ActiveUserFactory()
                self.second_user = ActiveUserFactory()
                friendship_request = Friend.objects.add_friend(from_user=self.first_user, to_user=self.second_user)
                self.page_url = '/{}/friends/request/reject/{}/'.format(self.second_user.slug, friendship_request.pk)
                self.second_user_friends_list_url = '/{}/friends/'.format(self.second_user.slug)

            def test_visitor_cannot_reject_friendship_request(self):
                """
                Asserts a logged-out visitor is redirected to the login page when trying to reject a friendship request.
                """
                self.client.logout()
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
                self.assertIsNone(obj=r.context)

            def test_user_cannot_reject_friendship_request_they_sent_another_user(self):
                """
                Asserts the user who sent the friendship request gets a 403 Forbidden response when trying to reject it themselves.
                """
                self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.post(path=self.page_url)
                self.assertEqual(first=r.status_code, second=403)

            def test_user_that_has_received_request_can_reject_it(self):
                """
                Asserts the user who received the friendship request can reject it, removing the request without becoming friends and seeing the "friendship request rejected" success message.
                """
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
        class RejectFriendshipRequestViewAllMainLanguagesEnglishTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests rejecting a friendship request, run once in English (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class RejectFriendshipRequestViewAllMainLanguagesFrenchTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests rejecting a friendship request, run once in French (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class RejectFriendshipRequestViewAllMainLanguagesGermanTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests rejecting a friendship request, run once in German (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class RejectFriendshipRequestViewAllMainLanguagesSpanishTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests rejecting a friendship request, run once in Spanish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class RejectFriendshipRequestViewAllMainLanguagesPortugueseTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests rejecting a friendship request, run once in Portuguese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class RejectFriendshipRequestViewAllMainLanguagesItalianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests rejecting a friendship request, run once in Italian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class RejectFriendshipRequestViewAllMainLanguagesDutchTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests rejecting a friendship request, run once in Dutch (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class RejectFriendshipRequestViewAllMainLanguagesJapaneseTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Japanese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class RejectFriendshipRequestViewAllMainLanguagesRussianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Russian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class RejectFriendshipRequestViewAllMainLanguagesChineseTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Chinese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class RejectFriendshipRequestViewAllMainLanguagesPolishTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Polish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class RejectFriendshipRequestViewAllMainLanguagesPersianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Persian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class RejectFriendshipRequestViewAllMainLanguagesHebrewTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests rejecting a friendship request, run once in Hebrew (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class RejectFriendshipRequestViewAllMainLanguagesKoreanTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Korean (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class RejectFriendshipRequestViewAllMainLanguagesArabicTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Arabic (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class RejectFriendshipRequestViewAllMainLanguagesIndonesianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Indonesian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class RejectFriendshipRequestViewAllMainLanguagesUkrainianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Ukrainian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class RejectFriendshipRequestViewAllMainLanguagesTurkishTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Turkish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class RejectFriendshipRequestViewAllMainLanguagesVietnameseTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Vietnamese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class RejectFriendshipRequestViewAllMainLanguagesCzechTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Czech (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class RejectFriendshipRequestViewAllMainLanguagesSwedishTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Swedish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class RejectFriendshipRequestViewAllMainLanguagesFinnishTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Finnish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class RejectFriendshipRequestViewAllMainLanguagesHungarianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Hungarian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class RejectFriendshipRequestViewAllMainLanguagesThaiTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Thai (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class RejectFriendshipRequestViewAllMainLanguagesGreekTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Greek (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class RejectFriendshipRequestViewAllMainLanguagesMalayTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Malay (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class RejectFriendshipRequestViewAllMainLanguagesSerbianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Serbian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class RejectFriendshipRequestViewAllMainLanguagesRomanianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Romanian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class RejectFriendshipRequestViewAllMainLanguagesBengaliTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Bengali (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class RejectFriendshipRequestViewAllMainLanguagesCatalanTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Catalan (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class RejectFriendshipRequestViewAllMainLanguagesNorwegianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Norwegian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class RejectFriendshipRequestViewAllMainLanguagesBulgarianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Bulgarian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class RejectFriendshipRequestViewAllMainLanguagesDanishTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Danish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class RejectFriendshipRequestViewAllMainLanguagesSlovakTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Slovak (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class RejectFriendshipRequestViewAllMainLanguagesHindiTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Hindi (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class RejectFriendshipRequestViewAllMainLanguagesEstonianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Estonian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class RejectFriendshipRequestViewAllMainLanguagesCroatianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Croatian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class RejectFriendshipRequestViewAllMainLanguagesAzerbaijaniTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Azerbaijani (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class RejectFriendshipRequestViewAllMainLanguagesCantoneseTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Cantonese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class RejectFriendshipRequestViewAllMainLanguagesLithuanianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Lithuanian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class RejectFriendshipRequestViewAllMainLanguagesSlovenianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Slovenian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class RejectFriendshipRequestViewAllMainLanguagesBasqueTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Basque (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class RejectFriendshipRequestViewAllMainLanguagesArmenianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Armenian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class RejectFriendshipRequestViewAllMainLanguagesUzbekTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Uzbek (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class RejectFriendshipRequestViewAllMainLanguagesTamilTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Tamil (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class RejectFriendshipRequestViewAllMainLanguagesLatvianTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests rejecting a friendship request, run once in Latvian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class RemoveFriendViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin, TestCaseMixin):
            """
            Mixin that tests removing a friend, run once per supported language via the AllMainLanguages subclasses below.
            """

            def set_up(self):
                """
                Create two active users and make them friends, without logging in as either.
                """
                super().set_up()
                self.first_user = ActiveUserFactory()
                self.second_user = ActiveUserFactory()
                Friend.objects.add_friend(from_user=self.first_user, to_user=self.second_user).accept()
                self.page_url = '/{}/friends/remove/'.format(self.second_user.slug)
                self.opposite_url = '/{}/friends/remove/'.format(self.first_user.slug)

            def test_visitor_has_no_access(self):
                """
                Asserts a logged-out visitor is redirected to the login page when trying to remove a friend.
                """
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
                self.assertIsNone(obj=r.context)

            def test_user_can_remove_other_user(self):
                """
                Asserts the first user can remove the second user as a friend, deleting the friendship and showing the "you have removed this user from your friends" success message.
                """
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
                """
                Asserts the second user can remove the first user as a friend, deleting the friendship and showing the "you have removed this user from your friends" success message.
                """
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
        class RemoveFriendViewAllMainLanguagesEnglishTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            """
            Tests removing a friend, run once in English (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class RemoveFriendViewAllMainLanguagesFrenchTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            """
            Tests removing a friend, run once in French (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class RemoveFriendViewAllMainLanguagesGermanTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            """
            Tests removing a friend, run once in German (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class RemoveFriendViewAllMainLanguagesSpanishTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            """
            Tests removing a friend, run once in Spanish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class RemoveFriendViewAllMainLanguagesPortugueseTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            """
            Tests removing a friend, run once in Portuguese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class RemoveFriendViewAllMainLanguagesItalianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            """
            Tests removing a friend, run once in Italian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class RemoveFriendViewAllMainLanguagesDutchTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            """
            Tests removing a friend, run once in Dutch (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class RemoveFriendViewAllMainLanguagesJapaneseTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Japanese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class RemoveFriendViewAllMainLanguagesRussianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Russian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class RemoveFriendViewAllMainLanguagesChineseTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Chinese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class RemoveFriendViewAllMainLanguagesPolishTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Polish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class RemoveFriendViewAllMainLanguagesPersianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Persian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class RemoveFriendViewAllMainLanguagesHebrewTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            """
            Tests removing a friend, run once in Hebrew (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class RemoveFriendViewAllMainLanguagesKoreanTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Korean (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class RemoveFriendViewAllMainLanguagesArabicTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Arabic (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class RemoveFriendViewAllMainLanguagesIndonesianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Indonesian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class RemoveFriendViewAllMainLanguagesUkrainianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Ukrainian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class RemoveFriendViewAllMainLanguagesTurkishTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Turkish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class RemoveFriendViewAllMainLanguagesVietnameseTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Vietnamese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class RemoveFriendViewAllMainLanguagesCzechTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Czech (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class RemoveFriendViewAllMainLanguagesSwedishTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Swedish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class RemoveFriendViewAllMainLanguagesFinnishTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Finnish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class RemoveFriendViewAllMainLanguagesHungarianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Hungarian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class RemoveFriendViewAllMainLanguagesThaiTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Thai (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class RemoveFriendViewAllMainLanguagesGreekTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Greek (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class RemoveFriendViewAllMainLanguagesMalayTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Malay (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class RemoveFriendViewAllMainLanguagesSerbianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Serbian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class RemoveFriendViewAllMainLanguagesRomanianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Romanian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class RemoveFriendViewAllMainLanguagesBengaliTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Bengali (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class RemoveFriendViewAllMainLanguagesCatalanTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Catalan (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class RemoveFriendViewAllMainLanguagesNorwegianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Norwegian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class RemoveFriendViewAllMainLanguagesBulgarianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Bulgarian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class RemoveFriendViewAllMainLanguagesDanishTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Danish (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class RemoveFriendViewAllMainLanguagesSlovakTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Slovak (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class RemoveFriendViewAllMainLanguagesHindiTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Hindi (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class RemoveFriendViewAllMainLanguagesEstonianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Estonian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class RemoveFriendViewAllMainLanguagesCroatianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Croatian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class RemoveFriendViewAllMainLanguagesAzerbaijaniTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Azerbaijani (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class RemoveFriendViewAllMainLanguagesCantoneseTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Cantonese (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class RemoveFriendViewAllMainLanguagesLithuanianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Lithuanian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class RemoveFriendViewAllMainLanguagesSlovenianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Slovenian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class RemoveFriendViewAllMainLanguagesBasqueTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Basque (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class RemoveFriendViewAllMainLanguagesArmenianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Armenian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class RemoveFriendViewAllMainLanguagesUzbekTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Uzbek (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class RemoveFriendViewAllMainLanguagesTamilTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Tamil (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class RemoveFriendViewAllMainLanguagesLatvianTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests removing a friend, run once in Latvian (as part of the suite that runs this mixin's tests in all main languages).
            """

            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class FriendListsViewsObjectListTestCaseMixin(TestCaseMixin):
            """
            Mixin that tests the object list rendered by the friend list, received friendship requests and sent friendship requests views, used by the three OnlyEnglishTestCase classes below.
            """

            def set_up(self):
                """
                Create eight users with several friendships and friendship requests, and staggered last-visit times, with some users set to a long-inactive last visit.
                """
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
                """
                Update user_3, user_5 and user_7 to only match users of gender "other", to test filtering by match on Speedy Match.
                """
                self.user_3.speedy_match_profile.gender_to_match = [User.GENDER_OTHER]
                self.user_5.speedy_match_profile.gender_to_match = [User.GENDER_OTHER]
                self.user_7.speedy_match_profile.gender_to_match = [User.GENDER_OTHER]
                self.user_3.save_user_and_profile()
                self.user_5.save_user_and_profile()
                self.user_7.save_user_and_profile()
                self.user_1 = User.objects.get(pk=self.user_1.pk)


        @only_on_sites_with_login
        class UserFriendListViewObjectListOnlyEnglishTestCase(FriendListsViewsObjectListTestCaseMixin, SiteTestCase):
            """
            Tests the object list rendered by the user friend list view, run only once (in English) since it is language-independent.
            """

            def test_site_user_friend_list_view_object_list(self):
                """
                Asserts site_friends and speedy_net_friends only include friendships where the user is the "to user" and are ordered by the friend's last visit (most recent first), and that on Speedy Match, site_friends is additionally filtered to only include matching friends once genders are updated, while speedy_net_friends remains unaffected.
                """
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
            """
            Tests the object list rendered by the received friendship requests view, run only once (in English) since it is language-independent.
            """

            def test_site_received_friendship_requests_list_view_object_list(self):
                """
                Asserts received_friendship_requests only includes requests where the user is the "to user", is ordered by the sender's last visit (most recent first), and on Speedy Match only includes senders who match the user once genders are updated.
                """
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
            """
            Tests the object list rendered by the sent friendship requests view, run only once (in English) since it is language-independent.
            """

            def test_site_sent_friendship_requests_list_view_object_list(self):
                """
                Asserts sent_friendship_requests only includes requests where the user is the "from user", is ordered by the recipient's last visit (most recent first), and on Speedy Match only includes recipients who match the user once genders are updated.
                """
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


