from django import template

from speedy.core.blocks.models import Block

register = template.Library()


@register.simple_tag
def has_blocked(blocker, blocked):
    """
    Template tag checking whether blocker has blocked blocked.

    :param blocker: The entity that may have blocked blocked.
    :type blocker: speedy.core.accounts.models.Entity
    :param blocked: The entity that may be blocked.
    :type blocked: speedy.core.accounts.models.Entity
    :return: True if blocker has blocked blocked, False otherwise.
    :rtype: bool
    """
    return Block.objects.has_blocked(blocker=blocker, blocked=blocked)


