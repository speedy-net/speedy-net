from django.contrib.sites.models import Site
from django.db.models import Q

from speedy.core.base.managers import BaseManager


class ChatManager(BaseManager):
    def get_queryset(self):
        return super().get_queryset().filter(site=Site.objects.get_current())

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


class MessageManager(BaseManager):
    def send_message(self, from_entity, to_entity=None, chat=None, text=None):
        from .models import Chat
        assert bool(from_entity and to_entity) != bool(from_entity and chat)
        assert text
        if (not (chat)):
            chat = Chat.objects.chat_with(ent1=from_entity, ent2=to_entity)
        chat.last_message = self.create(chat=chat, sender=from_entity, text=text)
        chat.date_updated = chat.last_message.date_created
        chat.save(update_fields={'last_message', 'date_updated'})
        chat.mark_read(entity=from_entity)
        return chat.last_message


class ReadMarkManager(BaseManager):
    def mark(self, chat, entity):
        read_mark, created = self.get_or_create(chat=chat, entity=entity)
        if (not (created)):
            read_mark.save(update_fields={'date_updated'})
        return read_mark


