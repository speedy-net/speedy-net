from django.conf import settings as django_settings

from speedy.core.base import cache_manager

CACHE_TYPES = {
    'blocked': 'speedy-core-blocks-blocked-{entity_pk}',
    'blocking': 'speedy-core-blocks-blocking-{entity_pk}',
    'received_friendship_requests_count': 'speedy-core-friends-received-friendship-requests-count-{entity_pk}',
    'unread_chats_count': 'speedy-core-messages-unread-chats-count-{entity_pk}',
    'matches': 'speedy-match-accounts-matches-{entity_pk}',
}

BUST_CACHES = {
    'all': list(CACHE_TYPES.keys()),
    'blocked': ['blocked'],
    'blocking': ['blocking'],
    'received_friendship_requests_count': ['received_friendship_requests_count'],
    'unread_chats_count': ['unread_chats_count'],
    'matches': ['matches'],
}


def cache_key(cache_type, entity_pk):
    """
    Build the cache key for a particular type of cached value.
    """
    return CACHE_TYPES[cache_type].format(entity_pk=entity_pk)


def bust_cache(cache_type, entity_pk, version=None):
    """
    Bust the cache for a given type of cached value, can bust multiple caches.

    If BUST_ALL_CACHES_FOR_A_USER setting is True, do it. In this case, cache_type is ignored.
    """
    if (django_settings.BUST_ALL_CACHES_FOR_A_USER is True):
        bust_keys = BUST_CACHES['all']
    else:
        bust_keys = BUST_CACHES[cache_type]
    keys = [cache_key(cache_type=cache_type, entity_pk=entity_pk) for cache_type in bust_keys]
    cache_manager.cache_delete_many(keys=keys, version=version)


