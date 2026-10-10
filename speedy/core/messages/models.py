from django.contrib.sites.models import Site
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator

from speedy.core.base.managers import BaseManager
from speedy.core.base.models import TimeStampedModel
from speedy.core.base.fields import RegularUDIDField
from speedy.core.accounts.cache_helper import bust_cache
from speedy.core.accounts.models import Entity, User
from .managers import ChatManager, MessageManager, ReadMarkManager


class Chat(TimeStampedModel):
    """
    Represents a chat between entities.

    Attributes:
        id (RegularUDIDField): The unique identifier for the chat.
        site (ForeignKey): The site associated with the chat.
        ent1 (ForeignKey): The first participant in a private chat.
        ent2 (ForeignKey): The second participant in a private chat.
        group (ManyToManyField): The participants in a group chat.
        is_group (BooleanField): Indicates if the chat is a group chat.
        last_message (ForeignKey): The last message in the chat.
    """
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
        """
        :return: True if this is a private (two-participant) chat, False if it's a group chat.
        :rtype: bool
        """
        return (not (self.is_group))

    @property
    def participants(self):
        """
        :return: The chat's participants - a tuple of (ent1, ent2) for a private chat, or the group members ordered by join date for a group chat.
        :rtype: tuple or django.db.models.QuerySet
        """
        if (self.is_private):
            return (self.ent1, self.ent2)
        else:
            return self.group.order_by('date_created')

    @property
    def participants_count(self):
        """
        :return: The number of participants in the chat.
        :rtype: int
        """
        return len(self.participants)

    @property
    def messages_queryset(self):
        """
        :return: The queryset of all messages in the chat.
        :rtype: django.db.models.QuerySet
        """
        return self.messages.all()

    @property
    def messages_count(self):
        """
        :return: The number of messages in the chat.
        :rtype: int
        """
        return len(self.messages_queryset)

    @property
    def senders_ids(self):
        """
        :return: The set of ids of the entities who have sent at least one message in the chat.
        :rtype: set
        """
        return {message.sender.id for message in self.messages_queryset if (message.sender)}

    class Meta:
        verbose_name = _('chat')
        verbose_name_plural = _('chats')
        ordering = ('-last_message__date_created', '-date_updated')

    def __str__(self):
        """
        :return: A string representation of the chat, including its id, participants, and message/sender counts.
        :rtype: str
        """
        participants = ', '.join(str(ent.user.name) if ent else str(_("Unknown")) for ent in self.participants)
        senders_list = [str(ent.user.name) if ent else str(_("Unknown")) for ent in self.participants if (ent and (ent.id in self.senders_ids))]
        if (len(senders_list) > 0):
            senders = ', '.join(senders_list)
        else:
            senders = str(_("None"))
        return "<Chat {}: {} ({} {}, {}: {})>".format(self.id, participants, self.messages_count, "message" if (self.messages_count == 1) else "messages", "sender" if (len(senders_list) == 1) else "senders", senders)

    def save(self, *args, **kwargs):
        """
        Save the Chat instance to the database.

        :param args: Additional positional arguments passed to the parent method.
        :param kwargs: Additional keyword arguments passed to the parent method.
        :return: The result of the parent save method.
        :raises AssertionError: If the private chat does not have two distinct participants or if the group chat has participants.
        """
        if (self.is_private):
            assert self.ent1
            assert self.ent2
            assert (not (self.ent1 == self.ent2))
            assert (self.group.count() == 0)
        else:
            assert (self.ent1 is None)
            assert (self.ent2 is None)
        # Only assign site if it's not already assigned.
        if (self.site_id is None):
            self.site = Site.objects.get_current()
        assert (self.site_id is not None)
        return super().save(*args, **kwargs)

    def get_slug(self, current_user: Entity):
        """
        Get the slug for the chat based on the current user.

        :param current_user: The current user.
        :type current_user: Entity
        :return: The slug of the other participant for a private chat, or the chat id otherwise.
        :rtype: str or int
        """
        if (self.is_private):
            if (self.ent1_id == current_user.id):
                return self.ent2.slug
            elif (self.ent2_id == current_user.id):
                return self.ent1.slug
        return self.id

    def get_other_participants(self, entity):
        """
        Get the other participants in the chat excluding the given entity.

        :param entity: The entity to exclude.
        :type entity: Entity
        :return: The other participants in the chat.
        :rtype: list
        """
        assert (entity.id in [p.id for p in self.participants])
        return [p for p in self.participants if (not (p.id == entity.id))]

    def mark_read(self, entity):
        """
        Mark the chat as read for the given entity.

        :param entity: The entity marking the chat as read.
        :type entity: Entity
        :return: The ReadMark instance for the entity and chat.
        :rtype: ReadMark
        """
        return ReadMark.objects.mark(chat=self, entity=entity)


class Message(TimeStampedModel):
    """
    Represents a message in a chat.

    Attributes:
        id (RegularUDIDField): The unique identifier for the message.
        chat (ForeignKey): The chat the message belongs to.
        sender (ForeignKey): The sender of the message.
        text (TextField): The content of the message.
    """
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
        """
        Return a string representation of the message.

        Returns:
            str: The string representation of the message.
        """
        return '{}: {}'.format(self.sender.user if self.sender else str(_("Unknown")), self.text[:140])


class ReadMark(TimeStampedModel):
    """
    Represents a read mark for a chat by an entity.

    Attributes:
        entity (ForeignKey): The entity that read the chat.
        chat (ForeignKey): The chat that was read.
    """
    entity = models.ForeignKey(to=Entity, verbose_name=_('entity'), on_delete=models.CASCADE, related_name='+')
    chat = models.ForeignKey(to=Chat, verbose_name=_('chat'), on_delete=models.CASCADE, related_name='+')

    objects = ReadMarkManager()

    class Meta:
        verbose_name = _('read mark')
        verbose_name_plural = _('read marks')
        unique_together = ('entity', 'chat')
        ordering = ('-date_created',)
        get_latest_by = 'date_created'


@receiver(signal=models.signals.post_save, sender=Chat)
def invalidate_unread_chats_count_after_update_chat(sender, instance: Chat, **kwargs):
    """
    Signal receiver that invalidates the unread chats count cache after a chat is updated.

    :param sender: The model class that sent the signal.
    :type sender: type
    :param instance: The Chat instance that was saved.
    :type instance: Chat
    :param kwargs: Additional keyword arguments.
    """
    if (instance.last_message is not None):
        other_participants = instance.get_other_participants(entity=instance.last_message.sender)
        bust_cache(cache_type='unread_chats_count', entities_pks=[p.pk for p in other_participants])


@receiver(signal=models.signals.post_save, sender=ReadMark)
def invalidate_unread_chats_count_after_read_mark(sender, instance: ReadMark, **kwargs):
    """
    Signal receiver that invalidates the unread chats count cache after a read mark is created.

    :param sender: The model class that sent the signal.
    :type sender: type
    :param instance: The ReadMark instance that was saved.
    :type instance: ReadMark
    :param kwargs: Additional keyword arguments.
    """
    bust_cache(cache_type='unread_chats_count', entities_pks=[instance.entity.pk])


@receiver(signal=models.signals.post_save, sender=Message)
def mail_user_on_new_message(sender, instance: Message, created, **kwargs):
    """
    Signal receiver that sends an email to users when a new message is created.

    :param sender: The model class that sent the signal.
    :type sender: type
    :param instance: The Message instance that was saved.
    :type instance: Message
    :param created: Whether the instance was created.
    :type created: bool
    :param kwargs: Additional keyword arguments.
    """
    if (created):
        other_participants = instance.chat.get_other_participants(entity=instance.sender)
        for entity in other_participants:
            if ((entity.user.is_active) and (entity.user.notify_on_message == User.NOTIFICATIONS_ON)):
                entity.user.mail_user(template_name_prefix='email/messages/new_message', context={
                    'message': instance,
                })


