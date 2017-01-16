from django import template

from ..models import Block

register = template.Library()


@register.simple_tag
def has_blocked(blocker, blockee):
    return Block.objects.has_blocked(blocker=blocker, blockee=blockee)
