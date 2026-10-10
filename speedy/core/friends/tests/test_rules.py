"""
Test cases for the permission rules of the friends app of Speedy Core.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from friendship.models import Friend

        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.blocks.models import Block

        from speedy.core.friends.rules import friendship_request_sent, friendship_request_received, are_friends


        @only_on_sites_with_login
        class RequestRulesOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the friends.request permission rule, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates two active users for the tests.
                test_user_can_send_request_to_other_user(self): Asserts a user has permission to send a friendship request to another user.
                test_user_cannot_send_request_to_other_user_if_blocked(self): Asserts neither user has permission to send a friendship request to the other if the other user has blocked them.
                test_user_cannot_send_request_to_himself(self): Asserts a user has no permission to send a friendship request to themselves.
                test_user_cannot_send_second_request(self): Asserts a user has no permission to send a second friendship request after they are already friends.
            """

            def set_up(self):
                """
                Create two active users for the tests.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()

            def test_user_can_send_request_to_other_user(self):
                """
                Asserts the user has permission to send a friendship request to the other user.
                """
                self.assertIs(expr1=self.user.has_perm(perm='friends.request', obj=self.other_user), expr2=True)

            def test_user_cannot_send_request_to_other_user_if_blocked(self):
                """
                Asserts neither user has permission to send a friendship request to the other user, after the other user has blocked them.
                """
                Block.objects.block(blocker=self.other_user, blocked=self.user)
                self.assertIs(expr1=self.user.has_perm(perm='friends.request', obj=self.other_user), expr2=False)
                self.assertIs(expr1=self.other_user.has_perm(perm='friends.request', obj=self.user), expr2=False)

            def test_user_cannot_send_request_to_himself(self):
                """
                Asserts the user has no permission to send a friendship request to themselves.
                """
                self.assertIs(expr1=self.user.has_perm(perm='friends.request', obj=self.user), expr2=False)

            def test_user_cannot_send_second_request(self):
                """
                Asserts the user has no permission to send a friendship request to the other user after they are already friends.
                """
                Friend.objects.add_friend(from_user=self.user, to_user=self.other_user)
                self.assertIs(expr1=self.user.has_perm(perm='friends.request', obj=self.other_user), expr2=False)


        @only_on_sites_with_login
        class ViewRequestsRulesOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the friends.view_requests permission rule, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates two active users for the tests.
                test_user_cannot_view_incoming_requests_for_other_user(self): Asserts a user has no permission to view another user's incoming friendship requests.
                test_user_can_view_incoming_requests(self): Asserts a user has permission to view their own incoming friendship requests.
            """

            def set_up(self):
                """
                Create two active users for the tests.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()

            def test_user_cannot_view_incoming_requests_for_other_user(self):
                """
                Asserts the user has no permission to view another user's incoming friendship requests.
                """
                self.assertIs(expr1=self.user.has_perm(perm='friends.view_requests', obj=self.other_user), expr2=False)

            def test_user_can_view_incoming_requests(self):
                """
                Asserts the user has permission to view their own incoming friendship requests.
                """
                self.assertIs(expr1=self.user.has_perm(perm='friends.view_requests', obj=self.user), expr2=True)


        @only_on_sites_with_login
        class ViewFriendListRulesTestCaseMixin(TestCaseMixin):
            """
            Mixin that tests the friends.view_friend_list permission rule. Subclasses run it once in English (on Speedy Net) or once per site (on Speedy Match, where it is overridden).

            Methods:
                set_up(self): Creates two active users for the tests.
                test_user_can_view_his_own_friend_list(self): Asserts a user has permission to view their own friend list.
                test_user_can_view_another_user_friend_list(self): Not implemented in this mixin.
                test_user_cannot_view_another_user_friend_list(self): Not implemented in this mixin.
            """

            def set_up(self):
                """
                Create two active users for the tests.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()

            def test_user_can_view_his_own_friend_list(self):
                """
                Asserts the user has permission to view their own friend list.
                """
                self.assertIs(expr1=self.user.has_perm(perm='friends.view_friend_list', obj=self.user), expr2=True)

            def test_user_can_view_another_user_friend_list(self):
                """
                Not implemented in this mixin. Subclasses must override this test.
                """
                raise NotImplementedError("This test is not implemented in this mixin.")

            def test_user_cannot_view_another_user_friend_list(self):
                """
                Not implemented in this mixin. Subclasses must override this test.
                """
                raise NotImplementedError("This test is not implemented in this mixin.")


        @only_on_sites_with_login
        class RemoveRulesOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the friends.remove permission rule, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates two active users and makes them friends.
                test_user_can_remove_other_user(self): Asserts a user has permission to remove the other user as a friend.
                test_other_user_can_remove_user(self): Asserts the other user has permission to remove the user as a friend.
                test_user_cannot_remove_himself(self): Asserts a user has no permission to remove themselves as a friend.
                test_user_cannot_remove_other_user_if_not_friends(self): Asserts a user has no permission to remove the other user as a friend once they are no longer friends.
            """

            def set_up(self):
                """
                Create two active users and make them friends.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()
                Friend.objects.add_friend(from_user=self.user, to_user=self.other_user).accept()

            def test_user_can_remove_other_user(self):
                """
                Asserts the user has permission to remove the other user as a friend.
                """
                self.assertIs(expr1=self.user.has_perm(perm='friends.remove', obj=self.other_user), expr2=True)

            def test_other_user_can_remove_user(self):
                """
                Asserts the other user has permission to remove the user as a friend.
                """
                self.assertIs(expr1=self.other_user.has_perm(perm='friends.remove', obj=self.user), expr2=True)

            def test_user_cannot_remove_himself(self):
                """
                Asserts the user has no permission to remove themselves as a friend.
                """
                self.assertIs(expr1=self.user.has_perm(perm='friends.remove', obj=self.user), expr2=False)

            def test_user_cannot_remove_other_user_if_not_friends(self):
                """
                Asserts the user has no permission to remove the other user as a friend once they are no longer friends.
                """
                Friend.objects.remove_friend(from_user=self.user, to_user=self.other_user)
                self.assertIs(expr1=self.user.has_perm(perm='friends.remove', obj=self.other_user), expr2=False)


        @only_on_sites_with_login
        class FriendshipRequestRulesOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the friendship_request_sent, friendship_request_received and are_friends predicates, run only once (in English) since they are language-independent.

            Methods:
                set_up(self): Creates two active users for the tests.
                test_friendship_request_sent_false(self): Asserts friendship_request_sent is False in both directions when no request was sent.
                test_friendship_request_sent_true(self): Asserts friendship_request_sent is True only in the direction the request was sent.
                test_friendship_request_received_false(self): Asserts friendship_request_received is False in both directions when no request was received.
                test_friendship_request_received_true(self): Asserts friendship_request_received is True only in the direction the request was received.
                test_are_friends_false(self): Asserts are_friends is False in both directions when the users are not friends.
                test_are_friends_true(self): Asserts are_friends is True in both directions once the users are friends.
            """

            def set_up(self):
                """
                Create two active users for the tests.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()

            def test_friendship_request_sent_false(self):
                """
                Asserts friendship_request_sent is False in both directions when no friendship request was sent.
                """
                self.assertIs(expr1=friendship_request_sent(user=self.user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=friendship_request_sent(user=self.other_user, other_user=self.user), expr2=False)

            def test_friendship_request_sent_true(self):
                """
                Asserts friendship_request_sent is True only from the user who sent the friendship request to the other user, and False in the opposite direction.
                """
                Friend.objects.add_friend(from_user=self.user, to_user=self.other_user)
                self.assertIs(expr1=friendship_request_sent(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=friendship_request_sent(user=self.other_user, other_user=self.user), expr2=False)

            def test_friendship_request_received_false(self):
                """
                Asserts friendship_request_received is False in both directions when no friendship request was received.
                """
                self.assertIs(expr1=friendship_request_received(user=self.user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=friendship_request_received(user=self.other_user, other_user=self.user), expr2=False)

            def test_friendship_request_received_true(self):
                """
                Asserts friendship_request_received is True only for the user who received the friendship request, and False in the opposite direction.
                """
                Friend.objects.add_friend(from_user=self.other_user, to_user=self.user)
                self.assertIs(expr1=friendship_request_received(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=friendship_request_received(user=self.other_user, other_user=self.user), expr2=False)

            def test_are_friends_false(self):
                """
                Asserts are_friends is False in both directions when the users are not friends.
                """
                self.assertIs(expr1=are_friends(user=self.user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=are_friends(user=self.other_user, other_user=self.user), expr2=False)

            def test_are_friends_true(self):
                """
                Asserts are_friends is True in both directions once the friendship request has been accepted.
                """
                Friend.objects.add_friend(from_user=self.user, to_user=self.other_user).accept()
                self.assertIs(expr1=are_friends(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=are_friends(user=self.other_user, other_user=self.user), expr2=True)


