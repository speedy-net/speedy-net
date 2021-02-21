from django.db import models
from django.dispatch import receiver
from friendship.models import Friend


@receiver(signal=models.signals.post_save, sender=Friend)
def update_user_cached_counts_on_new_friend(sender, instance: Friend, created, **kwargs):
    if (created):
        user = instance.to_user
        user.cached_counts.friends = user.friends.count()


@receiver(signal=models.signals.post_delete, sender=Friend)
def update_user_cached_counts_on_unfriend(sender, instance: Friend, **kwargs):
    user = instance.to_user
    user.cached_counts.friends = user.friends.count()
