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

            Methods:
                set_up(self): Creates two active users and logs in as the first user.
                test_visitor_can_open_the_page(self): Not implemented in this mixin.
                test_visitor_cannot_open_the_page(self): Not implemented in this mixin.
                test_user_can_open_other_users_friends_page(self): Not implemented in this mixin.
                test_user_cannot_open_other_users_friends_page(self): Not implemented in this mixin.
                test_user_can_open_his_friends_page(self): Asserts a logged-in user can open their own friends page.
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
                raise NotImplementedError("This test is not implemented in this mixin.")

            def test_visitor_cannot_open_the_page(self):
                """
                Not implemented in this mixin. Subclasses must override this test.
                """
                raise NotImplementedError("This test is not implemented in this mixin.")

            def test_user_can_open_other_users_friends_page(self):
                """
                Not implemented in this mixin. Subclasses must override this test.
                """
                raise NotImplementedError("This test is not implemented in this mixin.")

            def test_user_cannot_open_other_users_friends_page(self):
                """
                Not implemented in this mixin. Subclasses must override this test.
                """
                raise NotImplementedError("This test is not implemented in this mixin.")

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

            Methods:
                set_up(self): Creates two active users and logs in as the first user.
                test_visitor_cannot_open_the_page(self): Asserts a logged-out visitor is redirected to the login page.
                test_user_can_open_the_page(self): Asserts a logged-in user can open their own received friendship requests page.
                test_user_cannot_open_other_users_requests_page(self): Asserts a logged-in user gets a 403 when trying to view another user's received friendship requests page.
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

            Methods:
                set_up(self): Creates two active users and logs in as the first user.
                test_visitor_cannot_open_the_page(self): Asserts a logged-out visitor is redirected to the login page.
                test_user_can_open_the_page(self): Asserts a logged-in user can open their own sent friendship requests page.
                test_user_cannot_open_other_users_requests_page(self): Asserts a logged-in user gets a 403 when trying to view another user's sent friendship requests page.
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

            Methods:
                set_up(self): Creates two active users, logs in as the first user, and builds the friendship request page URLs.
                test_visitor_cannot_send_friendship_request(self): Asserts a logged-out visitor is redirected to the login page.
                test_user_can_send_friendship_request(self): Asserts a logged-in user can send a friendship request and sees a success message.
                test_user_cannot_send_friendship_request_twice(self): Asserts sending a second friendship request to the same user does not create a duplicate and shows an error message.
                test_user_cannot_send_friendship_request_to_a_user_who_sent_them_a_friendship_request(self): Asserts a user cannot send a friendship request to a user who already sent them one, in either direction.
                test_user_cannot_send_friendship_request_to_a_friend(self): Asserts a user cannot send a friendship request to an existing friend.
                test_user_cannot_send_friendship_request_to_himself(self): Asserts a user cannot send a friendship request to themselves.
                test_user_can_send_friendship_request_if_not_maximum(self): Asserts a user can send a friendship request when they have fewer than the maximum allowed friends.
                test_user_cannot_send_friendship_request_if_maximum(self): Asserts a user cannot send a friendship request when they already have the maximum allowed friends.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
            """
            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class UserFriendshipRequestViewAllMainLanguagesHebrewTestCase(UserFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests sending a friendship request, run once in Hebrew (as part of the suite that runs this mixin's tests in all main languages).

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
            """
            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class CancelFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin, TestCaseMixin):
            """
            Mixin that tests cancelling a friendship request, run once per supported language via the AllMainLanguages subclasses below.

            Methods:
                set_up(self): Creates two active users, logs in as the first user, and builds the cancel friendship request page URL.
                test_visitor_cannot_cancel_friendship_request(self): Asserts a logged-out visitor is redirected to the login page.
                test_user_can_cancel_friendship_request(self): Asserts a logged-in user can cancel a friendship request they sent and sees a success message.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
            """
            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class CancelFriendshipRequestViewAllMainLanguagesHebrewTestCase(CancelFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests cancelling a friendship request, run once in Hebrew (as part of the suite that runs this mixin's tests in all main languages).

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
            """
            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class AcceptFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin, TestCaseMixin):
            """
            Mixin that tests accepting a friendship request, run once per supported language via the AllMainLanguages subclasses below.

            Methods:
                set_up(self): Creates two active users, has the first user send the second a friendship request, and builds the accept friendship request page URL.
                test_visitor_cannot_accept_friendship_request(self): Asserts a logged-out visitor is redirected to the login page.
                test_user_cannot_accept_friendship_request_they_sent_another_user(self): Asserts the user who sent the request gets a 403 when trying to accept it themselves.
                test_user_that_has_received_request_can_accept_it(self): Asserts the user who received the request can accept it, becoming friends and seeing a success message.
                test_user_that_has_received_request_can_accept_it_if_not_maximum(self): Asserts the receiving user can accept the request when they have fewer than the maximum allowed friends.
                test_user_that_has_received_request_cannot_accept_it_if_maximum(self): Asserts the receiving user cannot accept the request when they already have the maximum allowed friends.
                test_user_that_has_received_request_can_accept_it_if_other_not_maximum(self): Asserts the receiving user can accept the request when the sender has fewer than the maximum allowed friends.
                test_user_that_has_received_request_cannot_accept_it_if_other_maximum(self): Asserts the receiving user cannot accept the request when the sender already has the maximum allowed friends.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
            """
            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AcceptFriendshipRequestViewAllMainLanguagesHebrewTestCase(AcceptFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests accepting a friendship request, run once in Hebrew (as part of the suite that runs this mixin's tests in all main languages).

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
            """
            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class RejectFriendshipRequestViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin, TestCaseMixin):
            """
            Mixin that tests rejecting a friendship request, run once per supported language via the AllMainLanguages subclasses below.

            Methods:
                set_up(self): Creates two active users, has the first user send the second a friendship request, and builds the reject friendship request page URL.
                test_visitor_cannot_reject_friendship_request(self): Asserts a logged-out visitor is redirected to the login page.
                test_user_cannot_reject_friendship_request_they_sent_another_user(self): Asserts the user who sent the request gets a 403 when trying to reject it themselves.
                test_user_that_has_received_request_can_reject_it(self): Asserts the user who received the request can reject it, removing the request and seeing a success message.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
            """
            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class RejectFriendshipRequestViewAllMainLanguagesHebrewTestCase(RejectFriendshipRequestViewTestCaseMixin, SiteTestCase):
            """
            Tests rejecting a friendship request, run once in Hebrew (as part of the suite that runs this mixin's tests in all main languages).

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
            """
            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class RemoveFriendViewTestCaseMixin(SpeedyCoreFriendsLanguageMixin, TestCaseMixin):
            """
            Mixin that tests removing a friend, run once per supported language via the AllMainLanguages subclasses below.

            Methods:
                set_up(self): Creates two active users and makes them friends, without logging in as either.
                test_visitor_has_no_access(self): Asserts a logged-out visitor is redirected to the login page.
                test_user_can_remove_other_user(self): Asserts the first user can remove the second user as a friend and sees a success message.
                test_other_user_can_remove_first_user(self): Asserts the second user can remove the first user as a friend and sees a success message.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
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

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
            """
            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class RemoveFriendViewAllMainLanguagesHebrewTestCase(RemoveFriendViewTestCaseMixin, SiteTestCase):
            """
            Tests removing a friend, run once in Hebrew (as part of the suite that runs this mixin's tests in all main languages).

            Methods:
                validate_all_values(self): Asserts the current language code is as expected, in addition to the base class's validations.
            """
            def validate_all_values(self):
                """
                Assert the current language code is as expected, in addition to the base class's validations.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class FriendListsViewsObjectListTestCaseMixin(TestCaseMixin):
            """
            Mixin that tests the object list rendered by the friend list, received friendship requests and sent friendship requests views, used by the three OnlyEnglishTestCase classes below.

            Methods:
                set_up(self): Creates eight users with several friendships and friendship requests, and staggered last-visit times (some users long inactive).
                update_users_gender_to_match_to_gender_other(self): Updates some users to only match users of gender "other", to test filtering by match on Speedy Match.
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

            Methods:
                test_site_user_friend_list_view_object_list(self): Asserts site_friends and speedy_net_friends are ordered by last visit, and that site_friends is filtered by match on Speedy Match once genders are updated.
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

            Methods:
                test_site_received_friendship_requests_list_view_object_list(self): Asserts received_friendship_requests is ordered by the sender's last visit and filtered by match on Speedy Match once genders are updated.
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

            Methods:
                test_site_sent_friendship_requests_list_view_object_list(self): Asserts sent_friendship_requests is ordered by the recipient's last visit and filtered by match on Speedy Match once genders are updated.
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


