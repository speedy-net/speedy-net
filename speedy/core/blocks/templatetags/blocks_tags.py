from django import template

from speedy.core.blocks.models import Block

register = template.Library()


@register.simple_tag
def has_blocked(blocker, blocked):
    return Block.objects.has_blocked(blocker=blocker, blocked=blocked)


