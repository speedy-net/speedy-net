from django import template

register = template.Library()


@register.simple_tag
def get_other_participant(chat, request_user):
    """
    :type chat: speedy.net.im.models.Chat
    :type request_user: speedy.net.accounts.models.User
    """
    assert chat.is_private
    for entity in chat.participants:
        if entity.id != request_user.id:
            return entity
