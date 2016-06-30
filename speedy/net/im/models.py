import uuid

from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.core.models import TimeStampedModel
from speedy.net.accounts.models import Entity

from .managers import ChatManager, MessageManager


class Chat(TimeStampedModel):
    class Meta:
        verbose_name = _('chat')
        verbose_name_plural = _('chat')
        ordering = ('-date_updated',)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(verbose_name=_('site'), to=Site, on_delete=models.SET_NULL, null=True)
    participants = models.ManyToManyField(verbose_name=_('participants'), to=Entity)

    objects = ChatManager()

    def __str__(self):
        return ', '.join(str(ent.user) for ent in self.participants.order_by('-date_created'))


class Message(TimeStampedModel):
    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ('-date_created',)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(verbose_name=_('chat'), to=Chat, on_delete=models.SET_NULL, null=True)
    sender = models.ForeignKey(verbose_name=_('sender'), to=Entity, on_delete=models.SET_NULL, null=True)
    text = models.TextField(verbose_name=_('message'))

    objects = MessageManager()

    def __str__(self):
        return '{}: {}'.format(self.sender.user, self.text[:140])
