from time import sleep
from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_sites_with_login
    from speedy.core.messages.models import Chat, Message, ReadMark

    from speedy.core.accounts.test.user_factories import ActiveUserFactory
    from speedy.core.messages.test.factories import ChatFactory


    @only_on_sites_with_login
    class ChatManagerTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            ChatFactory(is_group=True)
            self.user1 = ActiveUserFactory()
            self.user2 = ActiveUserFactory()
            self.user3 = ActiveUserFactory()
            self.chat_1_2 = ChatFactory(ent1=self.user1, ent2=self.user2)
            self.chat_1_2_3 = ChatFactory(group=(self.user1, self.user2, self.user3))

        def test_chats(self):
            chats = list(Chat.objects.chats(entity=self.user1))
            self.assertListEqual(list1=chats, list2=[self.chat_1_2_3, self.chat_1_2])
            chats = list(Chat.objects.chats(entity=self.user3))
            self.assertListEqual(list1=chats, list2=[self.chat_1_2_3])

        def test_chat_with_two_users_returns_existing_one(self):
            chat = Chat.objects.chat_with(ent1=self.user1, ent2=self.user2)
            self.assertEqual(first=chat, second=self.chat_1_2)

        def test_chat_with_two_users_creates_new_one(self):
            initial_chat_count = Chat.objects.count()
            user4 = ActiveUserFactory()
            chat = Chat.objects.chat_with(ent1=self.user1, ent2=user4)
            self.assertEqual(first=Chat.objects.count(), second=initial_chat_count + 1)
            self.assertIsNotNone(obj=chat.id)
            self.assertEqual(first=chat.participants_count, second=2)
            entities_ids = set(ent.id for ent in chat.participants)
            self.assertSetEqual(set1=entities_ids, set2={self.user1.id, user4.id})

        def test_chat_with_multiple_users_creates_new_one(self):
            Chat.objects.group_chat_with(self.user1, self.user2, self.user3)

        def test_mark_read(self):
            chat = Chat.objects.chat_with(ent1=self.user1, ent2=self.user2)
            self.assertEqual(first=ReadMark.objects.count(), second=0)
            rmark = chat.mark_read(entity=self.user2)
            self.assertEqual(first=ReadMark.objects.count(), second=1)
            self.assertEqual(first=rmark.chat, second=chat)
            self.assertEqual(first=rmark.entity.id, second=self.user2.id)


    @only_on_sites_with_login
    class MessageManagerTestCase(SiteTestCase):
        def test_sending_message_creates_new_chat(self):
            user1 = ActiveUserFactory()
            user2 = ActiveUserFactory()
            self.assertEqual(first=Chat.objects.count(), second=0)
            self.assertEqual(first=ReadMark.objects.count(), second=0)
            message = Message.objects.send_message(from_entity=user1, to_entity=user2, text='Hello')
            self.assertEqual(first=Chat.objects.count(), second=1)
            chat = message.chat
            self.assertEqual(first=chat.participants_count, second=2)
            self.assertTrue(expr=chat.is_private)
            self.assertFalse(expr=chat.is_group)
            self.assertEqual(first=chat.ent1.id, second=user1.id)
            self.assertEqual(first=chat.ent2.id, second=user2.id)
            entities_ids = set(ent.id for ent in chat.participants)
            self.assertSetEqual(set1=entities_ids, set2={user1.id, user2.id})
            self.assertEqual(first=message.sender_id, second=user1.id)
            self.assertEqual(first=message.text, second='Hello')
            self.assertEqual(first=ReadMark.objects.count(), second=1)
            rmark = ReadMark.objects.latest()
            self.assertEqual(first=rmark.chat, second=chat)
            self.assertEqual(first=rmark.entity_id, second=user1.id)

        def test_sending_message_to_existing_chat(self):
            user1 = ActiveUserFactory()
            chat = ChatFactory(ent1=user1)
            self.assertEqual(first=Chat.objects.count(), second=1)
            self.assertEqual(first=ReadMark.objects.count(), second=0)
            message = Message.objects.send_message(from_entity=user1, chat=chat, text='Hello2')
            self.assertEqual(first=Chat.objects.count(), second=1)
            self.assertEqual(first=message.chat, second=chat)
            self.assertEqual(first=message.sender_id, second=user1.id)
            self.assertEqual(first=message.text, second='Hello2')
            self.assertEqual(first=ReadMark.objects.count(), second=1)
            rmark = ReadMark.objects.latest()
            self.assertEqual(first=rmark.chat, second=chat)
            self.assertEqual(first=rmark.entity_id, second=user1.id)


    @only_on_sites_with_login
    class ReadMarkManagerTestCase(SiteTestCase):
        def test_mark(self):
            user = ActiveUserFactory()
            chat = ChatFactory(ent1=user)
            self.assertEqual(first=ReadMark.objects.count(), second=0)
            rmark = ReadMark.objects.mark(chat, user)
            self.assertEqual(first=ReadMark.objects.count(), second=1)
            self.assertEqual(first=rmark.chat, second=chat)
            self.assertEqual(first=rmark.entity.id, second=user.id)
            old_rmark = rmark
            sleep(1)
            rmark = ReadMark.objects.mark(chat, user)
            self.assertEqual(first=rmark.id, second=old_rmark.id)
            self.assertGreater(a=rmark.date_updated, b=old_rmark.date_updated)


