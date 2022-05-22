import django
from django.contrib.sites.models import Site
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator

from speedy.core.base.managers import BaseManager
from speedy.core.base.models import TimeStampedModel
from speedy.core.base.fields import RegularUDIDField
from speedy.core.accounts.models import Entity, User
from .managers import ChatManager, MessageManager, ReadMarkManager


class Chat(TimeStampedModel):
    id = RegularUDIDField()
    site = models.ForeignKey(to=Site, verbose_name=_('site'), on_delete=models.PROTECT)
    ent1 = models.ForeignKey(to=Entity, verbose_name=_('participant 1'), on_delete=models.PROTECT, blank=True, null=True, related_name='+')
    ent2 = models.ForeignKey(to=Entity, verbose_name=_('participant 2'), on_delete=models.PROTECT, blank=True, null=True, related_name='+')
    group = models.ManyToManyField(to=Entity, verbose_name=_('participants'))
    is_group = models.BooleanField(verbose_name=_('is group chat'), default=False)
    last_message = models.ForeignKey(to='Message', verbose_name=_('last message'), on_delete=models.SET_NULL, blank=True, null=True, related_name='+')

    objects = ChatManager()
    all_sites_objects = BaseManager()

    @property
    def is_private(self):
        return (not (self.is_group))

    @property
    def participants(self):
        if (self.is_private):
            return (self.ent1, self.ent2)
        else:
            return self.group.order_by('date_created')

    @property
    def participants_count(self):
        return len(self.participants)

    @property
    def messages_queryset(self):
        return self.messages.all()

    @property
    def messages_count(self):
        return len(self.messages_queryset)

    @property
    def senders_ids(self):
        return {message.sender.id for message in self.messages_queryset if (message.sender)}

    class Meta:
        verbose_name = _('chat')
        verbose_name_plural = _('chats')
        ordering = ('-last_message__date_created', '-date_updated')

    def __str__(self):
        participants = ', '.join(str(ent.user.name) if ent else str(_("Unknown")) for ent in self.participants)
        senders_list = [str(ent.user.name) if ent else str(_("Unknown")) for ent in self.participants if (ent and (ent.id in self.senders_ids))]
        if (len(senders_list) > 0):
            senders = ', '.join(senders_list)
        else:
            senders = str(_("None"))
        return "<Chat {}: {} ({} {}, {}: {})>".format(self.id, participants, self.messages_count, "message" if (self.messages_count == 1) else "messages", "sender" if (len(senders_list) == 1) else "senders", senders)

    def save(self, *args, **kwargs):
        if (self.is_private):
            assert self.ent1
            assert self.ent2
            assert (not (self.ent1 == self.ent2))
            assert (self.group.count() == 0)
            if ((self.id == '') and (django.VERSION >= (4, 1))):
                # Django 4.1: "Related managers for ForeignKey, ManyToManyField, and GenericRelation are now cached on the Model instance to which they belong."
                # Remove the cached related manager with related_val = ('',) for self.group, since '' is generally valid for foreign keys but is not for Chat.id.
                self._state.related_managers_cache.pop('group')
        else:
            assert (self.ent1 is None)
            assert (self.ent2 is None)
        self.site = Site.objects.get_current()
        return super().save(*args, **kwargs)

    def get_slug(self, current_user: Entity):
        if (self.is_private):
            if (self.ent1_id == current_user.id):
                return self.ent2.slug
            elif (self.ent2_id == current_user.id):
                return self.ent1.slug
        return self.id

    def get_other_participants(self, entity):
        assert (entity.id in [p.id for p in self.participants])
        return [p for p in self.participants if (not (p.id == entity.id))]

    def mark_read(self, entity):
        return ReadMark.objects.mark(chat=self, entity=entity)


class Message(TimeStampedModel):
    id = RegularUDIDField()
    chat = models.ForeignKey(to=Chat, verbose_name=_('chat'), on_delete=models.PROTECT, blank=True, null=True, related_name='messages')
    sender = models.ForeignKey(to=Entity, verbose_name=_('sender'), on_delete=models.PROTECT, blank=True, null=True)
    text = models.TextField(verbose_name=_('message'), max_length=50000, validators=[MaxLengthValidator(limit_value=50000)])

    objects = MessageManager()

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ('-date_created',)
        get_latest_by = 'date_created'

    def __str__(self):
        return '{}: {}'.format(self.sender.user if self.sender else str(_("Unknown")), self.text[:140])


class ReadMark(TimeStampedModel):
    entity = models.ForeignKey(to=Entity, verbose_name=_('entity'), on_delete=models.CASCADE, related_name='+')
    chat = models.ForeignKey(to=Chat, verbose_name=_('chat'), on_delete=models.CASCADE, related_name='+')

    objects = ReadMarkManager()

    class Meta:
        verbose_name = _('read mark')
        verbose_name_plural = _('read marks')
        unique_together = ('entity', 'chat')
        ordering = ('-date_created',)
        get_latest_by = 'date_created'


@receiver(signal=models.signals.post_save, sender=Message)
def mail_user_on_new_message(sender, instance: Message, created, **kwargs):
    if (created):
        other_participants = instance.chat.get_other_participants(entity=instance.sender)
        for entity in other_participants:
            if (entity.user.notify_on_message == User.NOTIFICATIONS_ON):
                entity.user.mail_user(template_name_prefix='email/messages/new_message', context={
                    'message': instance,
                })


