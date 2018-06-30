from time import sleep

from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software
from speedy.core.blocks.models import Block
from .test_factories import ChatFactory
from ..models import Message, ReadMark, Chat


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class ChatListViewTestCase(TestCase):
    def setUp(self):
        self.user1 = ActiveUserFactory()
        self.user2 = ActiveUserFactory()
        self.user3 = ActiveUserFactory()
        self.chat_1_2 = ChatFactory(ent1=self.user1, ent2=self.user2)
        self.chat_2_3 = ChatFactory(ent1=self.user2, ent2=self.user3)
        self.chat_3_1 = ChatFactory(ent1=self.user3, ent2=self.user1)
        self.page_url = '/messages/'

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_can_see_a_list_of_his_chats(self):
        self.client.login(username=self.user1.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertListEqual(list1=list(r.context['chat_list']), list2=[self.chat_3_1, self.chat_1_2])


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class ChatDetailViewTestCase(TestCase):
    def setUp(self):
        self.user1 = ActiveUserFactory()
        self.user2 = ActiveUserFactory()
        self.user3 = ActiveUserFactory()
        self.chat_1_2 = ChatFactory(ent1=self.user1, ent2=self.user2)
        self.chat_2_3 = ChatFactory(ent1=self.user2, ent2=self.user3)
        self.chat_3_1 = ChatFactory(ent1=self.user3, ent2=self.user1)
        Message.objects.send_message(from_entity=self.user1, chat=self.chat_1_2, text='My message')
        Message.objects.send_message(from_entity=self.user2, chat=self.chat_1_2, text='First unread message')
        Message.objects.send_message(from_entity=self.user2, chat=self.chat_1_2, text='Second unread message')
        self.page_url = '/messages/{}/'.format(self.chat_1_2.id)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_can_read_a_chat_he_has_access_to(self):
        self.client.login(username=self.user1.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        messages = r.context['message_list']
        self.assertEqual(first=len(messages), second=3)

    def test_user_can_read_chat_with_a_blocker(self):
        self.client.login(username=self.user1.slug, password='111')
        Block.objects.block(blocker=self.user2, blocked=self.user1)
        Block.objects.block(blocker=self.user1, blocked=self.user2)
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class SendMessageToChatViewTestCase(TestCase):
    def setUp(self):
        self.user1 = ActiveUserFactory()
        self.user2 = ActiveUserFactory()
        self.user3 = ActiveUserFactory()
        self.chat_1_2 = ChatFactory(ent1=self.user1, ent2=self.user2)
        self.chat_2_3 = ChatFactory(ent1=self.user2, ent2=self.user3)
        self.chat_3_1 = ChatFactory(ent1=self.user3, ent2=self.user1)
        self.chat_url = '/messages/{}/'.format(self.chat_1_2.get_slug(current_user=self.user1))
        self.page_url = '/messages/{}/send/'.format(self.chat_1_2.id)
        self.data = {
            'text': 'Hi Hi Hi',
        }

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.page_url, self.data)
        self.assertEqual(first=r.status_code, second=403)

    def test_get_redirects_to_chat_page(self):
        self.client.login(username=self.user1.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url=self.chat_url)

    def test_user_can_write_to_a_chat_he_has_access_to(self):
        self.client.login(username=self.user1.slug, password='111')
        r = self.client.post(self.page_url, self.data)
        self.assertRedirects(response=r, expected_url=self.chat_url)

    def test_cannot_write_to_a_blocker(self):
        self.client.login(username=self.user1.slug, password='111')
        Block.objects.block(blocker=self.user2, blocked=self.user1)
        r = self.client.post(self.page_url, self.data)
        self.assertEqual(first=r.status_code, second=403)

    def test_cannot_write_to_a_blocked(self):
        self.client.login(username=self.user1.slug, password='111')
        Block.objects.block(blocker=self.user1, blocked=self.user2)
        r = self.client.post(self.page_url, self.data)
        self.assertEqual(first=r.status_code, second=403)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class SendMessageToUserViewTestCase(TestCase):
    def setUp(self):
        self.user1 = ActiveUserFactory()
        self.user2 = ActiveUserFactory()
        self.page_url = '/messages/{}/compose/'.format(self.user2.slug)
        self.data = {
            'text': 'Hi Hi Hi',
        }

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))
        r = self.client.post(self.page_url, self.data)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_cannot_send_message_to_self(self):
        self.client.login(username=self.user2.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))
        r = self.client.post(self.page_url, self.data)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_can_see_a_form(self):
        self.client.login(username=self.user1.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='im/message_form.html')

    def test_user_gets_redirected_to_existing_chat(self):
        chat = Chat.on_site.chat_with(self.user1, self.user2)
        self.client.login(username=self.user1.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/messages/{}/'.format(self.user2.slug))

    def test_user_can_submit_the_form(self):
        self.client.login(username=self.user1.slug, password='111')
        self.assertEqual(first=Message.objects.count(), second=0)
        r = self.client.post(self.page_url, self.data)
        self.assertEqual(first=Message.objects.count(), second=1)
        message = Message.objects.latest()
        chat = message.chat
        self.assertRedirects(response=r, expected_url='/messages/{}/'.format(chat.get_slug(current_user=self.user1)))
        self.assertEqual(first=message.text, second='Hi Hi Hi')
        self.assertEqual(first=message.sender.id, second=self.user1.id)
        self.assertEqual(first=chat.last_message, second=message)
        self.assertEqual(first=chat.ent1.id, second=self.user1.id)
        self.assertEqual(first=chat.ent2.id, second=self.user2.id)
        self.assertTrue(expr=chat.is_private)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class MarkChatAsReadViewTestCase(TestCase):
    def setUp(self):
        self.user1 = ActiveUserFactory()
        self.chat = ChatFactory(ent1=self.user1)
        self.messages = []
        self.messages.append(Message.objects.send_message(from_entity=self.chat.ent1, chat=self.chat, text='text'))
        sleep(0.1)
        self.messages.append(Message.objects.send_message(from_entity=self.chat.ent2, chat=self.chat, text='text'))
        sleep(0.1)
        self.chat_url = '/messages/{}/'.format(self.chat.get_slug(current_user=self.user1))
        self.page_url = '/messages/{}/mark-read/'.format(self.chat.id)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_can_mark_chat_as_read(self):
        # ~~~~ TODO: this test fails locally sometimes.
        self.client.login(username=self.user1.slug, password='111')
        self.assertLess(a=ReadMark.objects.get(entity_id=self.user1.id).date_updated, b=self.messages[1].date_created)
        r = self.client.post(self.page_url)
        self.assertRedirects(response=r, expected_url=self.chat_url)
        self.assertGreater(a=ReadMark.objects.get(entity_id=self.user1.id).date_updated, b=self.messages[1].date_created)
