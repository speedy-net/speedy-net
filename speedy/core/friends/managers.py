from django.conf import settings as django_settings
from friendship.models import Friend, cache as friendship_cache, cache_key as friendship_cache_key

from speedy.core.accounts.cache_helper import cache_key
from speedy.core.base import cache_manager


class FriendManager:

    @classmethod
    def get_friends_count(cls, user):
        """
        Get friends count independent of Speedy Net or Speedy Match logic.
        Cache invalidated by django-friendship as registered in BUST_CACHES in speedy.core.patches.friendship_patches.
        Better performance than len(Friend.objects.friends(user=user)). Equivalent to user.friends.count() with cache.

        :type user: speedy.core.accounts.models.User
        """
        key = friendship_cache_key(type='friends_count', user_pk=user.pk)
        friends_count = friendship_cache.get(key=key)

        if (friends_count is None):
            friends_count = Friend.objects.filter(to_user=user).count()
            friendship_cache.set(key=key, value=friends_count)

        return friends_count


class FriendshipRequestManager:

    @classmethod
    def get_received_friendship_requests_count(cls, user):
        """
        Return the number of received friendship requests in the current site.
        In Speedy Net, only active users.
        In Speedy Match, only active users who match the current user and is dependent on language.
        Invalidate based on raw requests count.

        :type user: speedy.core.accounts.models.User
        :return: The number of received friendship requests in the current site.
        """
        key = cache_key(cache_type='received_friendship_requests_count', entity_pk=user.pk)
        cached_value = cache_manager.cache_get(key=key, sliding_timeout=django_settings.CACHE_GET_RECEIVED_FRIENDSHIP_REQUESTS_COUNT_SLIDING_TIMEOUT)
        raw_count = len(Friend.objects.requests(user=user))
        if ((cached_value is not None) and (cached_value['raw_count'] == raw_count)):
            count = cached_value['count']
        else:
            count = len(user.get_received_friendship_requests())
            value = {
                'count': count,
                'raw_count': raw_count,
            }
            cache_manager.cache_set(key=key, value=value, timeout=django_settings.CACHE_SET_RECEIVED_FRIENDSHIP_REQUESTS_COUNT_TIMEOUT)
        return count


