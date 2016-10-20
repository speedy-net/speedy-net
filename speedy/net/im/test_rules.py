from speedy.core.test import TestCase

from speedy.net.accounts.test_factories import UserFactory
from speedy.net.blocks.models import Block
from .test_factories import ChatFactory


class SendMessageTestCase(TestCase):
    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()

    def test_cannot_send_message_to_self(self):
        self.assertFalse(self.user1.has_perm('im.send_message', self.user1))

    def test_can_send_message_to_other_user(self):
        self.assertTrue(self.user1.has_perm('im.send_message', self.user2))

    def test_cannot_send_message_to_other_user_if_blocked(self):
        Block.objects.block(self.user2, self.user1)
        self.assertFalse(self.user1.has_perm('im.send_message', self.user2))
        self.assertTrue(self.user2.has_perm('im.send_message', self.user1))


class ViewChatsTestCase(TestCase):
    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()

    def test_can_see_his_chats(self):
        self.assertTrue(self.user1.has_perm('im.view_chats', self.user1))

    def test_cannot_see_other_user_chats(self):
        self.assertFalse(self.user1.has_perm('im.view_chats', self.user2))


class ReadChatTestCase(TestCase):
    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()
        self.chat_1_2 = ChatFactory(ent1=self.user1, ent2=self.user2)
        self.chat_1_3 = ChatFactory(ent1=self.user1, ent2=self.user3)

    def test_can_read_his_chat(self):
        self.assertTrue(self.user2.has_perm('im.read_chat', self.chat_1_2))

    def test_cannot_read_a_chat_user_is_not_participate_in(self):
        self.assertFalse(self.user2.has_perm('im.read_chat', self.chat_1_3))
