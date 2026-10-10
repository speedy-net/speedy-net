from django import template

from speedy.core.messages.models import ReadMark, Chat

register = template.Library()


@register.simple_tag
def get_other_participant(chat, user):
    """
    Returns the other participant of a private chat, i.e. the participant who isn't the given user.

    :param chat: The private chat.
    :type chat: speedy.core.messages.models.Chat
    :param user: The user whose counterpart in the chat should be returned.
    :type user: speedy.core.accounts.models.User
    :return: The other participant of the chat.
    :rtype: speedy.core.accounts.models.Entity
    """
    assert chat.is_private
    other_participants = chat.get_other_participants(entity=user)
    assert (len(other_participants) == 1)
    return other_participants[0]


@register.simple_tag
def annotate_chats_with_read_marks(chat_list, entity):
    """
    Sets the is_unread attribute on each chat in chat_list, based on the entity's read marks.

    :param chat_list: The list of chats to annotate.
    :type chat_list: list of speedy.core.messages.models.Chat
    :param entity: The entity whose read marks should be used.
    :type entity: speedy.core.accounts.models.Entity
    :return: An empty string.
    :rtype: str
    """
    return ReadMark.objects.annotate_chats_with_read_marks(chat_list=chat_list, entity=entity)


@register.simple_tag
def annotate_messages_with_read_marks(message_list, entity):
    """
    Sets the is_unread attribute on each message in message_list, based on whether the entity's read mark for the message's chat is older than the message.

    :param message_list: The list of messages to annotate.
    :type message_list: list of speedy.core.messages.models.Message
    :param entity: The entity whose read marks should be used.
    :type entity: speedy.core.accounts.models.Entity
    :return: An empty string.
    :rtype: str
    """
    chats = set(message.chat for message in message_list)
    read_marks = {read_mark.chat_id: read_mark for read_mark in ReadMark.objects.filter(chat__in=chats, entity=entity)}
    for message in message_list:
        read_mark = read_marks.get(message.chat_id)
        if (read_mark is None):
            message.is_unread = True
        else:
            message.is_unread = message.date_created > read_mark.date_updated
    return ''


@register.filter
def get_chat_slug(chat, current_user):
    """
    Returns the slug to use for the chat relative to the current user.

    :param chat: The chat whose slug should be returned.
    :type chat: speedy.core.messages.models.Chat
    :param current_user: The entity the slug should be relative to.
    :type current_user: speedy.core.accounts.models.Entity
    :return: The chat's slug.
    :rtype: str
    """
    return chat.get_slug(current_user=current_user)


@register.simple_tag
def unread_chats_count(entity):
    """
    :param entity: The entity whose unread chats should be counted.
    :type entity: speedy.core.accounts.models.Entity
    :return: The number of unread chats for the entity.
    :rtype: int
    """
    return Chat.objects.count_unread_chats(entity=entity)


