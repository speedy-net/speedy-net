from speedy.core.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software

from speedy.net.accounts.tests.test_factories import UserFactory
from .test_factories import ChatFactory


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class ChatTestCase(TestCase):
    def test_id_length(self):
        chat = ChatFactory()
        self.assertEqual(first=len(chat.id), second=20)

    def test_str(self):
        chat = ChatFactory(ent1=UserFactory(first_name='Walter', last_name='White'),
                           ent2=UserFactory(first_name='Jesse', last_name='Pinkman'))
        self.assertEqual(first=str(chat), second='Walter White, Jesse Pinkman')
