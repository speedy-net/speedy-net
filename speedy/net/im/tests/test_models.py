from speedy.core.test import TestCase

from speedy.net.accounts.tests.test_factories import UserFactory
from .test_factories import ChatFactory


class ChatTestCase(TestCase):
    def test_id_length(self):
        chat = ChatFactory()
        self.assertEqual(len(chat.id), 15)

    def test_str(self):
        chat = ChatFactory(ent1=UserFactory(first_name='Walter', last_name='White'),
                           ent2=UserFactory(first_name='Jesse', last_name='Pinkman'))
        self.assertEqual(str(chat), 'Walter White, Jesse Pinkman')
