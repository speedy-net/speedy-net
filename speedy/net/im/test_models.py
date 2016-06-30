from django.test import TestCase

from speedy.net.accounts.test_factories import UserFactory
from .test_factories import ChatFactory


class ChatTestCase(TestCase):
    def test_str(self):
        chat = ChatFactory(participants=[UserFactory(first_name='Walter', last_name='White'),
                                         UserFactory(first_name='Jesse', last_name='Pinkman')])
        self.assertEqual(str(chat), 'Jesse Pinkman, Walter White')

