from django.db import models
from friendship.models import Friend


class BlockManager(models.Manager):
    def block(self, blocker, blockee):
        block, created = self.get_or_create(blocker=blocker, blockee=blockee)
        Friend.objects.remove_friend(blocker, blockee)
        return block

    def unblock(self, blocker, blockee):
        try:
            return self.get(blocker__id=blocker.id, blockee__id=blockee.id).delete()
        except self.model.DoesNotExist:
            return

    def has_blocked(self, blocker, blockee):
        return self.filter(blocker__id=blocker.id, blockee__id=blockee.id).exists()

    def there_is_block(self, user_1, user_2):
        return self.has_blocked(blocker=user_1, blockee=user_2) or self.has_blocked(blocker=user_2, blockee=user_1)
