"""
Test factories for the messages app of Speedy Core, including the ChatFactory.
"""
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
            """
            Factory for creating Chat instances for tests, defaulting to a private chat between two new active users.

            Methods:
                group(self, created, extracted, **kwargs): Post-generation hook that adds the given entities as group chat participants.
                group_chat_with(cls, group): Creates a new group chat with the given group of entities.
            """
            ent1 = factory.SubFactory(ActiveUserFactory)
            ent2 = factory.SubFactory(ActiveUserFactory)

            class Meta:
                model = Chat
                skip_postgeneration_save = True  # Avoid warning in factory-boy>=3.3,<4.0

            @factory.post_generation
            def group(self: Chat, created, extracted, **kwargs):
                """
                Post-generation hook that, when a group of entities is passed as the 'group' factory parameter, adds them as participants of this (already created) group chat.

                :param created: Whether the chat instance was created.
                :type created: bool
                :param extracted: The iterable of entities to add to the group chat, or None if not provided.
                :type extracted: iterable of speedy.core.accounts.models.Entity or None
                :param kwargs: Additional keyword arguments.
                """
                if (extracted is not None):
                    assert (self.is_group is True)
                    for entity in extracted:
                        self.group.add(entity)

            @classmethod
            def group_chat_with(cls, group):
                """
                Creates a new group chat with the given entities as participants.

                :param group: The entities to add as participants of the group chat.
                :type group: iterable of speedy.core.accounts.models.Entity
                :return: The newly created group chat.
                :rtype: speedy.core.messages.models.Chat
                """
                return cls(ent1=None, ent2=None, is_group=True, group=group)


