from time import sleep

from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.messages.models import Message, ReadMark
        from speedy.core.messages.templatetags import core_messages_tags_and_filters

        from speedy.core.accounts.test.user_factories import ActiveUserFactory
        from speedy.core.messages.test.factories import ChatFactory


        @only_on_sites_with_login
        class GetOtherParticipantTestCase(SiteTestCase):
            def test_tag(self):
                user_1 = ActiveUserFactory()
                user_2 = ActiveUserFactory()
                chat = ChatFactory(ent1=user_1, ent2=user_2)
                self.assertEqual(first=core_messages_tags_and_filters.get_other_participant(chat=chat, user=user_1).id, second=user_2.id)
                self.assertEqual(first=core_messages_tags_and_filters.get_other_participant(chat=chat, user=user_2).id, second=user_1.id)


        @only_on_sites_with_login
        class AnnotateChatsWithReadMarksTestCase(SiteTestCase):
            def test_tag(self):
                user_1 = ActiveUserFactory()
                chats = [
                    ChatFactory(ent1=user_1),  # 0 - no messages, no read mark
                    ChatFactory(ent1=user_1),  # 1 - no messages, has read mark
                    ChatFactory(ent1=user_1),  # 2 - has messages, no read mark
                    ChatFactory(ent1=user_1),  # 3 - has messages, has read mark, read
                    ChatFactory(ent1=user_1),  # 4 - has messages, has read mark, unread
                ]

                def _message(index):
                    Message.objects.send_message(from_entity=chats[index].ent2, chat=chats[index], text='text')
                    sleep(0.1)

                def _mark(index):
                    chats[index].mark_read(entity=user_1)
                    sleep(0.1)

                _message(2)
                _message(3)
                _message(4)
                _mark(1)
                _mark(3)
                _mark(4)
                _message(4)

                output = core_messages_tags_and_filters.annotate_chats_with_read_marks(chat_list=chats, entity=user_1)
                self.assertEqual(first=output, second='')
                self.assertFalse(expr=chats[0].is_unread)
                self.assertFalse(expr=chats[1].is_unread)
                self.assertTrue(expr=chats[2].is_unread)
                self.assertFalse(expr=chats[3].is_unread)
                self.assertTrue(expr=chats[4].is_unread)


        @only_on_sites_with_login
        class AnnotateMessagesWithReadMarksTestCase(SiteTestCase):
            def test_tag(self):
                user_1 = ActiveUserFactory()
                user_2 = ActiveUserFactory()
                chat = ChatFactory(ent1=user_1, ent2=user_2)
                messages = []
                messages.append(Message.objects.send_message(from_entity=user_2, chat=chat, text='User 2 First Message'))
                sleep(0.001)
                messages.append(Message.objects.send_message(from_entity=user_1, chat=chat, text='User 1 Message'))
                sleep(0.001)
                messages.append(Message.objects.send_message(from_entity=user_2, chat=chat, text='User 2 Second Message'))
                sleep(0.001)
                self.assertEqual(first=ReadMark.objects.count(), second=2)

                output = core_messages_tags_and_filters.annotate_messages_with_read_marks(message_list=messages, entity=user_1)
                self.assertEqual(first=output, second='')
                self.assertFalse(expr=messages[0].is_unread)
                self.assertFalse(expr=messages[1].is_unread)
                self.assertTrue(expr=messages[2].is_unread)

                output = core_messages_tags_and_filters.annotate_messages_with_read_marks(message_list=messages, entity=user_2)
                self.assertEqual(first=output, second='')
                self.assertFalse(expr=messages[0].is_unread)
                self.assertFalse(expr=messages[1].is_unread)
                self.assertFalse(expr=messages[2].is_unread)


        @only_on_sites_with_login
        class UnreadChatsCount(SiteTestCase):
            def test_tag(self):
                user_1 = ActiveUserFactory()
                user_2 = ActiveUserFactory()
                user_3 = ActiveUserFactory()

                chats = [
                    ChatFactory(ent1=user_1, ent2=user_2),
                    ChatFactory(ent1=user_3, ent2=user_1),
                    ChatFactory(ent1=user_2, ent2=user_3),
                ]

                Message.objects.send_message(from_entity=user_1, chat=chats[0], text='text')
                sleep(0.1)
                Message.objects.send_message(from_entity=user_2, chat=chats[0], text='text')
                sleep(0.1)
                Message.objects.send_message(from_entity=user_2, chat=chats[0], text='text')
                sleep(0.1)

                Message.objects.send_message(from_entity=user_3, chat=chats[1], text='text')
                sleep(0.1)
                Message.objects.send_message(from_entity=user_1, chat=chats[1], text='text')
                sleep(0.1)
                Message.objects.send_message(from_entity=user_3, chat=chats[1], text='text')
                sleep(0.1)

                Message.objects.send_message(from_entity=user_2, chat=chats[2], text='text')
                sleep(0.1)
                Message.objects.send_message(from_entity=user_3, chat=chats[2], text='text')
                sleep(0.1)

                self.assertEqual(first=core_messages_tags_and_filters.unread_chats_count(entity=user_1), second=1 + 1 + 0)
                self.assertEqual(first=core_messages_tags_and_filters.unread_chats_count(entity=user_2), second=0 + 0 + 1)
                self.assertEqual(first=core_messages_tags_and_filters.unread_chats_count(entity=user_3), second=0 + 0 + 0)


