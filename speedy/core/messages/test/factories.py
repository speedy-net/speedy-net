import factory
from django.conf import settings as django_settings

from speedy.core.messages.models import Chat

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.test.user_factories import ActiveUserFactory


if (django_settings.LOGIN_ENABLED):

    class ChatFactory(factory.django.DjangoModelFactory):
        ent1 = factory.SubFactory(ActiveUserFactory)
        ent2 = factory.SubFactory(ActiveUserFactory)

        class Meta:
            model = Chat

        @factory.post_generation
        def group(self, created, extracted, **kwargs):
            if (extracted is not None):
                self.is_group = True
                for entity in extracted:
                    self.group.add(entity)


