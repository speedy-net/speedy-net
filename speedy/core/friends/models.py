from django.db import models
from django.dispatch import receiver
from friendship.models import Friend

from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile


@receiver(signal=models.signals.post_save, sender=Friend)
def update_friends_count_on_new_friend(sender, instance: Friend, created, **kwargs):
    if (created):
        user = instance.to_user
        user.speedy_net_profile.friends_count = user.friends.count()
        user.speedy_net_profile.save()


@receiver(signal=models.signals.post_delete, sender=Friend)
def update_friends_count_on_unfriend(sender, instance: Friend, **kwargs):
    user = instance.to_user
    # Do .filter(...).update(...) because for cascade delete User -> Friend, accessing user.speedy_net_profile will re-create deleted SpeedyNetSiteProfile
    SpeedyNetSiteProfile.objects.filter(user=user).update(friends_count=user.friends.count())


