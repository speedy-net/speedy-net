from django.conf import settings as django_settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from friendship.models import Friend

from speedy.core.base import cache_manager

CACHE_TYPES = {
    'received_friendship_requests_count': 'speedy-frrc-%s',
}


def cache_key(type, entity_pk):
    return CACHE_TYPES[type] % entity_pk


class FriendshipRequestManager:

    @classmethod
    def get_received_friendship_requests_count(cls, user):
        """
        Get received friendship requests count in Speedy Net or Speedy Match.
        Invalidate based on raw requests count.

        :type user: speedy.core.accounts.models.User
        """
        key = cache_key(type='received_friendship_requests_count', entity_pk=user.pk)
        cached_value = cache_manager.cache_get(key=key, sliding_timeout=DEFAULT_TIMEOUT)
        raw_count = len(Friend.objects.requests(user=user))
        if ((cached_value is not None) and (cached_value['site_id'] == django_settings.SITE_ID) and (cached_value['raw_count'] == raw_count)):
            count = cached_value['count']
        else:
            count = len(user.get_received_friendship_requests())
            value = {
                'count': count,
                'raw_count': raw_count,
                'site_id': django_settings.SITE_ID,
            }
            cache_manager.cache_set(key=key, value=value)
        return count


