from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software
from speedy.core.blocks.models import Block
from .test_factories import ChatFactory


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class SendMessageTestCase(TestCase):
    def setUp(self):
        self.user1 = ActiveUserFactory()
        self.user2 = ActiveUserFactory()

    def test_cannot_send_message_to_self(self):
        self.assertFalse(expr=self.user1.has_perm('im.send_message', self.user1))

    def test_can_send_message_to_other_user(self):
        self.assertTrue(expr=self.user1.has_perm('im.send_message', self.user2))

    def test_cannot_send_message_to_other_user_if_blocked(self):
        Block.objects.block(blocker=self.user2, self.user1)
        self.assertFalse(expr=self.user1.has_perm('im.send_message', self.user2))
        self.assertFalse(expr=self.user2.has_perm('im.send_message', self.user1))


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class ViewChatsTestCase(TestCase):
    def setUp(self):
        self.user1 = ActiveUserFactory()
        self.user2 = ActiveUserFactory()

    def test_can_see_his_chats(self):
        self.assertTrue(expr=self.user1.has_perm('im.view_chats', self.user1))

    def test_cannot_see_other_user_chats(self):
        self.assertFalse(expr=self.user1.has_perm('im.view_chats', self.user2))


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class ReadChatTestCase(TestCase):
    def setUp(self):
        self.user1 = ActiveUserFactory()
        self.user2 = ActiveUserFactory()
        self.user3 = ActiveUserFactory()
        self.chat_1_2 = ChatFactory(ent1=self.user1, ent2=self.user2)
        self.chat_1_3 = ChatFactory(ent1=self.user1, ent2=self.user3)

    def test_can_read_his_chat(self):
        self.assertTrue(expr=self.user2.has_perm('im.read_chat', self.chat_1_2))

    def test_cannot_read_a_chat_user_is_not_participate_in(self):
        self.assertFalse(expr=self.user2.has_perm('im.read_chat', self.chat_1_3))
