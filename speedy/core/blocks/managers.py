import logging

from django.utils.translation import gettext_lazy as _
from django.conf import settings as django_settings
from django.core.exceptions import ValidationError

from speedy.core.accounts.cache_helper import bust_cache_by_keys, cache_key, get_keys_for_bust_cache
from speedy.core.base import cache_manager
from speedy.core.base.managers import BaseManager
from speedy.core.accounts.models import Entity, User

logger = logging.getLogger(__name__)


class BlockManager(BaseManager):
    """
    Manager for the Block model, providing operations to block/unblock entities and query block relationships.

    Methods:
        _update_caches(self, blocker, blocked): Invalidate the cached blocked/blocking entities ids after a block or unblock.
        block(self, blocker, blocked): Block an entity, creating a Block instance if one doesn't already exist.
        unblock(self, blocker, blocked): Remove the Block instance(s) between blocker and blocked.
        remove_all_blocks_by_entity(self, blocker): Remove all blocks created by the given entity.
        remove_all_blocks_of_entity(self, blocked): Remove all blocks targeting the given entity.
        has_blocked(self, blocker, blocked): Check whether blocker has blocked blocked.
        there_is_block(self, entity_1, entity_2): Check whether there is a block in either direction between the two entities.
        get_blocked_entities_ids(self, blocker): Get the (cached) ids of entities blocked by blocker.
        get_blocking_entities_ids(self, blocked): Get the (cached) ids of entities blocking blocked.
        get_blocked_list_to_queryset(self, blocker): Get a queryset of Block instances for the entities blocker has blocked (including inactive users).
    """
    def _update_caches(self, blocker, blocked):
        """
        Update caches after block or unblock.
        """
        keys1 = get_keys_for_bust_cache(cache_type='blocked', entities_pks=[blocker.pk])
        keys2 = get_keys_for_bust_cache(cache_type='blocking', entities_pks=[blocked.pk])
        bust_cache_by_keys(cache_keys=keys1 + keys2)
        if ('blocked_entities_ids' in blocker.__dict__):
            del blocker.blocked_entities_ids
        if ('blocking_entities_ids' in blocked.__dict__):
            del blocked.blocking_entities_ids

    def block(self, blocker, blocked):
        """
        Block an entity. If blocker has already blocked blocked, return the existing Block instance.

        :param blocker: The entity that blocks.
        :type blocker: speedy.core.accounts.models.Entity
        :param blocked: The entity that is blocked.
        :type blocked: speedy.core.accounts.models.Entity
        :return: The Block instance.
        :rtype: speedy.core.blocks.models.Block
        :raises django.core.exceptions.ValidationError: If blocker and blocked are the same entity.
        """
        if (blocker == blocked):
            raise ValidationError(_("Users cannot block themselves."))

        block, created = self.get_or_create(blocker=blocker, blocked=blocked)
        self._update_caches(blocker=blocker, blocked=blocked)
        return block

    def unblock(self, blocker, blocked):
        """
        Remove the block (if any) of blocked by blocker.

        :param blocker: The entity that blocks.
        :type blocker: speedy.core.accounts.models.Entity
        :param blocked: The entity that is blocked.
        :type blocked: speedy.core.accounts.models.Entity
        """
        for block in self.filter(blocker__pk=blocker.pk, blocked__pk=blocked.pk):
            block.delete()
        self._update_caches(blocker=blocker, blocked=blocked)

    def remove_all_blocks_by_entity(self, blocker):
        """
        Remove all blocks created by blocker.

        :param blocker: The entity that blocks.
        :type blocker: speedy.core.accounts.models.Entity
        """
        for block in self.filter(blocker__pk=blocker.pk):
            block.delete()
        self._update_caches(blocker=blocker, blocked=blocker)

    def remove_all_blocks_of_entity(self, blocked):
        """
        Remove all blocks targeting blocked.

        :param blocked: The entity that is blocked.
        :type blocked: speedy.core.accounts.models.Entity
        """
        for block in self.filter(blocked__pk=blocked.pk):
            block.delete()
        self._update_caches(blocker=blocked, blocked=blocked)

    def has_blocked(self, blocker, blocked):
        """
        Check whether blocker has blocked blocked.

        :param blocker: The entity that may have blocked blocked.
        :type blocker: speedy.core.accounts.models.Entity
        :param blocked: The entity that may be blocked.
        :type blocked: speedy.core.accounts.models.Entity
        :return: True if blocker has blocked blocked, False otherwise (including when either argument is not an Entity).
        :rtype: bool
        """
        if ((not (isinstance(blocker, Entity))) or (not (isinstance(blocked, Entity)))):
            return False
        if ('blocked_entities_ids' in blocker.__dict__):
            return (blocked.pk in blocker.blocked_entities_ids)
        if ('blocking_entities_ids' in blocked.__dict__):
            return (blocker.pk in blocked.blocking_entities_ids)
        return (blocked.pk in blocker.blocked_entities_ids)

    def there_is_block(self, entity_1, entity_2):
        """
        Check whether there is a block between the two entities, in either direction.

        :param entity_1: The first entity.
        :type entity_1: speedy.core.accounts.models.Entity
        :param entity_2: The second entity.
        :type entity_2: speedy.core.accounts.models.Entity
        :return: True if entity_1 has blocked entity_2 or entity_2 has blocked entity_1, False otherwise.
        :rtype: bool
        """
        return self.has_blocked(blocker=entity_1, blocked=entity_2) or self.has_blocked(blocker=entity_2, blocked=entity_1)

    def get_blocked_entities_ids(self, blocker):
        """
        Get the ids of entities blocked by blocker, using the cache when available.

        :param blocker: The entity that blocks.
        :type blocker: speedy.core.accounts.models.Entity
        :return: A list of ids of the entities blocked by blocker.
        :rtype: list
        """
        blocked_key = cache_key(cache_type='blocked', entity_pk=blocker.pk)
        try:
            blocked_entities_ids = cache_manager.cache_get(key=blocked_key, sliding_timeout=django_settings.CACHE_GET_BLOCKED_ENTITIES_IDS_SLIDING_TIMEOUT)
        except Exception as e:
            logger.warning("BlockManager::get_blocked_entities_ids:cache_manager.cache_get raised an exception, blocker={blocker}, Exception={e}".format(
                blocker=blocker,
                e=str(e),
            ))
            blocked_entities_ids = None
        if (blocked_entities_ids is None):
            blocked_entities_ids = list(self.filter(blocker=blocker).values_list('blocked_id', flat=True))
            try:
                cache_manager.cache_set(key=blocked_key, value=blocked_entities_ids, timeout=django_settings.CACHE_SET_BLOCKED_ENTITIES_IDS_TIMEOUT)
            except Exception as e:
                logger.warning("BlockManager::get_blocked_entities_ids:cache_manager.cache_set raised an exception, blocker={blocker}, Exception={e}".format(
                    blocker=blocker,
                    e=str(e),
                ))
        return blocked_entities_ids

    def get_blocking_entities_ids(self, blocked):
        """
        Get the ids of entities blocking blocked, using the cache when available.

        :param blocked: The entity that is blocked.
        :type blocked: speedy.core.accounts.models.Entity
        :return: A list of ids of the entities blocking blocked.
        :rtype: list
        """
        blocking_key = cache_key(cache_type='blocking', entity_pk=blocked.pk)
        try:
            blocking_entities_ids = cache_manager.cache_get(key=blocking_key, sliding_timeout=django_settings.CACHE_GET_BLOCKING_ENTITIES_IDS_SLIDING_TIMEOUT)
        except Exception as e:
            logger.warning("BlockManager::get_blocking_entities_ids:cache_manager.cache_get raised an exception, blocked={blocked}, Exception={e}".format(
                blocked=blocked,
                e=str(e),
            ))
            blocking_entities_ids = None
        if (blocking_entities_ids is None):
            blocking_entities_ids = list(self.filter(blocked=blocked).values_list('blocker_id', flat=True))
            try:
                cache_manager.cache_set(key=blocking_key, value=blocking_entities_ids, timeout=django_settings.CACHE_SET_BLOCKING_ENTITIES_IDS_TIMEOUT)
            except Exception as e:
                logger.warning("BlockManager::get_blocking_entities_ids:cache_manager.cache_set raised an exception, blocked={blocked}, Exception={e}".format(
                    blocked=blocked,
                    e=str(e),
                ))
        return blocking_entities_ids

    def get_blocked_list_to_queryset(self, blocker):
        """
        Get a queryset of Block instances for the entities blocker has blocked, including blocked inactive users, with related data prefetched.

        :param blocker: The entity that blocks.
        :type blocker: speedy.core.accounts.models.Entity
        :return: A queryset of Block instances ordered by date_created descending.
        :rtype: django.db.models.QuerySet
        """
        from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

        # Include also inactive users.
        blocked_users = User.objects.filter(pk__in=self.filter(blocker=blocker).values_list('blocked_id', flat=True))

        return self.filter(blocker=blocker).filter(blocked__in=blocked_users).prefetch_related("blocked", "blocked__user", "blocked__user__{}".format(SpeedyNetSiteProfile.RELATED_NAME), "blocked__user__{}".format(SpeedyMatchSiteProfile.RELATED_NAME), "blocked__user__photo").order_by('-date_created')


