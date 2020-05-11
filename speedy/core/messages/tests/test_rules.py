from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_sites_with_login
    from speedy.core.blocks.models import Block

    from speedy.core.accounts.test.user_factories import ActiveUserFactory
    from speedy.core.messages.test.factories import ChatFactory


    @only_on_sites_with_login
    class SendMessageRulesTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user_1 = ActiveUserFactory()
            self.user_2 = ActiveUserFactory()

        def test_cannot_send_message_to_self(self):
            self.assertFalse(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_1))

        def test_can_send_message_to_other_user(self):
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))

        def test_cannot_send_message_to_other_user_if_blocked(self):
            Block.objects.block(blocker=self.user_2, blocked=self.user_1)
            self.assertFalse(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
            self.assertFalse(expr=self.user_2.has_perm(perm='messages.send_message', obj=self.user_1))


    @only_on_sites_with_login
    class ViewChatsRulesTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user_1 = ActiveUserFactory()
            self.user_2 = ActiveUserFactory()

        def test_can_see_his_chats(self):
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_chats', obj=self.user_1))

        def test_cannot_see_other_user_chats(self):
            self.assertFalse(expr=self.user_1.has_perm(perm='messages.view_chats', obj=self.user_2))


    @only_on_sites_with_login
    class ReadChatRulesTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user_1 = ActiveUserFactory()
            self.user_2 = ActiveUserFactory()
            self.user_3 = ActiveUserFactory()
            self.chat_1_2 = ChatFactory(ent1=self.user_1, ent2=self.user_2)
            self.chat_1_3 = ChatFactory(ent1=self.user_1, ent2=self.user_3)

        def test_can_read_his_chat(self):
            self.assertTrue(expr=self.user_2.has_perm(perm='messages.read_chat', obj=self.chat_1_2))

        def test_cannot_read_a_chat_user_is_not_participate_in(self):
            self.assertFalse(expr=self.user_2.has_perm(perm='messages.read_chat', obj=self.chat_1_3))


