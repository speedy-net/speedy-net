from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_sites_with_login
    from speedy.core.im.forms import MessageForm

    from speedy.core.accounts.test.user_factories import ActiveUserFactory
    from speedy.core.im.test.factories import ChatFactory


    @only_on_sites_with_login
    class MessageFormTestCase(SiteTestCase):
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


