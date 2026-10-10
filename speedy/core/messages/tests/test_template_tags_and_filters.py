"""
Test cases for the template tags and filters of the messages app of Speedy Core.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from time import sleep

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login

        from speedy.core.accounts.test.user_factories import ActiveUserFactory
        from speedy.core.messages.test.factories import ChatFactory

        from speedy.core.messages.models import Message, ReadMark
        from speedy.core.messages.templatetags import core_messages_tags_and_filters


        @only_on_sites_with_login
        class GetOtherParticipantOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the get_other_participant template tag, run only once (in English) since it is language-independent.

            Methods:
                test_tag(self): Asserts get_other_participant returns each user's counterpart in a private chat.
            """

            def test_tag(self):
                """
                Asserts get_other_participant returns the other user when called for either participant of a private chat.
                """
                user_1 = ActiveUserFactory()
                user_2 = ActiveUserFactory()
                chat = ChatFactory(ent1=user_1, ent2=user_2)
                self.assertEqual(first=core_messages_tags_and_filters.get_other_participant(chat=chat, user=user_1).id, second=user_2.id)
                self.assertEqual(first=core_messages_tags_and_filters.get_other_participant(chat=chat, user=user_2).id, second=user_1.id)


        @only_on_sites_with_login
        class AnnotateChatsWithReadMarksOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the annotate_chats_with_read_marks template tag, run only once (in English) since it is language-independent.

            Methods:
                test_tag(self): Asserts annotate_chats_with_read_marks correctly sets is_unread on chats with and without messages and read marks.
            """

            def test_tag(self):
                """
                Asserts annotate_chats_with_read_marks returns an empty string and sets is_unread correctly on five chats covering combinations of having messages and/or a read mark, including a chat with a new message sent after the read mark.
                """
                user_1 = ActiveUserFactory()
                chats = [
                    ChatFactory(ent1=user_1),  # 0 - no messages, no read mark
                    ChatFactory(ent1=user_1),  # 1 - no messages, has read mark
                    ChatFactory(ent1=user_1),  # 2 - has messages, no read mark
                    ChatFactory(ent1=user_1),  # 3 - has messages, has read mark, read
                    ChatFactory(ent1=user_1),  # 4 - has messages, has read mark, unread
                ]

                def _message(index):
                    """
                    Sends a test message in the chat at the given index and pauses briefly to ensure distinct timestamps.

                    :param index: The index of the chat in the chats list.
                    :type index: int
                    """
                    Message.objects.send_message(from_entity=chats[index].ent2, chat=chats[index], text='text')
                    sleep(0.1)

                def _mark(index):
                    """
                    Marks the chat at the given index as read for user_1 and pauses briefly to ensure distinct timestamps.

                    :param index: The index of the chat in the chats list.
                    :type index: int
                    """
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
                self.assertIs(expr1=chats[0].is_unread, expr2=False)
                self.assertIs(expr1=chats[1].is_unread, expr2=False)
                self.assertIs(expr1=chats[2].is_unread, expr2=True)
                self.assertIs(expr1=chats[3].is_unread, expr2=False)
                self.assertIs(expr1=chats[4].is_unread, expr2=True)


        @only_on_sites_with_login
        class AnnotateMessagesWithReadMarksOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the annotate_messages_with_read_marks template tag, run only once (in English) since it is language-independent.

            Methods:
                test_tag(self): Asserts annotate_messages_with_read_marks sets is_unread correctly for each entity based on their read marks.
            """

            def test_tag(self):
                """
                Asserts annotate_messages_with_read_marks returns an empty string and marks messages as unread only when they were sent after the entity's read mark on their chat, checking both participants of the chat.
                """
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
                self.assertIs(expr1=messages[0].is_unread, expr2=False)
                self.assertIs(expr1=messages[1].is_unread, expr2=False)
                self.assertIs(expr1=messages[2].is_unread, expr2=True)

                output = core_messages_tags_and_filters.annotate_messages_with_read_marks(message_list=messages, entity=user_2)
                self.assertEqual(first=output, second='')
                self.assertIs(expr1=messages[0].is_unread, expr2=False)
                self.assertIs(expr1=messages[1].is_unread, expr2=False)
                self.assertIs(expr1=messages[2].is_unread, expr2=False)


        @only_on_sites_with_login
        class UnreadChatsCountOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the unread_chats_count template tag, run only once (in English) since it is language-independent.

            Methods:
                test_tag(self): Asserts unread_chats_count returns the correct number of unread chats for each of three users across three chats.
            """

            def test_tag(self):
                """
                Asserts unread_chats_count returns the correct count of unread chats for each of three users, given a set of messages sent across three chats between them.
                """
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


