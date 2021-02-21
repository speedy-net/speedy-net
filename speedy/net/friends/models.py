from django.db import models
from django.dispatch import receiver
from friendship.models import Friend


@receiver(signal=models.signals.post_save, sender=Friend)
def update_friends_count_on_new_friend(sender, instance: Friend, created, **kwargs):
    if (created):
        user = instance.to_user
        user.speedy_net_profile.friends_count = user.friends.count()
        user.speedy_net_profile.save()


@receiver(signal=models.signals.post_delete, sender=Friend)
def update_friends_count_on_unfriend(sender, instance: Friend, **kwargs):
    user = instance.to_user
    user.speedy_net_profile.friends_count = user.friends.count()
    user.speedy_net_profile.save()
