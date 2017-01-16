from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from friendship.models import Friend, FriendshipRequest

from speedy.core.blocks.models import Block


@receiver(signal=models.signals.post_save, sender=Block)
def delete_friendship_requests_on_block(sender, instance: Block, **kwargs):
    q1 = Q(from_user=instance.blocker, to_user=instance.blockee)
    q2 = Q(from_user=instance.blockee, to_user=instance.blocker)
    active_requests = FriendshipRequest.objects.filter(q1 | q2)
    for request in active_requests:
        request.cancel()


@receiver(signal=models.signals.post_save, sender=Block)
def delete_friends_on_block(sender, instance: Block, **kwargs):
    Friend.objects.remove_friend(from_user=instance.blocker, to_user=instance.blockee)
