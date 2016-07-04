from django import template
from django.utils.timezone import datetime

register = template.Library()

from ..models import ReadMark


@register.simple_tag
def get_other_participant(chat, user):
    """
    :type chat: speedy.net.im.models.Chat
    :type user: speedy.net.accounts.models.User
    """
    assert chat.is_private
    for entity in chat.participants:
        if entity.id != user.id:
            return entity

@register.simple_tag
def annotate_chats_with_read_marks(chat_list, user):
    """
    :type chat_list: [speedy.net.im.models.Chat]
    :type user: speedy.net.accounts.models.User
    """
    rmarks = {rmark.chat_id: rmark for rmark in ReadMark.objects.filter(chat__in=chat_list, entity=user)}
    for chat in chat_list:
        rmark = rmarks.get(chat.id)
        if chat.last_message is None:
            chat.is_unread = False
        elif rmark is None:
            chat.is_unread = True
        else:
            chat.is_unread = chat.last_message.date_created > rmark.date_updated
    return ''


@register.simple_tag
def annotate_messages_with_read_marks(message_list, user):
    """
    :type message_list: [speedy.net.im.models.Message]
    :type user: speedy.net.accounts.models.User
    """
    chats = set(message.chat for message in message_list)
    rmarks = {rmark.chat_id: rmark for rmark in ReadMark.objects.filter(chat__in=chats, entity=user)}
    for message in message_list:
        rmark = rmarks.get(message.chat_id)
        if rmark is None:
            message.is_unread = True
        else:
            message.is_unread = message.date_created > rmark.date_updated
    return ''
