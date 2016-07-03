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

    def chat_with(self, ent1, ent2):
        try:
            return self.get(Q(ent1=ent1, ent2=ent2)
                            | Q(ent1=ent2, ent2=ent1))
        except self.model.DoesNotExist:
            return self.create(ent1=ent1, ent2=ent2)

    def group_chat_with(self, *entities):
        chat = self.create(is_group=True)
        for entity in entities:
            chat.group.add(entity)
        return chat


class MessageManager(models.Manager):
    def send_private(self, from_entity, to_entity, text):
        from speedy.net.im.models import Chat
        chat = Chat.on_site.chat_with(from_entity, to_entity)
        return self.create(chat=chat, sender=from_entity, text=text)
