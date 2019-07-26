from django.contrib.sites.models import Site
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from speedy.core.base.models import TimeStampedModel, RegularUDIDField
from speedy.core.accounts.models import Entity, User
from .managers import ChatManager, MessageManager, ReadMarkManager


class Chat(TimeStampedModel):
    id = RegularUDIDField()
    site = models.ForeignKey(to=Site, verbose_name=_('site'), on_delete=models.PROTECT)
    ent1 = models.ForeignKey(to=Entity, verbose_name=_('participant 1'), on_delete=models.SET_NULL, blank=True, null=True, related_name='+')
    ent2 = models.ForeignKey(to=Entity, verbose_name=_('participant 2'), on_delete=models.SET_NULL, blank=True, null=True, related_name='+')
    group = models.ManyToManyField(to=Entity, verbose_name=_('participants'))
    is_group = models.BooleanField(verbose_name=_('is group chat'), default=False)
    last_message = models.ForeignKey(to='Message', verbose_name=_('last message'), on_delete=models.SET_NULL, blank=True, null=True, related_name='+')

    objects = ChatManager()

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

    class Meta:
        verbose_name = _('chat')
        verbose_name_plural = _('chats')
        ordering = ('-last_message__date_created', '-date_updated')

    def __str__(self):
        return ', '.join(str(ent.user.name) for ent in self.participants)

    def save(self, *args, **kwargs):
        if (self.is_private):
            assert self.ent1
            assert self.ent2
            assert self.ent1 != self.ent2
            assert self.group.count() == 0
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
        return [p for p in self.participants if (p.id != entity.id)]

    def mark_read(self, entity):
        return ReadMark.objects.mark(self, entity)


class Message(TimeStampedModel):
    id = RegularUDIDField()
    chat = models.ForeignKey(to=Chat, verbose_name=_('chat'), on_delete=models.SET_NULL, blank=True, null=True)
    sender = models.ForeignKey(to=Entity, verbose_name=_('sender'), on_delete=models.SET_NULL, blank=True, null=True)
    text = models.TextField(verbose_name=_('message'))

    objects = MessageManager()

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ('-date_created',)
        get_latest_by = 'date_created'

    def __str__(self):
        return '{}: {}'.format(self.sender.user, self.text[:140])


class ReadMark(TimeStampedModel):
    entity = models.ForeignKey(to=Entity, verbose_name=_('entity'), on_delete=models.CASCADE, related_name='+')
    chat = models.ForeignKey(to=Chat, verbose_name=_('chat'), on_delete=models.CASCADE, related_name='+')

    objects = ReadMarkManager()

    class Meta:
        verbose_name = _('read mark')
        verbose_name_plural = _('read marks')
        get_latest_by = 'date_created'


@receiver(models.signals.post_save, sender=Message)
def mail_user_on_new_message(sender, instance: Message, created, **kwargs):
    if (not (created)):
        return
    other_participants = instance.chat.get_other_participants(entity=instance.sender)
    for entity in other_participants:
        if (entity.user.notify_on_message == User.NOTIFICATIONS_ON):
            entity.user.mail_user(template_name_prefix='messages/email/new_message', context={
                'message': instance,
            })


