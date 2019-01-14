from time import sleep
from django.conf import settings as django_settings

from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_sites_with_login
from speedy.core.im.models import Message, ReadMark
from speedy.core.im.templatetags import im_tags

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.test.user_factories import ActiveUserFactory
    from speedy.core.im.test.factories import ChatFactory


@only_on_sites_with_login
class GetOtherParticipantTestCase(SiteTestCase):
    def test_tag(self):
        user1 = ActiveUserFactory()
        user2 = ActiveUserFactory()
        chat = ChatFactory(ent1=user1, ent2=user2)
        self.assertEqual(first=im_tags.get_other_participant(chat, user1).id, second=user2.id)
        self.assertEqual(first=im_tags.get_other_participant(chat, user2).id, second=user1.id)


@only_on_sites_with_login
class AnnotateChatsWithReadMarksTestCase(SiteTestCase):
    def test_tag(self):
        user1 = ActiveUserFactory()
        chats = [
            ChatFactory(ent1=user1),  # 0 - no messages, no read mark
            ChatFactory(ent1=user1),  # 1 - no messages, has read mark
            ChatFactory(ent1=user1),  # 2 - has messages, no read mark
            ChatFactory(ent1=user1),  # 3 - has messages, has read mark, read
            ChatFactory(ent1=user1),  # 4 - has messages, has read mark, unread
        ]

        def _message(index):
            Message.objects.send_message(from_entity=chats[index].ent2, chat=chats[index], text='text')
            sleep(0.1)

        def _mark(index):
            chats[index].mark_read(user1)
            sleep(0.1)

        _message(2)
        _message(3)
        _message(4)
        _mark(1)
        _mark(3)
        _mark(4)
        _message(4)

        output = im_tags.annotate_chats_with_read_marks(chats, user1)
        self.assertEqual(first=output, second='')
        self.assertFalse(expr=chats[0].is_unread)
        self.assertFalse(expr=chats[1].is_unread)
        self.assertTrue(expr=chats[2].is_unread)
        self.assertFalse(expr=chats[3].is_unread)
        self.assertTrue(expr=chats[4].is_unread)


@only_on_sites_with_login
class AnnotateMessagesWithReadMarksTestCase(SiteTestCase):
    def test_tag(self):
        user1 = ActiveUserFactory()
        user2 = ActiveUserFactory()
        chat = ChatFactory(ent1=user1, ent2=user2)
        messages = [
            Message.objects.send_message(from_entity=user2, chat=chat, text='User 2 First Message'),
            Message.objects.send_message(from_entity=user1, chat=chat, text='User 1 Message'),
            Message.objects.send_message(from_entity=user2, chat=chat, text='User 2 Second Message'),
        ]
        self.assertEqual(first=ReadMark.objects.count(), second=2)

        output = im_tags.annotate_messages_with_read_marks(messages, user1)
        self.assertEqual(first=output, second='')
        self.assertFalse(expr=messages[0].is_unread)
        self.assertFalse(expr=messages[1].is_unread)
        self.assertTrue(expr=messages[2].is_unread)

        output = im_tags.annotate_messages_with_read_marks(messages, user2)
        self.assertEqual(first=output, second='')
        self.assertFalse(expr=messages[0].is_unread)
        self.assertFalse(expr=messages[1].is_unread)
        self.assertFalse(expr=messages[2].is_unread)


@only_on_sites_with_login
class UnreadChatsCount(SiteTestCase):
    def test_tag(self):
        user1 = ActiveUserFactory()
        user2 = ActiveUserFactory()
        user3 = ActiveUserFactory()

        chats = [
            ChatFactory(ent1=user1, ent2=user2),
            ChatFactory(ent1=user3, ent2=user1),
            ChatFactory(ent1=user2, ent2=user3),
        ]

        Message.objects.send_message(from_entity=user1, chat=chats[0], text='text')
        sleep(0.1)
        Message.objects.send_message(from_entity=user2, chat=chats[0], text='text')
        sleep(0.1)
        Message.objects.send_message(from_entity=user2, chat=chats[0], text='text')
        sleep(0.1)

        Message.objects.send_message(from_entity=user3, chat=chats[1], text='text')
        sleep(0.1)
        Message.objects.send_message(from_entity=user1, chat=chats[1], text='text')
        sleep(0.1)
        Message.objects.send_message(from_entity=user3, chat=chats[1], text='text')
        sleep(0.1)

        Message.objects.send_message(from_entity=user2, chat=chats[2], text='text')
        sleep(0.1)
        Message.objects.send_message(from_entity=user3, chat=chats[2], text='text')
        sleep(0.1)

        self.assertEqual(first=im_tags.unread_chats_count(user1), second=1 + 1 + 0)
        self.assertEqual(first=im_tags.unread_chats_count(user2), second=0 + 0 + 1)
        self.assertEqual(first=im_tags.unread_chats_count(user3), second=0 + 0 + 0)


