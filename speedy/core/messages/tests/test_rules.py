from time import sleep
from dateutil.relativedelta import relativedelta

from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_sites_with_login
    from speedy.core.blocks.models import Block

    from speedy.core.accounts.test.user_factories import ActiveUserFactory
    from speedy.core.messages.test.factories import ChatFactory
    from speedy.core.messages.models import Message


    @only_on_sites_with_login
    class SendMessageRulesTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user_1 = ActiveUserFactory()
            self.user_2 = ActiveUserFactory()

        def _create_users(self, users_count):
            for i in range(users_count):
                setattr(self, "user_{}".format(3 + i), ActiveUserFactory())

        def test_cannot_send_message_to_self(self):
            self.assertFalse(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_1))
            self.assertFalse(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_1))

        def test_can_send_message_to_other_user(self):
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))

        def test_cannot_send_message_to_other_user_if_blocked(self):
            Block.objects.block(blocker=self.user_2, blocked=self.user_1)
            self.assertFalse(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
            self.assertFalse(expr=self.user_2.has_perm(perm='messages.send_message', obj=self.user_1))
            self.assertFalse(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
            self.assertFalse(expr=self.user_2.has_perm(perm='messages.view_send_message_button', obj=self.user_1))

        def test_can_send_message_to_other_user_if_didnt_send_too_many_emails_1(self):
            self._create_users(users_count=6)
            chats = dict()
            for i in range(4):
                chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='test@example.com')
                sleep(0.01)
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))

        def test_can_send_message_to_other_user_if_didnt_send_too_many_emails_2(self):
            self._create_users(users_count=6)
            chats = dict()
            for i in range(5):
                chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Hello!')
                sleep(0.01)
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))

        def test_cannot_send_message_to_other_user_if_sent_too_many_emails_1(self):
            self._create_users(users_count=6)
            chats = dict()
            for i in range(5):
                chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='test@example.com')
                sleep(0.01)
            self.assertFalse(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))
            Message.objects.send_message(from_entity=self.user_7, chat=chats[str(4)], text='Hello!')
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))
            chats[str(5)] = ChatFactory(ent1=self.user_1, ent2=self.user_8)
            Message.objects.send_message(from_entity=self.user_1, chat=chats[str(5)], text='Hello!')
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))
            Message.objects.send_message(from_entity=self.user_1, chat=chats[str(5)], text='hello@example.org')
            self.assertFalse(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))
            Message.objects.send_message(from_entity=self.user_8, chat=chats[str(5)], text='Hi.')
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))

        def test_cannot_send_message_to_other_user_if_sent_too_many_emails_2(self):
            self._create_users(users_count=20)
            chats = dict()
            for i in range(4):
                chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='test@example.com')
                sleep(0.01)
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))
            for i in range(15):
                chats[str(4 + i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(4 + 3 + i)))
                Message.objects.send_message(from_entity=self.user_1, chat=chats[str(4 + i)], text='test@example.com')
                sleep(0.01)
                self.assertFalse(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))
            for i in range(4):
                Message.objects.send_message(from_entity=getattr(self, "user_{}".format(3 + i)), chat=chats[str(i)], text='Hello!')
                sleep(0.01)
                self.assertFalse(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))
            for i in range(12):
                Message.objects.send_message(from_entity=getattr(self, "user_{}".format(4 + 3 + i)), chat=chats[str(4 + i)], text='Hello!')
                sleep(0.01)
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))

        def test_cannot_send_message_to_other_user_if_sent_too_many_emails_3(self):
            self._create_users(users_count=30)
            self.user_1.date_created -= relativedelta(days=30)
            self.user_1.save_user_and_profile()
            chats = dict()
            for i in range(19):
                chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='test@example.com')
                sleep(0.01)
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))
            for i in range(5):
                chats[str(19 + i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(19 + 3 + i)))
                Message.objects.send_message(from_entity=self.user_1, chat=chats[str(19 + i)], text='test@example.com')
                sleep(0.01)
                self.assertFalse(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))

        def test_can_send_message_to_other_user_if_didnt_send_too_many_identical_messages(self):
            self._create_users(users_count=50)
            chats = dict()
            for i in range(40):
                chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Hello {}'.format(i % 2))
                sleep(0.01)
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))

        def test_cannot_send_message_to_other_user_if_sent_too_many_identical_messages_1(self):
            self._create_users(users_count=50)
            chats = dict()
            for i in range(29):
                chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Hello')
                sleep(0.01)
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))
            for i in range(11):
                chats[str(29 + i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(29 + 3 + i)))
                Message.objects.send_message(from_entity=self.user_1, chat=chats[str(29 + i)], text='Hello')
                sleep(0.01)
                self.assertFalse(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))
            for i in range(11):
                Message.objects.send_message(from_entity=getattr(self, "user_{}".format(29 + 3 + i)), chat=chats[str(29 + i)], text='Hello!')
                sleep(0.01)
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))

        def test_cannot_send_message_to_other_user_if_sent_too_many_identical_messages_2(self):
            self._create_users(users_count=80)
            chats = dict()
            for i in range(70):
                chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Hello {}'.format(i % 2))
                sleep(0.01)
                if (i < 58):
                    self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
                else:
                    self.assertFalse(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
                self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))
            self.assertFalse(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2))
            self.assertTrue(expr=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3))


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


