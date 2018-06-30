from django.db import models
from friendship.models import Friend
from django.core.exceptions import ValidationError


class BlockManager(models.Manager):
    def block(self, blocker, blocked):
        if blocker == blocked:
            raise ValidationError("Users cannot block themselves.")
        block, created = self.get_or_create(blocker=blocker, blocked=blocked)
        Friend.objects.remove_friend(blocker, blocked)
        return block

    def unblock(self, blocker, blocked):
        try:
            return self.get(blocker__id=blocker.id, blocked__id=blocked.id).delete()
        except self.model.DoesNotExist:
            return

    def has_blocked(self, blocker, blocked):
        return self.filter(blocker__id=blocker.id, blocked__id=blocked.id).exists()

    def there_is_block(self, user_1, user_2):
        return self.has_blocked(blocker=user_1, blocked=user_2) or self.has_blocked(blocker=user_2, blocked=user_1)
