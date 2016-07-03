from django.test import TestCase

from speedy.net.accounts.test_factories import UserFactory
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
