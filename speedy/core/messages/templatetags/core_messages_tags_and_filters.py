from django import template

from speedy.core.messages.models import ReadMark, Chat

register = template.Library()


@register.simple_tag
def get_other_participant(chat, user):
    """
    :type chat: speedy.core.messages.models.Chat
    :type user: speedy.core.accounts.models.User
    """
    assert chat.is_private
    other_participants = chat.get_other_participants(entity=user)
    assert (len(other_participants) == 1)
    return other_participants[0]


@register.simple_tag
def annotate_chats_with_read_marks(chat_list, entity):
    """
    :type chat_list: [speedy.core.messages.models.Chat]
    :type entity: speedy.core.accounts.models.Entity
    """
    return ReadMark.objects.annotate_chats_with_read_marks(chat_list=chat_list, entity=entity)


@register.simple_tag
def annotate_messages_with_read_marks(message_list, entity):
    """
    :type message_list: [speedy.core.messages.models.Message]
    :type entity: speedy.core.accounts.models.Entity
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
    :type chat: speedy.core.messages.models.Chat
    :type current_user: speedy.core.accounts.models.Entity
    :return: str
    """
    return chat.get_slug(current_user=current_user)


@register.simple_tag
def unread_chats_count(entity):
    return Chat.objects.count_unread_chats(entity=entity)


