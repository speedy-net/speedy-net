from time import sleep

from django.test import TestCase

from speedy.net.accounts.test_factories import UserFactory
from .models import Chat, Message, ReadMark
from .test_factories import ChatFactory


class ChatManagerTestCase(TestCase):
    def setUp(self):
        ChatFactory(is_group=True)
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()
        self.chat_1_2 = ChatFactory(ent1=self.user1, ent2=self.user2)
        self.chat_1_2_3 = ChatFactory(group=(self.user1, self.user2, self.user3))

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

    def test_mark_read(self):
        chat = Chat.on_site.chat_with(self.user1, self.user2)
        self.assertEqual(ReadMark.objects.count(), 0)
        rmark = chat.mark_read(self.user2)
        self.assertEqual(ReadMark.objects.count(), 1)
        self.assertEqual(rmark.chat, chat)
        self.assertEqual(rmark.entity.id, self.user2.id)

class MessageManagerTestCase(TestCase):
    def test_sending_message_creates_new_chat(self):
        user1 = UserFactory()
        user2 = UserFactory()
        self.assertEqual(Chat.objects.count(), 0)
        self.assertEqual(ReadMark.objects.count(), 0)
        message = Message.objects.send_message(from_entity=user1, to_entity=user2, text='Hello')
        self.assertEqual(Chat.objects.count(), 1)
        chat = message.chat
        self.assertEqual(chat.participants_count, 2)
        self.assertTrue(chat.is_private)
        self.assertFalse(chat.is_group)
        self.assertEqual(chat.ent1.id, user1.id)
        self.assertEqual(chat.ent2.id, user2.id)
        entities_ids = set(ent.id for ent in chat.participants)
        self.assertSetEqual(entities_ids, {user1.id, user2.id})
        self.assertEqual(message.sender_id, user1.id)
        self.assertEqual(message.text, 'Hello')
        self.assertEqual(ReadMark.objects.count(), 1)
        rmark = ReadMark.objects.latest()
        self.assertEqual(rmark.chat, chat)
        self.assertEqual(rmark.entity_id, user1.id)

    def test_sending_message_to_exising_chat(self):
        user1 = UserFactory()
        chat = ChatFactory(ent1=user1)
        self.assertEqual(Chat.objects.count(), 1)
        self.assertEqual(ReadMark.objects.count(), 0)
        message = Message.objects.send_message(from_entity=user1, chat=chat, text='Hello2')
        self.assertEqual(Chat.objects.count(), 1)
        self.assertEqual(message.chat, chat)
        self.assertEqual(message.sender_id, user1.id)
        self.assertEqual(message.text, 'Hello2')
        self.assertEqual(ReadMark.objects.count(), 1)
        rmark = ReadMark.objects.latest()
        self.assertEqual(rmark.chat, chat)
        self.assertEqual(rmark.entity_id, user1.id)


class ReadMarkManagerTestCase(TestCase):
    def test_mark(self):
        user = UserFactory()
        chat = ChatFactory(ent1=user)
        self.assertEqual(ReadMark.objects.count(), 0)
        rmark = ReadMark.objects.mark(chat, user)
        self.assertEqual(ReadMark.objects.count(), 1)
        self.assertEqual(rmark.chat, chat)
        self.assertEqual(rmark.entity.id, user.id)
        old_rmark = rmark
        sleep(1)
        rmark = ReadMark.objects.mark(chat, user)
        self.assertEqual(rmark.id, old_rmark.id)
        self.assertGreater(rmark.date_updated, old_rmark.date_updated)
