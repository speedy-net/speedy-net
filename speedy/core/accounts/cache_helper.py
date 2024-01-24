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
    'blocked': ['blocked', 'matches'],
    'blocking': ['blocking', 'matches'],
    'received_friendship_requests_count': ['received_friendship_requests_count'],
    'unread_chats_count': ['unread_chats_count'],
    'matches': ['matches', 'received_friendship_requests_count'],
}


def cache_key(cache_type, entity_pk):
    """
    Build the cache key for a particular type of cached value.

    :param cache_type: Required. One of the keys of CACHE_TYPES.
    :param entity_pk: Required. The pk of the entity.
    :return: A cache key.
    """
    return CACHE_TYPES[cache_type].format(entity_pk=entity_pk)


def get_keys_for_bust_cache(cache_type, entities_pks):
    """
    Get the bust cache keys for a given type of cached value.

    If BUST_ALL_CACHES_FOR_A_USER setting is True, return all cache keys. In this case, cache_type is ignored.

    :param cache_type: Required. One of the keys of BUST_CACHES.
    :param entities_pks: Required. A list of entity pks.
    :return: A list of cache keys.
    """
    if (django_settings.BUST_ALL_CACHES_FOR_A_USER is True):
        bust_keys = BUST_CACHES['all']
    else:
        bust_keys = BUST_CACHES[cache_type]
    return [cache_key(cache_type=k, entity_pk=entity_pk) for k in bust_keys for entity_pk in entities_pks]


def bust_cache_by_keys(cache_keys):
    """
    Bust the cache for the given cache_keys.

    :param cache_keys: Required. A list of cache keys.
    """
    cache_manager.cache_delete_many(keys=cache_keys)


def bust_cache(cache_type, entities_pks):
    """
    Bust the cache for a given type of cached value, can bust multiple caches.

    If BUST_ALL_CACHES_FOR_A_USER setting is True, do it. In this case, cache_type is ignored.

    :param cache_type: Required. One of the keys of BUST_CACHES.
    :param entities_pks: Required. A list of entity pks.
    """
    keys = get_keys_for_bust_cache(cache_type=cache_type, entities_pks=entities_pks)
    bust_cache_by_keys(cache_keys=keys)


