"""
Managers for the messages app of Speedy Core: ChatManager, MessageManager and ReadMarkManager.
"""
from collections import defaultdict

from django.conf import settings as django_settings
from django.contrib.sites.models import Site
from django.db.models import Q

from speedy.core.accounts.cache_helper import cache_key
from speedy.core.base import cache_manager
from speedy.core.base.managers import BaseManager


class ChatManager(BaseManager):
    """
    Manager for the Chat model, providing methods for querying and creating chats and for counting messages/chats matching various criteria.

    Methods:
        get_queryset(self): Returns the queryset of chats restricted to the current site, with messages and senders prefetched.
        chats(self, entity): Returns the queryset of chats the given entity participates in.
        chat_with(self, ent1, ent2, create): Returns the private chat between two entities, creating it if it doesn't exist and create is True.
        group_chat_with(self, *entities): Creates a new group chat with the given entities as participants.
        count_chats_with_string_in_messages_and_only_one_sender(self, entity, string_in_messages, created_after): Counts the entity's chats, created after a given date, that contain a string in a message and have only the entity as sender.
        count_chats_with_strings_in_messages_and_only_one_sender(self, entity, strings_in_messages, created_after): Returns the maximum count, over several strings, of chats matching count_chats_with_string_in_messages_and_only_one_sender.
        count_identical_messages_in_chats_with_only_one_sender(self, entity): Returns the count and text of the most repeated long message sent by the entity in chats where it is the only sender.
        count_unread_chats(self, entity): Returns the number of unread chats for the given entity, using a cache.
    """
    def get_queryset(self):
        """
        Returns the queryset of chats restricted to the current site, with messages and their senders prefetched.

        :return: The queryset of Chat instances for the current site.
        :rtype: django.db.models.QuerySet
        """
        return super().get_queryset().filter(site=Site.objects.get_current()).prefetch_related('messages', 'messages__sender', 'messages__sender__user')

    def chats(self, entity):
        """
        Returns the queryset of chats the given entity participates in, whether as a group member or as a private chat participant.

        :param entity: The entity whose chats should be returned.
        :type entity: speedy.core.accounts.models.Entity
        :return: The queryset of Chat instances the entity participates in.
        :rtype: django.db.models.QuerySet
        """
        return self.filter(Q(group__in=[entity]) | Q(ent1_id=entity.id) | Q(ent2_id=entity.id))

    def chat_with(self, ent1, ent2, create=True):
        """
        Returns the private chat between the two given entities, creating a new one if it doesn't exist and create is True.

        :param ent1: One participant of the private chat.
        :type ent1: speedy.core.accounts.models.Entity
        :param ent2: The other participant of the private chat.
        :type ent2: speedy.core.accounts.models.Entity
        :param create: Whether to create the chat if it doesn't already exist. Defaults to True.
        :type create: bool
        :return: The existing or newly created private chat between the two entities, or None if it doesn't exist and create is False.
        :rtype: speedy.core.messages.models.Chat or None
        """
        chats = self.filter(Q(ent1=ent1, ent2=ent2) | Q(ent1=ent2, ent2=ent1))
        if (len(chats) == 1):
            return chats[0]
        else:
            if (create):
                return self.create(ent1=ent1, ent2=ent2)
            else:
                return None

    def group_chat_with(self, *entities):
        """
        Creates a new group chat with the given entities as participants.

        :param entities: The entities to add as participants of the group chat.
        :type entities: speedy.core.accounts.models.Entity
        :return: The newly created group chat.
        :rtype: speedy.core.messages.models.Chat
        """
        chat = self.create(is_group=True)
        for entity in entities:
            chat.group.add(entity)
        return chat

    def count_chats_with_string_in_messages_and_only_one_sender(self, entity, string_in_messages, created_after):
        """
        Counts the entity's chats, created after a given date, that contain a message with the given string and have the entity as the only sender.

        :param entity: The entity whose chats should be counted.
        :type entity: speedy.core.accounts.models.Entity
        :param string_in_messages: The string to search for in the chats' messages.
        :type string_in_messages: str
        :param created_after: Only messages created at or after this date are considered.
        :type created_after: datetime.datetime
        :return: The number of matching chats.
        :rtype: int
        """
        chats = self.chats(entity=entity).filter(messages__text__icontains=string_in_messages, messages__date_created__gte=created_after).distinct()
        return len({chat.id for chat in chats if (chat.senders_ids == {entity.id})})

    def count_chats_with_strings_in_messages_and_only_one_sender(self, entity, strings_in_messages, created_after):
        """
        Returns the maximum, over all the given strings, of the count of the entity's chats that contain that string and have the entity as the only sender.

        :param entity: The entity whose chats should be counted.
        :type entity: speedy.core.accounts.models.Entity
        :param strings_in_messages: The strings to search for in the chats' messages.
        :type strings_in_messages: list of str
        :param created_after: Only messages created at or after this date are considered.
        :type created_after: datetime.datetime
        :return: The highest matching chats count among all the given strings.
        :rtype: int
        """
        return max([self.count_chats_with_string_in_messages_and_only_one_sender(entity=entity, string_in_messages=string_in_messages, created_after=created_after) for string_in_messages in strings_in_messages])

    def count_identical_messages_in_chats_with_only_one_sender(self, entity):
        """
        Finds, among the chats where the entity is the only sender, the identical message text (of at least 25 characters) sent the most times, and returns how many times it was sent together with its text.

        :param entity: The entity whose chats and messages should be examined.
        :type entity: speedy.core.accounts.models.Entity
        :return: A tuple of (count, text) for the most repeated message, or (0, "") if there are none.
        :rtype: tuple
        """
        d = defaultdict(int)
        chats = self.chats(entity=entity).distinct()
        for chat in chats:
            if (chat.senders_ids == {entity.id}):
                for message in chat.messages.all():
                    if (len(message.text) >= 25):
                        d[message.text] += 1
        l1 = sorted([(d[k], k) for k in d.keys()] + [(0, "")], reverse=True)
        return l1[0]

    def count_unread_chats(self, entity):
        """
        Returns the number of unread chats for the given entity, reading from the cache when available and otherwise computing and caching the value.

        :param entity: The entity whose unread chats should be counted.
        :type entity: speedy.core.accounts.models.Entity
        :return: The number of unread chats for the entity.
        :rtype: int
        """
        from .models import ReadMark
        unread_chats_count_cache_key = cache_key(cache_type='unread_chats_count', entity_pk=entity.pk)
        unread_chats_count = cache_manager.cache_get(key=unread_chats_count_cache_key, sliding_timeout=django_settings.CACHE_GET_UNREAD_CHATS_COUNT_SLIDING_TIMEOUT)
        if (unread_chats_count is None):
            chat_list = self.chats(entity=entity)
            ReadMark.objects.annotate_chats_with_read_marks(chat_list=chat_list, entity=entity)
            unread_chats_count = len([c for c in chat_list if (c.is_unread)])
            cache_manager.cache_set(key=unread_chats_count_cache_key, value=unread_chats_count, timeout=django_settings.CACHE_SET_UNREAD_CHATS_COUNT_TIMEOUT)
        return unread_chats_count


class MessageManager(BaseManager):
    """
    Manager for the Message model, providing a method for creating a message and attaching it to an existing or new chat.

    Methods:
        send_message(self, from_entity, to_entity, chat, text): Creates a message from one entity to another entity or an existing chat, and updates the chat accordingly.
    """
    def send_message(self, from_entity, to_entity=None, chat=None, text=None):
        """
        Creates a new message from an entity, either to another entity (creating or reusing their private chat) or to an existing chat, and updates the chat's last message and marks it as read for the sender.

        :param from_entity: The entity sending the message.
        :type from_entity: speedy.core.accounts.models.Entity
        :param to_entity: The entity to send the message to, when sending to a new or existing private chat. Mutually exclusive with chat.
        :type to_entity: speedy.core.accounts.models.Entity or None
        :param chat: The existing chat to send the message to. Mutually exclusive with to_entity.
        :type chat: speedy.core.messages.models.Chat or None
        :param text: The text of the message.
        :type text: str
        :return: The newly created message.
        :rtype: speedy.core.messages.models.Message
        """
        from .models import Chat
        assert bool(from_entity and to_entity) != bool(from_entity and chat)
        assert text
        if (not (chat)):
            chat = Chat.objects.chat_with(ent1=from_entity, ent2=to_entity)
        chat.last_message = self.create(chat=chat, sender=from_entity, text=text)
        chat.date_updated = chat.last_message.date_created
        chat.save()
        chat.mark_read(entity=from_entity)
        return chat.last_message


class ReadMarkManager(BaseManager):
    """
    Manager for the ReadMark model, providing methods for annotating chats with their unread status and for marking a chat as read.

    Methods:
        annotate_chats_with_read_marks(self, chat_list, entity): Sets the is_unread attribute on each chat in chat_list based on the entity's read marks.
        mark(self, chat, entity): Creates or updates the read mark for the given chat and entity.
    """
    def annotate_chats_with_read_marks(self, chat_list, entity):
        """
        Sets the is_unread attribute on each chat in chat_list, based on whether the entity has a read mark for that chat newer than its last message.

        :param chat_list: The list of chats to annotate.
        :type chat_list: list of speedy.core.messages.models.Chat
        :param entity: The entity whose read marks should be used to determine the unread status.
        :type entity: speedy.core.accounts.models.Entity
        :return: An empty string (so the tag can be used in templates).
        :rtype: str
        """
        read_marks = {read_mark.chat_id: read_mark for read_mark in self.filter(chat__in=chat_list, entity=entity)}
        for chat in chat_list:
            read_mark = read_marks.get(chat.id)
            if (chat.last_message is None):
                chat.is_unread = False
            elif (read_mark is None):
                chat.is_unread = True
            else:
                chat.is_unread = chat.last_message.date_created > read_mark.date_updated
        return ''

    def mark(self, chat, entity):
        """
        Creates a new read mark for the given chat and entity, or updates the existing one's timestamp.

        :param chat: The chat being marked as read.
        :type chat: speedy.core.messages.models.Chat
        :param entity: The entity who read the chat.
        :type entity: speedy.core.accounts.models.Entity
        :return: The created or updated read mark.
        :rtype: speedy.core.messages.models.ReadMark
        """
        read_mark, created = self.get_or_create(chat=chat, entity=entity)
        if (not (created)):
            read_mark.save()
        return read_mark


