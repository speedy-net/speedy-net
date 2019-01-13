from django.conf import settings as django_settings

from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_sites_with_login
from speedy.core.blocks.models import Block

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.tests.test_factories import ActiveUserFactory
    from speedy.core.im.tests.test_factories import ChatFactory


@only_on_sites_with_login
class SendMessageTestCase(SiteTestCase):
    def set_up(self):
        super().set_up()
        self.user1 = ActiveUserFactory()
        self.user2 = ActiveUserFactory()

    def test_cannot_send_message_to_self(self):
        self.assertFalse(expr=self.user1.has_perm(perm='im.send_message', obj=self.user1))

    def test_can_send_message_to_other_user(self):
        self.assertTrue(expr=self.user1.has_perm(perm='im.send_message', obj=self.user2))

    def test_cannot_send_message_to_other_user_if_blocked(self):
        Block.objects.block(blocker=self.user2, blocked=self.user1)
        self.assertFalse(expr=self.user1.has_perm(perm='im.send_message', obj=self.user2))
        self.assertFalse(expr=self.user2.has_perm(perm='im.send_message', obj=self.user1))


@only_on_sites_with_login
class ViewChatsTestCase(SiteTestCase):
    def set_up(self):
        super().set_up()
        self.user1 = ActiveUserFactory()
        self.user2 = ActiveUserFactory()

    def test_can_see_his_chats(self):
        self.assertTrue(expr=self.user1.has_perm(perm='im.view_chats', obj=self.user1))

    def test_cannot_see_other_user_chats(self):
        self.assertFalse(expr=self.user1.has_perm(perm='im.view_chats', obj=self.user2))


@only_on_sites_with_login
class ReadChatTestCase(SiteTestCase):
    def set_up(self):
        super().set_up()
        self.user1 = ActiveUserFactory()
        self.user2 = ActiveUserFactory()
        self.user3 = ActiveUserFactory()
        self.chat_1_2 = ChatFactory(ent1=self.user1, ent2=self.user2)
        self.chat_1_3 = ChatFactory(ent1=self.user1, ent2=self.user3)

    def test_can_read_his_chat(self):
        self.assertTrue(expr=self.user2.has_perm(perm='im.read_chat', obj=self.chat_1_2))

    def test_cannot_read_a_chat_user_is_not_participate_in(self):
        self.assertFalse(expr=self.user2.has_perm(perm='im.read_chat', obj=self.chat_1_3))


