from django.conf import settings as django_settings
from friendship.models import Friend

from speedy.core.accounts.cache_helper import cache_key
from speedy.core.base import cache_manager


class FriendshipRequestManager:

    @classmethod
    def get_received_friendship_requests_count(cls, user):
        """
        Get received friendship requests count in Speedy Net or Speedy Match.
        Invalidate based on raw requests count.

        :type user: speedy.core.accounts.models.User
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


