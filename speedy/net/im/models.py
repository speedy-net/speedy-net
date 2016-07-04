import uuid

from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.core.models import TimeStampedModel
from speedy.net.accounts.models import Entity
from .managers import ChatManager, MessageManager, ReadMarkManager


class Chat(TimeStampedModel):
    class Meta:
        verbose_name = _('chat')
        verbose_name_plural = _('chat')
        ordering = ('-last_message__date_created', '-date_updated')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(verbose_name=_('site'), to=Site)
    ent1 = models.ForeignKey(verbose_name=_('participant 1'), to=Entity, null=True, blank=True, related_name='+')
    ent2 = models.ForeignKey(verbose_name=_('participant 2'), to=Entity, null=True, blank=True, related_name='+')
    group = models.ManyToManyField(verbose_name=_('participants'), to=Entity)
    is_group = models.BooleanField(verbose_name=_('is group chat'), default=False)
    last_message = models.ForeignKey(verbose_name=_('last message'), to='Message', blank=True, null=True,
                                     related_name='+')

    objects = models.Manager()
    on_site = ChatManager()

    def __str__(self):
        return ', '.join(str(ent.user) for ent in self.participants)

    def save(self, *args, **kwargs):
        if self.is_private:
            assert self.ent1
            assert self.ent2
            assert self.ent1 != self.ent2
            assert self.group.count() == 0
        self.site = Site.objects.get_current()
        return super().save(*args, **kwargs)

    @property
    def is_private(self):
        return not self.is_group

    @property
    def participants(self):
        if self.is_private:
            return (self.ent1, self.ent2)
        else:
            return self.participants.order_by('date_created')

    @property
    def participants_count(self):
        return len(self.participants)

    def mark_read(self, entity):
        return ReadMark.objects.mark(self, entity)


class Message(TimeStampedModel):
    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ('-date_created',)
        get_latest_by = 'date_created'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(verbose_name=_('chat'), to=Chat, on_delete=models.SET_NULL, null=True)
    sender = models.ForeignKey(verbose_name=_('sender'), to=Entity, on_delete=models.SET_NULL, null=True)
    text = models.TextField(verbose_name=_('message'))

    objects = MessageManager()

    def __str__(self):
        return '{}: {}'.format(self.sender.user, self.text[:140])


class ReadMark(TimeStampedModel):
    class Meta:
        verbose_name = _('read mark')
        verbose_name_plural = _('read marks')
        get_latest_by = 'date_created'

    entity = models.ForeignKey(verbose_name=_('entity'), to=Entity, related_name='+')
    chat = models.ForeignKey(verbose_name=_('chat'), to=Chat, related_name='+')

    objects = ReadMarkManager()
