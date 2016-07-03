from django.test import TestCase

from speedy.net.accounts.test_factories import UserFactory
from .models import Chat, Message
from .test_factories import ChatFactory


class ChatManagerTestCase(TestCase):
    def setUp(self):
        ChatFactory(is_group=True)
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()
        self.chat_1_2 = ChatFactory(ent1=self.user1, ent2=self.user2)
        self.chat_1_2_3 = ChatFactory(group=(self.user1, self.user2, self.user3), is_group=True)

    def test_chats(self):
        chats = list(Chat.on_site.chats(self.user1))
        self.assertListEqual(chats, [self.chat_1_2_3, self.chat_1_2])
        chats = list(Chat.on_site.chats(self.user3))
        self.assertListEqual(chats, [self.chat_1_2_3])

    def test_chat_with_two_users_returns_existing_one(self):
        chat = Chat.on_site.chat_with(self.user1, self.user2)
        self.assertEqual(chat, self.chat_1_2)

    def test_chat_with_two_users_creates_new_one(self):
        user4 = UserFactory()
        chat_count = Chat.objects.count()
        chat = Chat.on_site.chat_with(self.user1, user4)
        self.assertEqual(Chat.objects.count(), chat_count + 1)
        self.assertIsNotNone(chat.id)
        self.assertEqual(chat.participants_count, 2)
        entities_ids = set(ent.id for ent in chat.participants)
        self.assertSetEqual(entities_ids, {self.user1.id, user4.id})

    def test_chat_with_multiple_users_creates_new_one(self):
        Chat.on_site.group_chat_with(self.user1, self.user2, self.user3)


class MessageManagerTestCase(TestCase):
    def test_sending_message_creates_new_chat(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.assertEqual(Chat.objects.count(), 0)
        message = Message.objects.send_message(from_entity=self.user1, to_entity=self.user2, text='Hello')
        self.assertEqual(Chat.objects.count(), 1)
        self.assertEqual(message.chat.participants_count, 2)
        self.assertTrue(message.chat.is_private)
        self.assertFalse(message.chat.is_group)
        self.assertEqual(message.chat.ent1.id, self.user1.id)
        self.assertEqual(message.chat.ent2.id, self.user2.id)
        entities_ids = set(ent.id for ent in message.chat.participants)
        self.assertSetEqual(entities_ids, {self.user1.id, self.user2.id})
        self.assertEqual(message.sender_id, self.user1.id)
        self.assertEqual(message.text, 'Hello')

    def test_sending_message_to_exising_chat(self):
        self.user1 = UserFactory()
        self.chat = ChatFactory(ent1=self.user1)
        self.assertEqual(Chat.objects.count(), 1)
        message = Message.objects.send_message(from_entity=self.user1, chat=self.chat, text='Hello2')
        self.assertEqual(Chat.objects.count(), 1)
        self.assertEqual(message.chat, self.chat)
        self.assertEqual(message.sender_id, self.user1.id)
        self.assertEqual(message.text, 'Hello2')
