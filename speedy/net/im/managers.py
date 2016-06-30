from django.db import models
from django.db.models import Count


class ChatManager(models.Manager):
    def chat_with(self, *entities):
        assert len(entities) > 1
        try:
            qs = self.annotate(Count('participants'))
            qs = qs.filter(participants__count=len(entities))
            for entity in entities:
                qs = qs.filter(participants__in=[entity])
            return qs.get()
        except self.model.DoesNotExist:
            chat = self.create()
            for entity in entities:
                chat.participants.add(entity)
            return chat


class MessageManager(models.Manager):
    def send_private(self, from_entity, to_entity, text):
        from speedy.net.im.models import Chat
        chat = Chat.objects.chat_with(from_entity, to_entity)
        return self.create(chat=chat, sender=from_entity, text=text)
