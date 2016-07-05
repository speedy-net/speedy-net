from django.test import TestCase

from speedy.net.accounts.test_factories import UserFactory
from speedy.net.im.models import Message, ReadMark
from .templatetags import im_tags
from .test_factories import ChatFactory


class GetOtherParticipantTestCase(TestCase):
    def test_tag(self):
        user1 = UserFactory()
        user2 = UserFactory()
        chat = ChatFactory(ent1=user1, ent2=user2)
        self.assertEqual(im_tags.get_other_participant(chat, user1).id, user2.id)
        self.assertEqual(im_tags.get_other_participant(chat, user2).id, user1.id)


class AnnotateChatsWithReadMarksTestCase(TestCase):
    def test_tag(self):
        user1 = UserFactory()
        chats = [
            ChatFactory(ent1=user1),  # 0 - no messages, no read mark
            ChatFactory(ent1=user1),  # 1 - no messages, has read mark
            ChatFactory(ent1=user1),  # 2 - has messages, no read mark
            ChatFactory(ent1=user1),  # 3 - has messages, has read mark, read
            ChatFactory(ent1=user1),  # 4 - has messages, has read mark, unread
        ]

        def _message(index):
            Message.objects.send_message(from_entity=chats[index].ent2, chat=chats[index], text='text')

        def _mark(index):
            chats[index].mark_read(user1)

        _message(2)
        _message(3)
        _message(4)
        _mark(1)
        _mark(3)
        _mark(4)
        _message(4)

        output = im_tags.annotate_chats_with_read_marks(chats, user1)
        self.assertEqual(output, '')
        self.assertFalse(chats[0].is_unread)
        self.assertFalse(chats[1].is_unread)
        self.assertTrue(chats[2].is_unread)
        self.assertFalse(chats[3].is_unread)
        self.assertTrue(chats[4].is_unread)


class AnnotateMessagesWithReadMarksTestCase(TestCase):
    def test_tag(self):
        user1 = UserFactory()
        user2 = UserFactory()
        chat = ChatFactory(ent1=user1, ent2=user2)
        messages = [
            Message.objects.send_message(from_entity=user2, chat=chat, text='User 2 First Message'),
            Message.objects.send_message(from_entity=user1, chat=chat, text='User 1 Message'),
            Message.objects.send_message(from_entity=user2, chat=chat, text='User 2 Second Message'),
        ]
        self.assertEqual(ReadMark.objects.count(), 2)

        output = im_tags.annotate_messages_with_read_marks(messages, user1)
        self.assertEqual(output, '')
        self.assertFalse(messages[0].is_unread)
        self.assertFalse(messages[1].is_unread)
        self.assertTrue(messages[2].is_unread)

        output = im_tags.annotate_messages_with_read_marks(messages, user2)
        self.assertEqual(output, '')
        self.assertFalse(messages[0].is_unread)
        self.assertFalse(messages[1].is_unread)
        self.assertFalse(messages[2].is_unread)


class UnreadChatsCount(TestCase):
    def test_tag(self):
        user1 = UserFactory()
        user2 = UserFactory()
        user3 = UserFactory()

        chats = [
            ChatFactory(ent1=user1, ent2=user2),
            ChatFactory(ent1=user3, ent2=user1),
            ChatFactory(ent1=user2, ent2=user3),
        ]

        Message.objects.send_message(from_entity=user1, chat=chats[0], text='text')
        Message.objects.send_message(from_entity=user2, chat=chats[0], text='text')
        Message.objects.send_message(from_entity=user2, chat=chats[0], text='text')

        Message.objects.send_message(from_entity=user3, chat=chats[1], text='text')
        Message.objects.send_message(from_entity=user1, chat=chats[1], text='text')
        Message.objects.send_message(from_entity=user3, chat=chats[1], text='text')

        Message.objects.send_message(from_entity=user2, chat=chats[2], text='text')
        Message.objects.send_message(from_entity=user3, chat=chats[2], text='text')

        self.assertEqual(im_tags.unread_chats_count(user1), 1 + 1 + 0)
        self.assertEqual(im_tags.unread_chats_count(user2), 0 + 0 + 1)
        self.assertEqual(im_tags.unread_chats_count(user3), 0 + 0 + 0)
