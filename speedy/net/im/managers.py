from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q


class ChatManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(site=Site.objects.get_current())

    def chats(self, entity):
        return self.filter(Q(group__in=[entity])
                           | Q(ent1_id=entity.id)
                           | Q(ent2_id=entity.id))

    def chat_with(self, ent1, ent2, create=True):
        try:
            return self.get(Q(ent1=ent1, ent2=ent2)
                            | Q(ent1=ent2, ent2=ent1))
        except self.model.DoesNotExist:
            if create:
                return self.create(ent1=ent1, ent2=ent2)
            else:
                return None

    def group_chat_with(self, *entities):
        chat = self.create(is_group=True)
        for entity in entities:
            chat.group.add(entity)
        return chat


class MessageManager(models.Manager):
    def send_message(self, from_entity, to_entity=None, chat=None, text=None):
        from .models import Chat
        assert bool(from_entity and to_entity) != bool(from_entity and chat)
        assert text
        if not chat:
            chat = Chat.on_site.chat_with(from_entity, to_entity)
        chat.last_message = self.create(chat=chat, sender=from_entity, text=text)
        chat.date_updated = chat.last_message.date_created
        chat.save(update_fields={'last_message', 'date_updated'})
        chat.mark_read(from_entity)
        return chat.last_message


class ReadMarkManager(models.Manager):
    def mark(self, chat, entity):
        rmark, created = self.get_or_create(chat=chat, entity=entity)
        if not created:
            rmark.save(update_fields={'date_updated'})
        return rmark
