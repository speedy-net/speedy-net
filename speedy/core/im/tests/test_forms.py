from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software
from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from .test_factories import ChatFactory
from ..forms import MessageForm


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class MessageFormTestCase(TestCase):
    def test_form_to_chat_save(self):
        user = ActiveUserFactory()
        chat = ChatFactory(ent1=user)
        form = MessageForm(from_entity=user, chat=chat, data={'text': 'Hi!'})
        self.assertTrue(expr=form.is_valid())
        message = form.save()
        self.assertEqual(first=message.chat, second=chat)
        self.assertEqual(first=message.sender.user, second=user)
        self.assertEqual(first=message.text, second='Hi!')
        chat = message.chat
        self.assertEqual(first=chat.last_message, second=message)


