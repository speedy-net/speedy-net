from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login

        from speedy.core.accounts.test.user_factories import ActiveUserFactory
        from speedy.core.messages.test.factories import ChatFactory

        from speedy.core.messages.forms import MessageForm


        @only_on_sites_with_login
        class MessageFormOnlyEnglishTestCase(SiteTestCase):
            def test_form_to_chat_save(self):
                data = {
                    'text': 'Hi!',
                }
                user = ActiveUserFactory()
                chat = ChatFactory(ent1=user)
                form = MessageForm(from_entity=user, chat=chat, data=data)
                self.assertIs(expr1=form.is_valid(), expr2=True)
                message = form.save()
                self.assertEqual(first=message.chat, second=chat)
                self.assertEqual(first=message.sender.user, second=user)
                self.assertEqual(first=message.text, second='Hi!')
                chat = message.chat
                self.assertEqual(first=chat.last_message, second=message)


