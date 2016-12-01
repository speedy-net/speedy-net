from speedy.core.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software

from speedy.net.accounts.tests.test_factories import UserFactory
from ..forms import MessageForm
from .test_factories import ChatFactory


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class MessageFormTestCase(TestCase):
    def test_form_to_chat_save(self):
        user = UserFactory()
        chat = ChatFactory(ent1=user)
        form = MessageForm(from_entity=user, chat=chat, data={'text': 'Hi!'})
        self.assertTrue(form.is_valid())
        message = form.save()
        self.assertEqual(message.chat, chat)
        self.assertEqual(message.sender.user, user)
        self.assertEqual(message.text, 'Hi!')
        chat = message.chat
        self.assertEqual(chat.last_message, message)
