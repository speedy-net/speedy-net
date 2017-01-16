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
