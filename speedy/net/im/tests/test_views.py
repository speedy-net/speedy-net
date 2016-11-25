from speedy.core.test import TestCase

from speedy.net.accounts.tests.test_factories import UserFactory
from ..models import Message, ReadMark, Chat
from .test_factories import ChatFactory


class ChatListViewTestCase(TestCase):
    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()
        self.chat_1_2 = ChatFactory(ent1=self.user1, ent2=self.user2)
        self.chat_2_3 = ChatFactory(ent1=self.user2, ent2=self.user3)
        self.chat_3_1 = ChatFactory(ent1=self.user3, ent2=self.user1)
        self.page_url = '/{}/messages/'.format(self.user1.slug)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_can_see_a_list_of_his_chats(self):
        self.client.login(username=self.user1.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertEqual(r.status_code, 200)
        self.assertListEqual(list(r.context['chat_list']), [self.chat_3_1, self.chat_1_2])

    def test_user_cannot_see_a_list_of_chats_of_other_user(self):
        self.client.login(username=self.user2.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))


class ChatDetailViewTestCase(TestCase):
    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()
        self.chat_1_2 = ChatFactory(ent1=self.user1, ent2=self.user2)
        self.chat_2_3 = ChatFactory(ent1=self.user2, ent2=self.user3)
        self.chat_3_1 = ChatFactory(ent1=self.user3, ent2=self.user1)
        Message.objects.send_message(from_entity=self.user1, chat=self.chat_1_2, text='My message')
        Message.objects.send_message(from_entity=self.user2, chat=self.chat_1_2, text='First unread message')
        Message.objects.send_message(from_entity=self.user2, chat=self.chat_1_2, text='Second unread message')
        self.page_url = '/{}/messages/{}/'.format(self.user1.slug, self.chat_1_2.id)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_can_read_a_chat_he_has_access_to(self):
        self.client.login(username=self.user1.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertEqual(r.status_code, 200)
        messages = r.context['message_list']
        self.assertEqual(len(messages), 3)

    def test_user_cannot_read_a_chat_he_has_not_access_to(self):
        self.client.login(username=self.user3.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_cannot_read_a_chat_he_has_access_to_but_he_logged_in_as_another_user(self):
        self.client.login(username=self.user2.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))


class SendMessageToChatViewTestCase(TestCase):
    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()
        self.chat_1_2 = ChatFactory(ent1=self.user1, ent2=self.user2)
        self.chat_2_3 = ChatFactory(ent1=self.user2, ent2=self.user3)
        self.chat_3_1 = ChatFactory(ent1=self.user3, ent2=self.user1)
        self.chat_url = '/{}/messages/{}/'.format(self.user1.slug, self.chat_1_2.id)
        self.page_url = '/{}/messages/{}/send/'.format(self.user1.slug, self.chat_1_2.id)
        self.data = {
            'text': 'Hi Hi Hi',
        }

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.page_url, self.data)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_get_redirects_to_chat_page(self):
        self.client.login(username=self.user1.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertRedirects(r, self.chat_url)

    def test_user_can_write_to_a_chat_he_has_access_to(self):
        self.client.login(username=self.user1.slug, password='111')
        r = self.client.post(self.page_url, self.data)
        self.assertRedirects(r, self.chat_url)

    def test_user_cannot_write_to_a_chat_he_has_not_access_to(self):
        self.client.login(username=self.user3.slug, password='111')
        r = self.client.post(self.page_url, self.data)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_cannot_write_to_a_chat_he_has_access_to_but_he_logged_in_as_another_user(self):
        self.client.login(username=self.user2.slug, password='111')
        r = self.client.post(self.page_url, self.data)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))


class SendMessageToUserViewTestCase(TestCase):
    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.page_url = '/{}/messages/compose/'.format(self.user2.slug)
        self.data = {
            'text': 'Hi Hi Hi',
        }

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))
        r = self.client.post(self.page_url, self.data)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_cannot_send_message_to_self(self):
        self.client.login(username=self.user2.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))
        r = self.client.post(self.page_url, self.data)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_can_see_a_form(self):
        self.client.login(username=self.user1.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'im/message_form.html')

    def test_user_gets_redirected_to_existing_chat(self):
        chat = Chat.on_site.chat_with(self.user1, self.user2)
        self.client.login(username=self.user1.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/{}/messages/{}/'.format(self.user1.slug, chat.id))

    def test_user_can_submit_the_form(self):
        self.client.login(username=self.user1.slug, password='111')
        self.assertEqual(Message.objects.count(), 0)
        r = self.client.post(self.page_url, self.data)
        self.assertEqual(Message.objects.count(), 1)
        message = Message.objects.latest()
        chat = message.chat
        self.assertRedirects(r, '/{}/messages/{}/'.format(self.user1.slug, chat.id))
        self.assertEqual(message.text, 'Hi Hi Hi')
        self.assertEqual(message.sender.id, self.user1.id)
        self.assertEqual(chat.last_message, message)
        self.assertEqual(chat.ent1.id, self.user1.id)
        self.assertEqual(chat.ent2.id, self.user2.id)
        self.assertTrue(chat.is_private)


class MarkChatAsReadViewTestCase(TestCase):
    def setUp(self):
        self.user1 = UserFactory()
        self.chat = ChatFactory(ent1=self.user1)
        self.messages = []
        self.messages.append(Message.objects.send_message(from_entity=self.chat.ent1, chat=self.chat, text='text'))
        self.messages.append(Message.objects.send_message(from_entity=self.chat.ent2, chat=self.chat, text='text'))
        self.chat_url = '/{}/messages/{}/'.format(self.user1.slug, self.chat.id)
        self.page_url = '/{}/messages/{}/mark-read/'.format(self.user1.slug, self.chat.id)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_can_mark_chat_as_read(self):
        # ~~~~ TODO: this test fails locally sometimes.
        self.client.login(username=self.user1.slug, password='111')
        self.assertLess(ReadMark.objects.get(entity_id=self.user1.id).date_updated, self.messages[1].date_created)
        r = self.client.post(self.page_url)
        self.assertRedirects(r, self.chat_url)
        self.assertGreater(ReadMark.objects.get(entity_id=self.user1.id).date_updated, self.messages[1].date_created)
