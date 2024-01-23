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
    'matches': ['matches'],
}


def cache_key(cache_type, entity_pk):
    """
    Build the cache key for a particular type of cached value.
    """
    return CACHE_TYPES[cache_type].format(entity_pk=entity_pk)


def bust_cache(cache_type, entity_pk=None, entities_pks=None):
    """
    Bust the cache for a given type of cached value, can bust multiple caches.

    If BUST_ALL_CACHES_FOR_A_USER setting is True, do it. In this case, cache_type is ignored.

    :param cache_type:
    :param entity_pk:    Either entity_pk or entities_pks must be passed
    :param entities_pks: Either entity_pk or entities_pks must be passed
    """
    if (django_settings.BUST_ALL_CACHES_FOR_A_USER is True):
        bust_keys = BUST_CACHES['all']
    else:
        bust_keys = BUST_CACHES[cache_type]
    if (entity_pk is not None):
        entities_pks = [entity_pk]
    keys = [cache_key(cache_type=k, entity_pk=entity_pk) for k in bust_keys for entity_pk in entities_pks]
    cache_manager.cache_delete_many(keys=keys)


