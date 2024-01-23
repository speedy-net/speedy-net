from django.conf import settings as django_settings

from speedy.core.base import cache_manager

CACHE_TYPES = {
    'blocked': 'speedy-bo-%s',
    'blocking': 'speedy-bd-%s',
    'matches': 'speedy-m-%s',
    'received_friendship_requests_count': 'speedy-frrc-%s',
    'unread_chats_count': 'speedy-cuc-%s',
}

BUST_CACHES = {
    'all': list(CACHE_TYPES.keys()),
    'blocked': ['blocked'],
    'blocking': ['blocking'],
    'matches': ['matches'],
    'unread_chats_count': ['unread_chats_count'],
}


def cache_key(type, entity_pk):
    """
    Build the cache key for a particular type of cached value.
    """
    return CACHE_TYPES[type] % entity_pk


def bust_cache(type, entity_pk, version=None):
    """
    Bust the cache for a given type, can bust multiple caches.

    If BUST_ALL_CACHES_FOR_A_USER setting is True, do it. In this case, the type argument is ignored.
    """
    if (django_settings.BUST_ALL_CACHES_FOR_A_USER is True):
        bust_keys = BUST_CACHES['all']
    else:
        bust_keys = BUST_CACHES[type]
    keys = [CACHE_TYPES[k] % entity_pk for k in bust_keys]
    cache_manager.cache_delete_many(keys=keys, version=version)
