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
        class ChatManagerTestCase(SiteTestCase):
            def set_up(self):
                super().set_up()
                ChatFactory()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.user_3 = ActiveUserFactory()
                self.chat_1_2 = ChatFactory(ent1=self.user_1, ent2=self.user_2)
                self.chat_1_2_3 = ChatFactory.group_chat_with(group=(self.user_1, self.user_2, self.user_3))

            def test_chats(self):
                chats = list(Chat.objects.chats(entity=self.user_1))
                self.assertListEqual(list1=chats, list2=[self.chat_1_2_3, self.chat_1_2])
                chats = list(Chat.objects.chats(entity=self.user_3))
                self.assertListEqual(list1=chats, list2=[self.chat_1_2_3])

            def test_chat_with_two_users_returns_existing_one(self):
                chat = Chat.objects.chat_with(ent1=self.user_1, ent2=self.user_2)
                self.assertEqual(first=chat, second=self.chat_1_2)

            def test_chat_with_two_users_creates_new_one(self):
                initial_chat_count = Chat.objects.count()
                user_4 = ActiveUserFactory()
                chat = Chat.objects.chat_with(ent1=self.user_1, ent2=user_4)
                self.assertEqual(first=Chat.objects.count(), second=initial_chat_count + 1)
                self.assertIsNotNone(obj=chat.id)
                self.assertEqual(first=chat.participants_count, second=2)
                entities_ids = set(ent.id for ent in chat.participants)
                self.assertSetEqual(set1=entities_ids, set2={self.user_1.id, user_4.id})

            def test_chat_with_multiple_users_creates_new_one(self):
                Chat.objects.group_chat_with(self.user_1, self.user_2, self.user_3)

            def test_mark_read(self):
                chat = Chat.objects.chat_with(ent1=self.user_1, ent2=self.user_2)
                self.assertEqual(first=ReadMark.objects.count(), second=0)
                read_mark = chat.mark_read(entity=self.user_2)
                self.assertEqual(first=ReadMark.objects.count(), second=1)
                self.assertEqual(first=read_mark.chat, second=chat)
                self.assertEqual(first=read_mark.entity.id, second=self.user_2.id)


        @only_on_sites_with_login
        class MessageManagerTestCase(SiteTestCase):
            def test_sending_message_creates_new_chat(self):
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
        class ReadMarkManagerTestCase(SiteTestCase):
            def test_mark(self):
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


