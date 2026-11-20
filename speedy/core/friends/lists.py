"""
Lazy, cached lists of friends of Speedy Core, used to paginate friend lists without loading all the friends of a user on every request.
"""
from django.conf import settings as django_settings

from friendship.models import Friend

from speedy.core.base import cache_manager
from speedy.core.accounts.cache_helper import cache_key


class SiteFriendsList(object):
    """
    A read-only sequence of the friendships (``Friend`` instances) of a user in the current site, ordered like ``User.site_friends``.

    The ordered list of friendship ids is cached, and only the friendships which are requested (by slicing) are loaded from the database.
    This makes it cheap to display one page of a long friend list.
    """

    def __init__(self, user):
        """
        Load the ordered list of friendship ids from the cache, or compute it (and cache it) if it isn't cached.

        :param user: The user whose friends are listed.
        :type user: speedy.core.accounts.models.User
        """
        self.user = user
        self._preloaded = {}
        key = cache_key(cache_type='site_friends', entity_pk=user.pk)
        ids = cache_manager.cache_get(key=key, sliding_timeout=django_settings.CACHE_GET_SITE_FRIENDS_SLIDING_TIMEOUT)
        if (ids is None):
            friendships = user.site_friends
            ids = [friendship.pk for friendship in friendships]
            self._preloaded = {friendship.pk: friendship for friendship in friendships}
            cache_manager.cache_set(key=key, value=ids, timeout=django_settings.CACHE_SET_SITE_FRIENDS_TIMEOUT)
        self._ids = ids

    def __len__(self):
        return len(self._ids)

    def __getitem__(self, item):
        if (isinstance(item, slice)):
            return self._load(ids=self._ids[item])
        return self._load(ids=[self._ids[item]])[0]

    def __iter__(self):
        return iter(self._load(ids=self._ids))

    def _load(self, ids):
        """
        Return the friendships with the given ids, in the same order, excluding friends who are no longer active.

        :param ids: The ids of the friendships to load.
        :type ids: list
        :return: The friendships.
        :rtype: list
        """
        from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

        missing_ids = [pk for pk in ids if (pk not in self._preloaded)]
        if (missing_ids):
            qs = Friend.objects.filter(pk__in=missing_ids).select_related('to_user').prefetch_related("from_user", "from_user__{}".format(SpeedyNetSiteProfile.RELATED_NAME), "from_user__{}".format(SpeedyMatchSiteProfile.RELATED_NAME), 'from_user__photo')
            for friendship in qs:
                self._preloaded[friendship.pk] = friendship
        friendships = [self._preloaded[pk] for pk in ids if (pk in self._preloaded)]
        return [friendship for friendship in friendships if (friendship.from_user.profile.is_active)]
