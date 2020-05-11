from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from speedy.core.base import cache_manager
from speedy.core.base.cache_manager import DEFAULT_TIMEOUT
from speedy.core.base.models import BaseManager
from speedy.core.accounts.models import Entity, User

CACHE_TYPES = {
    'blocked': 'speedy-bo-%s',
    'blocking': 'speedy-bd-%s',
}

BUST_CACHES = {
    'blocked': ['blocked'],
    'blocking': ['blocking'],
}


def cache_key(type, user_pk):
    """
    Build the cache key for a particular type of cached value.
    """
    return CACHE_TYPES[type] % user_pk


def bust_cache(type, user_pk):
    """
    Bust the cache for a given type, can bust multiple caches.
    """
    bust_keys = BUST_CACHES[type]
    keys = [CACHE_TYPES[k] % user_pk for k in bust_keys]
    cache_manager.cache_delete_many(keys)


def ensure_caches(user):
    """
    Ensure the cache for a given type.
    """
    from django.db.models import query

    if (not (isinstance(user, Entity))):
        return

    blocked_key = cache_key('blocked', user.pk)
    blocked_entities = cache_manager.cache_get(blocked_key, sliding_timeout=DEFAULT_TIMEOUT)
    if (blocked_entities is None):
        query.prefetch_related_objects([user], 'blocked_entities')
        cache_manager.cache_set(blocked_key, user._prefetched_objects_cache['blocked_entities'])
    else:
        if (not (hasattr(user, '_prefetched_objects_cache'))):
            user._prefetched_objects_cache = {}
        user._prefetched_objects_cache['blocked_entities'] = blocked_entities

    blocking_key = cache_key('blocking', user.pk)
    blocking_entities = cache_manager.cache_get(blocking_key, sliding_timeout=DEFAULT_TIMEOUT)
    if (blocking_entities is None):
        query.prefetch_related_objects([user], 'blocking_entities')
        cache_manager.cache_set(blocking_key, user._prefetched_objects_cache['blocking_entities'])
    else:
        if (not (hasattr(user, '_prefetched_objects_cache'))):
            user._prefetched_objects_cache = {}
        user._prefetched_objects_cache['blocking_entities'] = blocking_entities


class BlockManager(BaseManager):
    def _update_caches(self, blocker, blocked):
        """
        Update caches after block or unblock.
        """
        bust_cache('blocked', blocker.pk)
        bust_cache('blocking', blocked.pk)
        if hasattr(blocker, '_prefetched_objects_cache'):
            blocker._prefetched_objects_cache.pop('blocked_entities', None)
        if hasattr(blocked, '_prefetched_objects_cache'):
            blocked._prefetched_objects_cache.pop('blocking_entities', None)
        ensure_caches(user=blocker)

    def block(self, blocker, blocked):
        if (blocker == blocked):
            raise ValidationError(_("Users cannot block themselves."))

        block, created = self.get_or_create(blocker=blocker, blocked=blocked)
        self._update_caches(blocker=blocker, blocked=blocked)
        return block

    def unblock(self, blocker, blocked):
        self.filter(blocker__pk=blocker.pk, blocked__pk=blocked.pk).delete()
        self._update_caches(blocker=blocker, blocked=blocked)

    def has_blocked(self, blocker, blocked):
        if ((not (isinstance(blocker, Entity))) or (not (isinstance(blocked, Entity)))):
            return False
        if (blocker.blocked_entities.all()._result_cache is not None):
            return any(blocked.pk == block.blocked_id for block in blocker.blocked_entities.all())
        if (blocked.blocking_entities.all()._result_cache is not None):
            return any(blocker.pk == block.blocker_id for block in blocked.blocking_entities.all())
        return self.filter(blocker__pk=blocker.pk, blocked__pk=blocked.pk).exists()

    def there_is_block(self, user_1, user_2):
        return self.has_blocked(blocker=user_1, blocked=user_2) or self.has_blocked(blocker=user_2, blocked=user_1)

    def get_blocked_list_to_queryset(self, blocker):
        # filter out users that are only active in another language.
        blocked_users = User.objects.filter(pk__in=self.filter(blocker=blocker).values_list('blocked_id', flat=True))
        blocked_users = [u.pk for u in blocked_users if (u.profile.is_active)]

        return self.filter(blocker=blocker).filter(blocked__in=blocked_users).order_by('-date_created')


