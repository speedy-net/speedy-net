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
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()

            def test_user_can_send_request_to_other_user(self):
                self.assertIs(expr1=self.user.has_perm(perm='friends.request', obj=self.other_user), expr2=True)

            def test_user_cannot_send_request_to_other_user_if_blocked(self):
                Block.objects.block(blocker=self.other_user, blocked=self.user)
                self.assertIs(expr1=self.user.has_perm(perm='friends.request', obj=self.other_user), expr2=False)
                self.assertIs(expr1=self.other_user.has_perm(perm='friends.request', obj=self.user), expr2=False)

            def test_user_cannot_send_request_to_himself(self):
                self.assertIs(expr1=self.user.has_perm(perm='friends.request', obj=self.user), expr2=False)

            def test_user_cannot_send_second_request(self):
                Friend.objects.add_friend(from_user=self.user, to_user=self.other_user)
                self.assertIs(expr1=self.user.has_perm(perm='friends.request', obj=self.other_user), expr2=False)


        @only_on_sites_with_login
        class ViewRequestsRulesOnlyEnglishTestCase(SiteTestCase):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()

            def test_user_cannot_view_incoming_requests_for_other_user(self):
                self.assertIs(expr1=self.user.has_perm(perm='friends.view_requests', obj=self.other_user), expr2=False)

            def test_user_can_view_incoming_requests(self):
                self.assertIs(expr1=self.user.has_perm(perm='friends.view_requests', obj=self.user), expr2=True)


        @only_on_sites_with_login
        class ViewFriendListRulesTestCaseMixin(TestCaseMixin):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()

            def test_user_can_view_his_own_friend_list(self):
                self.assertIs(expr1=self.user.has_perm(perm='friends.view_friend_list', obj=self.user), expr2=True)

            def test_user_can_view_another_user_friend_list(self):
                raise NotImplementedError("This test is not implemented in this mixin.")

            def test_user_cannot_view_another_user_friend_list(self):
                raise NotImplementedError("This test is not implemented in this mixin.")


        @only_on_sites_with_login
        class RemoveRulesOnlyEnglishTestCase(SiteTestCase):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()
                Friend.objects.add_friend(from_user=self.user, to_user=self.other_user).accept()

            def test_user_can_remove_other_user(self):
                self.assertIs(expr1=self.user.has_perm(perm='friends.remove', obj=self.other_user), expr2=True)

            def test_other_user_can_remove_user(self):
                self.assertIs(expr1=self.other_user.has_perm(perm='friends.remove', obj=self.user), expr2=True)

            def test_user_cannot_remove_himself(self):
                self.assertIs(expr1=self.user.has_perm(perm='friends.remove', obj=self.user), expr2=False)

            def test_user_cannot_remove_other_user_if_not_friends(self):
                Friend.objects.remove_friend(from_user=self.user, to_user=self.other_user)
                self.assertIs(expr1=self.user.has_perm(perm='friends.remove', obj=self.other_user), expr2=False)


        @only_on_sites_with_login
        class FriendshipRequestRulesOnlyEnglishTestCase(SiteTestCase):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.other_user = ActiveUserFactory()

            def test_friendship_request_sent_false(self):
                self.assertIs(expr1=friendship_request_sent(user=self.user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=friendship_request_sent(user=self.other_user, other_user=self.user), expr2=False)

            def test_friendship_request_sent_true(self):
                Friend.objects.add_friend(from_user=self.user, to_user=self.other_user)
                self.assertIs(expr1=friendship_request_sent(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=friendship_request_sent(user=self.other_user, other_user=self.user), expr2=False)

            def test_friendship_request_received_false(self):
                self.assertIs(expr1=friendship_request_received(user=self.user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=friendship_request_received(user=self.other_user, other_user=self.user), expr2=False)

            def test_friendship_request_received_true(self):
                Friend.objects.add_friend(from_user=self.other_user, to_user=self.user)
                self.assertIs(expr1=friendship_request_received(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=friendship_request_received(user=self.other_user, other_user=self.user), expr2=False)

            def test_are_friends_false(self):
                self.assertIs(expr1=are_friends(user=self.user, other_user=self.other_user), expr2=False)
                self.assertIs(expr1=are_friends(user=self.other_user, other_user=self.user), expr2=False)

            def test_are_friends_true(self):
                Friend.objects.add_friend(from_user=self.user, to_user=self.other_user).accept()
                self.assertIs(expr1=are_friends(user=self.user, other_user=self.other_user), expr2=True)
                self.assertIs(expr1=are_friends(user=self.other_user, other_user=self.user), expr2=True)


