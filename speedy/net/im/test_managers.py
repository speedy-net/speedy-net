from django.test import TestCase

from speedy.net.accounts.test_factories import UserFactory
from .models import Chat, Message
from .test_factories import ChatFactory


class ChatManagerTestCase(TestCase):
    def setUp(self):
        ChatFactory()
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.chat_1_2 = ChatFactory(participants=(self.user1, self.user2))
        self.group_chat = ChatFactory(participants=(self.user1, UserFactory(), self.user2))

    def test_chat_with_returns_existing_one(self):
        chat = Chat.objects.chat_with(self.user1, self.user2)
        self.assertEqual(chat, self.chat_1_2)

    def test_chat_with_creates_new_one(self):
        user3 = UserFactory()
        chat_count = Chat.objects.count()
        chat = Chat.objects.chat_with(self.user1, user3)
        self.assertEqual(Chat.objects.count(), chat_count + 1)
        self.assertIsNotNone(chat.id)
        self.assertEqual(chat.participants.count(), 2)
        entities_ids = set(chat.participants.values_list('id', flat=True))
        self.assertSetEqual(entities_ids, {self.user1.id, user3.id})


class MessageManagerTestCase(TestCase):
    def test_sending_message_creates_new_chat(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.assertEqual(Chat.objects.count(), 0)
        message = Message.objects.send_private(self.user1, self.user2, 'Hello')
        self.assertEqual(Chat.objects.count(), 1)
        self.assertEqual(message.chat.participants.count(), 2)
        entities_ids = set(message.chat.participants.values_list('id', flat=True))
        self.assertSetEqual(entities_ids, {self.user1.id, self.user2.id})
        self.assertEqual(message.sender_id, self.user1.id)
        self.assertEqual(message.text, 'Hello')
