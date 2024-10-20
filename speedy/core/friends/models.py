from django.db import models
from django.dispatch import receiver
from friendship.models import Friend, FriendshipRequest

from speedy.core.accounts.cache_helper import bust_cache
from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile


@receiver(signal=models.signals.post_save, sender=Friend)
def update_all_friends_count_on_new_friend(sender, instance: Friend, created, **kwargs):
    if (created):
        user = instance.to_user
        user.speedy_net_profile.all_friends_count = user.friends.count()
        user.speedy_net_profile.save()


@receiver(signal=models.signals.post_delete, sender=Friend)
def update_all_friends_count_on_unfriend(sender, instance: Friend, **kwargs):
    user = instance.to_user
    # Do .filter(...).update(...) because for cascade delete User -> Friend, accessing user.speedy_net_profile will re-create deleted SpeedyNetSiteProfile
    SpeedyNetSiteProfile.objects.filter(user=user).update(all_friends_count=user.friends.count())


@receiver(signal=models.signals.post_save, sender=FriendshipRequest)
def invalidate_received_friendship_requests_count_after_friendship_request_created(sender, instance: FriendshipRequest, **kwargs):
    bust_cache(cache_type='received_friendship_requests_count', entities_pks=[instance.from_user.pk, instance.to_user.pk])


@receiver(signal=models.signals.post_delete, sender=FriendshipRequest)
def invalidate_received_friendship_requests_count_after_friendship_request_deleted(sender, instance: FriendshipRequest, **kwargs):
    bust_cache(cache_type='received_friendship_requests_count', entities_pks=[instance.from_user.pk, instance.to_user.pk])

