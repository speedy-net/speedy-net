"""
Test cases for the managers of the messages app of Speedy Core: chats, messages and read marks.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from time import sleep

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login

        from speedy.core.accounts.test.user_factories import ActiveUserFactory
        from speedy.core.messages.test.factories import ChatFactory

        from speedy.core.messages.models import Chat, Message, ReadMark


        @only_on_sites_with_login
        class ChatManagerOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the ChatManager's chats, chat_with, group_chat_with and count_unread_chats methods, and Chat.mark_read, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates seven active users and five chats (two private, two group, one private) among them.
                test_chats(self): Asserts chats() returns the correct chats, ordered most-recently-updated first, for several users.
                test_chat_with_two_users_returns_existing_one(self): Asserts chat_with returns the existing private chat between two users who already have one.
                test_chat_with_two_users_creates_new_one(self): Asserts chat_with creates a new private chat between two users who don't have one yet.
                test_chat_with_multiple_users_creates_new_one(self): Asserts group_chat_with creates a new group chat for three users.
                test_mark_read(self): Asserts chat.mark_read creates a ReadMark for the given entity on the given chat.
            """

            def set_up(self):
                """
                Creates seven active users and five chats (chat_1_2, chat_1_2_3, chat_4_5, chat_4_5_6, chat_4_7) among them, in a fixed creation order.
                """
                super().set_up()
                ChatFactory()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.user_3 = ActiveUserFactory()
                self.user_4 = ActiveUserFactory()
                self.user_5 = ActiveUserFactory()
                self.user_6 = ActiveUserFactory()
                self.user_7 = ActiveUserFactory()
                sleep(0.001)
                self.chat_1_2 = ChatFactory(ent1=self.user_1, ent2=self.user_2)
                sleep(0.001)
                self.chat_1_2_3 = ChatFactory.group_chat_with(group=(self.user_1, self.user_2, self.user_3))
                sleep(0.001)
                self.chat_4_5 = ChatFactory(ent1=self.user_4, ent2=self.user_5)
                sleep(0.001)
                self.chat_4_5_6 = ChatFactory.group_chat_with(group=(self.user_4, self.user_5, self.user_6))
                sleep(0.001)
                self.chat_4_7 = ChatFactory(ent1=self.user_4, ent2=self.user_7)
                sleep(0.001)

            def test_chats(self):
                """
                Asserts chats() returns, for each of several users, exactly the chats they participate in, ordered most-recently-updated first.
                """
                chats = list(Chat.objects.chats(entity=self.user_1))
                self.assertListEqual(list1=chats, list2=[self.chat_1_2_3, self.chat_1_2])
                chats = list(Chat.objects.chats(entity=self.user_3))
                self.assertListEqual(list1=chats, list2=[self.chat_1_2_3])
                chats = list(Chat.objects.chats(entity=self.user_4))
                self.assertListEqual(list1=chats, list2=[self.chat_4_7, self.chat_4_5_6, self.chat_4_5])
                chats = list(Chat.objects.chats(entity=self.user_5))
                self.assertListEqual(list1=chats, list2=[self.chat_4_5_6, self.chat_4_5])
                chats = list(Chat.objects.chats(entity=self.user_7))
                self.assertListEqual(list1=chats, list2=[self.chat_4_7])

            def test_chat_with_two_users_returns_existing_one(self):
                """
                Asserts chat_with returns the existing private chat between two users who already have one, instead of creating a new one.
                """
                chat = Chat.objects.chat_with(ent1=self.user_1, ent2=self.user_2)
                self.assertEqual(first=chat, second=self.chat_1_2)

            def test_chat_with_two_users_creates_new_one(self):
                """
                Asserts chat_with creates a new private chat with the correct two participants when none exists yet between the given users.
                """
                initial_chat_count = Chat.objects.count()
                user_8 = ActiveUserFactory()
                chat = Chat.objects.chat_with(ent1=self.user_1, ent2=user_8)
                self.assertEqual(first=Chat.objects.count(), second=initial_chat_count + 1)
                self.assertIsNotNone(obj=chat.id)
                self.assertEqual(first=chat.participants_count, second=2)
                entities_ids = set(ent.id for ent in chat.participants)
                self.assertSetEqual(set1=entities_ids, set2={self.user_1.id, user_8.id})

            def test_chat_with_multiple_users_creates_new_one(self):
                """
                Asserts group_chat_with successfully creates a new group chat for three users, without raising an error.
                """
                Chat.objects.group_chat_with(self.user_1, self.user_2, self.user_3)

            def test_mark_read(self):
                """
                Asserts chat.mark_read creates a single ReadMark for the given entity on the given chat.
                """
                chat = Chat.objects.chat_with(ent1=self.user_1, ent2=self.user_2)
                self.assertEqual(first=ReadMark.objects.count(), second=0)
                read_mark = chat.mark_read(entity=self.user_2)
                self.assertEqual(first=ReadMark.objects.count(), second=1)
                self.assertEqual(first=read_mark.chat, second=chat)
                self.assertEqual(first=read_mark.entity.id, second=self.user_2.id)


        @only_on_sites_with_login
        class MessageManagerOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the MessageManager.send_message method, run only once (in English) since it is language-independent.

            Methods:
                test_sending_message_creates_new_chat(self): Asserts send_message with to_entity creates a new chat, a message and a read mark for the sender.
                test_sending_message_to_existing_chat(self): Asserts send_message with an existing chat adds the message to it without creating a new chat.
            """

            def test_sending_message_creates_new_chat(self):
                """
                Asserts that sending a message to another user with no existing chat creates a new private chat, the message, and a read mark for the sender.
                """
                user_1 = ActiveUserFactory()
                user_2 = ActiveUserFactory()
                self.assertEqual(first=Chat.objects.count(), second=0)
                self.assertEqual(first=ReadMark.objects.count(), second=0)
                message = Message.objects.send_message(from_entity=user_1, to_entity=user_2, text='Hello')
                self.assertEqual(first=Chat.objects.count(), second=1)
                chat = message.chat
                self.assertEqual(first=chat.participants_count, second=2)
                self.assertIs(expr1=chat.is_private, expr2=True)
                self.assertIs(expr1=chat.is_group, expr2=False)
                self.assertEqual(first=chat.ent1.id, second=user_1.id)
                self.assertEqual(first=chat.ent2.id, second=user_2.id)
                entities_ids = set(ent.id for ent in chat.participants)
                self.assertSetEqual(set1=entities_ids, set2={user_1.id, user_2.id})
                self.assertEqual(first=message.sender_id, second=user_1.id)
                self.assertEqual(first=message.text, second='Hello')
                self.assertEqual(first=ReadMark.objects.count(), second=1)
                read_mark = ReadMark.objects.latest()
                self.assertEqual(first=read_mark.chat, second=chat)
                self.assertEqual(first=read_mark.entity_id, second=user_1.id)

            def test_sending_message_to_existing_chat(self):
                """
                Asserts that sending a message to an existing chat adds the message to that chat, without creating a new one, and creates a read mark for the sender.
                """
                user_1 = ActiveUserFactory()
                chat = ChatFactory(ent1=user_1)
                self.assertEqual(first=Chat.objects.count(), second=1)
                self.assertEqual(first=ReadMark.objects.count(), second=0)
                message = Message.objects.send_message(from_entity=user_1, chat=chat, text='Hello2')
                self.assertEqual(first=Chat.objects.count(), second=1)
                self.assertEqual(first=message.chat, second=chat)
                self.assertEqual(first=message.sender_id, second=user_1.id)
                self.assertEqual(first=message.text, second='Hello2')
                self.assertEqual(first=ReadMark.objects.count(), second=1)
                read_mark = ReadMark.objects.latest()
                self.assertEqual(first=read_mark.chat, second=chat)
                self.assertEqual(first=read_mark.entity_id, second=user_1.id)


        @only_on_sites_with_login
        class ReadMarkManagerOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the ReadMarkManager.mark method, run only once (in English) since it is language-independent.

            Methods:
                test_mark(self): Asserts mark creates a new read mark on first call and updates the existing one's timestamp on a subsequent call.
            """

            def test_mark(self):
                """
                Asserts that marking a chat as read for an entity creates a new read mark the first time, and updates (without recreating) the existing read mark's timestamp on a later call.
                """
                user = ActiveUserFactory()
                chat = ChatFactory(ent1=user)
                self.assertEqual(first=ReadMark.objects.count(), second=0)
                read_mark = ReadMark.objects.mark(chat=chat, entity=user)
                self.assertEqual(first=ReadMark.objects.count(), second=1)
                self.assertEqual(first=read_mark.chat, second=chat)
                self.assertEqual(first=read_mark.entity.id, second=user.id)
                old_read_mark = read_mark
                sleep(1)
                read_mark = ReadMark.objects.mark(chat=chat, entity=user)
                self.assertEqual(first=read_mark.id, second=old_read_mark.id)
                self.assertGreater(a=read_mark.date_updated, b=old_read_mark.date_updated)


