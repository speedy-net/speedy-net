from django.db import models
from django.dispatch import receiver
from friendship.models import Friend, FriendshipRequest

from speedy.core.accounts.cache_helper import bust_cache


@receiver(signal=models.signals.post_save, sender=Friend)
def update_all_friends_count_on_new_friend(sender, instance: Friend, created, **kwargs):
    """
    Update the "to user"'s all friends count on their Speedy Net profile whenever a new ``Friend`` instance is created.

    :param sender: The model class that sent the signal.
    :param instance: The ``Friend`` instance that was saved.
    :type instance: friendship.models.Friend
    :param created: Whether this is a newly created instance (as opposed to an update of an existing one).
    :param kwargs: Additional keyword arguments passed by the signal.
    """
    if (created):
        user = instance.to_user
        user.speedy_net_profile._update_all_friends_count()
        user.speedy_net_profile.save()


@receiver(signal=models.signals.post_delete, sender=Friend)
def update_all_friends_count_on_unfriend(sender, instance: Friend, **kwargs):
    """
    Update the "to user"'s all friends count on their Speedy Net profile whenever a ``Friend`` instance is deleted.

    :param sender: The model class that sent the signal.
    :param instance: The ``Friend`` instance that was deleted.
    :type instance: friendship.models.Friend
    :param kwargs: Additional keyword arguments passed by the signal, including ``origin`` (the object that originated the cascade delete, if any).
    """
    user = instance.to_user
    # Check origin because for cascade delete User -> Friend, accessing user.speedy_net_profile will re-create deleted SpeedyNetSiteProfile.
    if (not (user == kwargs.get('origin'))):
        user.speedy_net_profile._update_all_friends_count()
        user.speedy_net_profile.save()


@receiver(signal=models.signals.post_save, sender=FriendshipRequest)
def invalidate_received_friendship_requests_count_after_friendship_request_created(sender, instance: FriendshipRequest, **kwargs):
    """
    Invalidate the cached received friendship requests count of both users involved whenever a ``FriendshipRequest`` instance is created.

    :param sender: The model class that sent the signal.
    :param instance: The ``FriendshipRequest`` instance that was saved.
    :type instance: friendship.models.FriendshipRequest
    :param kwargs: Additional keyword arguments passed by the signal.
    """
    bust_cache(cache_type='received_friendship_requests_count', entities_pks=[instance.from_user.pk, instance.to_user.pk])


@receiver(signal=models.signals.post_delete, sender=FriendshipRequest)
def invalidate_received_friendship_requests_count_after_friendship_request_deleted(sender, instance: FriendshipRequest, **kwargs):
    """
    Invalidate the cached received friendship requests count of both users involved whenever a ``FriendshipRequest`` instance is deleted.

    :param sender: The model class that sent the signal.
    :param instance: The ``FriendshipRequest`` instance that was deleted.
    :type instance: friendship.models.FriendshipRequest
    :param kwargs: Additional keyword arguments passed by the signal.
    """
    bust_cache(cache_type='received_friendship_requests_count', entities_pks=[instance.from_user.pk, instance.to_user.pk])


