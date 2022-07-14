from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from speedy.core.base import cache_manager
from speedy.core.base.cache_manager import DEFAULT_TIMEOUT
from speedy.core.base.managers import BaseManager
from speedy.core.accounts.models import Entity, User

CACHE_TYPES = {
    'blocked': 'speedy-bo-%s',
    'blocking': 'speedy-bd-%s',
}

BUST_CACHES = {
    'blocked': ['blocked'],
    'blocking': ['blocking'],
}


def cache_key(type, entity_pk):
    """
    Build the cache key for a particular type of cached value.
    """
    return CACHE_TYPES[type] % entity_pk


def bust_cache(type, entity_pk, version=None):
    """
    Bust the cache for a given type, can bust multiple caches.
    """
    bust_keys = BUST_CACHES[type]
    keys = [CACHE_TYPES[k] % entity_pk for k in bust_keys]
    cache_manager.cache_delete_many(keys=keys, version=version)


class BlockManager(BaseManager):
    def _update_caches(self, blocker, blocked):
        """
        Update caches after block or unblock.
        """
        bust_cache(type='blocked', entity_pk=blocker.pk)
        bust_cache(type='blocked', entity_pk=blocker.pk, version=2)
        bust_cache(type='blocking', entity_pk=blocked.pk)
        bust_cache(type='blocking', entity_pk=blocked.pk, version=2)
        if ('blocked_entities_ids' in blocker.__dict__):
            del blocker.blocked_entities_ids
        if ('blocking_entities_ids' in blocked.__dict__):
            del blocked.blocking_entities_ids

    def block(self, blocker, blocked):
        if (blocker == blocked):
            raise ValidationError(_("Users cannot block themselves."))

        block, created = self.get_or_create(blocker=blocker, blocked=blocked)
        self._update_caches(blocker=blocker, blocked=blocked)
        return block

    def unblock(self, blocker, blocked):
        for block in self.filter(blocker__pk=blocker.pk, blocked__pk=blocked.pk):
            block.delete()
        self._update_caches(blocker=blocker, blocked=blocked)

    def has_blocked(self, blocker, blocked):
        if ((not (isinstance(blocker, Entity))) or (not (isinstance(blocked, Entity)))):
            return False
        if ('blocked_entities_ids' in blocker.__dict__):
            return (blocked.pk in blocker.blocked_entities_ids)
        if ('blocking_entities_ids' in blocked.__dict__):
            return (blocker.pk in blocked.blocking_entities_ids)
        return (blocked.pk in blocker.blocked_entities_ids)

    def there_is_block(self, entity_1, entity_2):
        return self.has_blocked(blocker=entity_1, blocked=entity_2) or self.has_blocked(blocker=entity_2, blocked=entity_1)

    def get_blocked_entities_ids(self, blocker):
        blocked_key = cache_key(type='blocked', entity_pk=blocker.pk)
        try:
            blocked_entities_ids = cache_manager.cache_get(key=blocked_key, version=2, sliding_timeout=DEFAULT_TIMEOUT)
        except Exception:
            # ~~~~ TODO: Log warning
            blocked_entities_ids = None
        if (blocked_entities_ids is None):
            blocked_entities_ids = list(self.filter(blocker=blocker).values_list('blocked_id', flat=True))
            try:
                cache_manager.cache_set(key=blocked_key, value=blocked_entities_ids, version=2)
            except Exception:
                # ~~~~ TODO: Log warning
                pass
        return blocked_entities_ids

    def get_blocking_entities_ids(self, blocked):
        blocking_key = cache_key(type='blocking', entity_pk=blocked.pk)
        try:
            blocking_entities_ids = cache_manager.cache_get(key=blocking_key, version=2, sliding_timeout=DEFAULT_TIMEOUT)
        except Exception:
            # ~~~~ TODO: Log warning
            blocking_entities_ids = None
        if (blocking_entities_ids is None):
            blocking_entities_ids = list(self.filter(blocked=blocked).values_list('blocker_id', flat=True))
            try:
                cache_manager.cache_set(key=blocking_key, value=blocking_entities_ids, version=2)
            except Exception:
                # ~~~~ TODO: Log warning
                pass
        return blocking_entities_ids

    def get_blocked_list_to_queryset(self, blocker):
        from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

        # Include also inactive users.
        blocked_users = User.objects.filter(pk__in=self.filter(blocker=blocker).values_list('blocked_id', flat=True))

        return self.filter(blocker=blocker).filter(blocked__in=blocked_users).prefetch_related("blocked", "blocked__user", "blocked__user__{}".format(SpeedyNetSiteProfile.RELATED_NAME), "blocked__user__{}".format(SpeedyMatchSiteProfile.RELATED_NAME), "blocked__user__photo").order_by('-date_created')


