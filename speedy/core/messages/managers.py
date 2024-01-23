from collections import defaultdict

from django.conf import settings as django_settings
from django.contrib.sites.models import Site
from django.db.models import Q

from speedy.core.accounts.cache_helper import cache_key
from speedy.core.base import cache_manager
from speedy.core.base.managers import BaseManager


class ChatManager(BaseManager):
    def get_queryset(self):
        return super().get_queryset().filter(site=Site.objects.get_current()).prefetch_related('messages', 'messages__sender', 'messages__sender__user')

    def chats(self, entity):
        return self.filter(Q(group__in=[entity]) | Q(ent1_id=entity.id) | Q(ent2_id=entity.id))

    def chat_with(self, ent1, ent2, create=True):
        chats = self.filter(Q(ent1=ent1, ent2=ent2) | Q(ent1=ent2, ent2=ent1))
        if (len(chats) == 1):
            return chats[0]
        else:
            if (create):
                return self.create(ent1=ent1, ent2=ent2)
            else:
                return None

    def group_chat_with(self, *entities):
        chat = self.create(is_group=True)
        for entity in entities:
            chat.group.add(entity)
        return chat

    def count_chats_with_string_in_messages_and_only_one_sender(self, entity, string_in_messages, created_after):
        chats = self.chats(entity=entity).filter(messages__text__icontains=string_in_messages, messages__date_created__gte=created_after).distinct()
        return len({chat.id for chat in chats if (chat.senders_ids == {entity.id})})

    def count_chats_with_strings_in_messages_and_only_one_sender(self, entity, strings_in_messages, created_after):
        return max([self.count_chats_with_string_in_messages_and_only_one_sender(entity=entity, string_in_messages=string_in_messages, created_after=created_after) for string_in_messages in strings_in_messages])

    def count_identical_messages_in_chats_with_only_one_sender(self, entity):
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
    def send_message(self, from_entity, to_entity=None, chat=None, text=None):
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
    def annotate_chats_with_read_marks(self, chat_list, entity):
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
        read_mark, created = self.get_or_create(chat=chat, entity=entity)
        if (not (created)):
            read_mark.save()
        return read_mark


