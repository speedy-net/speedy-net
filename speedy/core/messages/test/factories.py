from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from typing import TYPE_CHECKING

        import factory

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.messages.models import Chat

        ChatTypeHintMixin = object
        if (TYPE_CHECKING):
            ChatTypeHintMixin = Chat


        class ChatFactory(factory.django.DjangoModelFactory, ChatTypeHintMixin):
            ent1 = factory.SubFactory(ActiveUserFactory)
            ent2 = factory.SubFactory(ActiveUserFactory)

            class Meta:
                model = Chat
                skip_postgeneration_save = True  # Avoid warning in factory-boy>=3.3,<4.0

            @factory.post_generation
            def group(self: Chat, created, extracted, **kwargs):
                if (extracted is not None):
                    assert (self.is_group is True)
                    for entity in extracted:
                        self.group.add(entity)

            @classmethod
            def group_chat_with(cls, group):
                return cls(ent1=None, ent2=None, is_group=True, group=group)


