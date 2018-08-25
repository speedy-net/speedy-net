from django import template

register = template.Library()

from ..models import ReadMark, Chat


@register.simple_tag
def get_other_participant(chat, user):
    """
    :type chat: speedy.net.im.models.Chat
    :type user: speedy.net.accounts.models.User
    """
    assert chat.is_private
    return chat.get_other_participants(user)[0]


@register.simple_tag
def annotate_chats_with_read_marks(chat_list, entity):
    """
    :type chat_list: [speedy.net.im.models.Chat]
    :type entity: speedy.net.accounts.models.Entity
    """
    rmarks = {rmark.chat_id: rmark for rmark in ReadMark.objects.filter(chat__in=chat_list, entity=entity)}
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
def annotate_messages_with_read_marks(message_list, entity):
    """
    :type message_list: [speedy.net.im.models.Message]
    :type entity: speedy.net.accounts.models.Entity
    """
    chats = set(message.chat for message in message_list)
    rmarks = {rmark.chat_id: rmark for rmark in ReadMark.objects.filter(chat__in=chats, entity=entity)}
    for message in message_list:
        rmark = rmarks.get(message.chat_id)
        if rmark is None:
            message.is_unread = True
        else:
            message.is_unread = message.date_created > rmark.date_updated
    return ''


@register.filter
def get_chat_slug(chat, current_user):
    """
    :type chat: speedy.net.im.models.Chat
    :type current_user: speedy.net.accounts.models.Entity
    :return: str
    """
    return chat.get_slug(current_user=current_user)


@register.simple_tag
def unread_chats_count(entity):
    chat_list = Chat.on_site.chats(entity)
    annotate_chats_with_read_marks(chat_list, entity)
    return len([c for c in chat_list if c.is_unread])


