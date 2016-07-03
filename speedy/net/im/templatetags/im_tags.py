from django import template

register = template.Library()


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
