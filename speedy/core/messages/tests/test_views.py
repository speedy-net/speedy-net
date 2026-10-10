from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from time import sleep

        from dateutil.relativedelta import relativedelta

        from django.test import override_settings
        from django.core import mail

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.accounts.test.mixins import SpeedyCoreAccountsModelsMixin
        from speedy.core.messages.test.mixins import SpeedyCoreMessagesLanguageMixin

        from speedy.core.accounts.test.user_factories import ActiveUserFactory
        from speedy.core.messages.test.factories import ChatFactory

        from speedy.core.accounts.models import User
        from speedy.core.blocks.models import Block
        from speedy.core.messages.models import Message, ReadMark, Chat


        @only_on_sites_with_login
        class ChatListViewOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the chat list view, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates three active users and chats between them, with chat_1_2 created first and chat_3_1 last.
                test_visitor_has_no_access(self): Asserts a logged-out visitor is redirected to the login page.
                test_user_can_see_a_list_of_his_chats(self): Asserts a logged-in user sees his chats ordered from most to least recently active.
            """
            page_url = '/messages/'

            def set_up(self):
                """
                Creates three active users and chats between them, with chat_1_2 created first and chat_3_1 last.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.user_3 = ActiveUserFactory()
                sleep(0.01)
                self.chat_1_2 = ChatFactory(ent1=self.user_1, ent2=self.user_2)
                sleep(0.01)
                self.chat_2_3 = ChatFactory(ent1=self.user_2, ent2=self.user_3)
                sleep(0.01)
                self.chat_3_1 = ChatFactory(ent1=self.user_3, ent2=self.user_1)
                sleep(0.01)

            def test_visitor_has_no_access(self):
                """
                Asserts a logged-out visitor is redirected to the login page when accessing the chat list.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

            def test_user_can_see_a_list_of_his_chats(self):
                """
                Asserts a logged-in user gets the chats he participates in, ordered from most to least recently active.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertListEqual(list1=list(r.context['chat_list']), list2=[self.chat_3_1, self.chat_1_2])


        @only_on_sites_with_login
        class ChatDetailViewOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the chat detail view, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates three active users, chats between them, and three messages in chat_1_2.
                test_visitor_has_no_access(self): Asserts a logged-out visitor is redirected to the login page.
                test_user_can_read_a_chat_they_have_access_to(self): Asserts a user can read all messages of a chat he participates in.
                test_user_can_read_chat_with_a_blocker(self): Asserts a user can still read a chat even when the two users have blocked each other.
            """
            def set_up(self):
                """
                Creates three active users, chats between them, and three messages in chat_1_2.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.user_3 = ActiveUserFactory()
                self.chat_1_2 = ChatFactory(ent1=self.user_1, ent2=self.user_2)
                self.chat_2_3 = ChatFactory(ent1=self.user_2, ent2=self.user_3)
                self.chat_3_1 = ChatFactory(ent1=self.user_3, ent2=self.user_1)
                Message.objects.send_message(from_entity=self.user_1, chat=self.chat_1_2, text='My message')
                Message.objects.send_message(from_entity=self.user_2, chat=self.chat_1_2, text='First unread message')
                Message.objects.send_message(from_entity=self.user_2, chat=self.chat_1_2, text='Second unread message')
                self.page_url = '/messages/{}/'.format(self.chat_1_2.id)

            def test_visitor_has_no_access(self):
                """
                Asserts a logged-out visitor is redirected to the login page when accessing a chat.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

            def test_user_can_read_a_chat_they_have_access_to(self):
                """
                Asserts a user who participates in a chat can read it and gets all 3 of its messages.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                messages = r.context['message_list']
                self.assertEqual(first=len(messages), second=3)

            def test_user_can_read_chat_with_a_blocker(self):
                """
                Asserts a user can still read a chat with another user even after the two of them have blocked each other.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                Block.objects.block(blocker=self.user_2, blocked=self.user_1)
                Block.objects.block(blocker=self.user_1, blocked=self.user_2)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)


        @only_on_sites_with_login
        class ChatPollMessagesViewOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the chat poll messages view, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates two active users, a chat between them, and two messages with the "since" timestamp recorded between them.
                test_visitor_has_no_access(self): Asserts a logged-out visitor gets a forbidden response when polling a chat.
                test_user_gets_only_messages_newer_than_since(self): Asserts polling with the recorded "since" timestamp returns only the message sent after it.
                test_user_gets_no_messages_when_since_is_after_all_messages(self): Asserts polling with a "since" timestamp after all messages returns no messages.
                test_user_gets_all_messages_when_since_is_0(self): Asserts polling with since=0 returns all messages, newest first.
                test_user_cannot_poll_a_chat_they_have_no_access_to(self): Asserts a user who doesn't participate in the chat gets a not found response.
            """
            def set_up(self):
                """
                Creates two active users, a chat between them, and two messages with the "since" timestamp recorded between them.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.chat_1_2 = ChatFactory(ent1=self.user_1, ent2=self.user_2)
                self.message_1 = Message.objects.send_message(from_entity=self.user_1, chat=self.chat_1_2, text='First message')
                sleep(0.01)
                self.since = self.message_1.date_created.timestamp()
                sleep(0.01)
                self.message_2 = Message.objects.send_message(from_entity=self.user_2, chat=self.chat_1_2, text='Second message')
                self.page_url = '/messages/{}/poll/'.format(self.chat_1_2.id)

            def test_visitor_has_no_access(self):
                """
                Asserts a logged-out visitor gets a forbidden response when polling a chat.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url, data={'since': self.since})
                self.assertEqual(first=r.status_code, second=403)

            def test_user_gets_only_messages_newer_than_since(self):
                """
                Asserts polling with the recorded "since" timestamp returns only message_2, which was sent after it.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url, data={'since': self.since})
                self.assertEqual(first=r.status_code, second=200)
                messages = list(r.context['message_list'])
                self.assertListEqual(list1=messages, list2=[self.message_2])
                self.assertTrue(expr=r.context['ajax_view'])

            def test_user_gets_no_messages_when_since_is_after_all_messages(self):
                """
                Asserts polling with a "since" timestamp equal to the last message's creation time returns no messages.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                since = self.message_2.date_created.timestamp()
                r = self.client.get(path=self.page_url, data={'since': since})
                self.assertEqual(first=r.status_code, second=200)
                messages = list(r.context['message_list'])
                self.assertListEqual(list1=messages, list2=[])

            def test_user_gets_all_messages_when_since_is_0(self):
                """
                Asserts polling with since=0 returns all messages in the chat, ordered from newest to oldest.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url, data={'since': 0})
                self.assertEqual(first=r.status_code, second=200)
                messages = list(r.context['message_list'])
                self.assertListEqual(list1=messages, list2=[self.message_2, self.message_1])

            def test_user_cannot_poll_a_chat_they_have_no_access_to(self):
                """
                Asserts a user who is not a participant in the chat gets a not found response when polling it.
                """
                self.user_3 = ActiveUserFactory()
                self.client.login(username=self.user_3.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url, data={'since': self.since})
                self.assertEqual(first=r.status_code, second=404)


        @only_on_sites_with_login
        class SendMessageToChatViewOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the send message to chat view, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates three active users and chats between them, and prepares the message data to post.
                test_visitor_has_no_access(self): Asserts a logged-out visitor gets a forbidden response when posting a message.
                test_get_redirects_to_chat_page(self): Asserts a GET request to the send-message url redirects to the chat page.
                test_user_can_write_to_a_chat_they_have_access_to(self): Asserts a user who participates in a chat can post a message and is redirected to the chat page.
                test_cannot_write_to_other_user_if_blocked(self): Asserts a user who blocked the other user cannot post a message to their chat.
                test_cannot_write_to_other_user_if_blocking(self): Asserts a user who is blocked by the other user cannot post a message to their chat.
            """
            def set_up(self):
                """
                Creates three active users and chats between them, and prepares the message data to post.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.user_3 = ActiveUserFactory()
                self.chat_1_2 = ChatFactory(ent1=self.user_1, ent2=self.user_2)
                self.chat_2_3 = ChatFactory(ent1=self.user_2, ent2=self.user_3)
                self.chat_3_1 = ChatFactory(ent1=self.user_3, ent2=self.user_1)
                self.chat_url = '/messages/{}/'.format(self.chat_1_2.get_slug(current_user=self.user_1))
                self.page_url = '/messages/{}/send/'.format(self.chat_1_2.id)
                self.data = {
                    'text': 'Hi Hi Hi',
                }

            def test_visitor_has_no_access(self):
                """
                Asserts a logged-out visitor gets a forbidden response when posting a message to a chat.
                """
                self.client.logout()
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertEqual(first=r.status_code, second=403)

            def test_get_redirects_to_chat_page(self):
                """
                Asserts a GET request to the send-message url redirects to the chat page.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url=self.chat_url, status_code=302, target_status_code=200)

            def test_user_can_write_to_a_chat_they_have_access_to(self):
                """
                Asserts a user who participates in a chat can post a message to it and is redirected to the chat page.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertRedirects(response=r, expected_url=self.chat_url, status_code=302, target_status_code=200)

            def test_cannot_write_to_other_user_if_blocked(self):
                """
                Asserts a user who has blocked the other user gets a forbidden response when posting a message to their chat.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                Block.objects.block(blocker=self.user_1, blocked=self.user_2)
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertEqual(first=r.status_code, second=403)

            def test_cannot_write_to_other_user_if_blocking(self):
                """
                Asserts a user who is blocked by the other user gets a forbidden response when posting a message to their chat.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                Block.objects.block(blocker=self.user_2, blocked=self.user_1)
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertEqual(first=r.status_code, second=403)


        class SendMessageToUserViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreMessagesLanguageMixin, TestCaseMixin):
            """
            Mixin with tests for the compose-message-to-user view, reused by the per-language test cases below to validate behavior in all main languages.

            Methods:
                set_up(self): Creates two active users whose date_created is slightly in the past, and prepares the message data to post.
                test_visitor_has_no_access(self): Asserts a logged-out visitor is redirected to the login page on both GET and POST.
                test_user_cannot_send_message_to_self(self): Asserts a user gets a forbidden response when trying to compose a message to himself.
                test_user_can_see_a_form(self): Asserts a user composing a message to another user gets the message form template.
                test_user_gets_redirected_to_existing_chat(self): Asserts a user is redirected to the existing chat page if a chat with the other user already exists.
                test_user_can_submit_the_form_and_other_user_gets_notified_on_message_1(self): Asserts submitting the form creates a message and chat, redirects to the chat page, and sends a notification email to the recipient.
                test_user_can_submit_the_form_and_other_user_gets_notified_on_message_2(self): Asserts submitting the form with a very long (but valid) text still creates the message and sends a notification email.
                test_user_can_submit_the_form_and_other_user_doesnt_get_notified_on_message(self): Asserts no notification email is sent when the recipient has message notifications turned off.
                test_user_cannot_submit_the_form_with_text_too_long_1(self): Asserts submitting the form with text one character over the maximum length fails validation and creates no message.
                test_user_cannot_submit_the_form_with_text_too_long_2(self): Asserts submitting the form with a much longer invalid text fails validation and creates no message.
            """
            def set_up(self):
                """
                Creates two active users whose date_created is slightly in the past, and prepares the message data to post.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.user_1.date_created -= relativedelta(hours=0, minutes=10)  # relativedelta(hours=6, minutes=10)
                self.user_1.save_user_and_profile()
                self.user_2.date_created -= relativedelta(hours=0, minutes=10)  # relativedelta(hours=6, minutes=10)
                self.user_2.save_user_and_profile()
                self.page_url = '/messages/{}/compose/'.format(self.user_2.slug)
                self.data = {
                    'text': 'Hi Hi Hi',
                }

            def test_visitor_has_no_access(self):
                """
                Asserts a logged-out visitor is redirected to the login page on both GET and POST requests.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

            def test_user_cannot_send_message_to_self(self):
                """
                Asserts a user gets a forbidden response on both GET and POST when trying to compose a message to himself.
                """
                self.client.login(username=self.user_2.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=403)
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertEqual(first=r.status_code, second=403)

            def test_user_can_see_a_form(self):
                """
                Asserts a user composing a message to another user gets a 200 response with the message form template.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='messages/message_form.html')

            def test_user_gets_redirected_to_existing_chat(self):
                """
                Asserts a user composing a message to another user with whom a chat already exists is redirected to that chat's page.
                """
                chat = Chat.objects.chat_with(ent1=self.user_1, ent2=self.user_2)
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/messages/{}/'.format(self.user_2.slug), status_code=302, target_status_code=200)

            def test_user_can_submit_the_form_and_other_user_gets_notified_on_message_1(self):
                """
                Asserts submitting the compose form creates a message and private chat, redirects to the chat page, and sends one notification email to the recipient with the site-specific subject.
                """
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=2,
                    confirmed_email_address_count=2,
                    unconfirmed_email_address_count=0,
                )
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assert_user_email_addresses_count(
                    user=self.user_1,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.user_2 = User.objects.get(pk=self.user_2.pk)
                self.assert_user_email_addresses_count(
                    user=self.user_2,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assertEqual(first=len(mail.outbox), second=0)
                self.assertEqual(first=self.user_1.notify_on_message, second=User.NOTIFICATIONS_ON)
                self.assertEqual(first=self.user_2.notify_on_message, second=User.NOTIFICATIONS_ON)
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=Message.objects.count(), second=0)
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertEqual(first=Message.objects.count(), second=1)
                message = Message.objects.latest()
                chat = message.chat
                self.assertRedirects(response=r, expected_url='/messages/{}/'.format(chat.get_slug(current_user=self.user_1)), status_code=302, target_status_code=200)
                self.assertEqual(first=message.text, second='Hi Hi Hi')
                self.assertEqual(first=message.sender.id, second=self.user_1.id)
                self.assertEqual(first=chat.last_message, second=message)
                self.assertEqual(first=chat.ent1.id, second=self.user_1.id)
                self.assertEqual(first=chat.ent2.id, second=self.user_2.id)
                self.assertIs(expr1=chat.is_private, expr2=True)
                self.assertEqual(first=len(mail.outbox), second=1)
                self.assertEqual(first=mail.outbox[0].subject, second={
                    django_settings.SPEEDY_NET_SITE_ID: self._you_have_a_new_message_on_speedy_net_subject,
                    django_settings.SPEEDY_MATCH_SITE_ID: self._you_have_a_new_message_on_speedy_match_subject,
                }[self.site.id])

            def test_user_can_submit_the_form_and_other_user_gets_notified_on_message_2(self):
                """
                Asserts submitting the compose form with the maximum allowed length text (50000 characters) still creates the message and private chat, redirects to the chat page, and sends one notification email to the recipient.
                """
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=2,
                    confirmed_email_address_count=2,
                    unconfirmed_email_address_count=0,
                )
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assert_user_email_addresses_count(
                    user=self.user_1,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.user_2 = User.objects.get(pk=self.user_2.pk)
                self.assert_user_email_addresses_count(
                    user=self.user_2,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assertEqual(first=len(mail.outbox), second=0)
                self.assertEqual(first=self.user_1.notify_on_message, second=User.NOTIFICATIONS_ON)
                self.assertEqual(first=self.user_2.notify_on_message, second=User.NOTIFICATIONS_ON)
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=Message.objects.count(), second=0)
                data = self.data.copy()
                data['text'] = "a" * 50000
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=Message.objects.count(), second=1)
                message = Message.objects.latest()
                chat = message.chat
                self.assertRedirects(response=r, expected_url='/messages/{}/'.format(chat.get_slug(current_user=self.user_1)), status_code=302, target_status_code=200)
                self.assertEqual(first=message.text, second="a" * 50000)
                self.assertEqual(first=message.sender.id, second=self.user_1.id)
                self.assertEqual(first=chat.last_message, second=message)
                self.assertEqual(first=chat.ent1.id, second=self.user_1.id)
                self.assertEqual(first=chat.ent2.id, second=self.user_2.id)
                self.assertIs(expr1=chat.is_private, expr2=True)
                self.assertEqual(first=len(mail.outbox), second=1)
                self.assertEqual(first=mail.outbox[0].subject, second={
                    django_settings.SPEEDY_NET_SITE_ID: self._you_have_a_new_message_on_speedy_net_subject,
                    django_settings.SPEEDY_MATCH_SITE_ID: self._you_have_a_new_message_on_speedy_match_subject,
                }[self.site.id])

            def test_user_can_submit_the_form_and_other_user_doesnt_get_notified_on_message(self):
                """
                Asserts submitting the compose form creates the message and private chat but sends no notification email when the recipient has message notifications turned off.
                """
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=2,
                    confirmed_email_address_count=2,
                    unconfirmed_email_address_count=0,
                )
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assert_user_email_addresses_count(
                    user=self.user_1,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.user_2 = User.objects.get(pk=self.user_2.pk)
                self.assert_user_email_addresses_count(
                    user=self.user_2,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assertEqual(first=len(mail.outbox), second=0)
                self.user_2.notify_on_message = User.NOTIFICATIONS_OFF
                self.user_2.save_user_and_profile()
                self.assertEqual(first=self.user_1.notify_on_message, second=User.NOTIFICATIONS_ON)
                self.assertEqual(first=self.user_2.notify_on_message, second=User.NOTIFICATIONS_OFF)
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=Message.objects.count(), second=0)
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertEqual(first=Message.objects.count(), second=1)
                message = Message.objects.latest()
                chat = message.chat
                self.assertRedirects(response=r, expected_url='/messages/{}/'.format(chat.get_slug(current_user=self.user_1)), status_code=302, target_status_code=200)
                self.assertEqual(first=message.text, second='Hi Hi Hi')
                self.assertEqual(first=message.sender.id, second=self.user_1.id)
                self.assertEqual(first=chat.last_message, second=message)
                self.assertEqual(first=chat.ent1.id, second=self.user_1.id)
                self.assertEqual(first=chat.ent2.id, second=self.user_2.id)
                self.assertIs(expr1=chat.is_private, expr2=True)
                self.assertEqual(first=len(mail.outbox), second=0)

            def test_user_cannot_submit_the_form_with_text_too_long_1(self):
                """
                Asserts submitting the compose form with text of 50001 characters (one over the maximum) fails validation with the expected form error and creates no message.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=Message.objects.count(), second=0)
                data = self.data.copy()
                data['text'] = "a" * 50001
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._ensure_this_value_has_at_most_max_length_characters_errors_dict_by_value_length(value_length=50001))
                self.assertEqual(first=Message.objects.count(), second=0)

            def test_user_cannot_submit_the_form_with_text_too_long_2(self):
                """
                Asserts submitting the compose form with text of 1,000,000 characters fails validation with the expected form error and creates no message.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=Message.objects.count(), second=0)
                data = self.data.copy()
                data['text'] = "b" * 1000000
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._ensure_this_value_has_at_most_max_length_characters_errors_dict_by_value_length(value_length=1000000))
                self.assertEqual(first=Message.objects.count(), second=0)


        @only_on_sites_with_login
        class SendMessageToUserViewAllMainLanguagesEnglishTestCase(SendMessageToUserViewTestCaseMixin, SiteTestCase):
            """
            Runs SendMessageToUserViewTestCaseMixin's tests in English, the default language.

            Methods:
                validate_all_values(self): Asserts the active language code is 'en'.
            """
            def validate_all_values(self):
                """
                Asserts the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class SendMessageToUserViewAllMainLanguagesFrenchTestCase(SendMessageToUserViewTestCaseMixin, SiteTestCase):
            """
            Runs SendMessageToUserViewTestCaseMixin's tests in French.

            Methods:
                validate_all_values(self): Asserts the active language code is 'fr'.
            """
            def validate_all_values(self):
                """
                Asserts the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class SendMessageToUserViewAllMainLanguagesGermanTestCase(SendMessageToUserViewTestCaseMixin, SiteTestCase):
            """
            Runs SendMessageToUserViewTestCaseMixin's tests in German.

            Methods:
                validate_all_values(self): Asserts the active language code is 'de'.
            """
            def validate_all_values(self):
                """
                Asserts the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class SendMessageToUserViewAllMainLanguagesSpanishTestCase(SendMessageToUserViewTestCaseMixin, SiteTestCase):
            """
            Runs SendMessageToUserViewTestCaseMixin's tests in Spanish.

            Methods:
                validate_all_values(self): Asserts the active language code is 'es'.
            """
            def validate_all_values(self):
                """
                Asserts the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class SendMessageToUserViewAllMainLanguagesPortugueseTestCase(SendMessageToUserViewTestCaseMixin, SiteTestCase):
            """
            Runs SendMessageToUserViewTestCaseMixin's tests in Portuguese.

            Methods:
                validate_all_values(self): Asserts the active language code is 'pt'.
            """
            def validate_all_values(self):
                """
                Asserts the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class SendMessageToUserViewAllMainLanguagesItalianTestCase(SendMessageToUserViewTestCaseMixin, SiteTestCase):
            """
            Runs SendMessageToUserViewTestCaseMixin's tests in Italian.

            Methods:
                validate_all_values(self): Asserts the active language code is 'it'.
            """
            def validate_all_values(self):
                """
                Asserts the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class SendMessageToUserViewAllMainLanguagesDutchTestCase(SendMessageToUserViewTestCaseMixin, SiteTestCase):
            """
            Runs SendMessageToUserViewTestCaseMixin's tests in Dutch.

            Methods:
                validate_all_values(self): Asserts the active language code is 'nl'.
            """
            def validate_all_values(self):
                """
                Asserts the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class SendMessageToUserViewAllMainLanguagesHebrewTestCase(SendMessageToUserViewTestCaseMixin, SiteTestCase):
            """
            Runs SendMessageToUserViewTestCaseMixin's tests in Hebrew.

            Methods:
                validate_all_values(self): Asserts the active language code is 'he'.
            """
            def validate_all_values(self):
                """
                Asserts the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        class MarkChatAsReadViewOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the mark-chat-as-read view, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates an active user, a chat with two messages, and the chat/mark-read urls.
                test_visitor_has_no_access(self): Asserts a logged-out visitor is redirected to the login page.
                test_user_can_mark_chat_as_read(self): Asserts posting to the mark-read url updates the user's read mark to after the last message and redirects to the chat page.
            """
            def set_up(self):
                """
                Creates an active user, a chat with two messages, and the chat/mark-read urls.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.chat = ChatFactory(ent1=self.user_1)
                self.messages = []
                self.messages.append(Message.objects.send_message(from_entity=self.chat.ent1, chat=self.chat, text='text'))
                sleep(0.1)
                self.messages.append(Message.objects.send_message(from_entity=self.chat.ent2, chat=self.chat, text='text'))
                sleep(0.1)
                self.chat_url = '/messages/{}/'.format(self.chat.get_slug(current_user=self.user_1))
                self.page_url = '/messages/{}/mark-read/'.format(self.chat.id)

            def test_visitor_has_no_access(self):
                """
                Asserts a logged-out visitor is redirected to the login page when marking a chat as read.
                """
                self.client.logout()
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

            def test_user_can_mark_chat_as_read(self):
                """
                Asserts posting to the mark-read url updates the user's read mark to after the last message's creation time and redirects to the chat page.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                self.assertLess(a=ReadMark.objects.get(entity_id=self.user_1.id).date_updated, b=self.messages[1].date_created)
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url=self.chat_url, status_code=302, target_status_code=200)
                self.assertGreater(a=ReadMark.objects.get(entity_id=self.user_1.id).date_updated, b=self.messages[1].date_created)


