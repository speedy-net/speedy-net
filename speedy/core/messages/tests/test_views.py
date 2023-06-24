from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from time import sleep

        from django.test import override_settings
        from django.core import mail

        from speedy.core.base.test import tests_settings
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
        class ChatListViewTestCase(SiteTestCase):
            page_url = '/messages/'

            def set_up(self):
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
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

            def test_user_can_see_a_list_of_his_chats(self):
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertListEqual(list1=list(r.context['chat_list']), list2=[self.chat_3_1, self.chat_1_2])


        @only_on_sites_with_login
        class ChatDetailViewTestCase(SiteTestCase):
            def set_up(self):
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
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

            def test_user_can_read_a_chat_they_have_access_to(self):
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                messages = r.context['message_list']
                self.assertEqual(first=len(messages), second=3)

            def test_user_can_read_chat_with_a_blocker(self):
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                Block.objects.block(blocker=self.user_2, blocked=self.user_1)
                Block.objects.block(blocker=self.user_1, blocked=self.user_2)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)


        @only_on_sites_with_login
        class SendMessageToChatViewTestCase(SiteTestCase):
            def set_up(self):
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
                self.client.logout()
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertEqual(first=r.status_code, second=403)

            def test_get_redirects_to_chat_page(self):
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url=self.chat_url, status_code=302, target_status_code=200)

            def test_user_can_write_to_a_chat_they_have_access_to(self):
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertRedirects(response=r, expected_url=self.chat_url, status_code=302, target_status_code=200)

            def test_cannot_write_to_other_user_if_blocked(self):
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                Block.objects.block(blocker=self.user_1, blocked=self.user_2)
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertEqual(first=r.status_code, second=403)

            def test_cannot_write_to_other_user_if_blocking(self):
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                Block.objects.block(blocker=self.user_2, blocked=self.user_1)
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertEqual(first=r.status_code, second=403)


        class SendMessageToUserViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyCoreMessagesLanguageMixin):
            def set_up(self):
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.page_url = '/messages/{}/compose/'.format(self.user_2.slug)
                self.data = {
                    'text': 'Hi Hi Hi',
                }

            def test_visitor_has_no_access(self):
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

            def test_user_cannot_send_message_to_self(self):
                self.client.login(username=self.user_2.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=403)
                r = self.client.post(path=self.page_url, data=self.data)
                self.assertEqual(first=r.status_code, second=403)

            def test_user_can_see_a_form(self):
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='messages/message_form.html')

            def test_user_gets_redirected_to_existing_chat(self):
                chat = Chat.objects.chat_with(ent1=self.user_1, ent2=self.user_2)
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/messages/{}/'.format(self.user_2.slug), status_code=302, target_status_code=200)

            def test_user_can_submit_the_form_and_other_user_gets_notified_on_message_1(self):
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
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=Message.objects.count(), second=0)
                data = self.data.copy()
                data['text'] = "a" * 50001
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._ensure_this_value_has_at_most_max_length_characters_errors_dict_by_value_length(value_length=50001))
                self.assertEqual(first=Message.objects.count(), second=0)

            def test_user_cannot_submit_the_form_with_text_too_long_2(self):
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=Message.objects.count(), second=0)
                data = self.data.copy()
                data['text'] = "b" * 1000000
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._ensure_this_value_has_at_most_max_length_characters_errors_dict_by_value_length(value_length=1000000))
                self.assertEqual(first=Message.objects.count(), second=0)


        @only_on_sites_with_login
        class SendMessageToUserViewEnglishTestCase(SendMessageToUserViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class SendMessageToUserViewFrenchTestCase(SendMessageToUserViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class SendMessageToUserViewHebrewTestCase(SendMessageToUserViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        class MarkChatAsReadViewTestCase(SiteTestCase):
            def set_up(self):
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
                self.client.logout()
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

            def test_user_can_mark_chat_as_read(self):
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                self.assertLess(a=ReadMark.objects.get(entity_id=self.user_1.id).date_updated, b=self.messages[1].date_created)
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url=self.chat_url, status_code=302, target_status_code=200)
                self.assertGreater(a=ReadMark.objects.get(entity_id=self.user_1.id).date_updated, b=self.messages[1].date_created)


