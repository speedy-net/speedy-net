from speedy.core.base.test import TestCase, only_on_sites_with_login
from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from .test_factories import ChatFactory
from ..forms import MessageForm


@only_on_sites_with_login
class MessageFormTestCase(TestCase):
    def test_form_to_chat_save(self):
        data = {
            'text': 'Hi!',
        }
        user = ActiveUserFactory()
        chat = ChatFactory(ent1=user)
        form = MessageForm(from_entity=user, chat=chat, data=data)
        self.assertTrue(expr=form.is_valid())
        message = form.save()
        self.assertEqual(first=message.chat, second=chat)
        self.assertEqual(first=message.sender.user, second=user)
        self.assertEqual(first=message.text, second='Hi!')
        chat = message.chat
        self.assertEqual(first=chat.last_message, second=message)


