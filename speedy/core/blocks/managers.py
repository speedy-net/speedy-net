from friendship.models import Friend

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from speedy.core import cache_manager
from speedy.core.base.models import BaseManager
from speedy.core.accounts.models import User


class BlockManager(BaseManager):
    def block(self, blocker, blocked):
        from speedy.match.likes.models import UserLike

        if (blocker == blocked):
            raise ValidationError(_("Users cannot block themselves."))

        block, created = self.get_or_create(blocker=blocker, blocked=blocked)
        Friend.objects.remove_friend(from_user=blocker, to_user=blocked)
        UserLike.objects.remove_like(from_user=blocker, to_user=blocked)
        cache_manager.cache_delete_many([blocker.received_friendship_requests_count_cache_key, blocked.received_friendship_requests_count_cache_key])
        return block

    def unblock(self, blocker, blocked):
        self.filter(blocker__pk=blocker.pk, blocked__pk=blocked.pk).delete()
        cache_manager.cache_delete_many([blocker.received_friendship_requests_count_cache_key, blocked.received_friendship_requests_count_cache_key])

    def has_blocked(self, blocker, blocked):
        if (blocker.blocked_entities.all()._result_cache is not None):
            return (blocked in blocker.blocked_entities.all())
        if (blocked.blocking_entities.all()._result_cache is not None):
            return (blocker in blocked.blocking_entities.all())
        return (blocked in blocker.blocked_entities.all())

    def there_is_block(self, user_1, user_2):
        return self.has_blocked(blocker=user_1, blocked=user_2) or self.has_blocked(blocker=user_2, blocked=user_1)

    def get_blocked_list_to_queryset(self, blocker):
        # filter out users that are only active in another language.
        blocked_users = User.objects.filter(pk__in=self.filter(blocker=blocker).values_list('blocked_id', flat=True))
        blocked_users = [u.pk for u in blocked_users if (u.profile.is_active)]

        return self.filter(blocker=blocker).filter(blocked__in=blocked_users).order_by('-date_created')


